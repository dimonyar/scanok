from scanok.hashmd5 import str2hash
from scanok.forms import PartnerForm, TerminalBase
from scanok.sqlclasstable import DocDetails, DocHead, Good, Partners, PriceAndRemains, SalesReceipts, ScanHistory, \
    Stores, User

from settings.settings import database, password, port, server, user

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from scanok.epochtime import tact_to_data, data_to_tact
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView


# database = 'cb6321f3a9b155db5f1c42c322efd47b'


def conn_db(database):
    engine = create_engine(f'mssql+pymssql://{user}:{password}@{server}:{port}/{database}', echo=True)

    session = sessionmaker(bind=engine)
    s = session()
    return s


class Goods(ListView):
    s = conn_db(database)
    queryset = s.query(Good).order_by(Good.Name)
    template_name = 'goods.html'
    paginate_by = 25
    context_object_name = 'goods_list'
    s.close()


class Store(ListView):
    s = conn_db(database)
    queryset = s.query(Stores)
    template_name = 'stores.html'
    context_object_name = 'stores_list'
    s.close()


class Users(ListView):
    s = conn_db(database)
    queryset = s.query(User)
    template_name = 'users.html'
    context_object_name = 'users_list'
    s.close()


class Partner(ListView):
    s = conn_db(database)
    queryset = s.query(Partners).order_by(desc(Partners.PartnerF))
    template_name = 'partners.html'
    paginate_by = 25
    context_object_name = 'partners_list'
    s.close()


# class PartnerCreate(CreateView):
#     queryset = s.query(Partners)
#     template_name = 'create.html'
#     form_class = PartnerForm
#     success_url = reverse_lazy('partners')


def partner_create(request):

    if request.method == 'POST':
        form = PartnerForm(request.POST)
        s = conn_db(database)
        if form.is_valid():
            PartnerF = form.cleaned_data.get('PartnerF')
            if not PartnerF:
                queryset = s.query(Partners.PartnerF).order_by(Partners.PartnerF)[-1]
                PartnerF = str(int(queryset[0]) + 1)
            NamePartner = form.cleaned_data.get('NamePartner')
            if s.query(Partners.NamePartner).filter(Partners.NamePartner == NamePartner).first():
                print('A Partner with the same name already exists')
                return reverse_lazy('partner_create')
            Discount = form.cleaned_data.get('Discount')
            if not Discount:
                Discount = 0.0

            c1 = Partners(PartnerF=PartnerF, NamePartner=NamePartner, Discount=Discount, Deleted=0, Updated=1)
            s.add(c1)
            s.commit()

            return HttpResponseRedirect('/scanok/partners/')

    else:
        form = PartnerForm()
    return render(request, 'create.html', context={'form': form})


class Dochead(ListView):
    s = conn_db(database)
    queryset = s.query(DocHead.DocType, DocHead.Comment, Partners.NamePartner, DocHead.CreateDate, DocHead.DocStatus,
                       Stores.NameStore)
    template_name = 'dochead.html'
    paginate_by = 25
    context_object_name = 'dochead_list'
    s.close()
