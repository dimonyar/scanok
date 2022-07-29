import os

from django.conf import settings
from django.http import FileResponse

import pandas as pd

from scanok.sqlclasstable import Barcode, Good
from scanok.views import conn_db


def export_goods(request):
    s = conn_db(request)  # noqa: VNE001

    record = s.query(
        Good,
        Barcode
    ).outerjoin(
        Barcode, Barcode.GoodF == Good.GoodF
    ).filter(Good.Deleted == 0).order_by(Good.Name).all()

    good_f = []
    barcode = []
    code = []
    count = []
    name = []
    price = []
    unit = []
    for rec in record:
        good_f.append(rec.Good.GoodF)
        name.append(rec.Good.Name)
        price.append(rec.Good.Price)
        unit.append(rec.Good.Unit)

        if rec.Barcode:
            barcode.append(rec.Barcode.BarcodeName)
            code.append(rec.Barcode.Code)
            count.append(rec.Barcode.Count)
        else:
            barcode.append(None)
            code.append(None)
            count.append(None)

    path = os.path.join(settings.MEDIA_ROOT, str(request.user.id), 'download')

    if not os.path.exists(path):
        os.makedirs(path)

    set_export = {
        'sheet_name': 'Sheet1',
        'startrow': 0,
        'startcol': 0,
        'header': True,
        'columns': [
            'Code',
            'Name',
            'Unit',
            'Price',
            'Barcode',
            'Article',
            'Qty per pack'
        ]
    }

    name_column = {
        'Code': good_f,
        'Name': name,
        'Unit': unit,
        'Price': price,
        'Barcode': barcode,
        'Article': code,
        'Qty per pack': count
    }

    df = pd.DataFrame(list(zip(
        name_column[set_export['columns'][0]],
        name_column[set_export['columns'][1]],
        name_column[set_export['columns'][2]],
        name_column[set_export['columns'][3]],
        name_column[set_export['columns'][4]],
        name_column[set_export['columns'][5]],
        name_column[set_export['columns'][6]]
    )), columns=set_export['columns'])

    df.to_excel(
        f"{path}/output.xlsx",
        sheet_name=set_export['sheet_name'],
        index=False,
        startrow=set_export['startrow'],
        startcol=set_export['startcol'],
        header=set_export['header'],
        float_format="%.2f")

    response = FileResponse(open(f"static_content/{settings.MEDIA_URL}/{request.user.id}/download/output.xlsx", 'rb'))

    return response
