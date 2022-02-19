from scanok.sqlclasstable import DocDetails, DocHead, Good, Partners, PriceAndRemains, SalesReceipts, ScanHistory,\
    Stores, User

from settings.settings import database, password, port, server, user

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scanok.epochtime import tact_to_data, data_to_tact
from django.http import HttpResponse

from scanok.hashmd5 import str2hash

engine = create_engine(f'mssql+pymssql://{user}:{password}@{server}:{port}/{database}', echo=True)

session = sessionmaker(bind=engine)
s = session()


def start(request):
    goods = '/goods/'
    stores = '/stores/'
    users = '/user/'
    partners = '/partners/'
    dochead = '/dochead/'
    html = f'''
               <ul>
                 <li><a href="{goods}">{goods}</a></li>
                 <li><a href="{stores}">{stores}</a></li>
                 <li><a href="{users}">{users}</a></li>
                 <li><a href="{partners}">{partners}</a></li>
               </ul>
               <ul>
                 <li><a href="{dochead}">{dochead}</a></li>
               </ul>
               '''
    return HttpResponse(html)


def goods(request):
    result = s.query(Good.GoodF, Good.Name, Good.Unit, Good.Price)
    html = '<table border="1">' \
           '<col width="50" valign="top align="right">' \
           '<col width="500" valign="top" align="left">' \
           '<col width="50" valign="top" align="center">' \
           '<col width="100" valign="top" align="right">'
    for row in result:
        html += '<tr><td>' + row[0] + '</td><td>' + row[1] + '</td><td>' + row[2] + '</td><td>' + str(
            int(row[3])) + '</td></tr>'
    html += '</table>'

    return HttpResponse(html)


def stores(request):
    result = s.query(Stores.StoreF, Stores.NameStore)
    html = '<table border="1">' \
           '<col width="50" valign="top align="left">' \
           '<col width="300" valign="top" align="left">'
    for row in result:
        html += '<tr><td>' + row[0] + '</td><td>' + row[1] + '</td></tr>'
    html += '</table>'

    return HttpResponse(html)


def user(request):
    result = s.query(User.UserF, User.Name, User.Login, User.Password)
    html = '<table border="1">' \
           '<col width="50" valign="top align="left">' \
           '<col width="300" valign="top" align="left">' \
           '<col width="300" valign="top" align="left">' \
           '<col width="300" valign="top" align="left">'
    for row in result:
        user_f = str(row[0])
        name = row[1]
        login = row[2]
        pw = row[3]
        if user_f == '-1':
            continue
        html += '<tr><td>' + user_f + '</td><td width="auto">' + name + '</td><td width="auto">' \
                + login + '</td><td>' + pw + '</td></tr>'
    html += '</table>'

    return HttpResponse(html)


def partners(request):
    result = s.query(Partners.PartnerF, Partners.NamePartner, Partners.Discount).order_by(Partners.NamePartner)
    html = '<table border="1">' \
           '<col width="50" valign="top align="left">' \
           '<col width="500" valign="top" align="left">' \
           '<col width="50" valign="top" align="left">'
    for row in result:
        html += f'<tr><td>{row.PartnerF}</td><td>{row.NamePartner}</td><td width="auto">{str(row.Discount)}</td></tr>'
    html += '</table>'

    return HttpResponse(html)


def dochead(request):
    result = s.query(DocHead.DocType, DocHead.Comment, Partners.NamePartner, DocHead.CreateDate, DocHead.DocStatus,
                     Stores.NameStore).join(Partners).join(Stores)
    html = '<table border="1">' \
           '<col width="50" valign="top align="left">' \
           '<col width="500" valign="top" align="left">' \
           '<col width="100" valign="top" align="left">' \
           '<col width="100" valign="top" align="left">' \
           '<col width="100" valign="top" align="left">'
    typ = {1: 'приходный', 2: 'расходный', 3: 'инвентаризация', 4: 'перемещение', 5: 'списание', 6: 'возврат',
           7: 'сбор штрихкодов', 8: 'сбор штрихкодов с характеристиками'}
    for row in result:
        html += f'<tr><td>{typ[row.DocType]}</td><td>{row.Comment}</td><td>{row.NamePartner}</td><' \
                f'td>{tact_to_data(row.CreateDate)}</td><td>{str(row.DocStatus)}</td><td>{row.NameStore}</td></tr> '
    html += '</table>'

    return HttpResponse(html)
