from django.contrib import admin
from django.urls import path

from scanok.views import dochead, goods, partners, start,  stores, user


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', start),
    path('goods/', goods),
    path('stores/', stores),
    path('user/', user),
    path('partners/', partners),
    path('dochead/', dochead),

]
