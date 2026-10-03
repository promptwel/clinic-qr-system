from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from clinic_qr_system.email_utils import (
    send_test_email,
    get_email_provider_info,
    get_email_branding_context,
)

from .forms import GmailTestForm


def gmail_send_view(request):
    """
    Test and demonstrate customized Gmail SMTP email sending with clinic logo.
    """
    if request.method == 'POST':
        form = GmailTestForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            recipient_name = form.cleaned_data.get('recipient_name') or 'Valued Patient'
            subject = form.cleaned_data.get('subject') or f"{getattr(settings, 'CLINIC_NAME', 'Community Health Clinic')} Notification"
            message = form.cleaned_data['message']
            action_url = form.cleaned_data.get('action_url') or None
            action_text = form.cleaned_data.get('action_text') or None
            
            try:
                provider_info = get_email_provider_info()
                provider_name = provider_info.get('provider', 'unknown').upper()
                
                sent = send_test_email(
                    recipient_email=recipient,
                    message=message,
                    subject=subject,
                    recipient_name=recipient_name,
                    action_url=action_url,
                    action_text=action_text,
                )
                
                if sent:
                    messages.success(
                        request,
                        f'Branded email with clinic logo successfully sent to {recipient} via {provider_name}!'
                    )
                else:
                    messages.warning(request, f'Email not sent to {recipient}. Check SMTP configuration.')
                return redirect('gmail_test_send')
            except Exception as e:
                messages.error(request, f'Failed to send email: {e}')
    else:
        form = GmailTestForm()

    provider_info = get_email_provider_info()
    branding = get_email_branding_context()
    
    return render(request, 'gmail_test/form.html', {
        'form': form,
        'provider_info': provider_info,
        'branding': branding,
    })

