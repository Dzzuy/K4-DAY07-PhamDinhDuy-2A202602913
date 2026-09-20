from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from src import (
    EMBEDDING_PROVIDER_ENV,
    GEMINI_EMBEDDING_MODEL,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    Document,
    EmbeddingStore,
    GeminiEmbedder,
    LocalEmbedder,
    OpenAIEmbedder,
    SentenceChunker,
    _mock_embed,
)


CORPUS_DIR = Path("data/shopee-warranty")
QUERIES = [
    {
        "id": "Q1",
        "query": (
            "Đối với đơn hàng do Người bán tự vận chuyển, nếu Người mua không bấm “Đã nhận được hàng”, "
            "thời hạn tối đa để gửi yêu cầu Trả hàng/Hoàn tiền là bao lâu kể từ lúc đơn hàng được cập nhật "
            "“Lấy hàng thành công”?"
        ),
        "gold_doc": "return-refund-policy",
        "metadata_filter": None,
    },
    {
        "id": "Q2",
        "query": "Ba điều kiện bảo hành cơ bản mà Shopee khuyến cáo Người Mua cần đáp ứng là gì?",
        "gold_doc": "buyer-warranty-policy",
        "metadata_filter": None,
    },
    {
        "id": "Q3",
        "query": "Khi đăng bán sản phẩm trên Shopee, Người Bán phải điền những thông tin nào liên quan đến nguồn gốc và bảo hành?",
        "gold_doc": "seller-listing-policy",
        "metadata_filter": None,
    },
    {
        "id": "Q4",
        "query": "Với tranh chấp không phải khiếu nại Trả hàng/Hoàn tiền, Shopee đưa ra hướng giải quyết trong bao lâu sau khi nhận đủ thông tin/tài liệu?",
        "gold_doc": "dispute-process",
        "metadata_filter": None,
    },
    {
        "id": "Q5",
        "query": "Khi phát sinh nhu cầu bảo hành sản phẩm trên Shopee thì cần làm gì?",
        "gold_doc": "seller-warranty-policy",
        "metadata_filter": {"audience": "seller"},
    },
]


def parse_document(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"Missing frontmatter in {path}")

    metadata = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata, parts[2].strip()


def select_embedder():
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    try:
        if provider == "local":
            return LocalEmbedder(os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        if provider == "openai":
            return OpenAIEmbedder(os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
        if provider == "gemini":
            return GeminiEmbedder(os.getenv("GEMINI_EMBEDDING_MODEL", GEMINI_EMBEDDING_MODEL))
    except Exception as error:
        print(f"WARNING: {provider} embedder unavailable ({error.__class__.__name__}); using mock.")
    return _mock_embed


def load_chunks(chunker: SentenceChunker) -> tuple[list[Document], int]:
    documents = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        frontmatter, body = parse_document(path)
        for index, chunk in enumerate(chunker.chunk(body)):
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata={
                        **frontmatter,
                        "doc_id": path.stem,
                        "chunk_index": index,
                        "source": str(path),
                    },
                )
            )
    return documents, len({document.metadata["doc_id"] for document in documents})


def print_results(store: EmbeddingStore) -> None:
    for spec in QUERIES:
        print("\n" + "=" * 50)
        print(spec["id"])
        print(f"Query: {spec['query']}")
        print(f"Gold doc: {spec['gold_doc']}")
        print(f"Filter: {spec['metadata_filter']}")
        print("\nTOP-3")

        for rank, result in enumerate(
            store.search_with_filter(
                spec["query"], top_k=3, metadata_filter=spec["metadata_filter"]
            ),
            start=1,
        ):
            content = result["content"][:800]
            print(f"\n{rank}.")
            print(f"chunk_id: {result['id']}")
            print(f"doc_id: {result['metadata']['doc_id']}")
            print(f"audience: {result['metadata'].get('audience')}")
            print(f"score: {result['score']:.4f}")
            print(f"content:\n{content}")


def main() -> None:
    load_dotenv(override=False)
    chunker = SentenceChunker(max_sentences_per_chunk=3)
    chunks, corpus_docs = load_chunks(chunker)
    embedder = select_embedder()
    store = EmbeddingStore(collection_name="shopee_cp5", embedding_fn=embedder)
    store.add_documents(chunks)

    print("=== LAB 07 CP5 BENCHMARK ===")
    print("Strategy: SentenceChunker")
    print("max_sentences_per_chunk: 3")
    print(f"Corpus documents: {corpus_docs}")
    print(f"Chunks loaded: {store.get_collection_size()}")
    print(f"Embedding backend: {getattr(embedder, '_backend_name', embedder.__class__.__name__)}")
    if embedder is _mock_embed:
        print("WARNING: MockEmbedder does not encode semantic meaning.")
        print("Retrieval scores should not be interpreted as semantic quality.")

    print_results(store)


if __name__ == "__main__":
    main()
