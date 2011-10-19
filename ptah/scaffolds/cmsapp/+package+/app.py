import ptah.cms


class ApplicationRoot(ptah.cms.ApplicationRoot):

    __type__ = ptah.cms.Type('cmsapp')


APP_FACTORY = ptah.cms.ApplicationFactory(
    name='root', 
    title='{{project}} Application',
    tinfo = ApplicationRoot.__type__)
