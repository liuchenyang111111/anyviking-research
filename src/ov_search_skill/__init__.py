"""Helpers for searching a local corpus through OpenViking."""

from ov_search_skill.retrievers.base import Retriever, SearchResult
from ov_search_skill.retrievers.openviking import OpenVikingRetriever

__all__ = ["OpenVikingRetriever", "Retriever", "SearchResult"]
