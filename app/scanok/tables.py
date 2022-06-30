import django_tables2 as tables

from scanok import model_choices as mch
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

    def render_DocStatus(self, value): # noqa N802
        choices = dict(mch.DocHeadDocStatus.choices)
        if value in choices.keys():
            return choices[value]
        else:
            return value

    def render_CreateDate(self, value): # noqa N802
        return tact_to_data(value)

    class Meta:
        template_name = "django_tables2/bootstrap.html"
        empty_text = "You don't have documents."
