import agx.generator.gs
from zope.interface import implements
from agx.core.interfaces import IProfileLocation


class ProfileLocation(object):
    implements(IProfileLocation)
    name = u'gs.profile.uml'
    package = agx.generator.gs