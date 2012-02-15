from agx.core import (
    Scope,
    registerScope,
)
from node.ext.uml.interfaces import (
    IDependency,
    IClass,
)


class ProfileScope(Scope):

    def __call__(self, node):
        return node.stereotype('plone:gsprofile') is not None


class ContentTypeScope(Scope):

    def __call__(self, node):
        return node.stereotype('plone:content_type') is not None


class ViewClassScope(Scope):
    '''it covers view and dynamic_view'''
    def __call__(self, node):
        if not IClass.providedBy(node): return False
        return node.stereotype('plone:view') or \
            node.stereotype('plone:dynamic_view') is not None


class DynamicViewScope(Scope):

    def __call__(self, node):
        return node.stereotype('plone:dynamic_view') is not None

class BrowserPageScope(Scope):

    def __call__(self, node):
        if not IDependency.providedBy(node): return False
        return node.stereotype('plone:view')  is not None


registerScope('gsprofile', 'uml2fs', None, ProfileScope)
registerScope('contenttype', 'uml2fs', None, ContentTypeScope)
registerScope('viewclass', 'uml2fs', None, ViewClassScope)
registerScope('dynamicview', 'uml2fs', None, DynamicViewScope)
registerScope('dependency', 'uml2fs', [IDependency], Scope)

registerScope('browserpage', 'uml2fs', None, BrowserPageScope)
