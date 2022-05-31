from accounts.models import Device, User
from accounts.tasks import send_activation_email

from django import forms


class SignUpForm(forms.ModelForm):
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    confirm = forms.CharField(required=True, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm')

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['password'] != cleaned_data['confirm']:
            raise forms.ValidationError('Passwords should match!')

        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data

        user = super().save(commit=False)
        user.set_password(cleaned_data['password'])
        user.is_active = False

        if commit:
            user.save()

        send_activation_email.delay(user.username, user.email)

        return user


class DeviceFormUpdate(forms.ModelForm):
    name = forms.CharField(max_length=50, disabled=True)

    class Meta:
        model = Device
        fields = ('name', 'pseudonym', 'current')


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ('name', 'pseudonym', 'current')


class DeviceFormConfirm(forms.Form):
    confirm = forms.CharField(required=True)
