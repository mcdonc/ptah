""" Aplication Root """
import sqlalchemy as sqla
import ptah
from ptah import config
from zope import interface

from tinfo import Type
from node import Node, Session, set_policy
from container import Container
from interfaces import IApplicationRoot
from interfaces import IApplicationPolicy


class ApplicationRoot(Container):
    interface.implements(IApplicationRoot)

    __root_path__ = '/'

    __type__ = Type('app', 'Application')

    def __resource_url__(self, request, info):
        return self.__root_path__


class ApplicationPolicy(object):
    interface.implements(IApplicationPolicy)

    __name__ = ''
    __parent__ = None

    # default acl
    __acl__ = ptah.DEFAULT_ACL

    def __init__(self, request):
        self.request = request


Factories = {}

class ApplicationFactory(object):

    def __init__(self, path='', name='', title='',
                 tinfo = ApplicationRoot.__type__,
                 policy = ApplicationPolicy, default_root = None):
        self.id = '-'.join(part for part in path.split('/') if part)
        self.path = path if path.endswith('/') else '%s/'%path
        self.name = name
        self.title = title

        self.default_root = default_root
        if not path and default_root is None:
            self.default_root = True

        if isinstance(tinfo, type) and issubclass(tinfo, Node):
            tinfo = tinfo.__type__

        self.tinfo = tinfo
        self.policy = policy

        Factories[self.id] = self

        info = config.DirectiveInfo()
        info.attach(
            config.Action(None, discriminator=('ptah-cms:application', path))
            )

    _sql_get_root = ptah.QueryFreezer(
        lambda: Session.query(Container)\
            .filter(sqla.sql.and_(
                    Container.__name_id__ == sqla.sql.bindparam('name'),
                    Container.__type_id__ == sqla.sql.bindparam('type'))))

    def __call__(self, request=None):
        root = self._sql_get_root.first(name=self.name, type=self.tinfo.__uri__)
        if root is None:
            root = self.tinfo.create(title=self.title)
            root.__name_id__ = self.name
            root.__path__ = '/%s/'%root.__uri__
            Session.add(root)
            Session.flush()

        root.__root_path__ = self.path
        root.__parent__ = policy = self.policy(request)
        root.__default_root__ = self.default_root

        set_policy(policy)

        if request is not None:
            request.root = root
        return root


@config.cleanup
def cleanup():
    Factories.clear()
