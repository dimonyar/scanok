from accounts.models import Device

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView

from scanok.forms import GoodForm, PartnerForm, UserForm
from scanok.hashmd5 import str2hash
from scanok.sqlclasstable import DocHead, Good, Partners, Stores, User

from settings.settings import password, port, server, user

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker


def conn_db():
    if Device.objects.filter(current=True):
        database = Device.objects.get(current=True).name
    else:
        database = list(Device.objects.values_list('name')[:1])[0][0]

    engine = create_engine(f'mssql+pymssql://{user}:{password}@{server}:{port}/{database}', echo=True)

    session = sessionmaker(bind=engine)
    s = session()  # noqa: VNE001
    return s


class Goods(ListView):
    template_name = 'goods.html'
    paginate_by = 25
    context_object_name = 'goods_list'

    def get_queryset(self):
        s = conn_db()  # noqa: VNE001
        return s.query(Good).order_by(Good.Name)


def good_update(request, pk):
    s = conn_db()  # noqa: VNE001
    instance = s.query(Good).filter(Good.id == pk).one()

    good_f = instance.GoodF
    good_name = instance.Name
    good_price = instance.Price
    good_unit = instance.Unit
    if request.method == 'POST':
        form = GoodForm(request.POST)
        if form.is_valid():

            good_name = form.cleaned_data.get('Name')
            good_price = form.cleaned_data.get('Price')
            good_unit = form.cleaned_data['Unit']

            instance.update({
                Good.Name: good_name,
                Good.Price: good_price,
                Good.Unit: good_unit
            })
            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/goods/')

    else:
        form = GoodForm(initial={'GoodF': good_f, 'Name': good_name, 'Price': good_price, 'Unit': good_unit})
    return render(request, 'good_update.html', context={'form': form})


def good_create(request):
    s = conn_db()  # noqa: VNE001
    last_good = s.query(Good.GoodF).order_by(Good.GoodF)[-1]
    if request.method == 'POST':
        form = GoodForm(request.POST)
        if form.is_valid():
            good_f = form.cleaned_data.get('GoodF')
            if not good_f:
                good_f = str(int(last_good[0]) + 1)

            name = form.cleaned_data.get('Name')
            price = form.cleaned_data['Price']
            unit = form.cleaned_data['Unit']

            c1 = Good(GoodF=good_f, Name=name, Price=price, Deleted=0, Updated=1, Unit=unit, Field_2='A')
            s.add(c1)
            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/goods/')

    else:
        form = GoodForm(initial={'GoodF': str(int(last_good[0]) + 1), 'Unit': 'шт.'})
    return render(request, 'good_create.html', context={'form': form})


def good_delete(request, pk):
    s = conn_db()  # noqa: VNE001
    instance = s.query(Good).filter(Good.id == pk)
    if request.method == 'POST':
        instance.update({Good.Deleted: 1})
        s.commit()
        s.close()
        return HttpResponseRedirect('/scanok/goods/')
    else:
        return render(request, 'good_delete.html', context={'good': instance})


class Store(ListView):
    template_name = 'stores.html'
    context_object_name = 'stores_list'

    def get_queryset(self):
        s = conn_db()  # noqa: VNE001
        return s.query(Stores)


class Users(ListView):
    template_name = 'users.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        s = conn_db()  # noqa: VNE001
        return s.query(User)


def user_create(request):
    s = conn_db()  # noqa: VNE001
    last_userf = s.query(User.UserF).order_by(User.UserF)[-1]
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user_f = form.cleaned_data.get('UserF')
            if not user_f:
                user_f = str(int(last_userf[0]) + 1)

            login = form.cleaned_data.get('Login')
            if s.query(User.Login).filter(User.Login == login).first():
                return reverse_lazy('user_create')
            name = form.cleaned_data.get('Name')
            password = form.cleaned_data['Password']

            hash_password = str2hash(password)

            c1 = User(UserF=user_f, Login=login, Name=name, Password=hash_password, Deleted=0, Updated=1)
            s.add(c1)
            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/users/')

    else:
        form = UserForm(initial={'UserF': str(int(last_userf[0]) + 1)})
    return render(request, 'user_create.html', context={'form': form})


def user_delete(request, pk):
    s = conn_db()  # noqa: VNE001
    instance = s.query(User).filter(User.id == pk)
    if request.method == 'POST':
        instance.update({User.Deleted: 1})
        s.commit()
        s.close()
        return HttpResponseRedirect('/scanok/users/')
    else:
        return render(request, 'user_delete.html', context={'user': instance})


class Partner(ListView):
    template_name = 'partners.html'
    paginate_by = 25
    context_object_name = 'partners_list'

    def get_queryset(self):
        s = conn_db()  # noqa: VNE001
        return s.query(Partners).order_by(desc(Partners.PartnerF))


def partner_delete(request, pk):
    s = conn_db()  # noqa: VNE001
    instance = s.query(Partners).filter(Partners.id == pk)
    if request.method == 'POST':
        instance.update({Partners.Deleted: 1})
        s.commit()
        s.close()
        return HttpResponseRedirect('/scanok/partners/')
    else:
        return render(request, 'partner_delete.html', context={'partner': instance})


def partner_update(request, pk):
    s = conn_db()  # noqa: VNE001
    instance = s.query(Partners).filter(Partners.id == pk)
    partner_f = s.query(Partners.PartnerF).filter(Partners.id == pk).one()
    name_partner = s.query(Partners.NamePartner).filter(Partners.id == pk).one()
    discount = s.query(Partners.Discount).filter(Partners.id == pk).one()
    if request.method == 'POST':
        form = PartnerForm(request.POST)
        if form.is_valid():

            name_partner = form.cleaned_data.get('NamePartner')
            discount = form.cleaned_data.get('Discount')
            if not discount:
                discount = 0.0

            instance.update({Partners.NamePartner: name_partner,
                             Partners.Discount: discount, Partners.Deleted: 0, Partners.Updated: 1})
            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/partners/')

    else:
        form = PartnerForm(initial={'PartnerF': partner_f[0], 'NamePartner': name_partner[0], 'Discount': discount[0]})
    return render(request, 'partner_update.html', context={'form': form})


def partner_create(request):
    if request.method == 'POST':
        form = PartnerForm(request.POST)
        s = conn_db()  # noqa: VNE001
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
            s.close()

            return HttpResponseRedirect('/scanok/partners/')

    else:
        form = PartnerForm()
    return render(request, 'partner_create.html', context={'form': form})


class Dochead(ListView):
    template_name = 'dochead.html'
    paginate_by = 25
    context_object_name = 'dochead_list'

    def get_queryset(self):
        s = conn_db()  # noqa: VNE001
        return s.query(DocHead.DocType, DocHead.Comment, Partners.NamePartner, DocHead.CreateDate, DocHead.DocStatus,
                       Stores.NameStore)
