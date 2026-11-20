"""Types vocabularies"""

from eea.facetednavigation.vocabularies.utils import lowercase_text
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class PortalTypesVocabulary:
    """Vocabulary factory for portal types."""

    def __call__(self, *args, **kwargs):
        ttool = getToolByName(getSite(), "portal_types", None)
        if ttool is None:
            return None
        items = [(ttool[t].Title(), t) for t in ttool.listContentTypes()]
        items.sort(key=lowercase_text)
        items = [SimpleTerm(i[1], i[1], i[0]) for i in items]
        return SimpleVocabulary(items)
