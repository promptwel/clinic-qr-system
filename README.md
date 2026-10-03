# Clinic QR System: QR check-in and patient flow for a community clinic

Clinic QR System lets a patient register once, get a personal **QR code** by e-mail, and be checked in at every station of
the clinic with a scan. Reception queues the patient, the doctor consults, the lab and the vaccination desk record results,
the pharmacy dispenses, and the admin sees everything in reports. The patient sees their own records on a phone-friendly
portal. One Django project serves every role:

| Part | Folder | Who uses it |
|------|--------|-------------|
| **Patient portal** (phone and desktop) | `patients/`, `templates/registration/` | Patients: register, sign in, show the QR code, read records and reports |
| **Reception** | `dashboard/`, `visits/` | Receptionist / triage: walk-in registration, queue, log arrivals |
| **Doctor** | `dashboard/` | Doctors of 7 departments: claim, verify arrival, consult, prescribe |
| **Laboratory** | `dashboard/` | Lab staff: claim, receive, enter results |
| **Pharmacy** | `dashboard/` | Pharmacists: mark ready, dispense, reports |
| **Vaccination** | `dashboard/`, `vaccinations/` | Vaccination staff: dose planner, schedules, reminders |
| **Admin** | `dashboard/`, `patients/` | Clinic admin: patients, doctors, system accounts, reports, vaccine setup |

> All screenshots below use made-up demo data. Names, e-mails and phone numbers of real people are not shown. The demo
> data command is `python manage.py seed_demo` (safe to run again). Wherever a patient has no photo, the app shows the
> default **profile icon** (a person in a circle).

### Demo accounts

Every role is covered by a demo account. The demo password is set with `seed_demo --password` and is **not** listed here.

| Role | Usernames |
|------|-----------|
| Admin | `admin` |
| Reception | `reception1`, `reception_account` |
| Doctor | `doctor_cardiology`, `doctor_dermatology`, `doctor_ent`, `doctor_obgyn`, `doctor_pediatrics`, `doctor_radiology`, `doctor_surgery` |
| Laboratory | `lab1`, `laboratory_account` |
| Pharmacy | `pharmacy1`, `pharmacy_account` |
| Vaccination | `vaccination1`, `vaccination_account` |
| Patient | `maria-clara-santos`, `juan-miguel-dela-cruz`, `ana-liza-reyes` and 9 more demo patients |

Sign in at `/accounts/login/` with the username or the e-mail address.

## About this project

This system was built and completed as a **school project**. It shows how a small community clinic can replace paper
queues and paper records with a QR-code based flow: one registration, one QR code, and every station (reception, doctor,
laboratory, pharmacy, vaccination) reading the same patient record. It is a learning project, not a certified medical
product. Use the demo data only; do not enter real patient information into a copy that is open on the internet.

| | |
|---|---|
| **School** | _add your school name_ |
| **Course / subject** | _add your course or subject_ |
| **Adviser** | _add your adviser_ |
| **Team** | _add the member names_ |
| **School year** | _add the school year_ |
| **Built with** | Python 3.11+, Django 5.2, Bootstrap 5, SQLite (PostgreSQL optional) |

**Want to run it?** Jump to [Requirements](#requirements) and the [step-by-step walkthrough](#step-by-step-walkthrough).

---

## 1. Patient

The patient pages are built **mobile first**: one column on a phone, big tap targets (44 px), tables that scroll inside
their card, and a menu button instead of the sidebar. Each page below shows the **phone** view first and the **desktop**
view under it.

### Sign in
<img src="docs/screenshots/patient/01-login-mobile.png" width="260" align="left" hspace="12">

Sign in with a username or e-mail and a password. From here a new patient can open **Register & get QR**, reset a forgotten
password, or use **Quick Scan Login** with the QR code.

<br clear="all">

<img src="docs/screenshots/patient/01-login-desktop.png" width="900">

### Register and get a QR code
<img src="docs/screenshots/patient/04-register-mobile.png" width="260" align="left" hspace="12">

A new patient fills in name, age, contact number, address, e-mail, an optional photo (file or camera) and a password. No
photo? The profile icon is used.

<br clear="all">

<img src="docs/screenshots/patient/04-register-desktop.png" width="900">

<img src="docs/screenshots/patient/05-register-success-desktop.png" width="900">

After **Register & Get QR** the patient is signed in at once and lands on the portal. The QR code is e-mailed too (see
*E-mails* below).

### Forgot password
<img src="docs/screenshots/patient/02-forgot-password-mobile.png" width="260" align="left" hspace="12">

Enter the registered e-mail. The system sends a temporary password and asks for a new one at the next sign-in.

<br clear="all">

<img src="docs/screenshots/patient/02-forgot-password-desktop.png" width="900">

### Quick scan login
<img src="docs/screenshots/patient/03-qr-login-mobile.png" width="260" align="left" hspace="12">

**Scan QR Code** opens the phone camera and signs the patient in from their QR code. If the camera is blocked, type the
registered e-mail and press **Load Dashboard**.

<br clear="all">

<img src="docs/screenshots/patient/03-qr-login-desktop.png" width="900">

### Patient portal
<img src="docs/screenshots/patient/06-portal-mobile.png" width="260" align="left" hspace="12">

The home screen shows the profile card (photo or profile icon, patient ID and code, contact details), the personal QR
code, the latest updates, upcoming queue tickets, recent medical history, lab results and prescriptions with their status.
**Edit Profile** and **Change Password** sit on the profile card.

<br clear="all">

<img src="docs/screenshots/patient/06-portal-desktop.png" width="900">

### Show, download or print the QR code
<img src="docs/screenshots/patient/07-portal-qr-mobile.png" width="260" align="left" hspace="12">

The QR code scales to the width of the screen and stays scannable. **Download QR Code** saves it as a PNG and **Print QR
Code** prints only the code. Staff scan it at every station.

<br clear="all">

<img src="docs/screenshots/patient/07-portal-qr-desktop.png" width="900">

### Menu on a phone
<img src="docs/screenshots/patient/08-menu-mobile.png" width="260" align="left" hspace="12">

The menu button opens the sidebar: **My Portal**, **My Reports** and **My Account**.

<br clear="all">

### My medical records
<img src="docs/screenshots/patient/09-medical-records-mobile.png" width="260" align="left" hspace="12">

Pick a period and press **Filter** to see consultations, prescriptions, lab tests and vaccinations. **Print Report**,
**Export PDF**, **Export CSV** and **Export XLSX** produce a copy of the same records.

<br clear="all">

<img src="docs/screenshots/patient/09-medical-records-desktop.png" width="900">

<img src="docs/screenshots/patient/10-medical-records-lab-mobile.png" width="260" align="left" hspace="12">

Further down: prescriptions with the medicines and their status (**Pending**, **Ready for Pickup**, **Dispensed**), lab
tests with results, and vaccinations. Wide tables scroll sideways inside their card, never the whole page.

<br clear="all">

<img src="docs/screenshots/patient/10-medical-records-lab-desktop.png" width="900">

### Edit profile
<img src="docs/screenshots/patient/11-edit-profile-mobile.png" width="260" align="left" hspace="12">

Change name, age, e-mail, contact number, address and photo. A new e-mail address gets a fresh QR code automatically.

<br clear="all">

<img src="docs/screenshots/patient/11-edit-profile-desktop.png" width="900">

### Change password
<img src="docs/screenshots/patient/12-change-password-mobile.png" width="260" align="left" hspace="12">

Enter the current password and a new one (8 characters or more), with an eye button to show what is typed.

<br clear="all">

<img src="docs/screenshots/patient/12-change-password-desktop.png" width="900">

### First sign-in: set a new password
<img src="docs/screenshots/patient/13-first-password-mobile.png" width="260" align="left" hspace="12">

A patient registered by reception receives a temporary password. At the first sign-in the portal asks for a new one before
anything else.

<br clear="all">

<img src="docs/screenshots/patient/13-first-password-desktop.png" width="900">

### E-mails
<img src="docs/screenshots/patient/14-email-registration-mobile.png" width="200" hspace="6"><img src="docs/screenshots/patient/15-email-queue-mobile.png" width="200" hspace="6"><img src="docs/screenshots/patient/16-email-lab-result-mobile.png" width="200" hspace="6">

Three e-mails that read well on a phone: **welcome** (patient code, username and the QR code as an attachment), **queue
ticket** (queue number, service, department and what to do next) and **lab result ready** (test type and results).

<img src="docs/screenshots/patient/14-email-registration-desktop.png" width="300"> <img src="docs/screenshots/patient/15-email-queue-desktop.png" width="300"> <img src="docs/screenshots/patient/16-email-lab-result-desktop.png" width="300">

### Also in Patient (no screenshot)
- **Delete my account** (`/patients/account/delete/`): asks for confirmation, then removes the account.
- **QR download** (`/patients/qr-download/`): the PNG file of the personal QR code.
- **Auto sign-in** after registration; the QR code is e-mailed at the same time.

---

## 2. Reception

Accounts: `reception1`, `reception_account`.

### Reception dashboard
<img src="docs/screenshots/reception/01-dashboard.png" width="900">

Today's queue: time, patient (photo or profile icon), visit type (**Consultation**, **Laboratory**, **Vaccination**), queue
number (C-, L-, V-), department, status, and **Edit** / **Delete**. Claimed tickets cannot be edited.

### Walk-in registration
<img src="docs/screenshots/reception/02-walk-in-registration.png" width="900">

Register a walk-in patient (name, age, contact, address, e-mail, optional photo) and queue them for a consultation (with a
department), the lab or vaccination in one step.

<img src="docs/screenshots/reception/03-walk-in-queued.png" width="900">

The patient gets a queue number, a confirmation e-mail with the QR code and a queue notification. The new ticket is at the
top of the list.

### Scan / log arrival
<img src="docs/screenshots/reception/04-scan-arrival.png" width="900">

**Scan/Log Arrival** opens the camera to scan a patient's QR code. The e-mail box under the camera is the fallback.

### Log a visit
<img src="docs/screenshots/reception/05-log-visit.png" width="900">

The scan page fills in the patient code. Pick the service and the department and press **Log Visit** to queue the patient.

### Edit or delete a ticket
<img src="docs/screenshots/reception/06-edit-visit.png" width="900">

Change the department, queue number or notes of an unclaimed ticket.

<img src="docs/screenshots/reception/07-delete-visit.png" width="900">

Deleting asks for confirmation and is refused when the patient's queue is already done.

### Reception report
<img src="docs/screenshots/reception/08-reception-report.png" width="900">

Pick a period for the tickets logged by reception, with print and PDF / CSV / XLSX export.

### Also in Reception (no screenshot)
- **Queue e-mail** to the patient when a ticket is created.
- **Reports and exports** from the sidebar (PDF, CSV, XLSX).

---

## 3. Doctor

Accounts: one per department, `doctor_cardiology` to `doctor_surgery`. A doctor only sees the waiting list of their own
department.

### Doctor dashboard
<img src="docs/screenshots/doctor/01-dashboard.png" width="900">

Four lists: **Waiting (Reception)**, **Claimed · Waiting to Arrive**, **Ready to Consult** and **Not Done Consultations**.

### Claim a patient
<img src="docs/screenshots/doctor/02-claim-patient.png" width="900">

**Claim** takes the next patient of the department. The ticket moves to *Claimed*, waiting for the patient to arrive.

### Verify the patient's arrival
<img src="docs/screenshots/doctor/03-verify-arrival.png" width="900">

**Verify** opens a window to scan the patient's QR code or to type the e-mail. This stops the wrong person being seen.

<img src="docs/screenshots/doctor/04-ready-to-consult.png" width="900">

A verified patient moves to **Ready to Consult**.

### Consultation
<img src="docs/screenshots/doctor/05-consultation-form.png" width="900">

**Start Consultation** opens symptoms and history, primary and secondary diagnosis, the medicine rows, the prescription
summary, patient instructions and lifestyle advice.

<img src="docs/screenshots/doctor/06-consultation-filled.png" width="900">

Dosage, frequency and duration are numbers with units. The quantity and the **Prescription Summary** are worked out
automatically.

<img src="docs/screenshots/doctor/07-consultation-finished.png" width="900">

**Save & Mark Done** completes the visit and sends the prescription to the pharmacy. **Save (Not Done)** keeps it as a draft.

### Continue or finish a draft
<img src="docs/screenshots/doctor/11-dashboard-in-progress.png" width="900">

A draft stays under **Not Done Consultations** with **Edit** and **Finish**. While a draft is open, claiming another
patient is blocked.

<img src="docs/screenshots/doctor/12-edit-in-progress.png" width="900">

<img src="docs/screenshots/doctor/13-finish-in-progress.png" width="900">

### Doctor report
<img src="docs/screenshots/doctor/09-doctor-report.png" width="900">

Consultations, prescriptions, lab requests and vaccination requests of the doctor for a chosen period, with print and
PDF / CSV / XLSX export.

### Password
<img src="docs/screenshots/doctor/10-first-login-password.png" width="900">

A new doctor account must change its password at the first sign-in.

<img src="docs/screenshots/doctor/10-change-password.png" width="900">

Any signed-in user can change their own password from the same form.

### Every department
<img src="docs/screenshots/doctor/14-dashboard-dermatology.png" width="290"> <img src="docs/screenshots/doctor/14-dashboard-ent.png" width="290"> <img src="docs/screenshots/doctor/14-dashboard-obgyn.png" width="290">
<img src="docs/screenshots/doctor/14-dashboard-radiology.png" width="290"> <img src="docs/screenshots/doctor/14-dashboard-surgery.png" width="290">

Dermatology, ENT, OB-GYN, Radiology and Surgery each have their own waiting list.

### Also in Doctor (no screenshot)
- **Doctor accounts** are created and edited by the admin (see *Admin*).

---

## 4. Laboratory

Accounts: `lab1`, `laboratory_account`.

### Laboratory dashboard
<img src="docs/screenshots/lab/01-dashboard.png" width="900">

**Unclaimed** lab tickets from reception, **Claimed · Waiting to Arrive**, **Ready to Process** and **Not Done Lab Work**.

### Claim a request
<img src="docs/screenshots/lab/02-claim-request.png" width="900">

### Verify arrival and receive
<img src="docs/screenshots/lab/03-verify-and-receive.png" width="900">

Scan the QR code or type the patient's e-mail, check the profile shown, choose the **Test Type** (Hematology, Clinical
Microscopy, Clinical Chemistry, Immunology and Serology, Microbiology, Pathology) and press **Verify & Receive**.

<img src="docs/screenshots/lab/04-in-process.png" width="900">

The patient is now **Ready to Process**.

### Enter lab results
<img src="docs/screenshots/lab/05-lab-work-form.png" width="900">

**Start Lab Work** opens a form for the chosen test (here Hematology: WBC, RBC, hemoglobin, hematocrit, platelets, remarks).

<img src="docs/screenshots/lab/06-lab-results-filled.png" width="900">

**Mark as Done** saves the results and e-mails them to the patient. **Mark as Not Done** keeps the work open.

<img src="docs/screenshots/lab/07-lab-completed.png" width="900">

### Edit or complete work in progress
<img src="docs/screenshots/lab/07-edit-in-progress.png" width="900">

<img src="docs/screenshots/lab/08-mark-complete.png" width="900">

**Edit** reopens the form; **Complete** closes the request from the list.

### Sample results sheet
<img src="docs/screenshots/lab/08-lab-results-sample.png" width="900">

A page that shows how finished results for every test type read, with the interpretation.

### Laboratory report
<img src="docs/screenshots/lab/09-lab-report.png" width="900">

Completed lab results for a period, with print and export.

### Second account
<img src="docs/screenshots/lab/10-dashboard-laboratory-account.png" width="900">

`laboratory_account` sees the tickets it claimed.

### Also in Laboratory (no screenshot)
- **Result e-mail** to the patient when a result is marked done.

---

## 5. Pharmacy

Accounts: `pharmacy1`, `pharmacy_account`.

### Pharmacy dashboard
<img src="docs/screenshots/pharmacy/01-dashboard.png" width="900">

Counters for pending, dispensed today and dispensed this week; **Pending Prescriptions** with the medicines and the status;
**Recently Dispensed**; quick filters.

### Search prescriptions
<img src="docs/screenshots/pharmacy/02-search-prescriptions.png" width="900">

Search by patient name, doctor or medicine, filter by status and date, or press **Scan QR** to find a patient by their code.

### Mark ready
<img src="docs/screenshots/pharmacy/03-mark-ready.png" width="900">

**Mark Ready** tells the patient by e-mail that the medicine can be picked up.

### Dispense
<img src="docs/screenshots/pharmacy/04-dispense-prescription.png" width="900">

**Dispense** shows the patient, the prescription and each medicine to hand over.

<img src="docs/screenshots/pharmacy/05-dispense-filled.png" width="900">

Enter the dispensed quantity, a substitution note if needed, and pharmacy notes.

<img src="docs/screenshots/pharmacy/06-dispensed.png" width="900">

### Reports
<img src="docs/screenshots/pharmacy/07-pharmacy-reports.png" width="900">

All prescriptions of a period with status, medicines and dispensed time; print and export to PDF, CSV or XLSX.

<img src="docs/screenshots/pharmacy/09-pharmacy-report.png" width="900">

### Second account
<img src="docs/screenshots/pharmacy/08-dashboard-pharmacy-account.png" width="900">

### Also in Pharmacy (no screenshot)
- **Ready-for-pickup e-mail** to the patient.
- **View Patient** from a prescription opens the patient's record.

---

## 6. Vaccination

Accounts: `vaccination1`, `vaccination_account`.

### Vaccination dashboard
<img src="docs/screenshots/vaccination/01-dashboard.png" width="900">

The same four lists as the lab: unclaimed tickets, claimed and waiting to arrive, ready to vaccinate, and not done.

### Claim, verify and receive
<img src="docs/screenshots/vaccination/02-claim-request.png" width="900">

<img src="docs/screenshots/vaccination/03-verify-and-receive.png" width="900">

Scan the QR code or type the e-mail, confirm the patient, choose the **Vaccine Type**, and press **Verify & Receive**.

<img src="docs/screenshots/vaccination/04-in-process.png" width="900">

### Vaccination workspace
<img src="docs/screenshots/vaccination/05-vaccination-workspace.png" width="900">

Pick the vaccine and use the **Dose Planner**. **Add Booster** adds an extra dose.

<img src="docs/screenshots/vaccination/06-dose-recorded-autosave.png" width="900">

Tick each dose and set its date. Changes are saved automatically while typing. **Mark Done** is allowed when every required
dose has a date.

<img src="docs/screenshots/vaccination/07-vaccination-done.png" width="900">

### Finish work in progress
<img src="docs/screenshots/vaccination/08-finish-in-process.png" width="900">

**Edit** reopens the workspace and **Finish** closes a vaccination from the list.

### Vaccination report
<img src="docs/screenshots/vaccination/09-vaccination-report.png" width="900">

Each vaccination with its status and the dates of the first, second and third dose; filter by dose and vaccine type; print
and export.

### Second account
<img src="docs/screenshots/vaccination/10-dashboard-vaccination-account.png" width="900">

### Also in Vaccination (no screenshot)
- **Dose reminders** by e-mail for the next dose (see *Vaccine management* under Admin).

---

## 7. Admin

Account: `admin` (a Django superuser).

### Dashboard overview
<img src="docs/screenshots/admin/01-dashboard.png" width="900">

Counters (patients, visits today, pending prescriptions, labs today, vaccinations today, visits this month), activity by
department, a **Quick Report** with CSV export, the recent visits and the **Recent System Activity** log.

### Patients
<img src="docs/screenshots/admin/02-patient-management.png" width="900">

Search every patient by name, e-mail, code or contact. For each one: edit, resend the QR code, or open the record.

<img src="docs/screenshots/admin/03-resend-qr-confirm.png" width="900">

<img src="docs/screenshots/admin/04-resend-qr-sent.png" width="900">

**Resend QR Code** makes a new QR code and e-mails it to the patient.

### Patient records
<img src="docs/screenshots/admin/19-patient-list.png" width="900">

The patient list with **Add Patient** and CSV / Excel export.

<img src="docs/screenshots/admin/20-patient-detail.png" width="900">

One patient: QR code, medical history, laboratory results, vaccination history, prescriptions and appointments.

<img src="docs/screenshots/admin/21-add-patient.png" width="900">

<img src="docs/screenshots/admin/22-edit-patient.png" width="900">

<img src="docs/screenshots/admin/23-delete-patient.png" width="900">

Add, edit and delete a patient. Deleting lists exactly what will be removed and needs a second confirmation.

### Doctors
<img src="docs/screenshots/admin/14-doctor-management.png" width="900">

Doctors with their department and e-mail.

<img src="docs/screenshots/admin/15-add-doctor.png" width="900">

<img src="docs/screenshots/admin/16-edit-doctor.png" width="900">

<img src="docs/screenshots/admin/17-delete-doctor.png" width="900">

### System accounts
<img src="docs/screenshots/admin/05-system-accounts.png" width="900">

The reception, laboratory, pharmacy and vaccination accounts and all doctor accounts. Each row can be edited, given a
**Reset Password** (a temporary password is generated and shown once) or a **Set Password**.

<img src="docs/screenshots/admin/06-system-account-edit.png" width="450"> <img src="docs/screenshots/admin/06-system-account-set-password.png" width="450">

### Reports
<img src="docs/screenshots/admin/07-reports.png" width="900">

Visits, doctor consultations, lab tests and pharmacy visits for a period, activity by department, staff activity and a
department table (total, completed, pending). Print, PDF, CSV and XLSX.

<img src="docs/screenshots/admin/08-system-reports.png" width="900">

**System Reports** list every record by role and department for a period.

### Vaccine management
<img src="docs/screenshots/admin/24-vaccine-management.png" width="900">

Dose schedules: totals, completed, in progress, upcoming and overdue doses, and statistics per vaccine type.

<img src="docs/screenshots/admin/25-vaccine-types.png" width="900">

<img src="docs/screenshots/admin/26-patient-vaccinations.png" width="900">

<img src="docs/screenshots/admin/27-schedule-vaccination.png" width="900">

Vaccine types (doses and the days between them), each patient's vaccinations, and a form to schedule one.

### Password
<img src="docs/screenshots/admin/18-change-password.png" width="900">

### Also in Admin (no screenshot)
- **Django admin** (`/admin/`) for raw data and permissions.
- **Doctor password** set by the admin from the system accounts list.
- **Send reminders** and **Bulk operations** for vaccinations (`/vaccinations/`).

---

## Services it uses and the keys it needs

| Service | What it does here | Plan |
|---------|-------------------|------|
| **Gmail SMTP** (or any SMTP server) | QR code and welcome e-mail, queue tickets, lab results, ready-for-pickup, password reset | A Google account with an app password; free |
| **SQLite / PostgreSQL** | All data. SQLite is the default, PostgreSQL with the `DB_*` keys | Free |
| **Local disk (`media/`)** | Patient photos and QR code images. No cloud storage is used | Free |
| **Bootstrap 5, Bootstrap Icons, html5-qrcode** (CDN) | Layout, icons and the browser QR scanner | Free |
| **gunicorn + WhiteNoise** (`Procfile`) | Production web server and static files | Any host that runs Python 3.11 |

### Keys and settings (`.env`)

| Name | Goes in | Secret? | Used for |
|------|---------|---------|----------|
| `DJANGO_SECRET_KEY` | `.env` | **Yes** | Django signing key. Set a long random value in production |
| `DJANGO_DEBUG` | `.env` | No | `true` for local work, `false` in production |
| `DJANGO_ALLOWED_HOSTS` | `.env` | No | Comma-separated host names |
| `TIME_ZONE` | `.env` | No | Default `Asia/Manila` |
| `DB_ENGINE`, `DB_NAME` | `.env` | No | Database type and name (default SQLite file `db.sqlite3`) |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | `.env` | **Yes** (`DB_PASSWORD`) | PostgreSQL connection |
| `EMAIL_PROVIDER` | `.env` | No | `gmail` (SMTP) or `console` (print e-mails in the terminal) |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_TIMEOUT` | `.env` | No | SMTP server settings (Gmail by default) |
| `EMAIL_HOST_USER` | `.env` | Private | The sending address |
| `EMAIL_HOST_PASSWORD` | `.env` | **Yes** | Gmail app password |
| `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL` | `.env` | No | Sender shown to patients |
| `PUBLIC_APP_URL` | `.env` | No | Link used in e-mails (sign-in and portal buttons) |

`.env`, `*.key`, `*.crt`, `*.pem`, `accounts.txt`, `dummy_acc.txt` and `db.sqlite3` are git-ignored. Never commit real
passwords.

## Requirements

Everything you need before the first run.

### What you need installed

| Need | Version | Why |
|------|---------|-----|
| **Python** | 3.11 or newer (3.11.11 is pinned in `runtime.txt`) | Runs the Django project |
| **pip** | comes with Python | Installs the packages in `requirements.txt` |
| **Git** | any recent version | Downloads the project (`git clone`) |
| **A web browser** | current Chrome, Edge, Firefox or Safari | Opens the system; the QR scanner needs a camera |
| **Internet connection** | for the page loads | Bootstrap, Bootstrap Icons and the QR scanner library load from a CDN |
| **A Gmail account with an app password** | optional | Sends real e-mails. Without it use `EMAIL_PROVIDER=console` and e-mails print in the terminal |
| **PostgreSQL** | optional | The default database is SQLite and needs no setup |

It runs on Windows, macOS and Linux. No Node.js, Docker or build step is needed.

### Python packages (installed for you)

`pip install -r requirements.txt` installs everything. The main ones:

| Package | What it does here |
|---------|-------------------|
| `Django` | The web framework |
| `django-crispy-forms`, `crispy-bootstrap5` | Bootstrap-styled forms |
| `qrcode`, `pillow` | Makes the patient QR code images |
| `reportlab` | PDF export of reports |
| `openpyxl`, `pandas` | Excel and CSV export |
| `python-dotenv`, `django-environ` | Reads the `.env` file |
| `psycopg2-binary` | PostgreSQL driver (only used if you choose PostgreSQL) |
| `djangorestframework` | API helpers |
| `gunicorn` | Production web server (`Procfile`) |

### Settings you may change

See *Keys and settings (`.env`)* above. For a first run you only need three lines (step 3 below).

## Step-by-step walkthrough

### Part A: set up the system (about 10 minutes)

**1. Download the project**

```bash
git clone https://github.com/2Bol-afk/clinic_shit.git
cd clinic_shit
```

**2. Create a virtual environment and install the packages**

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows Git Bash
source .venv/Scripts/activate

# macOS and Linux
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

**3. Create the `.env` file** in the project root (next to `manage.py`). The smallest working file:

```text
DJANGO_SECRET_KEY=put-a-long-random-text-here
DJANGO_DEBUG=true
EMAIL_PROVIDER=console
```

Make a random key with `python -c "import secrets; print(secrets.token_urlsafe(50))"`. With `EMAIL_PROVIDER=console` every
e-mail (QR code, queue ticket, lab result) is printed in the terminal, so you can test without a mail account.

To send real e-mails, use these lines instead. The app password is a 16-character code made in your Google account under
*Security, App passwords*:

```text
EMAIL_PROVIDER=gmail
EMAIL_HOST_USER=yourclinic@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=yourclinic@gmail.com
PUBLIC_APP_URL=http://127.0.0.1:8000/accounts/login/
```

**4. Create the database and the role groups**

```bash
python manage.py migrate
python manage.py bootstrap_roles
```

**5. Create the admin account**

```bash
python manage.py createsuperuser
```

**6. (Recommended) Fill the system with demo data.** Choose your own demo password:

```bash
python manage.py seed_demo --password YourOwnPassword
```

This creates all staff accounts from the table at the top (reception, 7 doctors, lab, pharmacy, vaccination), 12 made-up
patients with QR codes, and a populated clinic day so no screen is empty. Run it again at any time to rebuild today's
queues.

**7. Start the server**

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** and sign in. To check the install, run `python manage.py test` (27 tests should pass).

### Part B: follow one patient through the clinic (about 15 minutes)

Use two browser windows (or one normal and one private window) so you can stay signed in as two people at once.

| Step | Sign in as | What to do | Where you see the result |
|------|-----------|------------|--------------------------|
| 1. Register | nobody (login page) | Press **Register & get QR**, fill in the form, press **Register & Get QR** | You land on the portal with your QR code; an e-mail with the QR code is sent (printed in the terminal in console mode) |
| 2. Queue the patient | `reception1` | **Scan / Log Arrival**: scan the QR code, or type the patient's e-mail in the box under the camera. Pick **Doctor Consultation** and a department, press **Log Visit** | The ticket (for example `C-10`) is on the reception dashboard; the patient gets a queue e-mail |
| 3. Consultation | the doctor of that department, for example `doctor_pediatrics` | **Claim**, then **Verify** (type the patient's e-mail, **Verify Arrival**), then **Start Consultation**. Fill symptoms, diagnosis and a medicine, then **Save & Mark Done** | The visit is finished and a prescription is created |
| 4. Medicine | `pharmacy1` | Find the prescription under **Pending Prescriptions**: **Mark Ready**, **Dispense**, **Dispense Prescription** | The patient's prescription status goes Pending, Ready for Pickup, Dispensed |
| 5. Laboratory | `reception1`, then `lab1` | Reception logs a ticket with service **Laboratory**. Then `lab1`: **Claim**, **Verify**, **Verify Email**, choose the **Test Type**, **Verify & Receive**, **Start Lab Work**, enter the values, **Mark as Done** | The patient gets the result by e-mail and sees it in *My Reports* |
| 6. Vaccination | `reception1`, then `vaccination1` | Reception logs a ticket with service **Vaccination/Immunization**. Then `vaccination1`: **Claim**, **Verify**, choose the **Vaccine Type**, **Verify & Receive**, **Start Vaccination**, tick each dose and set its date, **Mark Done** | Dose dates appear in the vaccination report and the vaccine management pages |
| 7. Patient review | the patient | **My Reports**, pick the dates, **Filter**; try **Export PDF** | Consultations, prescriptions, lab tests and vaccinations in one place |
| 8. Admin review | `admin` | **Dashboard**, **Reports**, **System Reports**, **Patients** (try **Resend QR Code**), **System Accounts** | Counters and tables for the whole clinic |

Tips for the walkthrough:
- A doctor only sees patients queued for their own department.
- A patient must be **verified** (QR scan or e-mail) before a doctor, lab or vaccination desk can start work. This is by
  design.
- In console mode, look at the terminal where `runserver` runs to read the e-mails.
- Every dashboard shows only **today's** queue. If a list looks empty on a new day, run `seed_demo` again.

### Part C: open it on a phone (patient view)

1. Put the computer and the phone on the same Wi-Fi.
2. Find the computer's address (`ipconfig` on Windows, `ifconfig` or `ip a` on macOS and Linux), for example `192.168.1.20`.
3. Add it to `.env`: `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.20`
4. Start the server for the network: `python manage.py runserver 0.0.0.0:8000`
5. On the phone open `http://192.168.1.20:8000` and sign in as a patient.

Phones only allow the **camera** on `localhost` or on an `https://` address. Over plain `http://` the page still works;
use the **e-mail** box instead of the camera scanner.

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` is not found | Install Python from python.org and tick *Add Python to PATH*; on macOS and Linux try `python3` |
| `pip install` fails on `psycopg2-binary` | Update pip (`python -m pip install --upgrade pip`); the package ships ready-made wheels for common systems |
| Page looks plain, no icons | The CDN is blocked or you are offline; connect to the internet and reload |
| `DisallowedHost` error | Add the address you typed to `DJANGO_ALLOWED_HOSTS` in `.env` |
| E-mails are not sent | Use `EMAIL_PROVIDER=console`, or check the Gmail app password and `EMAIL_HOST_USER` |
| Camera does not start | Allow the camera in the browser; on a phone use `https://` or the e-mail box |
| Cannot sign in after `seed_demo` | Run `python manage.py seed_demo --password YourOwnPassword --reset-passwords` |
| Port 8000 is busy | `python manage.py runserver 8001` |
| Static files missing in production | `pip install whitenoise` and run `python manage.py collectstatic` |

## Roles and permissions

Run the bootstrap command to create the default groups and the baseline permissions:

```bash
python manage.py bootstrap_roles
```

Create users and assign them to groups (examples):

```bash
python manage.py shell -c "from django.contrib.auth.models import User, Group; u=User.objects.create_user('reception1', password='<choose-a-password>'); u.groups.add(Group.objects.get(name='Reception'))"
python manage.py shell -c "from django.contrib.auth.models import User, Group; u=User.objects.create_user('dr1', password='<choose-a-password>'); u.groups.add(Group.objects.get(name='Doctor'))"
python manage.py shell -c "from django.contrib.auth.models import User, Group; u=User.objects.create_user('lab1', password='<choose-a-password>'); u.groups.add(Group.objects.get(name='Laboratory'))"
python manage.py shell -c "from django.contrib.auth.models import User, Group; u=User.objects.create_user('pharm1', password='<choose-a-password>'); u.groups.add(Group.objects.get(name='Pharmacy'))"
python manage.py shell -c "from django.contrib.auth.models import User, Group; u=User.objects.create_user('vax1', password='<choose-a-password>'); u.groups.add(Group.objects.get(name='Vaccination'))"
```

Access:
- Login: `/accounts/login/`
- Reception dashboard: `/dashboard/reception/`
- Doctor dashboard: `/dashboard/doctor/`
- Lab dashboard: `/dashboard/lab/`
- Pharmacy dashboard: `/dashboard/pharmacy/`
- Vaccination dashboard: `/dashboard/vaccination/`
- Admin dashboard: `/dashboard/admin/`
- Patient portal: `/patients/portal/`

## Apps
- `patients`: registration, portal, QR sign-in, staff and doctor profiles
- `visits`: visits, queue tickets, lab results, prescriptions, vaccination records
- `dashboard`: role dashboards, reports, admin screens, demo data command
- `vaccinations`: vaccine types, dose schedules and reminders

## Notes
- E-mail uses SMTP (Gmail by default). Set `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (Gmail App Password) and
  `DEFAULT_FROM_EMAIL` in `.env`. Set `EMAIL_PROVIDER=console` to print e-mails instead of sending them.
- Run from the repo root: `python manage.py runserver`. Tests: `python manage.py test`.
- To enable PostgreSQL, set the `DB_*` keys and install a server.
- Screenshots live in `docs/screenshots/<role>/`.
