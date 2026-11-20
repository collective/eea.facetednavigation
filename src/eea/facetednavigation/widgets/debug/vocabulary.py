"""Catalog specific vocabularies"""

from Products.CMFCore.utils import _getAuthenticatedUser
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class CurrentUserVocabulary:
    """Vocabulary factory for logged in user."""

    def __call__(self, *args, **kwargs):
        """See IVocabularyFactory interface"""
        user = _getAuthenticatedUser(getSite())
        user_id = user.getId()
        user_name = user.getUserName()

        return SimpleVocabulary([SimpleTerm(user_id, user_id, user_name)])
