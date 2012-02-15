import re
import os
from node.ext.directory import Directory
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
from node.ext import python
from node.ext.python.utils import Imports
from node.ext.uml.utils import (
    TaggedValues,
    UNSET,
)
from agx.generator.pyegg.utils import (
    templatepath,
    set_copyright,
)
from agx.generator.zca.utils import addZcmlRef


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
    templates.factories['.pt'] = XMLTemplate

    #create the browser:page entries
    for bp in tok.browserpages or [None]:
        viewname = tgv.direct('name', 'plone:view', 'view')
        name = tgv.direct('name', 'plone:view', view.xminame.lower())
        
        template_name = tgv.direct('template_name', 'plone:view', name + '.pt')
        permission = tgv.direct('permission', 'plone:view', None)
        layer = tgv.direct('layer', 'plone:view', None)

        if bp:
            bptgv = TaggedValues(bp)
            bptok = token(str(bp.supplier.uuid), False)
            _for = bptok.fullpath
            
            #consider uuid as an unset name
            if re.match('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}', bp.xminame):
                bpname = None
            else:
                bpname = bp.xminame.lower()
                
            if bp.xminame: viewname=bp.xminame
            viewname = bptgv.direct('name', 'plone:view', viewname)
            name = bptgv.direct('name', 'plone:view', bpname or name)
            
            #override template name
            template_name = bptgv.direct('template_name', 'plone:view', name + '.pt')
            permission = bptgv.direct('permission', 'plone:view', permission)
            layer = bptgv.direct('layer', 'plone:view', layer)
        else:
            _for = '*'
            
        found_browserpages = zcml.filter(tag='browser:page', attr='name', value=viewname)
        browser = None
        templatepath = 'templates/' + template_name
        
        if found_browserpages:
            for br in found_browserpages:
                if br.attrs.get('class') == classpath:
                    browser = br

        if not browser:     
            browser = SimpleDirective(name='browser:page', parent=zcml)
            
        browser.attrs['for'] = _for
        if not name is UNSET:
            browser.attrs['name'] = viewname
        browser.attrs['class'] = classpath
        browser.attrs['template'] = templatepath
        if permission:
            browser.attrs['permission'] = permission
            
        if layer:
            browser.attrs['layer'] = layer

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