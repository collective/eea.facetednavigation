""" Upgrade to 16.5
"""
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def disable_async_bundles(context):
    """Load the faceted bundles in order (defer, not async)"""
    registry = getUtility(IRegistry)
    for name in ("faceted.jquery", "faceted.view", "faceted.edit"):
        record = registry.records.get("plone.bundles/%s.load_async" % name)
        if record is not None:
            record.value = False
