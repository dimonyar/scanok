import django_tables2 as tables

from scanok.templatetags.extra_teg import tact_to_data


class DocHeadTable(tables.Table):
    DocType = tables.Column()
    Comment = tables.Column()
    NamePartner = tables.Column()
    DocStatus = tables.Column()
    NameStore = tables.Column()
    CreateDate = tables.Column()
    action = tables.TemplateColumn(
        template_name="dochead_action.html", verbose_name="", orderable=False
    )

    def render_createdate(self, value):
        return tact_to_data(value)

    class Meta:
        template_name = "django_tables2/bootstrap.html"
        empty_text = "You don't have documents."
