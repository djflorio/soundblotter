from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import password_validation
from django.template import loader
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils.translation import ugettext as _
import datetime, hashlib, random, sys

from accounts.models import Account

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                               widget=forms.PasswordInput)
    
    class Meta:
        model = Account
        fields = ('email','username')
        
    def clean_password2(self):
        # Check that both passwords match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2
    
    def save(self, data, commit=True):
        # Save password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.activation_key = data['activation_key']
        user.key_expires = timezone.now() + timezone.timedelta(days=2)
        
        if commit:
            user.save()

        return user
    
    def sendEmail(self, data):
        baseurl = settings.SITE_BASE_URL + "/accounts/activate_user/"
        html_message = loader.render_to_string(
            'accounts/email.html', {
                'username': data['username'],
                'email': data['email'],
                'activation_key': data['activation_key'],
                'baseurl': baseurl,
            }
        )
        try:
            send_mail("Account activation", "", "", [data['email']], fail_silently=False, html_message=html_message)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        
class UserChangeForm(forms.ModelForm):
    """A form for updating users in the admin panel. Includes all the
    fields on the user, but replaces the password field with admin's
    password hash display field."""
    
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Account
        fields = ('email', 'username', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
    
class UserLoginForm(forms.Form):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'email', 'id': 'post-email'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'password', 'id': 'post-pass'}))
    
class ForgotPassForm(forms.Form):
    email = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'email', 'id': 'post-email'}))
    
    def sendEmail(self, data):
        html_message = loader.render_to_string(
            'accounts/reset_pass_email.html', {
                'username': data['username'],
                'email': data['email'],
                'pwreset_key': data['pwreset_key'],
                'user_id': data['user_id'],
                'baseurl': data['baseurl'],
            }
        )
        try:
            send_mail("Reset your password", "", "", [data['email']], fail_silently=False, html_message=html_message)
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        
class ResetPassForm(forms.Form):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                               widget=forms.PasswordInput)
    
class SettingsForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('email', 'username')
        
class AccountDeleteForm(forms.Form):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'username', 'id': 'username'}))
    