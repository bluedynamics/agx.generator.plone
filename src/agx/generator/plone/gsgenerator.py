import re
import os

from node.ext.directory import Directory
from node.ext.template import DTMLTemplate
from node.ext.template import XMLTemplate


from node.ext.zcml import (
    ZCMLFile,
    SimpleDirective,
)
from agx.core import (
    handler,
    token,
)

from agx.core.util import (
    read_target_node,
    dotted_path,
)

from agx.generator.pyegg.utils import (
    egg_source,
    class_base_name,
)

from node.ext import python
from node.ext.python.interfaces import (
    IFunction,
    IModule,
)
from node.ext.python.utils import Imports


from node.ext.uml.utils import (
    Inheritance,
    TaggedValues,
    UNSET,
)

from agx.generator.pyegg.utils import (
    class_base_name,
    templatepath,
    set_copyright,
)

from agx.generator.zca.utils import addZcmlRef

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
    
    
#-----------------------------------------------------------------
#             browserviews
#-----------------------------------------------------------------

@handler('plonebrowserview', 'uml2fs', 'zcagenerator', 'viewclass', order=20)
def plonebrowserview(self, source, target):
    view = source
    if view.stereotype('pyegg:function'):
        # XXX: <<function>> <<adapter>> on class
        return
    tok = token(str(view.uuid), True, browserpages=[])
    pack = source.parent
    target = read_target_node(pack, target.target)
    targetclass = read_target_node(view, target)
    if isinstance(target, python.Module):
        targetdir = target.parent
    else:
        targetdir = target
    path = targetdir.path
    
    #get or create browser.zcml
    path.append('browser.zcml')
    fullpath = os.path.join(*path)
    if 'browser.zcml' not in targetdir.keys():
        zcml = ZCMLFile(fullpath)
        zcml.nsmap['browser'] = 'http://namespaces.zope.org/browser'
        targetdir['browser.zcml'] = zcml
    else:
        zcml = targetdir['browser.zcml']
    addZcmlRef(targetdir, zcml)
    targettok = token(str(targetclass.uuid), True, browserpages=[], provides=None)
    _for = [token(str(context.supplier.uuid), False).fullpath \
            for context in tok.browserpages] or ['*']
    
    classpath = dotted_path(view)
    tgv = TaggedValues(view)
    
    #create the templates dir
    if 'templates' not in targetdir.keys():
        targetdir['templates'] = Directory('templates')
        
    templates = targetdir['templates']
    
    #create the browser:page entries
    for bp in tok.browserpages or [None]:
        #XXX browserpage relation override must be implemented!
        #XXX if not name given take class name
        name = tgv.direct('name', 'plone:view', view.xminame.lower())
        template_name = tgv.direct('template_name', 'plone:template_name', view.xminame + '.pt')
        if bp:
            bptgv = TaggedValues(bp)
            bptok = token(str(context.supplier.uuid), False)
            _for = bptok.fullpath
            
            #consider uuid as an unset name
            
            if re.match('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}', bp.xminame):
                bpname = None
            else:
                bpname = bp.xminame.lower()
            name = bptgv.direct('name', 'plone:view', bpname or name)
            #override template name
            template_name = bptgv.direct('template_name', 'plone:template_name', name + '.pt')
        else:
            _for = '*'
            
        print 'browserpage:', name
        found_browserpages = zcml.filter(tag='browser:page', attr='name', value=name)
        if found_browserpages:
            browser = found_browserpages[0]
        else:     
            browser = SimpleDirective(name='browser:page', parent=zcml)
        browser.attrs['for'] = _for
        if not name is UNSET:
            browser.attrs['name'] = name
        browser.attrs['class'] = classpath
        templatepath = 'templates/' + template_name
        browser.attrs['template'] = templatepath

        #spit out the page vanilla template 
        if template_name not in templates.keys():
            pt = XMLTemplate()
            templates[template_name] = pt
    
            # set template for viewtemplate
            pt.template = 'agx.generator.plone:templates/viewtemplate.pt'

        
    


#This one colects all view dependencies
@handler('zcviewdepcollect', 'uml2fs', 'connectorgenerator',
         'dependency', order=10)
def zcviewdepcollect(self, source, target):
#    import pdb;pdb.set_trace()
    pack = source.parent
    dep = source
    context = source.supplier
    view = source.client
    target = read_target_node(pack, target.target)
    targetcontext = read_target_node(context, target)
    targetview = read_target_node(view, target)
    tok = token(str(view.uuid), True, browserpages=[])
    contexttok = token(str(context.uuid), True, fullpath=None)
    
    if targetcontext:
        contexttok.fullpath = dotted_path(context)
    else: #its a stub
        contexttok.fullpath = '.'.join(
            [TaggedValues(adaptee).direct('import', 'pyegg:stub'), context.name])
    if isinstance(target, python.Module):
        targetdir = target.parent
    else:
        targetdir = target
#    print 'adaptcollect:',adaptee.name
    tok.browserpages.append(dep)
    
@handler('zcviewfinalize', 'uml2fs', 'semanticsgenerator',
         'viewclass', order=80)
def zcviewfinalize(self, source, target):
    """Create zope interface.
    """
    if source.stereotype('pyegg:stub') is not None:
        return
    
    view = source
    targetview = read_target_node(view, target.target)
    name = source.name
    module = targetview.parent
#    import pdb;pdb.set_trace()
    imp = Imports(module)
    imp.set('Products.Five', [['BrowserView', None]])
    set_copyright(source, module)
    if module.classes(name):
        class_ = module.classes(name)[0]
    else:
        class_ = python.Class(name)
        module[name] = class_
        
    if 'BrowserView' not in targetview.bases:
        targetview.bases.append('BrowserView')
#    if not class_.bases:
#        class_.bases.append('Interface')
#    target.finalize(source, class_)

 

