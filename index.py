from documents import TransformedDocument


def count_terms(list_terms):
    result = dict()
    for item in list_terms:
        if item in result:
            result[item] += 1
        else:
            result[item] = 1
    return result


def combine_term_scores(list_terms, dict_terms):
    result = 0
    for item in list_terms:
        if item in dict_terms:
            result += dict_terms[item]
    return result


class Index:
    def __init__(self):
        self.id_to_terms_counts = dict()

    def add_document(self, doc: TransformedDocument):
        self.id_to_terms_counts[doc.doc_id] = count_terms(doc.terms)

    def search(self, processed_query: list[str]) -> list[str]:
        # query_terms_set = set(processed_query)

        results = dict()

        for doc_id, doc_term_dict in self.id_to_terms_counts.items():
            score = combine_term_scores(processed_query, doc_term_dict)
            results[doc_id] = score
        # TODO: Make results into a class.
        return sorted(results, key=results.get, reverse=True)



