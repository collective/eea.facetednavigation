"""Widget"""

from eea.facetednavigation import _
from eea.facetednavigation.vocabularies.autocomplete import IAutocompleteSuggest
from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.autocomplete.interfaces import DefaultSchemata
from eea.facetednavigation.widgets.autocomplete.interfaces import DisplaySchemata
from eea.facetednavigation.widgets.autocomplete.interfaces import ISolrConnectionManager
from eea.facetednavigation.widgets.autocomplete.interfaces import LayoutSchemata
from eea.facetednavigation.widgets.widget import Widget as AbstractWidget
from lxml import etree
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import queryUtility
from zope.interface import implementer

import json
import urllib


class Widget(AbstractWidget):
    """Widget"""

    # Widget properties
    widget_type = "autocomplete"
    widget_label = _("Text field with suggestions")

    index = ViewPageTemplateFile("widget.pt")
    groups = (DefaultSchemata, LayoutSchemata, DisplaySchemata)

    def quotestring(self, string):
        """Quote given string"""
        return '"%s"' % string

    def quote_bad_chars(self, string):
        """Quote bad chars in query string"""
        bad_chars = ["(", ")"]
        for char in bad_chars:
            string = string.replace(char, self.quotestring(char))
        return string

    def selection_id(self, value):
        """Return the id of a JSON encoded ``{"id": ..., "text": ...}``
        selection, as sent by the autocomplete widget, or None if value is
        not such a selection (plain search term, number, or a value from a
        URL saved before selections were JSON encoded).
        """
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if not isinstance(value, str):
            return None
        try:
            parsed = json.loads(value)
        except ValueError:
            return None
        if isinstance(parsed, dict) and "id" in parsed:
            return str(parsed["id"])
        return None

    def parse_json(self, value):
        """Replace JSON encoded selections with their ids.
        Other values are returned unchanged.
        """
        if isinstance(value, (tuple, list)):
            return [self.parse_json(v) for v in value]
        selection_id = self.selection_id(value)
        return value if selection_id is None else selection_id

    def normalize_string(self, value):
        """Process string values to be used in catalog query"""
        # Ensure words are string instances as ZCatalog requires strings
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        value = self.quote_bad_chars(value)
        return value

    def normalize_list(self, value):
        """Process list values to be used in catalog query"""
        return [self.normalize_string(word) for word in value]

    def normalize(self, value):
        """Process value to be used in catalog query"""
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if isinstance(value, str) and self.selection_id(value) is None:
            # Plain search terms: select2 send us values separated by a comma
            if "," in value:
                value = value.split(",")
        value = self.parse_json(value)
        if isinstance(value, (tuple, list)):
            value = self.normalize_list(value)
        elif isinstance(value, (bytes, str)):
            value = self.normalize_string(value)
        return value

    def query(self, form):
        """Get value from form and return a catalog dict query"""
        query = {}
        index = self.data.get("index", "")
        if not index:
            return query

        if self.hidden:
            value = self.default
        else:
            value = form.get(self.data.getId(), "")

        if not value:
            return query

        value = self.normalize(value)
        query[index] = {"query": value}

        # Not every index supports an operator, e.g. ZCTextIndex rejects it
        catalog = getToolByName(self.context, "portal_catalog")
        catalog_index = catalog.Indexes.get(index)
        if "operator" in getattr(catalog_index, "query_options", []):
            query[index]["operator"] = "and"
        return query

    def autocomplete_view(self):
        """Get the autocomplete view name"""
        view_name = self.data.get("autocomplete_view", "")
        return view_name


@implementer(IAutocompleteSuggest)
class SolrSuggest(BrowserView):
    """Solr Autocomplete view"""

    label = _("solr")

    def __call__(self):
        result = []
        term = self.request.get("term")
        manager = queryUtility(ISolrConnectionManager)
        if not manager or not term:
            return json.dumps(result)

        connection = manager.getConnection()
        if not connection:
            return json.dumps(result)

        # XXX this should really go into c.solr
        request = urllib.parse.urlencode({"q": term}, doseq=True)
        response = connection.doPost(
            connection.solrBase + "/suggest", request, connection.formheaders
        )
        root = etree.fromstring(response.read())
        suggestion = root.xpath("//arr[@name='suggestion']")
        if suggestion:
            suggestions = suggestion[0].findall("str")
            result = [{"id": s.text, "text": s.text} for s in suggestions]

        return json.dumps(result)
