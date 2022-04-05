from django.urls import path

from scanok import views as scanok_views

app_name = 'scanok'

urlpatterns = [
    path('goods/', scanok_views.Goods.as_view(), name='goods'),
    path('stores/', scanok_views.Store.as_view(), name='stores'),
    path('users/', scanok_views.Users.as_view(), name='users'),
    path('partners/', scanok_views.Partner.as_view(), name='partners'),
    path('partners/create/', scanok_views.partner_create, name='partner_create'),
    path('dochead/', scanok_views.Dochead.as_view(), name='dochead'),

]
