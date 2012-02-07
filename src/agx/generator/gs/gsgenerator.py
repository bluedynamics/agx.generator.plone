from node.ext.directory import Directory
from node.ext.template import DTMLTemplate
from node.ext.zcml import (
    ZCMLFile,
    SimpleDirective,
)
from agx.core import handler
from agx.core.util import read_target_node
from agx.generator.pyegg.utils import eggsource
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
        profiles = package['profiles.zcml'] = ZCMLFile()
    
    # add genericsetup XML namespace
    profiles.nsmap['genericsetup'] = 'http://namespaces.zope.org/genericsetup'
    
    # if include Products.GenericSetup missing, add it
    if not profiles.filter(tag='include',
                           attr='package',
                           value='Products.GenericSetup'):
        include = SimpleDirective(name='include', parent=profiles)
        include.attrs['package'] = 'Products.GenericSetup'
        include.attrs['file'] = 'meta.zcml'
    
    # read or create genericsetup:registerProfile directive for default profile
    if not profiles.filter(tag='genericsetup:registerProfile',
                           attr='name',
                           value='default'):
        profile = SimpleDirective(name='include', parent=profiles)
        profile.attrs['name'] = 'default'
    else:
        profile = profiles.filter(tag='genericsetup:registerProfile',
                                  attr='name',
                                  value='default')[0]
    
    # set default profile directive attributes
    # XXX: compute from model
    profile.attrs['title'] = 'Package title'
    profile.attrs['description'] = 'Extension profile for product_name'
    
    profile.attrs['directory'] = 'profiles/default'
    profile.attrs['provides'] = 'Products.GenericSetup.interfaces.EXTENSION'


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
    metadata.template = 'agx.generator.gs:templates/metadata.xml'
    
    # set template params
    # XXX: calculate from model
    metadata.params['version'] = 1.0
    metadata.params['description'] = 'Package description'
    metadata.params['dependencies'] = [
        'profile-foo.bar:default',
    ]


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
    cssregistry.template = 'agx.generator.gs:templates/cssregistry.xml'
    
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
    jsregistry.template = 'agx.generator.gs:templates/jsregistry.xml'
    
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


@handler('gsprofiletypes', 'uml2fs', 'hierarchygenerator',
         'gscontenttype', order=110)
def gsprofiletypes(self, source, target):
    """Create or extend types.xml and corresponding TYPENAME.xml.
    """
    package = read_target_node(eggsource(source), target.target)
    default = package['profiles']['default']
    
    # create types foder if not exists
    if not 'types' in default:
        default['types'] = Directory()
    
    # read or create types.xml
    if 'types.xml' in default:
        types = default['types.xml']
    else:
        types = default['types.xml'] = DTMLTemplate()
    
    # set template and params if not done yet
    if not types.template:
        types.template = 'agx.generator.gs:templates/types.xml'
        types.params['portalTypes'] = list()
    
    # add portal type to types.xml
    types.params['portalTypes'].append({
        'name': source.name,
        'meta_type': source.name,
    })
    
    # add TYPENAME.xml to types folder
    # read or create TYPENAME.xml
    name = '%s.xml' % source.name
    if name in default['types']:
        type = default['types'][name]
    else:
        type = default['types'][name] = DTMLTemplate()
    
    # set template used for TYPENAME.xml
    type.template = 'agx.generator.gs:templates/type.xml'
    
    # set template params
    # FTI properties can be added by prefixing param key with 'fti:'
    # XXX: calculate from model
    type.params['ctype'] = dict()
    type.params['ctype']['name'] = source.name
    type.params['ctype']['meta_type'] = source.name
    type.params['ctype']['type_name'] = source.name
    type.params['ctype']['type_description'] = source.name
    type.params['ctype']['content_icon'] = 'page_icon.gif'
    type.params['ctype']['content_meta_type'] = source.name
    type.params['ctype']['product_name'] = 'foo.bar.baz'
    type.params['ctype']['factory'] = 'blah'
    type.params['ctype']['global_allow'] = 'True'
    type.params['ctype']['filter_content_types'] = 'True'
    type.params['ctype']['allowed_content_types'] = list()
    type.params['ctype']['allow_discussion'] = 'False'
    type.params['ctype']['immediate_view'] = 'view'
    type.params['ctype']['suppl_views'] = list()
    type.params['ctype']['default_view'] = 'view'
    type.params['ctype']['type_aliases'] = list()
    type.params['ctype']['type_aliases'].append({
        'from': '(Default)',
        'to': '(dynamic view)',
    })
    type.params['ctype']['type_aliases'].append({
        'from': 'view',
        'to': '(selected layout)',
    })
    type.params['ctype']['type_aliases'].append({
        'from': 'edit',
        'to': 'base_edit',
    })
    type.params['ctype']['type_aliases'].append({
        'from': 'sharing',
        'to': '@@sharing',
    })
    type.params['ctype']['type_actions'] = list()
    type.params['ctype']['type_actions'].append({
        'id': 'edit',
        'name': 'Edit',
        'category': 'object',
        'condition': 'not:object/@@plone_lock_info/is_locked_for_current_user',
        'action': 'string:${object_url}/edit',
        'visible': 'True',
        'permissions': ['Modify portal content'],
    })
    type.params['ctype']['type_actions'].append({
        'id': 'view',
        'name': 'View',
        'category': 'object',
        'condition': 'python:1',
        'action': 'string:${object_url}/view',
        'visible': 'True',
        'permissions': ['View'],
    })


@handler('gsdynamicview', 'uml2fs', 'semanticsgenerator',
         'gsdependency', order=100)
def gsdynamicview(self, source, target):
    """Add view method to FTI's of all dependent content types.
    """
    if not source.supplier.stereotype('gs:content_type') \
      or not source.client.stereotype('gs:dynamic_view'):
        return
    content_type = source.supplier
    package = read_target_node(eggsource(content_type), target.target)
    default = package['profiles']['default']
    name = '%s.xml' % content_type.name
    type_xml = default['types'][name]
    type_xml.params['ctype']['suppl_views'].append(source.client.name)