Example of Content Model
------------------------

The Ptah Content model is quite high level and provides a lot of functionality.
By inherienting from ptah.cms.content.Content you gain the following:

  - Automatically get polymorphism with ptah_cms_node table.
  - You do not need to specify a "uri resolver"
  - You will get fieldset representation (schema-ish) from model
  - You get security at the model level
  - Your model can participate in REST api without any work
  - Your model will have events thrown upon creation/delete/update
  - Automatically generated Add/Edit forms
  - Models will be added in the ptah.cmsapp UI/content heirarchy

All of the above can be overridden if you want fine-grain control of the
specifics. 

Until we have a better way; lets just create a file, link.py in the
src/devapp/devapp directory.  and inside the initialize module just
import link,

A simple model::

    import sqlalchemy as sqla
    from pyramid.httpexceptions import HTTPFound

    from ptah import view, form
    import ptah.cms
    from ptah import checkPermission
    
    class Link(ptah.cms.Content):
        __tablename__ = 'ptah_cms_link'
        __type__ = ptah.cms.Type('link', permission=ptah.cms.AddContent)
        href = sqla.Column(sqla.Unicode)

    @view.pview(context=Link, permission=ptah.cms.View, layout='page')
    def link_view(context, request):
        """ This is a default view for a Link model.
            If you have permission to edit it it will display the form.
            If you do not have ability to edit it; you will be redirected.
        """
        can_edit = checkPermission(ptah.cms.ModifyContent, context, throw=False)

        if can_edit:
            vform = form.DisplayForm(context, request)
            vform.fields = Link.__type__.fieldset
            vform.content = {
                'title': context.title,
                'description': context.description,
                'href': context.href}
            vform.update()

            # Uncomment below if you do not want the layout wrapper
            #return vform.render()

            layout = view.query_layout(request, context)
            return layout(vform.render())

        raise HTTPFound(location=context.href)

Before querying your model in REST, check out the base REST call::

    $ curl http://localhost:8080/__rest__/cms/

    ...
    json results
    ...


You can now query for this model using REST::

    $ curl http://localhost:8080/__rest__/cms/types

 ...
 {
  "__uri__": "cms+type:link",
  "name": "link",
  "title": "Link",
  "description": "",
  "permission": "ptah-cms:Add",
  "fieldset": [
   {
    "type": "text",
    "name": "title",
    "title": "Title",
    "description": "",
    "required": true
   },
   {
    "type": "textarea",
    "name": "description",
    "title": "Description",
    "description": "",
    "required": false
   },
   {
    "type": "text",
    "name": "href",
    "title": "Href",
    "description": "",
    "required": true
   }
  ]
 },
 ...


If you add a new field to your schema you will see it show up.  You can
create, update, delete your Link items through REST calls.  See rest.py and
devapp/ptahclient.py for examples.  
