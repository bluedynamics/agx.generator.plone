from agx.core import (
    Scope,
    registerScope,
)
from node.ext.uml.interfaces import IDependency


class ProfileScope(Scope):

    def __call__(self, node):
        return node.stereotype('plone:gsprofile') is not None


class ContentTypeScope(Scope):

    def __call__(self, node):
        return node.stereotype('plone:content_type') is not None


class ViewScope(Scope):

    def __call__(self, node):
        return node.stereotype('plone:view') is not None


class DynamicViewScope(Scope):

    def __call__(self, node):
        return node.stereotype('plone:dynamic_view') is not None


registerScope('gsprofile', 'uml2fs', None, ProfileScope)
registerScope('contenttype', 'uml2fs', None, ContentTypeScope)
registerScope('view', 'uml2fs', None, DynamicViewScope)
registerScope('dynamicview', 'uml2fs', None, DynamicViewScope)
registerScope('dependency', 'uml2fs', [IDependency], Scope)