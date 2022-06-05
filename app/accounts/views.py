from random import choice
from string import ascii_letters, digits

from accounts.SmartStoreManagment_models import Devices as TableDevices
from accounts.forms import DeviceForm, DeviceFormConfirm, DeviceFormUpdate, SignUpForm
from accounts.models import Device, User
from accounts.tables import DeviceTable

from crum import get_current_user

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, RedirectView, UpdateView

from django_tables2 import SingleTableView

from formtools.wizard.views import SessionWizardView

from settings.settings import password, port, server, user

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class MyProfile(LoginRequiredMixin, UpdateView):
    queryset = User.objects.all()
    template_name = 'my_profile.html'
    success_url = reverse_lazy('index')
    fields = (
        'first_name',
        'last_name',
        'avatar',
    )

    def get_object(self, queryset=None):
        return self.request.user


class ActivateUser(RedirectView):
    url = reverse_lazy('login')

    def get_redirect_url(self, username):
        user = get_object_or_404(User, username=username)

        if user.is_active:
            messages.error(self.request, 'Account already activated!')
        else:
            user.is_active = True
            user.save(update_fields=['is_active'])
            messages.success(self.request, 'Account is activated!')

        return super().get_redirect_url()


class SignUp(CreateView):
    queryset = User.objects.all()
    template_name = 'signup.html'
    success_url = reverse_lazy('check-email')
    form_class = SignUpForm


class Devices(SingleTableView):
    model = Device
    table_class = DeviceTable
    template_name = 'devices.html'

    def get_queryset(self):
        current_id = get_current_user().id
        new_context = Device.objects.filter(
            user_id=current_id)
        return new_context


class DeviceUpdate(UpdateView):
    model = Device
    template_name = 'device_update.html'
    form_class = DeviceFormUpdate
    success_url = reverse_lazy('accounts:devices')


class DeviceDelete(DeleteView):
    model = Device
    template_name = 'device_delete.html'
    success_url = reverse_lazy('accounts:devices')


class DeviceCreate(SessionWizardView):
    template_name = 'device_create.html'
    form_list = [DeviceForm, DeviceFormConfirm]

    def render_next_step(self, form, **kwargs):
        if self.steps.current == '0':
            # Проверяем данный серийник в списке у текущего пользователя
            try:
                if Device.objects.get(name=form.cleaned_data['name'], user_id=get_current_user().id):
                    messages.error(self.request, f'Устройство с номером '
                                                 f'{form.cleaned_data["name"]}'
                                                 f' уже есть в Вашем списке')
                    return HttpResponseRedirect('/accounts/devices/')
            except Device.DoesNotExist:
                # Проверяем данный серийник в списке SmartStoreManagment.dbo.Devices
                engine = create_engine(
                    f'mssql+pymssql://'
                    f'{user}:{password}'
                    f'@{server}:{port}/'
                    f'SmartStoreManagment', echo=True
                )
                session = sessionmaker(bind=engine)
                s = session()  # noqa: VNE001

                list_devices = s.query(TableDevices.idDevice).all()

                if (form.cleaned_data['name'],) not in list_devices:
                    messages.error(self.request, 'Invalid serial number! Please try again ')
                    return HttpResponseRedirect('/accounts/devices/')

                # Генерируем случайную строку и записываем ее в SmartStoreManagment.dbo.Devices (confirmCode)
                captcha = ''.join(choice(ascii_letters + digits) for i in range(5))

                instance = s.query(TableDevices).filter(TableDevices.idDevice == form.cleaned_data['name'])

                instance.update({TableDevices.confirmCode: captcha})
                s.commit()
                s.close()
        return super().render_next_step(form, **kwargs)

    def done(self, form_list, *args, **kwargs):
        form_data = [form.cleaned_data for form in form_list]

        engine = create_engine(
            f'mssql+pymssql://'
            f'{user}:{password}'
            f'@{server}:{port}/'
            f'SmartStoreManagment', echo=True
        )
        session = sessionmaker(bind=engine)
        s = session()  # noqa: VNE001
        captcha = s.query(TableDevices.confirmCode
                          ).filter(
            TableDevices.idDevice == form_data[0]['name']
        )

        if form_data[1]['confirm'] == captcha[0][0]:
            current_user_id = get_current_user().id
            try:
                if Device.objects.get(name=form_data[0]['name']):
                    Device.objects.filter(
                        name=form_data[0]['name']
                    ).update(
                        pseudonym=form_data[0]['pseudonym'],
                        current=form_data[0]['current'],
                        user_id=current_user_id
                    )
            except Device.DoesNotExist:
                Device.objects.create(
                    name=form_data[0]['name'],
                    pseudonym=form_data[0]['pseudonym'],
                    current=form_data[0]['current'],
                    user_id=current_user_id
                )
        else:
            messages.error(self.request, 'Invalid confirm code! Please try again ')

        s.query(TableDevices).filter(
            TableDevices.idDevice == form_data[0]['name']
        ).update({TableDevices.confirmCode: None})
        s.commit()
        s.close()

        return HttpResponseRedirect('/accounts/devices/')
