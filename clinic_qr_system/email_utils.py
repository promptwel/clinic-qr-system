import os
"""
Email utility functions (Django SMTP).
Provides convenient functions for sending common types of emails.
"""
import logging
from typing import List, Optional, Dict, Any, Union
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.mail import send_mail as django_send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Context, Template

logger = logging.getLogger(__name__)


def get_email_branding_context() -> dict:
    from django.conf import settings
    return {
        'clinic_name': getattr(settings, 'CLINIC_NAME', 'Community Health Clinic'),
        'clinic_system_name': getattr(settings, 'CLINIC_SYSTEM_NAME', 'Clinic QR System'),
        'clinic_logo_url': 'cid:clinic_logo',  # embedded from static/images/clinic_logo_small.png
        'clinic_contact_email': getattr(settings, 'CLINIC_CONTACT_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', 'clinicqrsystem@gmail.com')),
        'clinic_contact_phone': getattr(settings, 'CLINIC_CONTACT_PHONE', '+1 (555) 234-5678'),
        'clinic_address': getattr(settings, 'CLINIC_ADDRESS', 'Community Health Clinic Center'),
    }


def _embed_logo(email) -> None:
    """Attach the local clinic logo inline so emails need no online image."""
    from email.mime.image import MIMEImage
    path = os.path.join(settings.BASE_DIR, 'static', 'images', 'clinic_logo_small.png')
    try:
        with open(path, 'rb') as f:
            img = MIMEImage(f.read())
    except OSError:
        return
    img.add_header('Content-ID', '<clinic_logo>')
    img.add_header('Content-Disposition', 'inline', filename='clinic_logo.png')
    email.mixed_subtype = 'related'
    email.attach(img)


def send_email_with_attachment(
    subject: str,
    message: str,
    recipient_list: List[str],
    attachment_data: Optional[Dict[str, Any]] = None,
    html_message: Optional[str] = None,
    from_email: Optional[str] = None,
    fail_silently: bool = False
) -> bool:
    """
    Send email with optional attachment.
    
    Args:
        subject: Email subject
        message: Plain text message
        recipient_list: List of recipient email addresses
        attachment_data: Dict with 'filename', 'content', 'mimetype' keys
        html_message: Optional HTML version of the message
        from_email: Sender email (uses DEFAULT_FROM_EMAIL if not provided)
        fail_silently: Whether to fail silently on errors
        
    Returns:
        bool: True if email was sent successfully
    """
    try:
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        
        if html_message:
            # Use EmailMultiAlternatives for HTML content
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list
            )
            email.attach_alternative(html_message, "text/html")
            if 'cid:clinic_logo' in html_message:
                _embed_logo(email)
        else:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                to=recipient_list
            )
        
        # Add attachment if provided
        if attachment_data:
            email.attach(
                attachment_data['filename'],
                attachment_data['content'],
                attachment_data.get('mimetype', 'application/octet-stream')
            )
        
        result = email.send(fail_silently=fail_silently)
        
        if result:
            logger.info(f"Email sent successfully to {recipient_list}")
        else:
            logger.warning(f"Email sending returned 0 for {recipient_list}")
            
        return bool(result)
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        if not fail_silently:
            raise
        return False


def send_patient_registration_email(
    patient_name: str,
    patient_code: str,
    patient_email: str,
    qr_code_data: Optional[bytes] = None,
    qr_filename: str = "qr_code.png",
    temp_password: Optional[str] = None,
    username: Optional[str] = None
) -> bool:
    """
    Send patient registration confirmation email with QR code.
    
    Args:
        patient_name: Patient's full name
        patient_code: Patient's unique code
        patient_email: Patient's email address
        qr_code_data: QR code image data (bytes)
        qr_filename: Filename for QR code attachment
        temp_password: Temporary password (if applicable)
        username: Username for login (if applicable)
        
    Returns:
        bool: True if email was sent successfully
    """
    # Prepare email content (clear login + reset instructions)
    subject = "Your Patient Portal Access and QR Code"

    login_url = os.getenv('PUBLIC_APP_URL', '') or 'http://127.0.0.1:8000/accounts/login/'
    message_lines = [
        f"Dear {patient_name},",
        "",
        "Welcome to Clinic QR System. Your account has been created.",
        f"Patient Code: {patient_code}",
    ]
    if username:
        message_lines.append(f"Portal Username (email): {username}")
    if temp_password:
        message_lines.append(f"Temporary Password: {temp_password}")
    message_lines.append("")
    message_lines.append(f"1) Go to: {login_url}")
    message_lines.append("2) Log in with the credentials above.")
    # Only include forced password-change note when a temp password is issued (walk-in)
    if temp_password:
        message_lines.append("3) You will be prompted to change your password immediately.")
    message_lines.extend([
        "",
        "Keep this email for your records. Your QR code is attached for faster check-in.",
        "",
        "Regards,",
        "Clinic QR System",
    ])
    message = "\n".join(message_lines)
    
    # Prepare attachment data
    attachment_data = None
    if qr_code_data:
        attachment_data = {
            'filename': qr_filename,
            'content': qr_code_data,
            'mimetype': 'image/png'
        }
    
    html_message = render_to_string('emails/patient_registration.html', {
        **get_email_branding_context(),
        'subject': subject,
        'patient_name': patient_name,
        'patient_code': patient_code,
        'username': username,
        'temp_password': temp_password,
        'login_url': login_url,
    })

    return send_email_with_attachment(
        subject=subject,
        message=message,
        recipient_list=[patient_email],
        attachment_data=attachment_data,
        html_message=html_message,
        fail_silently=False
    )


def send_test_email(
    recipient_email: str,
    message: str = "This is a test email from Clinic QR System via SMTP.",
    subject: str = "SMTP Test",
    recipient_name: Optional[str] = None,
    action_url: Optional[str] = None,
    action_text: Optional[str] = None,
) -> bool:
    """
    Send a branded HTML test email to verify email configuration.

    Args:
        recipient_email: Email address to send test to
        message: Test message content
        subject: Test email subject
        recipient_name: Optional name for the greeting
        action_url: Optional call-to-action button link
        action_text: Optional call-to-action button label

    Returns:
        bool: True if email was sent successfully
    """
    try:
        html_message = render_to_string('emails/custom_notification.html', {
            **get_email_branding_context(),
            'subject': subject,
            'title': subject,
            'message': message,
            'recipient_name': recipient_name,
            'action_url': action_url,
            'action_text': action_text,
        })
        result = send_email_with_attachment(
            subject=subject,
            message=message,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        
        if result:
            logger.info(f"Test email sent successfully to {recipient_email}")
        else:
            logger.warning(f"Test email sending returned 0 for {recipient_email}")
            
        return bool(result)
        
    except Exception as e:
        logger.error(f"Failed to send test email: {e}")
        raise


def send_notification_email(
    recipient_list: List[str],
    subject: str,
    message: str,
    html_message: Optional[str] = None,
    from_email: Optional[str] = None
) -> bool:
    """
    Send a notification email (no attachments).
    
    Args:
        recipient_list: List of recipient email addresses
        subject: Email subject
        message: Plain text message
        html_message: Optional HTML version
        from_email: Sender email
        
    Returns:
        bool: True if email was sent successfully
    """
    return send_email_with_attachment(
        subject=subject,
        message=message,
        recipient_list=recipient_list,
        html_message=html_message,
        from_email=from_email,
        fail_silently=False
    )


def send_queue_notification_email(
    patient_name: str,
    patient_email: str,
    queue_number: int,
    service_type: str,
    department: str = None,
    visit_id: int = None
) -> bool:
    """
    Send queue notification email to patient.
    
    Args:
        patient_name: Patient's full name
        patient_email: Patient's email address
        queue_number: Queue number assigned
        service_type: Type of service (laboratory, consultation, vaccination)
        department: Department name (for consultation)
        visit_id: Visit ID for reference
        
    Returns:
        bool: True if email was sent successfully
    """
    try:
        # Determine subject and content based on service type
        if service_type.lower() == 'laboratory':
            subject = "You Have Been Queued for Laboratory"
            message_parts = [
                f"Dear {patient_name},\n",
                "\nYou have been successfully added to the laboratory queue.\n",
                f"Your queue number is: {queue_number}\n",
                "\nPlease proceed to the laboratory when your number is called.\n",
                "The laboratory staff will assist you with your tests.\n\n",
                "Thank you for your patience.\n\n",
                "Regards,\nClinic QR System"
            ]
        elif service_type.lower() == 'consultation':
            subject = "You Have Been Queued for Consultation"
            dept_text = f" in the {department} department" if department else ""
            message_parts = [
                f"Dear {patient_name},\n",
                f"\nYou have been successfully added to the consultation queue{dept_text}.\n",
                f"Your queue number is: {queue_number}\n",
                f"Department: {department or 'General Consultation'}\n",
                "\nPlease wait in the designated area until your number is called.\n",
                "A doctor will see you shortly.\n\n",
                "Thank you for your patience.\n\n",
                "Regards,\nClinic QR System"
            ]
        elif service_type.lower() == 'vaccination':
            subject = "You Have Been Queued for Vaccination"
            message_parts = [
                f"Dear {patient_name},\n",
                "\nYou have been successfully added to the vaccination queue.\n",
                f"Your queue number is: {queue_number}\n",
                "\nPlease proceed to the vaccination area when your number is called.\n",
                "The vaccination staff will assist you with your immunization.\n\n",
                "Thank you for your patience.\n\n",
                "Regards,\nClinic QR System"
            ]
        else:
            # Generic queue notification
            subject = "You Have Been Added to the Queue"
            message_parts = [
                f"Dear {patient_name},\n",
                f"\nYou have been successfully added to the {service_type} queue.\n",
                f"Your queue number is: {queue_number}\n",
                "\nPlease wait until your number is called.\n",
                "Staff will assist you shortly.\n\n",
                "Thank you for your patience.\n\n",
                "Regards,\nClinic QR System"
            ]
        
        message = ''.join(message_parts)
        
        # Add visit ID to message if provided
        if visit_id:
            message += f"\n\nReference ID: {visit_id}"
        
        # Send the email
        result = send_notification_email(
            recipient_list=[patient_email],
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        )
        
        if result:
            logger.info(f"Queue notification email sent successfully to {patient_name} ({patient_email}) for {service_type} queue #{queue_number}")
        else:
            logger.warning(f"Queue notification email failed to send to {patient_name} ({patient_email})")
            
        return result
        
    except Exception as e:
        logger.error(f"Failed to send queue notification email to {patient_name} ({patient_email}): {e}")
        return False


def send_queue_notification_email_html(
    patient_name: str,
    patient_email: str,
    queue_number: int,
    service_type: str,
    department: str = None,
    visit_id: int = None
) -> bool:
    """
    Send queue notification email to patient with HTML formatting.
    
    Args:
        patient_name: Patient's full name
        patient_email: Patient's email address
        queue_number: Queue number assigned
        service_type: Type of service (laboratory, consultation, vaccination)
        department: Department name (for consultation)
        visit_id: Visit ID for reference
        
    Returns:
        bool: True if email was sent successfully
    """
    try:
        kind = service_type.lower()
        presets = {
            'laboratory': ("You Have Been Queued for Laboratory", "Laboratory Queue", "Laboratory",
                           ["Proceed to the Laboratory when your number is called.",
                            "Laboratory staff will assist you with your tests.",
                            "Have your patient ID or QR code ready."]),
            'consultation': ("You Have Been Queued for Consultation", "Consultation Queue", "Doctor Consultation",
                             ["Wait in the designated waiting area.",
                              "A doctor will see you when your number is called.",
                              "Have your patient ID and any relevant documents ready."]),
            'vaccination': ("You Have Been Queued for Vaccination", "Vaccination Queue", "Vaccination / Immunization",
                            ["Proceed to the Vaccination Area when your number is called.",
                             "Vaccination staff will assist you with your immunization.",
                             "Have your patient ID or QR code ready."]),
        }
        subject, heading, service_label, tips = presets.get(kind, (
            "You Have Been Added to the Queue", "Queue Notification", service_type.title(),
            ["Wait until your number is called.", "Staff will assist you shortly.", "Have your patient ID ready."]))
        html_content = render_to_string('emails/queue_notification.html', {
            **get_email_branding_context(),
            'subject': subject,
            'heading': heading,
            'service_label': service_label,
            'tips': tips,
            'patient_name': patient_name,
            'queue_number': queue_number,
            'department': (department or 'General Consultation') if kind == 'consultation' else department,
            'visit_id': visit_id,
            'portal_url': os.getenv('PUBLIC_APP_URL', '') or None,
        })

        # Create plain text version
        plain_text = f"""
Dear {patient_name},

You have been successfully added to the {service_type} queue.
Your queue number is: {queue_number}
{f'Department: {department}' if department else ''}

Please wait until your number is called.
Staff will assist you shortly.

Thank you for your patience.

Regards,
Clinic QR System
{f'Reference ID: {visit_id}' if visit_id else ''}
        """.strip()
        
        # Send the email with HTML content
        result = send_email_with_attachment(
            subject=subject,
            message=plain_text,
            recipient_list=[patient_email],
            html_message=html_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            fail_silently=False
        )
        
        if result:
            logger.info(f"Queue notification email (HTML) sent successfully to {patient_name} ({patient_email}) for {service_type} queue #{queue_number}")
        else:
            logger.warning(f"Queue notification email (HTML) failed to send to {patient_name} ({patient_email})")
            
        return result
        
    except Exception as e:
        logger.error(f"Failed to send queue notification email (HTML) to {patient_name} ({patient_email}): {e}")
        return False


def send_lab_result_email(
    patient_name: str,
    patient_email: str,
    lab_type: str,
    lab_results: str,
    visit_id: int,
    completed_at: str,
    attachment_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send lab result completion email to patient with results attachment.
    
    Args:
        patient_name: Patient's full name
        patient_email: Patient's email address
        lab_type: Type of lab test performed
        lab_results: Lab test results text
        visit_id: Visit ID for reference
        completed_at: Date/time when lab was completed
        attachment_data: Optional PDF attachment data
        
    Returns:
        bool: True if email was sent successfully
    """
    try:
        subject = "Your Lab Result is Ready"
        
        html_content = render_to_string('emails/lab_result.html', {
            **get_email_branding_context(),
            'subject': subject,
            'patient_name': patient_name,
            'lab_type': lab_type,
            'lab_results': lab_results,
            'visit_id': visit_id,
            'completed_at': completed_at,
            'portal_url': os.getenv('PUBLIC_APP_URL', '') or None,
        })

        # Create plain text version
        plain_text = f"""
Dear {patient_name},

Your lab result is ready!

Test Information:
- Test Type: {lab_type}
- Completed: {completed_at}
- Visit ID: {visit_id}

Test Results:
{lab_results}

Important Instructions:
- Please review your lab results carefully
- If you have any questions about your results, please contact your doctor
- You can log in to your patient portal to view your complete medical history
- If you need to visit the clinic, please bring this email or your patient ID

If you have any questions or concerns about your lab results, please don't hesitate to contact us.

Regards,
Clinic QR System
Laboratory Department
        """.strip()
        
        # Send the email with attachment
        result = send_email_with_attachment(
            subject=subject,
            message=plain_text,
            recipient_list=[patient_email],
            html_message=html_content,
            attachment_data=attachment_data,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            fail_silently=False
        )
        
        if result:
            logger.info(f"Lab result email sent successfully to {patient_name} ({patient_email}) for {lab_type} test")
        else:
            logger.warning(f"Lab result email failed to send to {patient_name} ({patient_email})")
            
        return result
        
    except Exception as e:
        logger.error(f"Failed to send lab result email to {patient_name} ({patient_email}): {e}")
        return False


def get_email_provider_info() -> Dict[str, Any]:
    """
    Get information about the current email provider configuration.
    
    Returns:
        Dict with provider information
    """
    provider = getattr(settings, 'EMAIL_PROVIDER', 'unknown')
    
    info = {
        'provider': provider,
        'backend': getattr(settings, 'EMAIL_BACKEND', 'unknown'),
        'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'unknown'),
    }
    
    if provider == 'gmail':
        info.update({
            'smtp_host': getattr(settings, 'EMAIL_HOST', 'unknown'),
            'smtp_port': getattr(settings, 'EMAIL_PORT', 'unknown'),
            'use_tls': getattr(settings, 'EMAIL_USE_TLS', False),
        })
    
    return info
