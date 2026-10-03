"""Idempotent demo data: staff accounts, made-up patients with QR codes, and a populated clinic day.

    python manage.py seed_demo [--password PW]

Re-running keeps the accounts and rebuilds the demo patients' visits so every dashboard has "today" data.
Demo patients are the ones whose email ends with @demo.clinic.local.
"""
import hashlib
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from patients.models import DEPARTMENT_CHOICES, Doctor, Patient, StaffProfile
from patients.utils import generate_qr_code
from dashboard.models import AuditLog
from vaccinations.models import PatientVaccination, VaccineDose, VaccineType
from visits.models import (
    Laboratory, LabResult, Prescription, PrescriptionMedicine, ServiceType,
    VaccinationRecord, VaccinationType, Visit,
)

DEMO_DOMAIN = 'demo.clinic.local'
DEPTS = [d[0] for d in DEPARTMENT_CHOICES]

STAFF = [  # (username, group)
    ('reception1', 'Reception'), ('reception_account', 'Reception'),
    ('lab1', 'Laboratory'), ('laboratory_account', 'Laboratory'),
    ('pharmacy1', 'Pharmacy'), ('pharmacy_account', 'Pharmacy'),
    ('vaccination1', 'Vaccination'), ('vaccination_account', 'Vaccination'),
]
PATIENTS = [  # (full name, age, address, contact)
    ('Maria Clara Santos', 34, 'Purok 3, Brgy. San Roque', '09171234501'),
    ('Juan Miguel dela Cruz', 45, 'Purok 1, Brgy. Poblacion', '09171234502'),
    ('Ana Liza Reyes', 28, 'Purok 5, Brgy. Bagumbayan', '09171234503'),
    ('Jose Antonio Ramos', 61, 'Purok 2, Brgy. San Isidro', '09171234504'),
    ('Katrina Mae Villanueva', 9, 'Purok 4, Brgy. Poblacion', '09171234505'),
    ('Eduardo Bautista', 52, 'Purok 6, Brgy. San Roque', '09171234506'),
    ('Rosario Aquino', 73, 'Purok 1, Brgy. Bagumbayan', '09171234507'),
    ('Paolo Gabriel Mendoza', 19, 'Purok 7, Brgy. San Isidro', '09171234508'),
    ('Lourdes Castillo', 38, 'Purok 2, Brgy. Poblacion', '09171234509'),
    ('Miguel Angelo Torres', 5, 'Purok 3, Brgy. Bagumbayan', '09171234510'),
    ('Grace Anne Flores', 41, 'Purok 8, Brgy. San Roque', '09171234511'),
    ('Ramon Dizon', 57, 'Purok 5, Brgy. San Isidro', '09171234512'),
]
MEDS = [
    ('Paracetamol', '500mg', 'Every 6 hours', '5 days', '20 tablets'),
    ('Amoxicillin', '500mg', 'Every 8 hours', '7 days', '21 capsules'),
    ('Cetirizine', '10mg', 'Once daily', '7 days', '7 tablets'),
    ('Losartan', '50mg', 'Once daily', '30 days', '30 tablets'),
    ('Ibuprofen', '400mg', 'Every 8 hours', '3 days', '9 tablets'),
]
DIAGNOSES = [
    ('Fever, headache, body malaise', 'Viral syndrome'),
    ('Cough and colds for 3 days', 'Acute upper respiratory infection'),
    ('Skin rash, itchiness', 'Allergic dermatitis'),
    ('Elevated blood pressure, dizziness', 'Hypertension, stage 1'),
    ('Ear pain, difficulty hearing', 'Otitis media'),
]
LAB_RESULTS = {
    'Hematology': {'hemoglobin': '13.8 g/dL', 'wbc': '7.2 x10^9/L', 'platelets': '250 x10^9/L'},
    'Clinical Chemistry': {'glucose': '92 mg/dL', 'cholesterol': '178 mg/dL', 'creatinine': '0.9 mg/dL'},
    'Clinical Microscopy': {'urinalysis': 'Normal', 'color': 'Yellow', 'pus cells': '0-2/hpf'},
}


class Command(BaseCommand):
    help = 'Create/refresh demo accounts, patients and a populated clinic day (idempotent).'

    def add_arguments(self, parser):
        parser.add_argument('--password', default='admin123', help='Password for newly created demo accounts (local/dev only).')
        parser.add_argument('--reset-passwords', action='store_true', help='Also reset the password of accounts that already exist.')

    @transaction.atomic
    def handle(self, *args, **opts):
        self.pw = opts['password']
        self.reset = opts['reset_passwords']
        self.now = timezone.now()
        call_command('bootstrap_roles', verbosity=0)
        self.groups = {n: Group.objects.get_or_create(name=n)[0] for n in
                       ['Reception', 'Doctor', 'Laboratory', 'Pharmacy', 'Vaccination', 'Patient', 'Admin']}
        self.svc = {n: ServiceType.objects.get_or_create(name=n)[0]
                    for n in ['Laboratory', 'Vaccination', *[v for v, _ in Laboratory.choices]]}
        self._admin()
        self.users = {u: self._user(u, g) for u, g in STAFF}
        self.doctors = {d: self._doctor(d) for d in DEPTS}
        self._reset_demo_patients()
        self.patients = [self._patient(*p) for p in PATIENTS]
        self._history()
        self._queues()
        self._vaccine_schedules()
        self._audit()
        self.stdout.write(self.style.SUCCESS(
            f'Demo ready: {len(self.users) + len(self.doctors) + 1} staff accounts, {len(self.patients)} patients.'))

    # -- accounts ---------------------------------------------------------
    def _user(self, username, group, email=None, **extra):
        u, created = User.objects.get_or_create(
            username=username, defaults={'email': email or f'{username}@clinic.local', **extra})
        if created or self.reset:
            u.set_password(self.pw)
            u.save()
        u.groups.add(self.groups[group])
        role = {'Reception': 'reception', 'Doctor': 'doctor', 'Laboratory': 'lab', 'Pharmacy': 'pharmacy',
                'Vaccination': 'vaccination_staff'}.get(group)
        if role:
            StaffProfile.objects.update_or_create(user=u, defaults={'role': role})
        return u

    def _admin(self):
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@example.com', self.pw)

    def _doctor(self, dept):
        username = 'doctor_' + dept.lower().replace('-', '')
        u = self._user(username, 'Doctor', first_name='Dr', last_name=dept)
        Doctor.objects.update_or_create(user=u, defaults={
            'full_name': f'Dr. {dept} Specialist', 'specialization': dept, 'must_change_password': False})
        return u

    def _reset_demo_patients(self):
        Visit.objects.filter(patient__email__endswith='@' + DEMO_DOMAIN).delete()

    def _patient(self, name, age, address, contact):
        slug = slugify(name)
        email = f'{slug}@{DEMO_DOMAIN}'
        user = self._user(slug, 'Patient', email=email)
        p, created = Patient.objects.get_or_create(email=email, defaults={
            'user': user, 'full_name': name, 'age': age, 'address': address, 'contact': contact,
            'patient_code': hashlib.md5(slug.encode()).hexdigest()[:10].upper()})
        if not p.qr_code:
            generate_qr_code(p)
        return p

    # -- visit builders ---------------------------------------------------
    def _visit(self, patient, service, ago_min=0, days=0, **kw):
        v = Visit.objects.create(patient=patient, service=service, **kw)
        Visit.objects.filter(pk=v.pk).update(timestamp=self.now - timedelta(days=days, minutes=ago_min))
        return v

    def _rx(self, visit, doctor, status, i):
        rx = Prescription.objects.create(visit=visit, doctor=doctor, status=status)
        if status == Prescription.Status.DISPENSED:
            rx.dispensed_by = self.users['pharmacy1']
            rx.dispensed_at = self.now
            rx.save()
        for m in (MEDS[i % 5], MEDS[(i + 2) % 5]):
            PrescriptionMedicine.objects.create(
                prescription=rx, drug_name=m[0], dosage=m[1], frequency=m[2], duration=m[3], quantity=m[4])
        return rx

    def _history(self):
        """Finished work: past days plus earlier today, so every patient report is full."""
        P = Prescription.Status
        for i, p in enumerate(self.patients):
            dept = DEPTS[i % 7]
            doc = self.doctors[dept]
            symptoms, dx = DIAGNOSES[i % 5]
            for days in (10, 3, 0):
                v = self._visit(p, 'doctor', ago_min=120 + i * 7, days=days, status='done', department=dept,
                                doctor_user=doc, created_by=doc, symptoms=symptoms, diagnosis=dx,
                                prescription_notes=MEDS[i % 5][0], doctor_done=True, doctor_done_at=self.now)
                status = [P.DISPENSED, P.DISPENSED, [P.PENDING, P.READY, P.DISPENSED][i % 3]][(10, 3, 0).index(days)]
                self._rx(v, doc, status, i + days)
            lab_type = ['Hematology', 'Clinical Chemistry', 'Clinical Microscopy'][i % 3]
            for days in (3, 0):
                if days == 0 and i >= 8:
                    continue
                v = self._visit(p, 'lab', ago_min=90 + i * 5, days=days, status='done', lab_test_type=lab_type,
                                service_type=self.svc[lab_type], lab_completed=True, lab_completed_at=self.now,
                                lab_results='; '.join(f'{k}: {x}' for k, x in LAB_RESULTS[lab_type].items()),
                                assigned_to=self.users['lab1'], created_by=self.users['lab1'])
                LabResult.objects.create(visit=v, lab_type=lab_type, status='done', results=LAB_RESULTS[lab_type])
            if i % 2 == 0:
                vt = [VaccinationType.INFLUENZA, VaccinationType.COVID19, VaccinationType.TETANUS][i % 3]
                for days in (10, 0):
                    v = self._visit(p, 'vaccination', ago_min=60 + i * 4, days=days, status='done',
                                    vaccine_type=vt, vaccine_dose='Dose 1', vaccination_date=(self.now - timedelta(days=days)).date(),
                                    assigned_to=self.users['vaccination1'], created_by=self.users['vaccination1'])
                    VaccinationRecord.objects.create(
                        visit=v, patient=p, vaccine_type=vt, status='done', administered_by=self.users['vaccination1'],
                        details={'vaccine': vt, 'doses': [{'key': 'dose1', 'label': 'Dose 1', 'checked': True,
                                                           'date': str((self.now - timedelta(days=days)).date())}]})

    def _ticket(self, patient, n, minutes, kind='doctor', dept='', **kw):
        notes = {'laboratory': '[Visit: Laboratory] ', 'vaccination': '[Visit: Vaccination] '}.get(kind, '')
        extra = {'service_type': self.svc['Laboratory' if kind == 'laboratory' else 'Vaccination']} if kind != 'doctor' else {}
        return self._visit(patient, 'reception', ago_min=minutes, queue_number=n, department=dept,
                           notes=notes + 'Walk-in', created_by=self.users['reception1'], **extra, **kw)

    def _queues(self):
        """Today's live queues for reception, every doctor, lab, vaccination."""
        P = self.patients
        # Doctors: one waiting ticket each; cardiology also has claimed / verified / in-progress work.
        for j, dept in enumerate(DEPTS):
            self._ticket(P[(j + 1) % 12], j + 1, 40 - j * 3, dept=dept)
        cardio = self.doctors['Cardiology']
        self._ticket(P[7], 8, 35, dept='Cardiology', status='claimed', claimed_by=cardio, claimed_at=self.now)
        self._ticket(P[8], 9, 30, dept='Cardiology', status='claimed', claimed_by=cardio, claimed_at=self.now,
                     doctor_arrived=True, doctor_status='ready_to_consult')
        self._visit(P[9], 'doctor', ago_min=10, status='in_process', department='Cardiology', doctor_user=cardio,
                    created_by=cardio, symptoms='Chest tightness on exertion', diagnosis='')
        # Lab
        lab1, lab2 = self.users['lab1'], self.users['laboratory_account']
        self._ticket(P[0], 1, 25, 'laboratory')
        self._ticket(P[1], 2, 24, 'laboratory')
        self._ticket(P[2], 3, 22, 'laboratory', status='claimed', lab_claimed_by=lab1, lab_claimed_at=self.now)
        self._ticket(P[10], 4, 20, 'laboratory', status='claimed', lab_claimed_by=lab2, lab_claimed_at=self.now)
        for i, state in zip((3, 4, 5, 6), ('in_process', 'in_process', 'queue', 'not_done')):
            lab_type = ['Hematology', 'Clinical Chemistry', 'Clinical Microscopy', 'Hematology'][i - 3]
            v = self._visit(P[i], 'lab', ago_min=15, status='in_process' if state == 'in_process' else 'queued',
                            lab_test_type=lab_type, service_type=self.svc[lab_type], assigned_to=lab1,
                            queue_number=10 + i, created_by=lab1)
            LabResult.objects.create(visit=v, lab_type=lab_type, status=state, results={})
        # Vaccination
        vax1, vax2 = self.users['vaccination1'], self.users['vaccination_account']
        self._ticket(P[3], 1, 28, 'vaccination')
        self._ticket(P[4], 2, 26, 'vaccination', status='claimed', assigned_to=vax1, claimed_at=self.now)
        self._ticket(P[11], 3, 21, 'vaccination', status='claimed', assigned_to=vax2, claimed_at=self.now)
        for i, state, vt in ((5, 'in_process', VaccinationType.HEPATITIS_B), (6, 'queue', VaccinationType.INFLUENZA),
                             (7, 'not_done', VaccinationType.MMR)):
            v = self._visit(P[i], 'vaccination', ago_min=12, status='in_process', vaccine_type=vt,
                            assigned_to=vax1, queue_number=10 + i, created_by=vax1)
            VaccinationRecord.objects.create(visit=v, patient=P[i], vaccine_type=vt, status=state,
                                             administered_by=vax1, details={'vaccine': vt, 'doses': [
                                                 {'key': 'dose1', 'label': 'Dose 1', 'checked': False, 'date': ''}]})

    def _audit(self):
        """A few audit rows so the admin 'Recent System Activity' panel is not empty."""
        AuditLog.objects.filter(details__startswith='[demo]').delete()
        rows = [('LOGIN', 'reception1', 'signed in'), ('CREATE_PATIENT', 'reception1', 'registered Maria Clara Santos'),
                ('CREATE_VISIT', 'reception1', 'queued Juan Miguel dela Cruz for Pediatrics'),
                ('CREATE_PRESCRIPTION', 'doctor_cardiology', 'prescribed Losartan 50mg'),
                ('CREATE_LAB_RESULT', 'lab1', 'recorded Hematology result'),
                ('DISPENSE_MEDICINE', 'pharmacy1', 'dispensed Paracetamol 500mg'),
                ('CREATE_VACCINATION', 'vaccination1', 'administered Influenza dose 1'),
                ('RESEND_QR_CODE', 'admin', 'resent QR code to a patient')]
        for i, (action, who, text) in enumerate(rows):
            log = AuditLog.objects.create(user=User.objects.filter(username=who).first(), action=action,
                                          details=f'[demo] {text}', ip_address='127.0.0.1')
            AuditLog.objects.filter(pk=log.pk).update(timestamp=self.now - timedelta(minutes=5 * (len(rows) - i)))

    def _vaccine_schedules(self):
        """Vaccine types plus per-patient dose schedules (Vaccine management pages): done, upcoming and overdue."""
        specs = [('COVID-19 Vaccine', [0, 28]), ('Influenza (Flu) Vaccine', [0]),
                 ('Hepatitis B Vaccine', [0, 30, 180]), ('Tetanus Vaccine', [0, 28, 180])]
        types = [VaccineType.objects.update_or_create(name=n, defaults={
            'total_doses_required': len(iv), 'dose_intervals': iv, 'description': f'{n} schedule'})[0] for n, iv in specs]
        PatientVaccination.objects.filter(patient__email__endswith='@' + DEMO_DOMAIN).delete()
        today = timezone.localdate()
        for i, ago in enumerate([60, 35, 27, 10, 200, 5, 28, 100]):
            vt, p = types[i % 4], self.patients[i]
            started = today - timedelta(days=ago)
            pv = PatientVaccination.objects.create(patient=p, vaccine_type=vt, started_date=started,
                                                   created_by=self.users['vaccination1'])
            done = 0
            for n, iv in enumerate(vt.dose_intervals, 1):
                sched = started + timedelta(days=iv)
                given = sched <= today - timedelta(days=2) and not (i in (1, 4) and n == len(vt.dose_intervals))
                done += given
                VaccineDose.objects.create(
                    vaccination=pv, dose_number=n, scheduled_date=sched, administered=given,
                    administered_date=sched if given else None, administered_by=self.users['vaccination1'] if given else None,
                    batch_number=f'B{1000 + i * 7 + n}' if given else '', site_of_injection='Left arm' if given else '')
            if done == len(vt.dose_intervals):
                PatientVaccination.objects.filter(pk=pv.pk).update(completed=True, completion_date=today)
