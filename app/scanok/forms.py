from django import forms


class PartnerForm(forms.Form):
    PartnerF = forms.CharField(label='PartnerF', required=False, max_length=50)
    NamePartner = forms.CharField(label='NamePartner', required=False, max_length=50)
    Discount = forms.DecimalField(label='Discount', required=False, max_value=100, decimal_places=2)


class GoodForm(forms.Form):
    GoodF = forms.CharField(label='GoodF', required=False, max_length=30)
    Name = forms.CharField(label='Name', required=True, max_length=300)
    Price = forms.DecimalField(label='Price', required=True, decimal_places=2)
    Unit = forms.CharField(label='Unit', required=True, max_length=20)


class BarcodeForm(forms.Form):
    GoodF = forms.CharField(label='GoodF', required=False, max_length=30)
    BarcodeName = forms.CharField(label='BarcodeName', required=False, max_length=127)
    Code = forms.CharField(label='Code', required=False, max_length=30)
    Count = forms.FloatField(label='Count', required=False)


class UserForm(forms.Form):
    UserF = forms.CharField(label='UserF', required=False, max_length=50)
    Login = forms.CharField(label='Login', required=True, max_length=50)
    Name = forms.CharField(label='Name', required=True, max_length=50)
    Password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['Password'].isdecimal() is not True:
            raise forms.ValidationError('Passwords must contain only numbers!')
        return cleaned_data


class StoreForm(forms.Form):
    StoreF = forms.CharField(label='GoodF', required=False, max_length=50)
    NameStore = forms.CharField(label='NameStore', required=True, max_length=50)


class DocheadForm(forms.Form):
    Comment = forms.CharField(label='Comment', required=False, max_length=50)
    PartnerF = forms.ChoiceField(choices=())
    MainStoreF = forms.ChoiceField(choices=())
    AlternateStoreF = forms.ChoiceField(choices=())
    DocType = forms.ChoiceField(choices=())
    UserF = forms.ChoiceField(choices=())
    BarcodeDocu = forms.CharField(label='BarcodeDocu', required=False, max_length=50)
    Discount = forms.FloatField(label='Count', required=False)

    def __init__(self, *args, **kwargs):
        users = tuple(kwargs.pop('UserF'))
        partners = tuple(kwargs.pop('PartnerF'))
        stores = tuple(kwargs.pop('MainStoreF'))
        doctype = (
            (1, 'приходный'),
            (2, 'расходный'),
            (3, 'инвентаризация'),
            (4, 'перемещение'),
            (5, 'списание'),
            (6, 'возврат'),
        )
        super().__init__(*args, **kwargs)
        self.fields['UserF'] = forms.ChoiceField(choices=users, required=False, label='User')
        self.fields['PartnerF'] = forms.ChoiceField(choices=partners, required=False, label='Partner')
        self.fields['MainStoreF'] = forms.ChoiceField(choices=stores, required=False, label='MainStore')
        self.fields['AlternateStoreF'] = forms.ChoiceField(choices=stores, required=False, label='AlternateStore')
        self.fields['DocType'] = forms.ChoiceField(choices=doctype, required=False, label='DocType')
