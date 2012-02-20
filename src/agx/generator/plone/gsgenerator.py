from node.ext.directory import Directory
from node.ext.template import DTMLTemplate
from node.ext.zcml import (
    ZCMLFile,
    SimpleDirective,
)
from agx.core import handler
from agx.generator.pyegg.utils import egg_source


@handler('gsprofiledirectories', 'uml2fs', 'hierarchygenerator',
         'gsprofile', order=100)
def gsprofiledirectories(self, source, target):
    """Create GS profile directories.
    """
    package = target.anchor
    
    # create profiles directory and subdirectories if not exists
    if not 'profiles' in package:
        package['profiles'] = Directory()
    
    # create default profile folder if not exists
    if not 'default' in package['profiles']:
        package['profiles']['default'] = Directory()
    
    # create uninstall profile folder if not exists
    if not 'uninstall' in package['profiles']:
        package['profiles']['uninstall'] = Directory()
    
    # set child node factories for xml files
    package['profiles']['default'].factories['.xml'] = DTMLTemplate
    package['profiles']['uninstall'].factories['.xml'] = DTMLTemplate


@handler('gsprofilezcml', 'uml2fs', 'hierarchygenerator',
         'gsprofile', order=110)
def gsprofilezcml(self, source, target):
    """Create configure.zcml if not exists yet, profiles.zcml and profile
    specific directives.
    """
    package = target.anchor
    
    # read or create configure.zcml
    if 'configure.zcml' in package:
        configure = package['configure.zcml']
    else:
        configure = package['configure.zcml'] = ZCMLFile()
    
    # if include profile.zcml missing, add it
    if not configure.filter(tag='include', attr='file', value='profiles.zcml'):
        include = SimpleDirective(name='include', parent=configure)
        include.attrs['file'] = 'profiles.zcml'
    
    # read or create profiles.zcml
    if 'profiles.zcml' in package:
        profiles = package['profiles.zcml']
    else:
        snmap = {
            None: 'http://namespaces.zope.org/zope',
            'genericsetup': 'http://namespaces.zope.org/genericsetup',
        }
        profiles = package['profiles.zcml'] = ZCMLFile(nsmap=snmap)
    
    # if include Products.GenericSetup missing, add it
    if not profiles.filter(tag='include',
                           attr='package',
                           value='Products.GenericSetup'):
        include = SimpleDirective(name='include', parent=profiles)
        include.attrs['package'] = 'Products.GenericSetup'
        include.attrs['file'] = 'meta.zcml'
    
    # read or create install profile directive
    if not profiles.filter(tag='genericsetup:registerProfile',
                           attr='name',
                           value='default'):
        install = SimpleDirective(name='genericsetup:registerProfile',
                                  parent=profiles)
        install.attrs['name'] = 'default'
    else:
        install = profiles.filter(tag='genericsetup:registerProfile',
                                  attr='name',
                                  value='default')[0]
    
    egg_name = egg_source(source).name
    
    # set default profile directive attributes
    install.attrs['title'] = '%s install' % egg_name
    install.attrs['description'] = 'Install %s in Plone' % egg_name
    install.attrs['directory'] = 'profiles/default'
    install.attrs['provides'] = 'Products.GenericSetup.interfaces.EXTENSION'
    
    # read or create uninstall profile directive
    if not profiles.filter(tag='genericsetup:registerProfile',
                           attr='name',
                           value='uninstall'):
        uninstall = SimpleDirective(name='genericsetup:registerProfile',
                                    parent=profiles)
        uninstall.attrs['name'] = 'uninstall'
    else:
        uninstall = profiles.filter(tag='genericsetup:registerProfile',
                                  attr='name',
                                  value='uninstall')[0]
    
    # set uninstall profile directive attributes
    uninstall.attrs['title'] = '%s uninstall' % egg_name
    uninstall.attrs['description'] = 'Uninstall %s in Plone' % egg_name
    uninstall.attrs['directory'] = 'profiles/uninstall'
    uninstall.attrs['provides'] = 'Products.GenericSetup.interfaces.EXTENSION'


@handler('gsprofilemetadata', 'uml2fs', 'hierarchygenerator',
         'gsprofile', order=110)
def gsprofilemetadata(self, source, target):
    """Create metadata.xml
    """
    package = target.anchor
    default = package['profiles']['default']
    
    # read or create metadata.xml
    if 'metadata.xml' in default:
        metadata = default['metadata.xml']
    else:
        metadata = default['metadata.xml'] = DTMLTemplate()
    
    # set template used for metadata.xml
    metadata.template = 'agx.generator.plone:templates/metadata.xml'
    
    # set template params
    # XXX: calculate from model
    metadata.params['version'] = '1'
    metadata.params['description'] = 'Package description'
    metadata.params['dependencies'] = list()


@handler('gsprofilecssregistry', 'uml2fs', 'hierarchygenerator',
         'gsprofile', order=110)
def gsprofilecssregistry(self, source, target):
    """Create cssregistry.xml
    """
    package = target.anchor
    default = package['profiles']['default']
    
    # read or create cssregistry.xml
    if 'cssregistry.xml' in default:
        cssregistry = default['cssregistry.xml']
    else:
        cssregistry = default['cssregistry.xml'] = DTMLTemplate()
    
    # set template used for cssregistry.xml
    cssregistry.template = 'agx.generator.plone:templates/cssregistry.xml'
    
    # set template params
    # XXX: calculate from model
    cssregistry.params['css'] = [{                      
        'title': '',
        'cacheable': 'True',
        'compression': 'save',
        'cookable': 'True',
        'enabled': '1',
        'expression': '',
        'id': 'myfancystyle.css',
        'media': 'all',
        'rel': 'stylesheet',
        'rendering': 'import',
    }]


@handler('gsprofilejsregistry', 'uml2fs', 'hierarchygenerator',
         'gsprofile', order=110)
def gsprofilejsregistry(self, source, target):
    """Create jsregistry.xml
    """
    package = target.anchor
    default = package['profiles']['default']
    
    # read or create jsregistry.xml
    if 'jsregistry.xml' in default:
        jsregistry = default['jsregistry.xml']
    else:
        jsregistry = default['jsregistry.xml'] = DTMLTemplate()
    
    # set template used for jsregistry.xml
    jsregistry.template = 'agx.generator.plone:templates/jsregistry.xml'
    
    # set template params
    # XXX: calculate from model
    jsregistry.params['scripts'] = [{
        'cacheable': 'True',
        'compression': 'safe',
        'cookable': 'True',
        'enabled': 'True',
        'expression': '',
        'id': 'myfancyscript.js',
        'inline': 'False',
    }]