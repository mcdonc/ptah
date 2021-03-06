""" password tool """
from os import urandom
from random import randint
from codecs import getencoder
from hashlib import sha1
from base64 import urlsafe_b64encode, urlsafe_b64decode
from datetime import timedelta

import ptah
from ptah import config, form, token

from settings import PTAH_CONFIG
from interfaces import _

PASSWORD_CHANGER_ID = 'ptah:password-changer'


TOKEN_TYPE = token.TokenType(
    '35c9b7df958f4e93ae9b275a7dc2219e', timedelta(minutes=10))


class PlainPasswordManager(object):
    """PLAIN password manager."""

    def encode(self, password, salt=None):
        return '{plain}%s'%password

    def check(self, encoded, password):
        if encoded != password:
            return encoded == '{plain}%s'%password
        return True


class SSHAPasswordManager(object):
    """SSHA password manager."""

    _encoder = getencoder("utf-8")

    def encode(self, password, salt=None):
        if salt is None:
            salt = urandom(4)
        hash = sha1(self._encoder(password)[0])
        hash.update(salt)
        return '{ssha}' + urlsafe_b64encode(hash.digest() + salt)

    def check(self, encoded_password, password):
        # urlsafe_b64decode() cannot handle unicode input string. We
        # encode to ascii. This is safe as the encoded_password string
        # should not contain non-ascii characters anyway.
        encoded_password = encoded_password.encode('ascii')
        byte_string = urlsafe_b64decode(encoded_password[6:])
        salt = byte_string[20:]
        return encoded_password == self.encode(password, salt)


class PasswordTool(object):
    """ Password management utility. """

    min_length = 5
    letters_digits = False
    letters_mixed_case = False

    pm = {'{plain}': PlainPasswordManager(),
          '{ssha}': SSHAPasswordManager(),
          }
    passwordManager = pm['{plain}']

    def check(self, encoded, password):
        """ check encoded password with plain password """
        try:
            pm, pwd = encoded.split('}', 1)
        except:
            return self.passwordManager.check(encoded, password)

        manager = self.pm.get('%s}'%pm)
        if manager is not None:
            return manager.check(encoded, password)
        return False

    def encode(self, password, salt=None):
        """ encode password with current password manager """
        return self.manager.encode(password, salt)

    def can_change_password(self, principal):
        """ can principal password be changed """
        return ptah.extract_uri_schema(principal.uri) in \
            config.registry.storage[PASSWORD_CHANGER_ID]

    def get_principal(self, passcode):
        """ generate passcode for principal """
        data = token.service.get(passcode)

        if data is not None:
            return ptah.resolve(data)

    def generate_passcode(self, principal):
        """ generate passcode for principal """
        return token.service.generate(TOKEN_TYPE, principal.uri)

    def remove_passcode(self, passcode):
        """ remove passcode """
        token.service.remove(passcode)

    def change_password(self, passcode, password):
        """ change password """
        principal = self.get_principal(passcode)

        self.remove_passcode(passcode)

        if principal is not None:
            changers = config.registry.storage[PASSWORD_CHANGER_ID]

            changer = changers.get(ptah.extract_uri_schema(principal.uri))
            if changer is not None:
                changer(principal, self.encode(password))
                return True

        return False

    def validate(self, password):
        """ Validate password """
        if len(password) < self.min_length:
            #return _('Password should be at least ${count} characters.',
            #         mapping={'count': self.min_length})
            return 'Password should be at least %s characters.'%\
                self.min_length
        elif self.letters_digits and \
                (password.isalpha() or password.isdigit()):
            return _('Password should contain both letters and digits.')
        elif self.letters_mixed_case and \
                (password.isupper() or password.islower()):
            return _('Password should contain letters in mixed case.')


passwordTool = PasswordTool()


def password_changer(schema):
    info = config.DirectiveInfo()

    def wrapper(changer):
        info.attach(
            config.Action(
                lambda config, schema, changer: \
                    config.storage[PASSWORD_CHANGER_ID].update(
                            {schema: changer}),
                (schema, changer),
                id = PASSWORD_CHANGER_ID,
                discriminator = (PASSWORD_CHANGER_ID, schema))
            )

        return changer

    return wrapper


def passwordValidator(field, appstruct):
    err = passwordTool.validate(appstruct)
    if err is not None:
        raise form.Invalid(field, err)


def passwordSchemaValidator(field, appstruct):
    if appstruct['password'] and appstruct['confirm_password']:
        if appstruct['password'] != appstruct['confirm_password']:
            raise form.Invalid(
                field, _("Password and Confirm Password should be the same."))

        passwordValidator(field, appstruct['password'])


PasswordSchema = form.Fieldset(

    form.FieldFactory(
        'password',
        'password',
        title = _(u'Password'),
        description = _(u'Enter password. '\
                        u'No spaces or special characters, should contain '\
                        u'digits and letters in mixed case.'),
        default = u''),

    form.FieldFactory(
        'password',
        'confirm_password',
        title = _(u'Confirm password'),
        description = _(u'Re-enter the password. '
                        u'Make sure the passwords are identical.'),
        default = u''),

    validator = passwordSchemaValidator
)


@config.subscriber(config.SettingsInitializing)
def initializing(ev):
    mng = PasswordTool.pm.get(PTAH_CONFIG.pwdmanager)
    if mng is None:
        mng = PasswordTool.pm.get('{%s}'%PTAH_CONFIG.pwdmanager)

    if mng is None:
        mng = PasswordTool.pm['{plain}']

    passwordTool.manager = mng
