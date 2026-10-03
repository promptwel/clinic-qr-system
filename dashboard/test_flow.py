"""End-to-end clinic flow: register -> reception -> doctor -> lab -> pharmacy -> vaccination."""
from django.contrib.auth.models import Group, User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from patients.models import Doctor, Patient
from visits.models import LabResult, Prescription, Visit


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ClinicFlowTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        def staff(name, group):
            u = User.objects.create_user(name, f'{name}@x.com', 'pw12345!')
            u.groups.add(Group.objects.get_or_create(name=group)[0])
            return u
        cls.reception = staff('rec', 'Reception')
        cls.lab = staff('lab', 'Laboratory')
        cls.pharm = staff('pharm', 'Pharmacy')
        cls.vax = staff('vax', 'Vaccination')
        cls.doc = staff('doc', 'Doctor')
        Doctor.objects.create(user=cls.doc, full_name='Doc', specialization='Cardiology', must_change_password=False)
        cls.admin = User.objects.create_superuser('adm', 'adm@x.com', 'pw12345!')

    def login(self, user):
        self.client.logout()
        self.client.force_login(user)

    def walkin(self, kind, email, dept=''):
        self.login(self.reception)
        r = self.client.post(reverse('reception_walkin'), {
            'full_name': 'Flow Patient', 'age': 30, 'address': '12 Main St, Quezon City', 'contact': '09171234567',
            'email': email, 'reception_visit_type': kind, 'department': dept,
        })
        self.assertEqual(r.status_code, 302, r.context['form'].errors if r.context and 'form' in r.context else '')
        p = Patient.objects.get(email=email)
        self.assertTrue(p.qr_code, 'QR not saved')
        self.assertFalse(p.profile_photo, 'no photo uploaded: templates show the default profile icon')
        self.assertTrue(p.user_id and p.must_change_password)
        v = Visit.objects.get(patient=p, service='reception')
        self.assertEqual(v.status, Visit.Status.QUEUED)
        self.assertEqual(v.queue_number, 1)
        return p, v

    def test_consultation_lab_pharmacy_flow(self):
        p, rec = self.walkin('consultation', 'flow1@x.com', 'Cardiology')
        self.assertTrue(any(p.patient_code in m.body and m.attachments for m in mail.outbox), 'no QR email')
        self.assertTrue(any('queue' in m.subject.lower() for m in mail.outbox), 'no queue email')

        # doctor claim + verify + consult
        self.login(self.doc)
        self.assertEqual(self.client.get(reverse('dashboard_doctor')).status_code, 200)
        self.client.post(reverse('doctor_claim'), {'reception_visit_id': rec.id})
        rec.refresh_from_db()
        self.assertEqual((rec.claimed_by, rec.status), (self.doc, Visit.Status.CLAIMED))
        r = self.client.post(reverse('doctor_verify_arrival'), {'reception_visit_id': rec.id, 'verify_code': p.patient_code})
        rec.refresh_from_db()
        self.assertTrue(rec.doctor_arrived)
        self.assertEqual(self.client.get(reverse('doctor_consult', args=[rec.id])).status_code, 200)
        self.client.post(reverse('doctor_consult', args=[rec.id]), {
            'symptoms': 'cough', 'diagnosis': 'flu', 'status': 'done',
            'medicine_0_name': 'Paracetamol', 'medicine_0_dosage': '500mg',
            'medicine_0_frequency': '3x', 'medicine_0_duration': '5d', 'medicine_0_quantity': '15',
        })
        rec.refresh_from_db()
        self.assertEqual((rec.status, rec.doctor_status), (Visit.Status.DONE, 'finished'))
        dv = Visit.objects.get(patient=p, service='doctor')
        self.assertTrue(dv.doctor_done)
        rx = Prescription.objects.get(visit=dv)
        self.assertEqual(rx.medicines.count(), 1)

        # pharmacy
        self.login(self.pharm)
        self.assertContains(self.client.get(reverse('dashboard_pharmacy')), 'Flow Patient')
        self.client.get(reverse('pharmacy_mark_ready', args=[rx.id]))
        rx.refresh_from_db()
        self.assertEqual(rx.status, Prescription.Status.READY)
        self.assertEqual(self.client.get(reverse('pharmacy_dispense', args=[rx.id])).status_code, 200)
        r = self.client.post(reverse('pharmacy_dispense', args=[rx.id]), {'pharmacy_notes': 'ok'})
        self.assertEqual(r.status_code, 302)
        rx.refresh_from_db()
        self.assertEqual(rx.status, Prescription.Status.DISPENSED)

        # lab from the doctor visit
        self.login(self.lab)
        self.assertEqual(self.client.get(reverse('dashboard_lab')).status_code, 200)
        self.client.post(reverse('lab_receive'), {'doctor_visit_id': dv.id, 'lab_test_type': 'Hematology'})
        lv = Visit.objects.get(patient=p, service='lab')
        self.assertEqual(LabResult.objects.get(visit=lv).status, 'in_process')
        self.assertEqual(self.client.get(reverse('lab_work', args=[lv.id])).status_code, 200)
        self.client.post(reverse('lab_work', args=[lv.id]), {'result_1': 'WBC 5', 'interpretation': 'normal', 'complete': '1'})
        lv.refresh_from_db()
        self.assertEqual(lv.status, Visit.Status.DONE)
        self.assertEqual(LabResult.objects.get(visit=lv).status, 'done')

        # reports + admin pages render
        for u in (self.doc, self.lab, self.pharm, self.reception, self.admin):
            self.login(u)
            r = self.client.get(reverse('reports_redirect'), follow=True)
            self.assertEqual(r.status_code, 200, (u.username, r.redirect_chain))
        self.login(self.admin)
        for name in ('admin_dashboard', 'admin_patient_management', 'admin_reports', 'admin_system_accounts', 'admin_system_reports'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_reception_lab_flow(self):
        p, rec = self.walkin('laboratory', 'flow2@x.com')
        self.login(self.lab)
        self.client.post(reverse('lab_claim'), {'reception_visit_id': rec.id})
        r = self.client.post(reverse('lab_receive'), {
            'reception_visit_id': rec.id, 'verify_code': p.patient_code, 'lab_test_type': 'Hematology'})
        lv = Visit.objects.get(patient=p, service='lab')
        self.client.post(reverse('lab_mark_done', args=[lv.id]), {'lab_results': 'ok'})
        lv.refresh_from_db(); rec.refresh_from_db()
        self.assertEqual((lv.status, rec.status), (Visit.Status.DONE, Visit.Status.DONE))

    def test_vaccination_flow(self):
        p, rec = self.walkin('vaccination', 'flow3@x.com')
        self.login(self.vax)
        self.assertEqual(self.client.get(reverse('dashboard_vaccination')).status_code, 200)
        self.client.post(reverse('vaccination_claim'), {'reception_visit_id': rec.id})
        self.client.post(reverse('vaccination_receive'), {
            'reception_visit_id': rec.id, 'verify_code': p.patient_code, 'vaccine_type': 'COVID-19 Vaccine'})
        vv = Visit.objects.get(patient=p, service='vaccination')
        self.assertEqual(self.client.get(reverse('vaccination_work', args=[vv.id])).status_code, 200)
        self.client.post(reverse('vaccination_finish', args=[vv.id]))
        vv.refresh_from_db(); rec.refresh_from_db()
        self.assertEqual((vv.status, rec.status), (Visit.Status.DONE, Visit.Status.DONE))

    def test_patient_portal(self):
        p, _ = self.walkin('consultation', 'flow4@x.com', 'Cardiology')
        self.login(p.user)
        r = self.client.get(reverse('post_login_redirect'))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('patient_password_first'))


class SidebarTest(TestCase):
    def test_sidebar_per_role(self):
        for name, group, url, label in [
            ('rec', 'Reception', 'dashboard_reception', 'Walk-in Registration'),
            ('lab', 'Laboratory', 'dashboard_lab', 'Dashboard'),
            ('pharm', 'Pharmacy', 'dashboard_pharmacy', 'Dashboard'),
        ]:
            u = User.objects.create_user(name, f'{name}@x.com', 'pw')
            u.groups.add(Group.objects.get_or_create(name=group)[0])
            self.client.force_login(u)
            self.assertContains(self.client.get(reverse(url)), 'app-sidebar')
            self.assertContains(self.client.get(reverse(url)), label)
        admin = User.objects.create_superuser('adm', 'a@x.com', 'pw')
        self.client.force_login(admin)
        r = self.client.get(reverse('admin_dashboard'))
        self.assertContains(r, 'System Accounts')
        self.assertNotContains(r, 'adminTabs')
        self.client.logout()
        self.assertNotContains(self.client.get('/accounts/login/'), 'app-sidebar')


class InputValidationTest(TestCase):
    def setUp(self):
        u = User.objects.create_user('rec', 'rec@x.com', 'pw')
        u.groups.add(Group.objects.get_or_create(name='Reception')[0])
        self.client.force_login(u)

    def post(self, **over):
        data = {'full_name': 'Maria Santos', 'age': 30, 'address': '12 Main St, Quezon City',
                'contact': '0917 123 4567', 'email': 'Maria@Example.com',
                'reception_visit_type': 'laboratory', 'department': ''}
        data.update(over)
        return self.client.post(reverse('reception_walkin'), data)

    def test_good_data_is_normalized(self):
        r = self.post()
        self.assertEqual(r.status_code, 302)
        p = Patient.objects.get()
        self.assertEqual((p.contact, p.email, p.full_name), ('09171234567', 'maria@example.com', 'Maria Santos'))

    def test_bad_data_rejected(self):
        for field, bad in [('full_name', 'Bob123'), ('full_name', 'A'), ('age', 200), ('age', -1),
                           ('contact', 'abc'), ('contact', '12345'), ('address', 'x'), ('email', 'nope')]:
            r = self.post(**{field: bad})
            self.assertEqual(r.status_code, 200, (field, bad))
            self.assertIn(field, r.context['form'].errors, (field, bad))
        r = self.post(reception_visit_type='consultation', department='')
        self.assertIn('department', r.context['form'].errors)
        self.assertEqual(Patient.objects.count(), 0)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class LocalImagesTest(TestCase):
    def test_email_logo_is_embedded_not_online(self):
        from clinic_qr_system.email_utils import send_patient_registration_email, send_test_email
        send_patient_registration_email('A B', 'CODE123456', 'a@b.com', b'png', 'qr.png', 'pw', 'a-b')
        send_test_email('a@b.com', 'hi', 'subj')
        for m in mail.outbox:
            html = [c for c, t in m.alternatives if t == 'text/html'][0]
            self.assertIn('cid:clinic_logo', html)
            self.assertNotIn('http://res.', html)
            self.assertNotIn('cloudinary', html)
            self.assertIn('<clinic_logo>', m.message().as_string())
