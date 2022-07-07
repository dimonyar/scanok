import json
import uuid
from datetime import datetime

from accounts.models import Device

from django.conf import settings
from django.contrib import messages
from django.core.paginator import EmptyPage, Paginator
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView

from django_tables2 import SingleTableView

from scanok.epochtime import data_to_tact
from scanok.forms import BarcodeForm, DocDetailsForm, DocheadForm, GoodForm, PartnerForm, StoreForm, UserForm
from scanok.hashmd5 import str2hash
from scanok.sqlclasstable import Barcode, DocDetails, DocHead, Good, Partners, ScanHistory, Stores, User
from scanok.tables import DocHeadTable
from scanok.util import next_f

from sqlalchemy import create_engine, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker


def conn_db(request):
    current_id = request.user.id
    try:
        database = Device.objects.get(user_id=current_id, current=True).name
    except Device.DoesNotExist:
        raise Http404
    else:
        engine = create_engine(f'mssql+pymssql://{settings.USER}:{settings.PASSWORD}@'
                               f'{settings.SERVER}:{settings.PORT}/{database}', echo=True)

        session = sessionmaker(bind=engine)
        s = session()  # noqa: VNE001
        return s


def good_barcode_list(request, pk=None):
    s = conn_db(request)  # noqa: VNE001
    if pk:
        query = s.query(Good, Barcode).join(
            Barcode, Barcode.GoodF == Good.GoodF
        ).filter(
            Good.id == pk
        )
    else:
        query = s.query(Good, Barcode).join(
            Barcode, Barcode.GoodF == Good.GoodF
        ).order_by(-Good.id)

    query_dict = {}
    for key, value in query:
        if query_dict.get(key):
            query_dict[key].append(value)
        else:
            query_dict.update({key: [value]})

    record = list(query_dict.items())

    return record


class Goods(ListView):
    template_name = 'goods.html'
    paginate_by = 25
    context_object_name = 'goods_list'

    def get_queryset(self):
        record = good_barcode_list(self.request)
        return record


class GoodsDetails(ListView):
    template_name = 'good_details.html'
    context_object_name = 'details_list'

    def get_queryset(self):
        record = good_barcode_list(self.request, self.kwargs['pk'])
        return record


def good_update(request, pk):
    record = good_barcode_list(request, pk)

    barcode_list = record[0][1]

    value = record[0][0]

    good_f = value.GoodF
    good_name = value.Name
    good_price = value.Price
    good_unit = value.Unit

    s = conn_db(request)  # noqa: VNE001
    instance = s.query(Good).filter(Good.id == pk)
    if request.method == 'POST':
        form = GoodForm(request.POST)
        if form.is_valid():
            good_name = form.cleaned_data.get('Name')
            good_price = form.cleaned_data.get('Price')
            good_unit = form.cleaned_data['Unit']

            instance.update({
                Good.Name: good_name,
                Good.Price: good_price,
                Good.Unit: good_unit,
                Good.Updated: 1.0,
            })
            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/goods/')

    else:
        form = GoodForm(initial={'GoodF': good_f, 'Name': good_name, 'Price': good_price, 'Unit': good_unit})

    return render(request, 'good_update.html', context={
        'form': form, 'barcode_list': barcode_list, 'pk': pk
    })


def good_create(request):
    s = conn_db(request)  # noqa: VNE001
    last_good = s.query(Good.GoodF).order_by(-Good.id).first()[0]

    if last_good:
        next_good_f = next_f(last_good)
    else:
        next_good_f = '1'

    if request.method == 'POST':
        form = GoodForm(request.POST)
        if form.is_valid():
            good_f = form.cleaned_data.get('GoodF')
            if not good_f:
                good_f = next_good_f

            name = form.cleaned_data.get('Name')
            price = form.cleaned_data['Price']
            unit = form.cleaned_data['Unit']

            c1 = Good(GoodF=good_f, Name=name, Price=price, Deleted=0, Updated=1, Unit=unit, Field_2='A')
            s.add(c1)
            s.commit()
            pk = c1.id
            s.close()

            return HttpResponseRedirect(f'/scanok/goods/add_barcode/{pk}/')

    else:
        form = GoodForm(initial={'GoodF': next_good_f, 'Unit': 'шт.'})
    return render(request, 'good_create.html', context={'form': form})


def good_delete(request, pk):
    s = conn_db(request)  # noqa: VNE001
    good = s.query(Good).filter(Good.id == pk)

    if request.method == 'POST':
        good.update({Good.Deleted: 1})
        s.query(Barcode).filter(Barcode.GoodF == good[0].GoodF).update({Barcode.Deleted: 1})
        s.commit()

        s.close()
        return HttpResponseRedirect('/scanok/goods/')
    else:
        return render(request, 'good_delete.html', context={'good': good})


def search_goods(request):
    if request.method == 'POST':
        search = json.loads(request.body).get('searchText')

        s = conn_db(request)  # noqa: VNE001
        goods = s.query(Good, Barcode).join(
            Barcode, Barcode.GoodF == Good.GoodF
        ).filter(or_(Barcode.BarcodeName == search, Good.GoodF == search, Good.Name.contains(search)))

        query_dict = {}

        for key, value in goods:
            value.__dict__.pop('_sa_instance_state')
            if query_dict.get(key):
                query_dict[key].append(value.__dict__)
            else:
                query_dict.update({key: [value.__dict__]})

        data = []
        for key, value in query_dict.items():
            key.__dict__.pop('_sa_instance_state')
            record = key.__dict__
            record.update({'Barcode': value})
            data.append(record)

        return JsonResponse(data, safe=False)


def barcode_create(request, pk):
    s = conn_db(request)  # noqa: VNE001

    good = s.query(Good).filter(Good.id == pk).one()
    good_f = good.GoodF
    if request.method == 'POST':
        form = BarcodeForm(request.POST)
        if form.is_valid():
            barcode = form.cleaned_data.get('BarcodeName')
            code = form.cleaned_data['Code']
            count = form.cleaned_data['Count']

            try:
                c1 = Barcode(GoodF=good_f, BarcodeName=barcode, Code=code, Deleted=0, Updated=1, Count=count)
                if c1:
                    s.add(c1)
                    s.commit()
                    s.close()
            except IntegrityError:
                request.session['entered_barcode'] = barcode
                request.session['entered_code'] = code
                request.session['entered_count'] = count
                request.session['good_f'] = good_f
                return HttpResponseRedirect(f'/scanok/goods/add_barcode/{pk}/#error')

            return HttpResponseRedirect(f'/scanok/goods/update/{pk}/')

    else:
        form = BarcodeForm(initial={'GoodF': good_f.zfill(6), 'Code': good_f.zfill(6), 'Count': 1.0})
    return render(request, 'barcode_create.html', context={'form': form, 'Good': good})


def barcode_update(request, pk):
    s = conn_db(request)  # noqa: VNE001

    query = s.query(Good.id, Barcode.GoodF, Barcode.BarcodeName, Barcode.Code, Barcode.Count).join(
        Barcode, Barcode.GoodF == Good.GoodF
    ).filter(
        Barcode.id == pk
    ).one()

    good_f = query['GoodF']
    barcode_name = query['BarcodeName']
    code = query['Code']
    count = query['Count']
    good_id = query['id']

    if request.method == 'POST':
        form = BarcodeForm(request.POST)
        if form.is_valid():
            barcode_name = form.cleaned_data.get('BarcodeName')
            code = form.cleaned_data['Code']
            count = form.cleaned_data['Count']

            instance = s.query(Barcode).filter(Barcode.id == pk)

            instance.update({
                Barcode.Code: code,
                Barcode.Count: count,
                Barcode.Updated: 1.0,
            })
            s.commit()
            s.close()
            return HttpResponseRedirect(f'/scanok/goods/update/{good_id}/')

    form = BarcodeForm(initial={
        'GoodF': good_f.zfill(6),
        'BarcodeName': barcode_name,
        'Code': code.zfill(6),
        'Count': count,
    })

    return render(request, 'barcode_update.html', context={'form': form})


def barcode_delete(request, pk):
    s = conn_db(request)  # noqa: VNE001

    instance = s.query(Good.id, Barcode.BarcodeName).join(
        Barcode, Barcode.GoodF == Good.GoodF
    ).filter(
        Barcode.id == pk
    ).one()

    barcode_name = instance['BarcodeName']
    good_id = instance['id']

    if request.method == 'POST':
        s.query(Barcode).filter(Barcode.id == pk).update({Barcode.Deleted: 1})
        s.commit()
        return HttpResponseRedirect(f'/scanok/goods/update/{good_id}/')

    return render(request, 'barcode_delete.html', context={'BarcodeName': barcode_name})


def barcode_assign(request, pk):
    barcode = request.session.get('entered_barcode')
    code = request.session.get('entered_code')
    count = request.session.get('entered_count')
    good_f = request.session.get('good_f')

    s = conn_db(request)  # noqa: VNE001

    instance = s.query(Barcode).filter(Barcode.BarcodeName == barcode)

    instance.update({
        Barcode.GoodF: good_f,
        Barcode.Code: code,
        Barcode.Count: count,
        Barcode.Updated: 1.0,
        Barcode.Deleted: 0.0,
    })
    s.commit()
    s.close()

    del request.session['entered_barcode']
    del request.session['entered_code']
    del request.session['entered_count']
    del request.session['good_f']

    return HttpResponseRedirect(f'/scanok/goods/update/{pk}/')


class Store(ListView):
    template_name = 'stores.html'
    context_object_name = 'stores_list'

    def get_queryset(self):
        s = conn_db(self.request)  # noqa: VNE001
        return s.query(Stores)


def store_create(request):
    s = conn_db(request)  # noqa: VNE001

    last_store_f = s.query(Stores.StoreF).order_by(-Stores.id).first()[0]

    if last_store_f:
        next_store_f = next_f(last_store_f)
    else:
        next_store_f = '1'

    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store_f = form.cleaned_data.get('StoreF')
            name_store = form.cleaned_data.get('NameStore')

            if not store_f:
                store_f = next_store_f
            try:
                c1 = Stores(StoreF=store_f, NameStore=name_store, Deleted=0, Updated=1)
                if c1:
                    s.add(c1)
                    s.commit()
                    s.close()
            except IntegrityError:
                messages.error(request, f'StoreF - {store_f} already used')
                return HttpResponseRedirect('/scanok/stores/create/')

            return HttpResponseRedirect('/scanok/stores/')
    else:
        form = StoreForm(initial={'StoreF': next_store_f})
    return render(request, 'store_create.html', context={'form': form})


def store_delete(request, pk):
    s = conn_db(request)  # noqa: VNE001
    instance = s.query(Stores).filter(Stores.id == pk)
    if request.method == 'POST':
        instance.update({Stores.Deleted: 1})
        s.commit()
        s.close()
        return HttpResponseRedirect('/scanok/stores/')
    else:
        return render(request, 'store_delete.html', context={'store': instance})


def store_update(request, pk):
    s = conn_db(request)  # noqa: VNE001
    instance = s.query(Stores).filter(Stores.id == pk)

    store = instance.one()
    store_f = store.StoreF
    name_store = store.NameStore

    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            name_store = form.cleaned_data.get('NameStore')

            instance.update({
                Stores.NameStore: name_store,
                Stores.Updated: 1.0,
            })

            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/stores/')

    else:
        form = StoreForm(initial={'StoreF': store_f, 'NameStore': name_store})

    return render(request, 'store_update.html', context={'form': form})


class Users(ListView):
    template_name = 'users.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        s = conn_db(self.request)  # noqa: VNE001
        return s.query(User).all()


def user_create(request):
    s = conn_db(request)  # noqa: VNE001

    last_user = s.query(User.UserF).order_by(-User.id).first()[0]

    if last_user:
        next_user_f = last_user + 1
    else:
        next_user_f = '1'

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user_f = form.cleaned_data.get('UserF')

            if not user_f:
                user_f = next_user_f

            login = form.cleaned_data.get('Login')
            if s.query(User.Login).filter(User.Login == login).first():
                messages.error(request, f'Login - {login} already used')
                return HttpResponseRedirect('/scanok/user/create/')

            name = form.cleaned_data.get('Name')
            password = form.cleaned_data['Password']

            hash_password = str2hash(password)

            c1 = User(UserF=user_f, Login=login, Name=name, Password=hash_password, Deleted=0, Updated=1)
            s.add(c1)
            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/users/')

    else:
        form = UserForm(initial={'UserF': next_user_f})
    return render(request, 'user_create.html', context={'form': form})


def user_update(request, pk):
    s = conn_db(request)  # noqa: VNE001
    instance = s.query(User).filter(User.id == pk)

    user = instance.one()

    user_f = user.UserF
    name = user.Name
    login = user.Login
    password_old = user.Password

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():

            login = form.cleaned_data.get('Login')
            name = form.cleaned_data.get('Name')
            password = form.cleaned_data.get('Password')

            if not password:
                password = password_old
            else:
                password = str2hash(password)

            instance.update({
                User.Login: login,
                User.Name: name,
                User.Password: password,
                User.Updated: 1.0
            })

            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/users/')

    else:
        form = UserForm(initial={'UserF': user_f, 'Login': login, 'Name': name})

    return render(request, 'user_update.html', context={'form': form})


def user_delete(request, pk):
    s = conn_db(request)  # noqa: VNE001
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
        s = conn_db(self.request)  # noqa: VNE001
        return s.query(Partners).order_by(-Partners.id)


def partner_delete(request, pk):
    s = conn_db(request)  # noqa: VNE001
    instance = s.query(Partners).filter(Partners.id == pk)
    if request.method == 'POST':
        instance.update({Partners.Deleted: 1})
        s.commit()
        s.close()
        return HttpResponseRedirect('/scanok/partners/')
    else:
        return render(request, 'partner_delete.html', context={'partner': instance})


def partner_update(request, pk):
    s = conn_db(request)  # noqa: VNE001
    instance = s.query(Partners).filter(Partners.id == pk)

    partners = instance.one()

    partner_f = partners.PartnerF
    name_partner = partners.NamePartner
    discount = partners.Discount

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
        form = PartnerForm(initial={'PartnerF': partner_f, 'NamePartner': name_partner, 'Discount': discount})
    return render(request, 'partner_update.html', context={'form': form})


def partner_create(request):
    s = conn_db(request)  # noqa: VNE001

    last_partner_f = s.query(Partners.PartnerF).order_by(-Partners.id).first()[0]

    if last_partner_f:
        next_partner_f = next_f(last_partner_f)
    else:
        next_partner_f = '1'

    if request.method == 'POST':
        form = PartnerForm(request.POST)

        if form.is_valid():
            partner_f = form.cleaned_data.get('PartnerF')
            if not partner_f:
                partner_f = next_partner_f
            name_partner = form.cleaned_data.get('NamePartner')
            discount = form.cleaned_data.get('Discount')

            if not discount:
                discount = 0.0

            c1 = Partners(PartnerF=partner_f, NamePartner=name_partner, Discount=discount, Deleted=0, Updated=1)
            s.add(c1)
            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/partners/')

    else:
        form = PartnerForm(initial={'PartnerF': next_partner_f, 'Discount': 0.0})
    return render(request, 'partner_create.html', context={'form': form})


class DocheadTable(SingleTableView):
    table_class = DocHeadTable
    template_name = 'dochead.html'
    paginate_by = 25

    def get_queryset(self):
        s = conn_db(self.request)  # noqa: VNE001
        record = s.query(
            DocHead.id,
            DocHead.DocType,
            DocHead.Comment,
            Partners.NamePartner,
            DocHead.CreateDate,
            DocHead.DocStatus,
            Stores.NameStore,
        ).outerjoin(
            Partners, Partners.PartnerF == DocHead.PartnerF
        ).outerjoin(
            Stores, Stores.StoreF == DocHead.MainStoreF
        ).order_by(-DocHead.CreateDate).all()

        return record


def doc_delete(request, pk):
    s = conn_db(request)  # noqa: VNE001
    instance = s.query(DocHead).filter(DocHead.id == pk)
    if request.method == 'POST':
        instance.delete()
        s.commit()
        s.close()
        return HttpResponseRedirect('/scanok/dochead/')
    else:
        return render(request, 'dochead_delete.html', context={'dochead': instance})


def doc_create(request):
    s = conn_db(request)  # noqa: VNE001

    users = s.query(User.UserF, User.Name).all()
    partners = s.query(Partners.PartnerF, Partners.NamePartner).order_by(-Partners.id)
    stores = s.query(Stores.StoreF, Stores.NameStore).order_by(Stores.NameStore)

    if request.method == 'POST':
        form = DocheadForm(request.POST, UserF=users, PartnerF=partners, MainStoreF=stores)

        if form.is_valid():
            comment = form.cleaned_data.get('Comment')
            partner = form.cleaned_data.get('PartnerF')
            main_store = form.cleaned_data.get('MainStoreF')
            alternate_store = form.cleaned_data.get('AlternateStoreF')
            doctype = form.cleaned_data.get('DocType')
            user = form.cleaned_data.get('UserF')
            if not user:
                user = -1
            barcodedocu = form.cleaned_data.get('BarcodeDocu')
            discount = form.cleaned_data.get('Discount')
            if not discount:
                discount = 0.0

            create_date = data_to_tact(datetime.now())

            c1 = DocHead(
                DocHeadF=uuid.uuid4(),
                Comment=comment,
                PartnerF=partner,
                MainStoreF=main_store,
                AlternateStoreF=alternate_store,
                DocType=doctype,
                UserF=user,
                BarcodeDocu=barcodedocu,
                CreateDate=create_date,
                DocStatus=0,
                Discount=discount,
                Deleted=0,
                Updated=1,
                UpdatedFromTSD=0,
                UpdateFrom1C=1
            )

            s.add(c1)
            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/dochead/')

    else:
        form = DocheadForm(initial={'Discount': 0.0}, UserF=users, PartnerF=partners, MainStoreF=stores)

    return render(request, 'doc_create.html', context={'form': form})


def doc_update(request, pk, page=1):
    s = conn_db(request)  # noqa: VNE001

    instance = s.query(DocHead).filter(DocHead.id == pk)

    doc_head = instance.one()
    comment = doc_head.Comment
    user = doc_head.UserF
    partner = doc_head.PartnerF
    main_store = doc_head.MainStoreF
    alternate_store = doc_head.AlternateStoreF
    doctype_code = doc_head.DocType.code
    barcodedocu = doc_head.BarcodeDocu
    discount = doc_head.Discount

    users = s.query(User.UserF, User.Name).all()
    partners = s.query(Partners.PartnerF, Partners.NamePartner).filter(Partners.Deleted == 0).order_by(-Partners.id)
    stores = s.query(Stores.StoreF, Stores.NameStore).filter(Stores.Deleted == 0).order_by(Stores.NameStore)

    query = s.query(
        DocDetails.GoodF,
        Good.Name,
        DocDetails.Price,
        DocDetails.Count_Doc,
        DocDetails.Count_Real,
        ScanHistory,
    ).join(
        Good, DocDetails.GoodF == Good.GoodF
    ).outerjoin(
        ScanHistory, ScanHistory.DocDetailsF == DocDetails.DocDetailsF
    ).filter(
        DocDetails.DocHeadF == doc_head.DocHeadF
    ).order_by(DocDetails.id)

    query_list = []
    for i in query:
        key = ((i[0], i[1], i[2], i[3], i[4],), i[5])
        query_list.append(key)

    query_dict = {}
    for key, value in query_list:
        if query_dict.get(key):
            query_dict[key].append(value)
        else:
            query_dict.update({key: [value]})

    record = list(query_dict.items())

    doc_details_list = record

    paginator = Paginator(doc_details_list, 25)

    try:
        doc_details_list = paginator.page(page)
    except EmptyPage:
        doc_details_list = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = DocheadForm(request.POST, UserF=users, PartnerF=partners, MainStoreF=stores)

        if form.is_valid():
            comment = form.cleaned_data.get('Comment')
            partner = form.cleaned_data.get('PartnerF')
            main_store = form.cleaned_data.get('MainStoreF')
            alternate_store = form.cleaned_data.get('AlternateStoreF')
            doctype = form.cleaned_data.get('DocType')
            user = form.cleaned_data.get('UserF')
            if not user:
                user = -1
            barcodedocu = form.cleaned_data.get('BarcodeDocu')
            discount = form.cleaned_data.get('Discount')
            if not discount:
                discount = 0.0

            instance.update({
                DocHead.Comment: comment,
                DocHead.PartnerF: partner,
                DocHead.MainStoreF: main_store,
                DocHead.AlternateStoreF: alternate_store,
                DocHead.DocType: doctype,
                DocHead.UserF: user,
                DocHead.BarcodeDocu: barcodedocu,
                DocHead.Discount: discount,
                DocHead.Updated: 1,
                DocHead.UpdateFrom1C: 1,
                DocHead.UpdatedFromTSD: 0,
            })

            s.commit()
            s.close()

            return HttpResponseRedirect('/scanok/dochead/')

    else:
        form = DocheadForm(initial={
            'Comment': comment,
            'BarcodeDocu': barcodedocu,
            'Discount': discount,
            'DocType': doctype_code,
            'PartnerF': partner,
            'MainStoreF': main_store,
            'AlternateStoreF': alternate_store,
            'UserF': user

        }, UserF=users, PartnerF=partners, MainStoreF=stores)

    return render(request, 'doc_update.html', context={'form': form, 'doc_details': doc_details_list, 'pk': pk})


def add_detail(request, pk):
    s = conn_db(request)  # noqa: VNE001

    doc_head = s.query(DocHead).filter(DocHead.id == pk).one()
    doc_head_f = doc_head.DocHeadF
    user = doc_head.UserF

    goods = s.query(Good.GoodF, Good.Name).filter(Good.Deleted == 0).order_by(Good.Name)

    if request.method == 'POST':
        form = DocDetailsForm(request.POST, GoodF=goods)

        if form.is_valid():

            good_f = form.cleaned_data.get('GoodF')
            count_doc = form.cleaned_data.get('Count_Doc')
            price = form.cleaned_data.get('Price')
            comment = form.cleaned_data.get('Spec_comment')
            create_date = data_to_tact(datetime.now())

            if not count_doc:
                count_doc = 1

            if not price:
                price = s.query(Good.Price).filter(Good.GoodF == good_f).one()[0]

            c1 = DocDetails(
                DocHeadF=doc_head_f,
                DocDetailsF=uuid.uuid4(),
                Bad_price=0,
                Price_problem=0,
                Count_Doc=count_doc,
                Count_Real=0,
                CreateDate=create_date,
                GoodF=good_f,
                Hend_enter=0,
                Price=price,
                Expiration=0,
                Spec_comment=comment,
                UserF=user,
                UpdatedFromTSD=0,
                UpdateFrom1C=1,
                Updated=1,
                Deleted=0
            )

            s.add(c1)
            s.commit()
            s.close()

            return HttpResponseRedirect(f'/scanok/dochead/update/{pk}/1/')

    else:
        form = DocDetailsForm(GoodF=goods)

    return render(request, 'add_detail.html', context={'form': form})
