from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from scanok import excel as scanok_excel
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

    path('goods/export', scanok_excel.export_goods, name='export_goods'),
    path('goods/settings_xls', scanok_excel.settings_xls, name='settings_xls'),

    path('stores/', scanok_views.Store.as_view(), name='stores'),
    path('stores/create/', scanok_views.store_create, name='store_create'),
    path('stores/delete/<int:pk>/', scanok_views.store_delete, name='store_delete'),
    path('stores/update/<int:pk>/', scanok_views.store_update, name='store_update'),

    path('users/', scanok_views.Users.as_view(), name='users'),
    path('users/create/', scanok_views.user_create, name='user_create'),
    path('users/delete/<int:pk>/', scanok_views.user_delete, name="user_delete"),
    path('users/update/<int:pk>/', scanok_views.user_update, name="user_update"),

    path('dochead/', scanok_views.DocheadTable.as_view(), name='dochead'),
    path('dochead/create/', scanok_views.doc_create, name='doc_create'),
    path('dochead/delete/<int:pk>/', scanok_views.doc_delete, name="dochead_delete"),
    path('dochead/update/<int:pk>/<int:page>/', scanok_views.doc_update, name="dochead_update"),
    path('dochead/update/<int:pk>/<int:page>/search-barcode/', csrf_exempt(scanok_views.search_barcode),
         name='search_barcode'),
    path('dochead/doc_hold/', csrf_exempt(scanok_views.doc_hold), name='doc_hold'),

    path('dochead/update/<int:pk>/<int:page>/add_detail', scanok_views.add_detail, name='add_detail'),
    path('dochead/update/<int:pk>/<int:page>/edit_detail/<int:plug>', scanok_views.update_detail, name='edit_detail'),
    path('dochead/update/<int:pk>/<int:page>/delete_detail/<int:plug>', scanok_views.detail_delete,
         name='detail_delete'),

    path('partners/', scanok_views.Partner.as_view(), name='partners'),
    path('partners/create/', scanok_views.partner_create, name='partner_create'),
    path('partners/delete/<int:pk>/', scanok_views.partner_delete, name="partner_delete"),
    path('partners/update/<int:pk>/', scanok_views.partner_update, name="partner_update"),



]
