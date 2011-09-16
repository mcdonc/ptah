""" add/edit user """
from zope import interface
from memphis import config, view, form
from pyramid.httpexceptions import HTTPFound

from ptah.security import passwordTool, PrincipalAddedEvent

from interfaces import _
from provider import CrowdUser, Session
from schemas import UserSchema, ManagerChangePasswordSchema
from module import ICrowdModule, ICrowdUser #, IManageUserAction


class CreateUserForm(form.Form):
    view.pyramidView('create.html', ICrowdModule, 'ptah-manage', layout='')

    __intr_path__ = '/ptah-manage/crowd/create.html'

    csrf = True
    label = _('Create new user')
    fields = form.Fields(UserSchema).omit('id', 'joined')

    @form.button(_('Create'), actype=form.AC_PRIMARY)
    def create(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        # create user
        user = CrowdUser(data['name'], data['login'], data['login'])
        # set password
        user.password = passwordTool.encodePassword(data['password'])
        Session.add(user)
        Session.flush()
        
        self.request.registry.notify(PrincipalAddedEvent(user))

        self.message('User has been created.', 'success')
        raise HTTPFound(location='./')


#class Info(object):
#    config.utility(name='user-info')
#    interface.implements(IManageUserAction)

#    title = _('Information')
#    action = 'index.html'

#    def available(self, principal):
#        return True


class UserInfo(form.Form):
    view.pyramidView('index.html', ICrowdUser,
                     'ptah-manage', default = True, layout='')

    __intr_path__ = '/ptah-manage/crowd/${user}/index.html'

    label = 'Update user'

    fields = form.Fields(UserSchema)
    fields['id'].readonly = True

    def getContent(self):
        return self.context.user

    @form.button(_('Modify'), actype=form.AC_PRIMARY)
    def modify(self):
        #user.validated = True
        #self.message("Account  has been validated.", 'info')
        pass

    @form.button(_('Remove'), actype=form.AC_DANGER)
    def remove(self):
        #user.validated = True
        #self.message("Account  has been validated.", 'info')
        pass


#class ChangePasswordAction(object):
#    config.utility(name='user-password')
#    interface.implements(IManageUserAction)

#    title = _('Change password')
#    action = 'password.html'

#    def available(self, principal):
#        return True


class ChangePassword(form.Form):
    view.pyramidView('password.html', ICrowdUser, 'ptah-manage', layout='')

    __intr_path__ = '/ptah-manage/crowd/${user}/password.html'

    csrf = True
    fields = form.Fields(ManagerChangePasswordSchema)

    label = _('Change password')
    description = _('Please specify password for this users.')

    @form.button(_('Change'), actype=form.AC_PRIMARY)
    def change(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        sm = self.request.registry

        self.context.user.password = \
            passwordTool.encodePassword(data['password'])

        self.message("User password has been changed.")
