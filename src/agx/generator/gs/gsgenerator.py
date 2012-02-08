from node.ext.directory import Directory
from node.ext.template import DTMLTemplate
from node.ext.zcml import (
    ZCMLFile,
    SimpleDirective,
)
from agx.core import handler
from agx.core.util import read_target_node
from agx.generator.pyegg.utils import (
    egg_source,
    class_base_name,
)
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
    
    # read or create genericsetup:registerProfile directive for default profile
    if not profiles.filter(tag='genericsetup:registerProfile',
                           attr='name',
                           value='default'):
        profile = SimpleDirective(name='genericsetup:registerProfile',
                                  parent=profiles)
        profile.attrs['name'] = 'default'
    else:
        profile = profiles.filter(tag='genericsetup:registerProfile',
                                  attr='name',
                                  value='default')[0]
    
    # set default profile directive attributes
    # XXX: compute from model
    profile.attrs['title'] = 'Install %s' % egg_source(source).name
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
    metadata.params['version'] = '1'
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


@handler('gsprofiletypes', 'uml2fs', 'connectorgenerator',
         'gscontenttype', order=100)
def gsprofiletypes(self, source, target):
    """Create or extend types.xml and corresponding TYPENAME.xml.
    """
    egg = egg_source(source)
    package = read_target_node(egg, target.target)
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
    
    class_ = read_target_node(source, target.target)
    full_name = '%s.%s' % (class_base_name(class_), class_.classname.lower())
    
    content_icon = '++resource++%s/%s_icon.png' % (egg.name, source.name)
    
    type.params['ctype'] = dict()
    
    # general
    type.params['ctype']['name'] = full_name
    type.params['ctype']['meta_type'] = 'Dexterity FTI'
    type.params['ctype']['i18n_domain'] = egg.name
    
    # basic metadata
    type.params['ctype']['title'] = source.name
    type.params['ctype']['description'] = source.name
    type.params['ctype']['content_icon'] = content_icon
    type.params['ctype']['allow_discussion'] = 'False'
    type.params['ctype']['global_allow'] = 'True'
    type.params['ctype']['filter_content_types'] = 'True'
    type.params['ctype']['allowed_content_types'] = list()
    
    # dexterity specific
    type.params['ctype']['schema'] = 'collective.soundcloud.types.alias.IAlias'
    type.params['ctype']['klass'] = 'plone.dexterity.content.Item'
    type.params['ctype']['add_permission'] = 'cmf.AddPortalContent'
    type.params['ctype']['behaviors'] = list()
    
    # View information
    type.params['ctype']['view_methods'] = ['view']
    type.params['ctype']['default_view'] = 'view'
    type.params['ctype']['default_view_fallback'] = 'False'
    
    # Method aliases
    type.params['ctype']['aliases'] = list()
    type.params['ctype']['aliases'].append({
        'from': '(Default)',
        'to': '(dynamic view)',
    })
    type.params['ctype']['aliases'].append({
        'from': 'view',
        'to': '(selected layout)',
    })
    type.params['ctype']['aliases'].append({
        'from': 'edit',
        'to': '@@edit',
    })
    type.params['ctype']['aliases'].append({
        'from': 'sharing',
        'to': '@@sharing',
    })
    
    # Actions
    type.params['ctype']['actions'] = list()
    type.params['ctype']['actions'].append({
        'action_id': 'edit',
        'title': 'Edit',
        'category': 'object',
        'condition_expr': 'not:object/@@plone_lock_info/is_locked_for_current_user',
        'url_expr': 'string:${object_url}/edit',
        'visible': 'True',
        'permissions': ['Modify portal content'],
    })
    type.params['ctype']['actions'].append({
        'action_id': 'view',
        'title': 'View',
        'category': 'object',
        'condition_expr': 'python:1',
        'url_expr': 'string:${object_url}/view',
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
    package = read_target_node(egg_source(content_type), target.target)
    default = package['profiles']['default']
    name = '%s.xml' % content_type.name
    type_xml = default['types'][name]
    type_xml.params['ctype']['view_methods'].append(source.client.name)