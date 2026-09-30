from chatbot.rag.vector_store import get_vector_store
from rich import print as rich_print


def retrieve_with_scores(query, k=5):
    vector_store = get_vector_store()

    results = vector_store.similarity_search_with_score(
        query,
        k=k
    )

    return results


# results = retrieve_with_scores("What is AI?", k=5)

# for doc, score in results:
#     rich_print({
#         "score": score,
#         "content": doc.page_content,
#         "metadata": doc.metadata,
#     })