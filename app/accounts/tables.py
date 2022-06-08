from accounts.models import Device

import django_tables2 as tables


class DeviceTable(tables.Table):
    action = tables.TemplateColumn(
        template_name="device_action.html", verbose_name="", orderable=False
    )

    created = tables.DateTimeColumn(format='d.m.Y')

    current = tables.TemplateColumn(
        template_name="device_current.html", verbose_name="current", orderable=False
    )

    class Meta:
        model = Device
        template_name = "django_tables2/bootstrap.html"
        fields = ('name', 'pseudonym', 'created', 'current')
        empty_text = "You don't have devices."
