""" default actions """
import ptah.cms

from .uiactions import uiaction

uiaction(
    ptah.cms.IContent, **{'id': 'view',
                          'title': 'View',
                          'action': '',
                          'permission': ptah.cms.View,
                          'sortWeight': 0.5})

uiaction(
    ptah.cms.IContent, **{'id': 'edit',
                          'title': 'Edit',
                          'action': 'edit.html',
                          'permission': ptah.cms.ModifyContent,
                          'sortWeight': 0.6})


uiaction(
    ptah.cms.IContainer, **{'id': 'adding',
                            'title': 'Add content',
                            'action': '+/',
                            'permission': ptah.cms.AddContent,
                            'sortWeight': 5.0})


uiaction(
    ptah.ILocalRolesAware, **{'id': 'sharing',
                              'title': 'Sharing',
                              'action': 'sharing.html',
                              'permission': ptah.cms.ShareContent,
                              'sortWeight': 10.0})
