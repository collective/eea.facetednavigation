"""Autocomplete widget specific vocabulary"""

from zope.component import getAdapters
from zope.component.hooks import getSite
from zope.interface import Attribute
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class AutocompleteVocabulary:
    """
    Vocabulary factory listing autocomplete suggestions views
    """

    def __call__(self, *args, **kwargs):
        """
        See IVocabularyFactory interface
        """
        site = getSite()
        factories = getAdapters((site, site.REQUEST), IAutocompleteSuggest)
        terms = [
            SimpleTerm(f[0], f[0], getattr(f[1], "label", f[0])) for f in factories
        ]
        return SimpleVocabulary(terms)


class IAutocompleteSuggest(Interface):
    """
    Interface for views generating autocomplete suggestions vocabulary.
    """

    label = Attribute("Suggestions name")

    def __call__(self):
        """
        Should return a json array of value/label objects.
        eg: [{'value':'42', 'label:'Answer to some question..'}, ...]
        """
