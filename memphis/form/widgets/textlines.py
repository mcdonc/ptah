""" Text Lines widget implementation """
import colander
from zope import interface

from memphis import config, view
from memphis.form import pagelets
from memphis.form.widgets import textarea

from interfaces import _, ITextLinesWidget


class TextLinesWidget(textarea.TextAreaWidget):
    """Input type sequence widget implementation."""
    config.adapts(colander.SchemaNode, colander.Sequence)
    config.adapts(colander.SchemaNode, colander.Sequence, name='textlines')
    interface.implementsOnly(ITextLinesWidget)

    __fname__ = 'textlines'
    __title__ = _('Text lines widget')
    __description__ = _('Text area based widget, '
                        'each line is treated as sequence element.')


view.registerPagelet(
    'form-display', ITextLinesWidget,
    template=view.template("memphis.form.widgets:textlines_display.pt"))

view.registerPagelet(
    'form-input', ITextLinesWidget,
    template=view.template("memphis.form.widgets:textlines_input.pt"))
