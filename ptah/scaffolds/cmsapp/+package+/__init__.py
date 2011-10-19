from pyramid.config import Configurator
from pyramid.asset import abspath_from_asset_spec

import ptah
import ptah.cmsapp
from ptah.cmsapp.content import Page
from ptah.crowd.provider import CrowdUser, Session

from .app import APP_FACTORY

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=APP_FACTORY, settings=settings)

    config.include('ptah')
    config.ptah_init()

    # some more setup
    root = APP_FACTORY()

    # admin user
    user = Session.query(CrowdUser).first()
    if user is None:
        user = CrowdUser('Admin', 'admin', 'admin@ptahproject.org', '12345')
        Session.add(user)

    # give manager role to admin
    if user.uri not in root.__local_roles__:
        root.__local_roles__[user.uri] = [ptah.cmsapp.Manager.id]
    
    ptah.authService.set_userid(user.uri)

    # create default page
    if 'front-page' not in root.keys():
        page = Page(title=u'Welcome to Ptah')
        page.text = open(
            abspath_from_asset_spec('welcome.pt'), 'rb').read()

        root['front-page'] = page

    import transaction; transaction.commit()

    return config.make_wsgi_app()
