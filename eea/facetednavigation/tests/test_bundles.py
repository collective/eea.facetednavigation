""" Bundles
"""
from eea.facetednavigation.tests.base import FUNCTIONAL_TESTING
from eea.facetednavigation.upgrades.evolve165 import disable_async_bundles
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from zope.component import getUtility

import re
import unittest


BUNDLES = ("faceted.jquery", "faceted.view", "faceted.edit")


class TestBundles(unittest.TestCase):
    """Faceted bundles"""

    layer = FUNCTIONAL_TESTING

    def test_bundles_run_in_order(self):
        """faceted-view.min.js needs jQuery.bbq from faceted-jquery.min.js:
        async scripts run in any order, deferred ones in document order.
        """
        browser = Browser(self.layer["app"])
        browser.open(self.layer["portal"].absolute_url())
        tags = re.findall(
            r'<script[^>]* data-bundle="faceted\.[^>]*>', browser.contents
        )
        self.assertEqual(len(tags), len(BUNDLES))
        for tag in tags:
            self.assertNotIn("async", tag)
            self.assertIn("defer", tag)

    def test_upgrade_disable_async_bundles(self):
        """Existing sites get the deferred bundles too"""
        registry = getUtility(IRegistry)
        for name in BUNDLES:
            registry["plone.bundles/%s.load_async" % name] = True
        disable_async_bundles(self.layer["portal"])
        for name in BUNDLES:
            self.assertFalse(registry["plone.bundles/%s.load_async" % name])
