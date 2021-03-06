""" Page """
import ptah
import sqlalchemy as sqla

from ptah import cms
from ptah.cmsapp.permissions import AddPage


class Page(cms.Content):

    __tablename__ = 'ptah_cmsapp_pages'

    __type__ = cms.Type(
        'page',
        title = 'Page',
        description = 'A page in the site.',
        permission = AddPage,
        name_suffix = '.html',
        )

    text = sqla.Column(sqla.Unicode,
                       info = {'field_type': 'tinymce'})


ptah.view.register_view(
    context = Page,
    permission = cms.View,
    template = ptah.view.template('ptah.cmsapp:templates/page.pt'))
