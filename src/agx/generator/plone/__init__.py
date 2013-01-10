# -*- coding: utf-8 -*-
import scope
import gsgenerator
import viewgenerator


def register():
    """Register this generator.
    """
    import agx.generator.plone
    from agx.core.config import register_generator
    register_generator(agx.generator.plone)
