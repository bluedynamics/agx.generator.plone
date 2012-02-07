from agx.core import (
    Scope,
    registerScope,
)
from node.ext.uml.interfaces import IDependency


class ProfileScope(Scope):

    def __call__(self, node):
        return node.stereotype('gs:profile') is not None


class ContentTypeScope(Scope):

    def __call__(self, node):
        return node.stereotype('gs:content_type') is not None


class DynamicViewScope(Scope):

    def __call__(self, node):
        return node.stereotype('gs:dynamic_view') is not None


registerScope('gsprofile', 'uml2fs', None, ProfileScope)
registerScope('gscontenttype', 'uml2fs', None, ContentTypeScope)
registerScope('gsdynamicview', 'uml2fs', None, DynamicViewScope)
registerScope('gsdependency', 'uml2fs', [IDependency], Scope)