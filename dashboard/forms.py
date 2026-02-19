from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from captcha.fields import CaptchaField

class AdminLoginForm(AdminAuthenticationForm):
    captcha = CaptchaField(label='CAPTCHA')
