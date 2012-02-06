from node.ext.directory import Directory
from node.ext.template import DTMLTemplate
from node.ext.zcml import (
    ZCMLFile,
    SimpleDirective,
)
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
    """Create metadata.xml
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


@handler('gsprofilezcml', 'uml2fs', 'hierarchygenerator',
         'gsprofile', order=120)
def gsprofilezcml(self, source, target):
    """Create configure.zcml if not exists yet, profiles.zcml and profile
    specific directives.
    """
    package = target.anchor
    if 'configure.zcml' in package:
        configure = package['configure.zcml']
    else:
        configure = package['configure.zcml'] = ZCMLFile()
    if not configure.filter(tag='include', attr='file', value='profiles.zcml'):
        include = SimpleDirective(name='include', parent=configure)
        include.attrs['file'] = 'profiles.zcml'
    if 'profiles.zcml' in package:
        profiles = package['profiles.zcml']
    else:
        profiles = package['profiles.zcml'] = ZCMLFile()
    profiles.nsmap['genericsetup'] = 'http://namespaces.zope.org/genericsetup'
    if not profiles.filter(tag='include',
                           attr='package',
                           value='Products.GenericSetup'):
        include = SimpleDirective(name='include', parent=profiles)
        include.attrs['package'] = 'Products.GenericSetup'
        include.attrs['file'] = 'meta.zcml'
    if not profiles.filter(tag='genericsetup:registerProfile',
                           attr='name',
                           value='default'):
        profile = SimpleDirective(name='include', parent=profiles)
        profile.attrs['name'] = 'default'
    else:
        profile = profiles.filter(tag='genericsetup:registerProfile',
                                  attr='name',
                                  value='default')[0]
    
    # XXX: compute from model
    profile.attrs['title'] = 'Package title'
    profile.attrs['description'] = 'Extension profile for product_name'
    
    profile.attrs['directory'] = 'profiles/default'
    profile.attrs['provides'] = 'Products.GenericSetup.interfaces.EXTENSION'
