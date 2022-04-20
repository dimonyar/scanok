from django.urls import path

from scanok import views as scanok_views

app_name = 'scanok'

urlpatterns = [
    path('goods/', scanok_views.Goods.as_view(), name='goods'),
    path('stores/', scanok_views.Store.as_view(), name='stores'),
    path('users/', scanok_views.Users.as_view(), name='users'),
    path('partners/', scanok_views.Partner.as_view(), name='partners'),
    path('dochead/', scanok_views.Dochead.as_view(), name='dochead'),

    path('partners/create/', scanok_views.partner_create, name='partner_create'),
    path('partners/delete/<int:pk>/', scanok_views.partner_delete, name="partner_delete"),
    path('partners/update/<int:pk>/', scanok_views.partner_update, name="partner_update"),

    path('users/create/', scanok_views.user_create, name='user_create'),
    path('users/delete/<int:pk>/', scanok_views.user_delete, name="user_delete"),
]
