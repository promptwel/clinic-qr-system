from django import forms


class GmailTestForm(forms.Form):
    recipient = forms.EmailField(
        label='Recipient Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'recipient@example.com',
            'required': True,
            'id': 'id_recipient',
        }),
        required=True,
        help_text='The destination email address that will receive the branded email.'
    )
    recipient_name = forms.CharField(
        label='Recipient Name',
        initial='Valued Patient',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Maria Santos',
            'id': 'id_recipient_name',
        }),
        required=False,
        help_text='Name used in the personalized email greeting.'
    )
    subject = forms.CharField(
        label='Email Subject',
        initial='Notice from Community Health Clinic',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Important Clinic Announcement',
            'id': 'id_subject',
        }),
        required=False,
        help_text='Subject line shown in the recipient inbox.'
    )
    message = forms.CharField(
        label='Message Body',
        initial=(
            "We are pleased to inform you that your patient account is active at Community Health Clinic.\n\n"
            "Our digital QR-based healthcare system allows you to effortlessly check in at reception, "
            "review doctor consultations, track laboratory requests, and receive timely immunization reminders.\n\n"
            "Please present your digital QR pass upon arrival at the clinic for prompt service."
        ),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Type your custom message here...',
            'required': True,
            'id': 'id_message',
        }),
        required=True,
        help_text='Main content of the email. Paragraph breaks will be formatted cleanly.'
    )
    action_url = forms.URLField(
        label='Call-to-Action Link (Optional)',
        initial='http://127.0.0.1:8000/accounts/login/',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://...',
            'id': 'id_action_url',
        }),
        required=False,
        help_text='Optional link for the primary action button (e.g. portal login URL).'
    )
    action_text = forms.CharField(
        label='Call-to-Action Button Label (Optional)',
        initial='Access Patient Portal',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Access Patient Portal',
            'id': 'id_action_text',
        }),
        required=False,
        help_text='Text displayed inside the prominent action button.'
    )

