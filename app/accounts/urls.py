from accounts import views

from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


app_name = 'accounts'

urlpatterns = [
    path('my-profile/', views.MyProfile.as_view(), name='my-profile'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('activate/<uuid:username>/', views.ActivateUser.as_view(), name='activate-user'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('devices/', views.Devices.as_view(), name='devices'),
    path('devices/create/', views.DeviceCreate.as_view(), name='device_create'),
    path('devices/update/<int:pk>/', views.DeviceUpdate.as_view(), name='device_update'),
    path('devices/delete/<int:pk>/', views.DeviceDelete.as_view(), name='device_delete'),
    path('devices/search-devices/', csrf_exempt(views.search_devices), name='search_devices'),
    path('devices/current-device/', csrf_exempt(views.current_device), name='current_devices'),
    path('devices/list-devices/', csrf_exempt(views.list_devices), name='list_devices'),


]
