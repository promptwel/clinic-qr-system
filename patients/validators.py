"""Shared input cleaning for patient data (used by every patient form)."""
import re

from django import forms

NAME_RE = re.compile(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'\-]*$")
PH_PHONE_RE = re.compile(r"^(?:\+63|63|0)\d{9,10}$")  # 09171234567, +639171234567, 028123456

NAME_PATTERN = r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'\-]{1,99}"        # HTML pattern attr
PHONE_PATTERN = r"(\+63|63|0)[0-9 \-()]{9,14}"
MAX_AGE = 120


class PatientDataCleanMixin:
    """clean_<field> methods for full_name, age, contact, address. Works on Form and ModelForm."""

    def clean_full_name(self):
        name = re.sub(r"\s+", " ", (self.cleaned_data.get('full_name') or '').strip())
        if len(name) < 2:
            raise forms.ValidationError('Enter the full name (at least 2 letters).')
        if not NAME_RE.match(name):
            raise forms.ValidationError("Name may only contain letters, spaces, apostrophes, hyphens and periods.")
        return name

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None or age < 0 or age > MAX_AGE:
            raise forms.ValidationError(f'Age must be between 0 and {MAX_AGE}.')
        return age

    def clean_contact(self):
        raw = (self.cleaned_data.get('contact') or '').strip()
        digits = re.sub(r"[\s\-()]", "", raw)
        if not PH_PHONE_RE.match(digits):
            raise forms.ValidationError('Enter a valid phone number, e.g. 09171234567 or +639171234567.')
        return digits

    def clean_address(self):
        addr = re.sub(r"\s+", " ", (self.cleaned_data.get('address') or '').strip())
        if len(addr) < 5:
            raise forms.ValidationError('Enter a complete address (at least 5 characters).')
        return addr
