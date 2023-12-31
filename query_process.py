import json
from collections import defaultdict
from typing import Dict, Any

from documents import DocumentStore, DictDocumentStore, Document
from index import BaseIndex
from tokenizer import tokenize


def preprocess_query(query_str: str) -> list[str]:
    return tokenize(query_str)


class FullDocumentsOutputFormatter:
    def format_out(self, results: list[str], document_store: DocumentStore):
        output_string = ''
        for doc_id in results:
            doc = document_store.get_by_doc_id(doc_id)
            output_string += f'({doc.doc_id}) {doc.text}\n\n'
        return output_string


class DocIdsOnlyFormatter:
    def format_out(self, results: list[str], document_store: DocumentStore, unused_processed_query):
        return results


def format_out(results: list[str], document_store: DocumentStore, unused_processed_query) -> str:
    output_string = ''
    for doc_id in results:
        doc = document_store.get_by_doc_id(doc_id)
        output_string += f'({doc.doc_id}) {doc.text}\n\n'
    return output_string


class QueryProcess:
    def __init__(self, document_store: DocumentStore, index: BaseIndex, stopwords: set[str] = None,
                 output_formatter=FullDocumentsOutputFormatter()):
        self.document_store = document_store
        self.index = index
        self.stopwords = stopwords
        self.output_formatter = output_formatter

    # returns a dictionary of the terms along with their synonyms in a dictionary
    def read(self: str):
        thesaurus = dict()
        with open(self) as fp:
            for line in fp:
                record = json.loads(line)
                thesaurus[record['term']] = record['syns']
        return thesaurus

    def expandQueries(self, query: str, thesaurus: dict) -> dict:
        # Representation for the queries called 'querySyns'
        querySyns = {}
        terms = preprocess_query(query)
        # Iterate through each term and add synonyms to querySyns

        for term in terms:
            synonyms = thesaurus.get(term, [])
            # Add the term itself to the list of synonyms for completeness
            querySyns[term] = [term] + synonyms
        return querySyns

    def search(self, query: str, thesaurus: dict, number_of_results: int) -> str:
        if self.stopwords is None:
            # we pass a list of terms from the query
            processed_query = [term for term in self.expandQueries(query, thesaurus)]
        else:
            # or we pass a list of synonyms from a query term
            processed_query = [syns for term, syns in self.expandQueries(query, thesaurus).items()
                               if term not in self.stopwords]
        results = self.index.search(processed_query, number_of_results)
        return self.output_formatter.format_out(results, self.document_store)

