from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit

from django import forms

from scanok import model_choices as mch


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
    PartnerF = forms.ChoiceField(choices=(), label='PartnerF')
    MainStoreF = forms.ChoiceField(choices=(), label='MainStoreF')
    AlternateStoreF = forms.ChoiceField(choices=(), label='AlternateStoreF')
    DocType = forms.ChoiceField(choices=(), label='DocType')
    UserF = forms.ChoiceField(choices=(), label='UserF')
    BarcodeDocu = forms.CharField(label='BarcodeDocu', required=False, max_length=50)
    Discount = forms.FloatField(label='Discount', required=False)

    def __init__(self, *args, **kwargs):
        users = tuple(kwargs.pop('UserF'))
        partners = tuple(kwargs.pop('PartnerF'))
        stores = tuple(kwargs.pop('MainStoreF'))

        docstatus = kwargs.pop('DocStatus')
        doctype = mch.DocHeadDocType.choices

        super().__init__(*args, **kwargs)
        self.fields['UserF'] = forms.ChoiceField(choices=users, required=False, label='User')
        self.fields['PartnerF'] = forms.ChoiceField(choices=partners, required=False, label='Partner')
        self.fields['MainStoreF'] = forms.ChoiceField(choices=stores, required=False, label='MainStore')
        self.fields['AlternateStoreF'] = forms.ChoiceField(choices=stores, required=False, label='AlternateStore')
        self.fields['DocType'] = forms.ChoiceField(choices=doctype, required=False, label='DocType')

        self.helper = FormHelper()
        if docstatus < 0:
            self.helper.layout = Layout(
                Row(
                    Column('Comment', wrapper_class='col-md-6', css_class='row-fluid'),
                    Column('DocType', wrapper_class='col-md-6', css_class='row-fluid'),
                ),
                Row(
                    Column('PartnerF', wrapper_class='col-md-6', css_class='row-fluid'),
                    Column('UserF', wrapper_class='col-md-6', css_class='row-fluid'),
                ),
                Row(
                    Column('MainStoreF', wrapper_class='col-md-6', css_class='row-fluid'),
                    Column('AlternateStoreF', wrapper_class='col-md-6', css_class='row-fluid'),
                ),
                Row(
                    Column('Discount', wrapper_class='col-md-6', css_class='row-fluid'),
                    Column('BarcodeDocu', wrapper_class='col-md-6', css_class='row-fluid'),
                ),

                Submit('submit', 'Apply')
            )
        else:
            self.helper.layout = Layout(
                Row(
                    Column('Comment', wrapper_class='col-md-6', css_class='row-fluid'),
                    Column('DocType', wrapper_class='col-md-6', css_class='row-fluid'),
                ),
                Row(
                    Column('PartnerF', wrapper_class='col-md-6', css_class='row-fluid'),
                    Column('UserF', wrapper_class='col-md-6', css_class='row-fluid'),
                ),
                Row(
                    Column('MainStoreF', wrapper_class='col-md-6', css_class='row-fluid'),
                    Column('AlternateStoreF', wrapper_class='col-md-6', css_class='row-fluid'),
                ),
                Row(
                    Column('Discount', wrapper_class='col-md-6', css_class='row-fluid'),
                    Column('BarcodeDocu', wrapper_class='col-md-6', css_class='row-fluid'),
                )
            )


class DocDetailsForm(forms.Form):

    GoodF = forms.CharField(label='GoodF', required=False, max_length=30)
    Count_Doc = forms.FloatField(label='Count_Doc', required=False)
    Price = forms.FloatField(label='Price', required=False)
    Spec_comment = forms.CharField(label='Comment', required=False, max_length=300)

    def __init__(self, *args, **kwargs):
        goods = tuple(kwargs.pop('GoodF'))

        super().__init__(*args, **kwargs)
        self.fields['GoodF'] = forms.ChoiceField(choices=goods, required=False, label='Name')
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('GoodF', wrapper_class='col-md-6', css_class='row-fluid'),
                Column('Count_Doc', wrapper_class='col-md-6', css_class='row-fluid'),
                Column('Price', wrapper_class='col-md-6', css_class='row-fluid'),
            ),
            Row(
                Column('Spec_comment', wrapper_class='col-md-6', css_class='row-fluid'),
            ),
            Submit('submit', 'APPLY')
        )
