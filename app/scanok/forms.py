from django import forms


class PartnerForm(forms.Form):
    PartnerF = forms.CharField(label='PartnerF', required=False, max_length=50)
    NamePartner = forms.CharField(label='NamePartner', required=False, max_length=50)
    Discount = forms.DecimalField(label='Discount', required=False, max_value=100, decimal_places=2)


class TerminalBase(forms.Form):
    SerialNumber = (
        ('MT9051-2WE-8K03195', 'MT9051-2WE-8K03195'),
        ('cb6321f3a9b155db5f1c42c322efd47b', 'cb6321f3a9b155db5f1c42c322efd47b'),
    )
    Base = forms.ChoiceField(choices=SerialNumber)
