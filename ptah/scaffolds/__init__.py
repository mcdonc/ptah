import os

from paste.script.templates import Template
from paste.util.template import paste_script_template_renderer

class PtahTemplate(Template):
    def pre(self, command, output_dir, vars):
        vars['random_string'] = os.urandom(20).encode('hex')
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        return Template.pre(self, command, output_dir, vars)

class CMSAppProjectTemplate(PtahTemplate):
    _template_dir = 'cmsapp'
    summary = 'Ptah CMS app project'
    template_renderer = staticmethod(paste_script_template_renderer)

