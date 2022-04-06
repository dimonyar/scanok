from accounts.forms import DeviceForm, SignUpForm
from accounts.models import Device, User

from crum import get_current_user

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, RedirectView, UpdateView


class MyProfile(LoginRequiredMixin, UpdateView):
    queryset = User.objects.all()
    template_name = 'my_profile.html'
    success_url = reverse_lazy('index')
    fields = (
        'first_name',
        'last_name',
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


class Devices(ListView):
    model = Device
    template_name = 'devices.html'
    context_object_name = 'devices_list'

    def get_queryset(self):
        current_id = get_current_user().id
        new_context = Device.objects.filter(
            user_id=current_id)
        return new_context


class DeviceCreate(CreateView):
    model = Device
    template_name = 'device_create.html'
    form_class = DeviceForm
    success_url = reverse_lazy('accounts:devices')

    def test_func(self):
        return self.request.user.is_superuser
