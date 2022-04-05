from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView

from scanok.forms import PartnerForm
from scanok.sqlclasstable import DocHead, Good, Partners, Stores, User

from settings.settings import database, password, port, server, user

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker


def conn_db(database):
    engine = create_engine(f'mssql+pymssql://{user}:{password}@{server}:{port}/{database}', echo=True)

    session = sessionmaker(bind=engine)
    s = session()   # noqa: VNE001
    return s


class Goods(ListView):
    s = conn_db(database)   # noqa: VNE001
    queryset = s.query(Good).order_by(Good.Name)
    template_name = 'goods.html'
    paginate_by = 25
    context_object_name = 'goods_list'
    s.close()


class Store(ListView):
    s = conn_db(database)   # noqa: VNE001
    queryset = s.query(Stores)
    template_name = 'stores.html'
    context_object_name = 'stores_list'
    s.close()


class Users(ListView):
    s = conn_db(database)   # noqa: VNE001
    queryset = s.query(User)
    template_name = 'users.html'
    context_object_name = 'users_list'
    s.close()


class Partner(ListView):
    s = conn_db(database)   # noqa: VNE001
    queryset = s.query(Partners).order_by(desc(Partners.PartnerF))
    template_name = 'partners.html'
    paginate_by = 25
    context_object_name = 'partners_list'
    s.close()


def partner_create(request):
    if request.method == 'POST':
        form = PartnerForm(request.POST)
        s = conn_db(database)  # noqa: VNE001
        if form.is_valid():
            partner_f = form.cleaned_data.get('PartnerF')
            if not partner_f:
                queryset = s.query(Partners.PartnerF).order_by(Partners.PartnerF)[-1]
                partner_f = str(int(queryset[0]) + 1)
            name_partner = form.cleaned_data.get('NamePartner')
            if s.query(Partners.NamePartner).filter(Partners.NamePartner == name_partner).first():
                return reverse_lazy('partner_create')
            discount = form.cleaned_data.get('Discount')
            if not discount:
                discount = 0.0

            c1 = Partners(PartnerF=partner_f, NamePartner=name_partner, Discount=discount, Deleted=0, Updated=1)
            s.add(c1)
            s.commit()

            return HttpResponseRedirect('/scanok/partners/')

    else:
        form = PartnerForm()
    return render(request, 'create.html', context={'form': form})


class Dochead(ListView):
    s = conn_db(database)  # noqa: VNE001
    queryset = s.query(DocHead.DocType, DocHead.Comment, Partners.NamePartner, DocHead.CreateDate, DocHead.DocStatus,
                       Stores.NameStore)
    template_name = 'dochead.html'
    paginate_by = 25
    context_object_name = 'dochead_list'
    s.close()
