""" basic app settings """
import uuid
import colander
import sqlahelper
import sqlalchemy
import pyramid_beaker
import translationstring
from ptah import config
from pyramid.interfaces import IAuthenticationPolicy, IAuthorizationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

from ptah.security import LocalRoles

_ = translationstring.TranslationStringFactory('ptah')

types = {
    '': (),
    'auth_tkt': (AuthTktAuthenticationPolicy, ('secret',), ('callback',)),
}

SECURITY = config.register_settings(
    'auth',

    config.SchemaNode(
        colander.Str(),
        name = 'policy',
        title = _('Authentication policy'),
        validator = colander.OneOf(types.keys()),
        required = False,
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'secret',
        title = _('Policy secret'),
        description = _('The secret (a string) used for auth_tkt '
                        'cookie signing'),
        required = False),

    config.SchemaNode(
        colander.Bool(),
        name = 'authorization',
        title = _('Authorization policy'),
        description = _('Enable/disable default authorization policy.'),
        required = False,
        default = True),

    title = _('Pyramid authentication settings'),
    validator = config.RequiredWithDependency('secret','policy','auth_tkt',''),
)
SECURITY['callback'] = LocalRoles


SESSION = config.register_settings(
    'session',

    config.SchemaNode(
        colander.Str(),
        name = 'type',
        title = _('The name of the back-end'),
        description = _('Available back-ends supplied with Beaker: file, dbm, memory, ext:memcached, ext:database, ext:google'),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'data_dir',
        title = _('Data directory'),
        description = _('Used with any back-end that stores its data in physical files, such as the dbm or file-based back-ends. This path should be an absolute path to the directory that stores the files.'),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'lock_dir',
        title = _('Lock directory'),
        description = _("Used with every back-end, to coordinate locking. With caching, this lock file is used to ensure that multiple processes/threads aren't attempting to re-create the same value at the same time (The Dog-Pile Effect)"),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'url',
        title = _('URL'),
        description = _('URL is specific to use of either ext:memcached or ext:database. When using one of those types, this option is required.'),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'key',
        required = False,
        title = _('Key'),
        default = '',
        description = _('Name of the cookie key used to save the session under.')),

    config.SchemaNode(
        colander.Str(),
        name = 'secret',
        required = False,
        title = _('Secret'),
        default = '',
        description = _('Used with the HMAC to ensure session integrity. This value should ideally be a randomly generated string.')),

    title = _('Pyramid session'),
    description = _('Beaker session configuration settings'),
    validator = (config.RequiredWithDependency('key', 'type', default=''),
                 config.RequiredWithDependency('secret', 'type', default='')),
)

SQLA = config.register_settings(
    'sqla',

    config.SchemaNode(
        colander.Str(),
        name = 'url',
        default = '',
        title = 'Engine URL',
        description = 'SQLAlchemy database engine URL'),

    config.SchemaNode(
        colander.Bool(),
        name = 'cache',
        default = True,
        title = 'Cache',
        description = 'Eanble SQLAlchemy statement caching'),

    title = 'SQLAlchemy settings',
    description = 'Configuration settings for a SQLAlchemy database engine.'
    )

SQL_compiled_cache = {}


@config.subscriber(config.SettingsInitializing)
def initializing(ev):
    # auth
    if not SECURITY.secret:
        SECURITY.secret = uuid.uuid4().get_hex()

    pname = SECURITY.policy
    if pname not in ('', 'no-policy'):
        policyFactory, attrs, kw = types[pname]

        settings = []
        for attr in attrs:
            settings.append(SECURITY.get(attr))

        kwargs = {'wild_domain': False}
        for attr in kw:
            kwargs[attr] = SECURITY.get(attr)

        policy = policyFactory(*settings, **kwargs)
        config.registry.registerUtility(policy, IAuthenticationPolicy)

    if SECURITY.authorization:
        config.registry.registerUtility(
            ACLAuthorizationPolicy(), IAuthorizationPolicy)


@config.subscriber(config.SettingsInitializing)
def sqla_initializing(ev):
    url = SQLA.url
    if url:
        engine_args = {}
        if SQLA.cache:
            engine_args['execution_options'] = \
                {'compiled_cache': SQL_compiled_cache}
        try:
            engine = sqlahelper.get_engine()
        except:
            engine = sqlalchemy.engine_from_config(
                {'sqlalchemy.url': url}, 'sqlalchemy.', **engine_args)
            sqlahelper.add_engine(engine)


@config.subscriber(config.AppStarting)
def start(ev):
    # session
    session_factory = pyramid_beaker \
       .session_factory_from_settings(SESSION)
    ev.config.set_session_factory(session_factory)
