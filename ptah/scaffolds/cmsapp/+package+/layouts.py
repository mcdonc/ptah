import ptah, ptah.cms
from ptah import view 
from ptah import manage, authService

class PageLayout(view.Layout):
    view.layout('page', ptah.cms.ApplicationRoot,
                layer = 'test',
                template = view.template('templates/layoutpage.pt'))

    """ override 'page' layout

    layer - identifier, import order does matter, last imported wins
    """

    def render(self, content, **kwargs):
        """ default implementation, just example. in most cases
        default implementation is ok. """
        if self.template is None:
            return content

        kwargs.update({'view': self,
                       'content': content,
                       'context': self.context,
                       'request': self.request,
                       'format': format})

        return self.template(**kwargs)


class WorkspaceLayout(view.Layout):
    view.layout('workspace', ptah.cms.ApplicationRoot,
                parent = 'page',
                layer = 'test',
                template = view.template('templates/layoutworkspace.pt'))

    """ same as PageLayout, it uses 'page' as parent layout """

    def update(self):
        self.user = ptah.authService.get_current_principal()
        self.ptahManager = ptah.manage.get_access_manager()(ptah.authService.get_userid()) 
        self.isAnon = self.user is None

