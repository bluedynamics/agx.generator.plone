from node.ext.directory import Directory
from node.ext.template import DTMLTemplate
from agx.core import handler
from agx.generator.gs.scope import (
    ProfileScope,
    ContentTypeScope,
    DynamicViewScope,
)


@handler('gsprofiledirectories', 'uml2fs', 'hierarchygenerator',
         'gsprofile', order=100)
def gsprofiledirectories(self, source, target):
    """Create GS profile directories.
    """
    package = target.anchor
    if not 'profiles' in package:
        package['profiles'] = Directory()
        package['profiles']['default'] = Directory()
        package['profiles']['uninstall'] = Directory()
    package['profiles']['default'].factories['.xml'] = DTMLTemplate
    package['profiles']['uninstall'].factories['.xml'] = DTMLTemplate


@handler('gsprofilemetadata', 'uml2fs', 'hierarchygenerator',
         'gsprofile', order=110)
def gsprofilemetadata(self, source, target):
    """Create GS profile directories.
    """
    package = target.anchor
    default = package['profiles']['default']
    if 'metadata.xml' in default:
        metadata = default['metadata.xml']
    else:
        metadata = default['metadata.xml'] = DTMLTemplate()
    metadata.template = 'agx.generator.gs:templates/metadata.xml'
    
    # XXX: calculate from model
    metadata.params['version'] = 1.0
    
    # XXX: calculate from model
    metadata.params['description'] = 'Package description'
    
    # XXX: calculate from model
    metadata.params['dependencies'] = [
        'profile-foo.bar:default',
    ]