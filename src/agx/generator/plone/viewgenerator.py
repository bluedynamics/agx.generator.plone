import re
import os

from zope.interface.interfaces import ComponentLookupError
from node.ext.directory import Directory
from node.ext.template import (
    XMLTemplate,
    DTMLTemplate,
)
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
from node.ext import python
from node.ext.python.utils import Imports
from node.ext.uml.utils import (
    TaggedValues,
    UNSET,
)
from agx.generator.pyegg.utils import (
    templatepath,
    set_copyright,
    implicit_dotted_path,
    egg_source,
)
from agx.generator.zca.utils import addZcmlRef
from node.ext.python import Attribute
from agx.generator.pyegg.utils import class_full_name


@handler('plonebrowserview', 'uml2fs', 'plonegenerator', 'viewclass', order=150)
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
    path.append('browser.zcml')
    fullpath = os.path.join(*path)
    if 'browser.zcml' not in targetdir:
        zcml = ZCMLFile(fullpath)
        zcml.nsmap['browser'] = 'http://namespaces.zope.org/browser'
        targetdir['browser.zcml'] = zcml
    else:
        zcml = targetdir['browser.zcml']
    addZcmlRef(targetdir, zcml)

    targettok = token(
        str(targetclass.uuid), True, browserpages=[], provides=None)
    
    
    _for = [token(str(context.supplier.uuid), False).fullpath \
            for context in tok.browserpages] or ['*']
            
    classpath = class_full_name(targetclass)
    tgv = TaggedValues(view)
    
    # create the templates dir
    if 'templates' not in targetdir.keys():
        targetdir['templates'] = Directory('templates')
        
    templates = targetdir['templates']
    templates.factories['.pt'] = XMLTemplate

    #create the browser:page entries
    for bp in tok.browserpages or [None]:
        #name of view: if it should have a constant name, change the last param
        viewname = tgv.direct('name', 'plone:view', None) or \
            tgv.direct('name', 'plone:dynamic_view', view.xminame.lower()) 
        name_raw = tgv.direct('name', 'plone:view', None) or \
            tgv.direct('name', 'plone:vdynamic_view', None)
            
        name=name_raw or view.xminame.lower()
        
        template_name_raw = tgv.direct('template_name', 'plone:view', None) or \
            tgv.direct('template_name', 'plone:dynamic_view', None)
            
        template_name=template_name_raw or name + '.pt'
        permission = tgv.direct('permission', 'plone:view', None) or \
            tgv.direct('permission', 'plone:dynamic_view', None)
        layer = tgv.direct('layer', 'plone:view', None) or \
            tgv.direct('layer', 'plone:dynamic_view', None)
            
        if bp:
            bptgv = TaggedValues(bp)
            bptok = token(str(bp.supplier.uuid), False)
            _for = bptok.fullpath
            
            #consider uuid as an unset name
            if re.match('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}', bp.xminame):
                bpname = None
            else:
                bpname = bp.xminame.lower()
                
            if bp.xminame: viewname = bp.xminame
            viewname = bptgv.direct('name', 'plone:view', None) or \
                bptgv.direct('name', 'plone:dynamic_view', viewname)
                
            name = bptgv.direct('name', 'plone:view', None) or \
                bptgv.direct('name', 'plone:dynamic_view', bpname or name)
            
            #override template name
            template_name = bptgv.direct(
                'template_name', 'plone:view', None) or \
                bptgv.direct(
                    'template_name', 'plone:dynamic_view', None) or \
                template_name_raw or name + '.pt'
                
            permission = bptgv.direct('permission', 'plone:view', None) or \
                bptgv.direct('permission', 'plone:dynamic_view', permission)
            layer = bptgv.direct('layer', 'plone:view', None) or \
                bptgv.direct('layer', 'plone:dynamic_view', layer)
        else:
            _for = '*'
        
        found_browserpages = zcml.filter(
            tag='browser:page', attr='name', value=viewname)
        
        browser = None
        templatepath = 'templates/' + template_name
        
        if found_browserpages:
            for br in found_browserpages:
                if br.attrs.get('class') == classpath:
                    browser = br

        if not browser:     
            browser = SimpleDirective(name='browser:page', parent=zcml)
            
        browser.attrs['for'] = _for
        if viewname and not viewname is UNSET:
            browser.attrs['name'] = viewname
        browser.attrs['class'] = classpath
        browser.attrs['template'] = templatepath
        browser.attrs['permission'] = permission or 'zope2.View'
            
        if layer:
            browser.attrs['layer'] = layer

        #spit out the page vanilla template 
        if template_name not in templates.keys():
            pt = XMLTemplate()
            templates[template_name] = pt
    
            # set template for viewtemplate
            pt.template = 'agx.generator.plone:templates/viewtemplate.pt'


@handler('zcviewdepcollect', 'uml2fs', 'connectorgenerator',
         'dependency', order=140)
def zcviewdepcollect(self, source, target):
    """Collect all view dependencies
    """
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
        try:
            dont_generate=token(str(targetcontext.uuid), False,dont_generate=False).dont_generate
            if dont_generate:
                iface=targetcontext.parent.classes('I'+targetcontext.classname)[0]
                contexttok.fullpath = class_full_name(iface)
            else:
                contexttok.fullpath = class_full_name(targetcontext)
        except ComponentLookupError: #dont_generate doesnt seem to be defined here
            pass
    else: #its a stub
        contexttok.fullpath = '.'.join(
            [TaggedValues(context).direct('import', 'pyegg:stub'), context.name])
    if isinstance(target, python.Module):
        targetdir = target.parent
    else:
        targetdir = target

    tok.browserpages.append(dep)


@handler('zcviewfinalize', 'uml2fs', 'plonegenerator',
         'viewclass', order=145)
def zcviewfinalize(self, source, target):
    """Create zope interface.
    """
    if source.stereotype('pyegg:stub') is not None:
        return
    
    view = source
    targetview = read_target_node(view, target.target)
    name = source.name
    module = targetview.parent
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


###############################
# move below to separate module

@handler('plone__init__', 'uml2fs', 'hierarchygenerator', 'gsprofile', order=30)
def plone__init__(self, source, target):
    egg = egg_source(source)
    eggname = egg.name
    targetdir = read_target_node(source, target.target)
    module = targetdir['__init__.py']

    imp = Imports(module)
    imp.set('zope.i18nmessageid', [['MessageFactory', None]])

    value = 'MessageFactory("%s")' % eggname
    atts = [att for att in module.attributes() if '_' in att.targets]

    if atts:
        atts[0].value = value
    else:
        module['_'] = Attribute('_', value)


@handler('resourcedirectory', 'uml2fs', 'zcasemanticsgenerator',
         'gsprofile', order=50)
def resourcedirectory(self, source, target):
    """Create resource directory and register in ZCML.
    """
    egg = egg_source(source)
    eggname = egg.name
    targetdir = read_target_node(source, target.target)
    
    if 'resources' not in targetdir.keys():
        targetdir['resources'] = Directory()
    
    path = targetdir.path
    path.append('browser.zcml')
    fullpath = os.path.join(*path)
    if 'browser.zcml' not in targetdir:
        zcml = ZCMLFile(fullpath)
        zcml.nsmap['browser'] = 'http://namespaces.zope.org/browser'
        targetdir['browser.zcml'] = zcml
    else:
        zcml = targetdir['browser.zcml']
    addZcmlRef(targetdir, zcml)
    
    if not zcml.filter(
            tag='browser:resourceDirectory', attr='name', value=eggname):
        directory = SimpleDirective(
            name='browser:resourceDirectory', parent=zcml)
        directory.attrs['name'] = eggname
        directory.attrs['directory'] = 'resources'


@handler('resourceregistries', 'uml2fs', 'zcasemanticsgenerator',
         'gsprofile', order=60)
def resourceregistries(self, source, target):
    """Create main.css and main.js file in resources directory.
    
    Runs after browser.zcml has been created.
    """
    egg = egg_source(source)
    eggname = egg.name
    targetdir = read_target_node(source, target.target)
    resources = targetdir['resources']
    resources.factories['main.css'] = DTMLTemplate
    resources.factories['main.js'] = DTMLTemplate
    
    if not 'main.css' in resources:
        css = resources['main.css'] = DTMLTemplate()
    else:
        css = resources['main.css']
    
    css.template = 'agx.generator.plone:templates/main.css.dtml'
    css.params['project'] = eggname
    
    css.SECTION_BEGIN = '/* code-section'
    css.SECTION_END = '/* /code-section'
    css.SECTION_POSTFIX = ' */'
    
    if not 'main.js' in resources:
        js = resources['main.js'] = DTMLTemplate()
    else:
        js = resources['main.js']
    
    js.template = 'agx.generator.plone:templates/main.js.dtml'
    js.params['project'] = eggname
    
    js.SECTION_BEGIN = '// code-section'
    js.SECTION_END = '// /code-section'
    js.SECTION_POSTFIX = ''
