"""Widget"""

from eea.facetednavigation import _
from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.debug.interfaces import DefaultSchemata
from eea.facetednavigation.widgets.debug.interfaces import LayoutSchemata
from eea.facetednavigation.widgets.widget import Widget as AbstractWidget


class Widget(AbstractWidget):
    """Widget"""

    widget_type = "debug"
    widget_label = _("Debugger")

    groups = (DefaultSchemata, LayoutSchemata)
    index = ViewPageTemplateFile("widget.pt")
