from node.ext.directory import Directory
from agx.core import handler
from agx.generator.gs.scope import (
    ProfileScope,
    ContentTypeScope,
    DynamicViewScope,
)


@handler('gsprofiledirectories', 'uml2fs', 'hierarchygenerator',
         'gsprofile', order=100)
def eggdocuments(self, source, target):
    """Create GS profile directories.
    """
    package = target.anchor
    if not 'profiles' in package:
        profiles = package['profiles'] = Directory()
        profiles['default'] = Directory()
        profiles['uninstall'] = Directory()