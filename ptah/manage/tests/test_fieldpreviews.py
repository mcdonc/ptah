import transaction
import ptah
from ptah import config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from ptah import form, config
from ptah.form.field import PREVIEW_ID
from ptah.manage import fieldpreviews

from base import Base


class TestFieldPreviews(Base):

    def test_multiChoicePreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.MultiChoiceField],
                      fieldpreviews.multiChoicePreview)

        request = DummyRequest()
        html = fieldpreviews.multiChoicePreview(request)
        self.assertIn('Multi choice field', html)

    def test_choicePreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.ChoiceField],
                      fieldpreviews.choicePreview)

        request = DummyRequest()
        html = fieldpreviews.choicePreview(request)
        self.assertIn('Choice field', html)

    def test_boolPreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.BoolField],
                      fieldpreviews.boolPreview)

        request = DummyRequest()
        html = fieldpreviews.boolPreview(request)
        self.assertIn('Boolean field', html)

    def test_radioPreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.RadioField],
                      fieldpreviews.radioPreview)

        request = DummyRequest()
        html = fieldpreviews.radioPreview(request)
        self.assertIn('Radio field', html)

    def test_textareaPreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.TextAreaField],
                      fieldpreviews.textareaPreview)

        request = DummyRequest()
        html = fieldpreviews.textareaPreview(request)
        self.assertIn('TextArea field', html)

    def test_linesPreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.LinesField],
                      fieldpreviews.linesPreview)

        request = DummyRequest()
        html = fieldpreviews.linesPreview(request)
        self.assertIn('Lines field', html)

    def test_textPreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.TextField],
                      fieldpreviews.textPreview)

        request = DummyRequest()
        html = fieldpreviews.textPreview(request)
        self.assertIn('Text field', html)

    def test_intPreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.IntegerField],
                      fieldpreviews.intPreview)

        request = DummyRequest()
        html = fieldpreviews.intPreview(request)
        self.assertIn('Integer field', html)

    def test_floatPreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.FloatField],
                      fieldpreviews.floatPreview)

        request = DummyRequest()
        html = fieldpreviews.floatPreview(request)
        self.assertIn('Float field', html)

    def test_decimalPreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.DecimalField],
                      fieldpreviews.decimalPreview)

        request = DummyRequest()
        html = fieldpreviews.decimalPreview(request)
        self.assertIn('Decimal field', html)

    def test_passwordPreview(self):
        previews = config.registry.storage[PREVIEW_ID]
        self.assertIs(previews[form.PasswordField],
                      fieldpreviews.passwordPreview)

        request = DummyRequest()
        html = fieldpreviews.passwordPreview(request)
        self.assertIn('Password field', html)


class TestFieldsModule(Base):

    def test_fields_module(self):
        from ptah.manage.manage import PtahManageRoute
        from ptah.manage.fields import FieldsModule

        request = DummyRequest()

        ptah.authService.set_userid('test')
        ptah.PTAH_CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['fields']

        self.assertIsInstance(mod, FieldsModule)

    def test_fields_view(self):
        from ptah.manage.fields import FieldsModule, FieldsView

        request = DummyRequest()

        mod = FieldsModule(None, request)

        res = FieldsView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

        from ptah.form.field import FIELD_ID, PREVIEW_ID

        fields = config.registry.storage[FIELD_ID]
        previews = config.registry.storage[PREVIEW_ID]

        view = FieldsView(None, request)
        view.update()

        self.assertEqual(len(view.fields), len(fields))
        self.assertIn('name', view.fields[0])
        self.assertIn('preview', view.fields[0])
