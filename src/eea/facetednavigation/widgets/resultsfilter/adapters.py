"""Adapters"""

from eea.facetednavigation.interfaces import IWidgetFilterBrains
from zope.interface import implementer


@implementer(IWidgetFilterBrains)
class WidgetFilterBrains:
    """Filter brains after query"""

    def __init__(self, context):
        self.widget = context

    def __call__(self, brains, form):
        """Filter brains"""
        for brain in brains:
            if self.widget.talexpr(brain):
                yield brain
