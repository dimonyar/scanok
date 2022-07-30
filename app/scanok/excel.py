import os

from accounts.models import User

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

import pandas as pd

from scanok.forms import SettingXls
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

    user = get_object_or_404(User, id=request.user.id)

    if user.params:
        params = eval(user.params)
    else:
        params = {'set_export': {
            'file_name': 'Good',
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
            ]}
        }

    set_export = params['set_export']

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
        f"{path}/{set_export['file_name']}.xlsx",
        sheet_name=set_export['sheet_name'],
        index=False,
        startrow=set_export['startrow'],
        startcol=set_export['startcol'],
        header=set_export['header'],
        float_format="%.2f")

    response = FileResponse(
        open(f"static_content/{settings.MEDIA_URL}/{request.user.id}/download/{set_export['file_name']}.xlsx", 'rb'))

    return response


def settings_xls(request):
    user = get_object_or_404(User, id=request.user.id)

    if user.params:
        params = eval(user.params)
    else:
        params = {'set_export': {
            'file_name': 'Good',
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
            ]}
        }

    set_export = params['set_export']

    columns = set_export['columns']

    column1 = columns[0]
    column2 = columns[1]
    column3 = columns[2]
    column4 = columns[3]
    column5 = columns[4]
    column6 = columns[5]
    column7 = columns[6]
    file_name = set_export['file_name']
    sheet_name = set_export['sheet_name']
    start_row = set_export['startrow']
    start_col = set_export['startcol']
    header = set_export['header']

    if request.method == 'POST':
        form = SettingXls(request.POST)
        if form.is_valid():
            column1 = form.cleaned_data.get('Column1')
            column2 = form.cleaned_data.get('Column2')
            column3 = form.cleaned_data.get('Column3')
            column4 = form.cleaned_data.get('Column4')
            column5 = form.cleaned_data.get('Column5')
            column6 = form.cleaned_data.get('Column6')
            column7 = form.cleaned_data.get('Column7')
            file_name = form.cleaned_data.get('file_name')
            sheet_name = form.cleaned_data.get('sheet_name')
            start_row = form.cleaned_data.get('startrow')
            start_col = form.cleaned_data.get('startcol')
            header = form.cleaned_data.get('header')

            params = {'set_export': {
                'file_name': file_name,
                'sheet_name': sheet_name,
                'startrow': start_row,
                'startcol': start_col,
                'header': header,
                'columns': [
                    column1,
                    column2,
                    column3,
                    column4,
                    column5,
                    column6,
                    column7,
                ]}
            }

            User.objects.filter(
                id=request.user.id
            ).update(
                params=params
            )
        return redirect('scanok:goods')

    form = SettingXls(initial={
        'Column1': column1,
        'Column2': column2,
        'Column3': column3,
        'Column4': column4,
        'Column5': column5,
        'Column6': column6,
        'Column7': column7,
        'file_name': file_name,
        'sheet_name': sheet_name,
        'startrow': start_row,
        'startcol': start_col,
        'header': header
    })

    return render(request, 'settings_xls.html', context={'form': form})
