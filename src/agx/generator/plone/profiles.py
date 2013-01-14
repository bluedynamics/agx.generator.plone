import agx.generator.plone
from zope.interface import implementer
from agx.core.interfaces import IProfileLocation


@implementer(IProfileLocation)
class ProfileLocation(object):
    name = u'plone.profile.uml'
    package = agx.generator.plone
