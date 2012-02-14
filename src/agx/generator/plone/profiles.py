import agx.generator.plone
from zope.interface import implements
from agx.core.interfaces import IProfileLocation


class ProfileLocation(object):
    implements(IProfileLocation)
    name = u'plone.profile.uml'
    package = agx.generator.plone