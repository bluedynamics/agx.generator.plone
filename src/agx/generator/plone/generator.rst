Test agx.generator.plone
========================

Setup configuration and emulate main routine::

    >>> from zope.configuration.xmlconfig import XMLConfig

    >>> import agx.core
    >>> XMLConfig('configure.zcml', agx.core)()

    >>> from agx.core.main import parse_options

    >>> import os
    >>> modelpath = os.path.join(datadir, 'agx.generator.plone-sample.uml')

    >>> import pkg_resources
    >>> subpath = 'profiles/pyegg.profile.uml'
    >>> eggprofilepath = \
    ...     pkg_resources.resource_filename('agx.generator.pyegg', subpath)

    >>> subpath = 'profiles/zca.profile.uml'
    >>> zcaprofilepath = \
    ...     pkg_resources.resource_filename('agx.generator.zca', subpath)

    >>> subpath = 'profiles/plone.profile.uml'
    >>> ploneprofilepath = \
    ...     pkg_resources.resource_filename('agx.generator.plone', subpath)

    >>> modelpaths = [modelpath, eggprofilepath, zcaprofilepath, ploneprofilepath]

    >>> outdir = os.path.join(datadir, 'agx.generator.plone-sample')
    >>> controller = agx.core.Controller()
    >>> target = controller(modelpaths, outdir)
    >>> target
    <Directory object '/.../agx.generator.plone/src/agx/generator/plone/testing/data/agx.generator.plone-sample' at ...>
