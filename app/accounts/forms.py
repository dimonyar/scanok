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


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ('name', 'pseudonym', 'current')


class DeviceChangeForm(forms.ModelForm):
    qs = Device.objects.values_list('name', flat=True)

    name = forms.ModelChoiceField(
        queryset=qs,
        empty_label='None',
    )

    class Meta:
        model = Device
        fields = ('name',)
