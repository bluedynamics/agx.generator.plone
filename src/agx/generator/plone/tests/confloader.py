from zope.interface import implements
from zope.configuration.xmlconfig import XMLConfig
from agx.core.interfaces import IConfLoader
import agx.generator.uml
import agx.generator.pyegg
import agx.generator.zca
import agx.generator.plone


class ConfLoader(object):
    
    implements(IConfLoader)
    
    transforms = [
        'xmi2uml',
        'uml2fs',
    ]
    
    def __call__(self):
        XMLConfig('configure.zcml', agx.generator.uml)()
        XMLConfig('configure.zcml', agx.generator.pyegg)()
        XMLConfig('configure.zcml', agx.generator.zca)()
        XMLConfig('configure.zcml', agx.generator.plone)()