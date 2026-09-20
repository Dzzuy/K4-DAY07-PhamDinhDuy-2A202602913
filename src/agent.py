from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong knowledge base."

        context_parts = []
        for index, result in enumerate(results, start=1):
            metadata = result["metadata"]
            source = next(
                (
                    metadata[key]
                    for key in ("source_url", "source", "title", "doc_id")
                    if metadata.get(key)
                ),
                result["id"],
            )
            context_parts.append(f"[{index}]\nSource: {source}\nContent: {result['content']}")

        prompt = (
            "Trả lời câu hỏi chỉ dựa trên context bên dưới. Không bịa thông tin. "
            "Nếu context chưa đủ, hãy nói không tìm thấy đủ thông tin. "
            "Khi phù hợp, hãy tham chiếu số nguồn như [1].\n\n"
            f"Context:\n{'\n\n'.join(context_parts)}\n\n"
            f"Question: {question}\nAnswer:"
        )
        return self.llm_fn(prompt)
