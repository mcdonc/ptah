""" addon system """
import pkg_resources
from ptah  import config, view, manage
from ptah.config import directives

from core import ADDONS


class AddonModule(manage.PtahModule):
    """Add-ons management"""

    title = 'Add-ons'
    manage.module('addons')


class AddonView(view.View):
    view.pview(
        context = AddonModule,
        template = view.template('ptah.addon:templates/addon.pt'))

    def update(self):
        data = []

        for dist in ADDONS:
            data.append(dist)

        self.addons = data

        if 'form.button.install' in self.request.POST:
            for name in self.request.POST.getall('addon'):
                for dist in self.addons:
                    if dist.project_name == name:
                        dist.activate()
                        actions = directives.scan(name, set())
                        pkg_resources.working_set.add(dist)
                        for action in actions:
                            action()
