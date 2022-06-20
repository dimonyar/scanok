from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from scanok import views as scanok_views


app_name = 'scanok'

urlpatterns = [
    path('goods/', scanok_views.Goods.as_view(), name='goods'),
    path('goods/create/', scanok_views.good_create, name='good_create'),
    path('goods/update/<int:pk>/', scanok_views.good_update, name='good_update'),
    path('goods/delete/<int:pk>/', scanok_views.good_delete, name='good_delete'),
    path('goods/details/<int:pk>/', scanok_views.GoodsDetails.as_view(), name='good_details'),
    path('goods/search-goods/', csrf_exempt(scanok_views.search_goods), name='search_goods'),

    path('goods/add_barcode/<int:pk>/', scanok_views.barcode_create, name='add_barcode'),
    path('goods/update_barcode/<int:pk>/', scanok_views.barcode_update, name='update_barcode'),
    path('goods/delete_barcode/<int:pk>/', scanok_views.barcode_delete, name='delete_barcode'),
    path('goods/assign_barcode/<int:pk>/', scanok_views.barcode_assign, name='assign_barcode'),

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
