"""Helpers for searching a local corpus through OpenViking."""

from anyviking_research.retrievers.base import Retriever, SearchResult
from anyviking_research.retrievers.openviking import OpenVikingRetriever

__all__ = ["OpenVikingRetriever", "Retriever", "SearchResult"]
