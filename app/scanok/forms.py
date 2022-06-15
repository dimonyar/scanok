from django import forms


class PartnerForm(forms.Form):
    PartnerF = forms.CharField(label='PartnerF', required=False, max_length=50)
    NamePartner = forms.CharField(label='NamePartner', required=False, max_length=50)
    Discount = forms.DecimalField(label='Discount', required=False, max_value=100, decimal_places=2)


class GoodForm(forms.Form):
    GoodF = forms.CharField(label='GoodF', required=False, max_length=30)
    Name = forms.CharField(label='Name', required=False, max_length=300)
    Price = forms.DecimalField(label='Price', required=False, decimal_places=2)
    Unit = forms.CharField(label='Unit', required=False, max_length=20)


class BarcodeForm(forms.Form):
    GoodF = forms.CharField(label='GoodF', required=False, max_length=30)
    BarcodeName = forms.CharField(label='BarcodeName', required=False, max_length=127)
    Code = forms.CharField(label='Code', required=False, max_length=30)
    Count = forms.FloatField(label='Count', required=False)


class UserForm(forms.Form):
    UserF = forms.CharField(label='UserF', required=True, max_length=50)
    Login = forms.CharField(label='Login', required=True, max_length=50)
    Name = forms.CharField(label='Name', required=True, max_length=50)
    Password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['Password'].isdecimal() is not True:
            raise forms.ValidationError('Passwords must contain only numbers!')
        return cleaned_data


class TerminalBase(forms.Form):
    SerialNumber = (
        ('MT9051-2WE-8K03195', 'MT9051-2WE-8K03195'),
        ('cb6321f3a9b155db5f1c42c322efd47b', 'cb6321f3a9b155db5f1c42c322efd47b'),
    )
    Base = forms.ChoiceField(choices=SerialNumber)
