from __future__ import annotations

import re
from pathlib import Path

from src import Document, EmbeddingStore, FixedSizeChunker, LocalEmbedder, RecursiveChunker, SentenceChunker

# ============================================================
# TEAM: ONLY CHANGE THIS ONE LINE
# FixedSizeChunker | SentenceChunker | RecursiveChunker | HeadingAwarePolicyChunker
# ============================================================

# STRATEGY = "FixedSizeChunker"
STRATEGY = "SentenceChunker"
# STRATEGY = "RecursiveChunker"
# STRATEGY = "HeadingAwarePolicyChunker"


CORPUS_DIR = Path("data/shopee-warranty")
TOP_K = 3

# Q1 merges the buyer/seller variants into one logical seller-filter query.
# Full answers are ground truth; markers only audit retrieved content.
GOLDEN_SET = [
    {"id": "Q1", "type": "metadata_filter", "query": "Quyền và trách nhiệm của tôi đối với việc bảo hành sản phẩm trên sàn là gì?", "metadata_filter": {"audience": "seller"}, "gold_answer": "Người Bán có trách nhiệm tiếp nhận bảo hành sản phẩm, dịch vụ cho Người Mua như cam kết trong Chính sách bảo hành sản phẩm của Người bán và/hoặc của nhà sản xuất và thông tin về Chính sách bảo hành này phải được được đăng tải trên Sàn Shopee trong phần mô tả về sản phẩm, dịch vụ.", "source_file": "seller-warranty-policy.md", "answer_markers": ["trách nhiệm tiếp nhận bảo hành", "Chính sách bảo hành", "phần mô tả"]},
    {"id": "Q2", "type": "data_lookup", "query": "Đối với đơn hàng do Người bán tự vận chuyển, tôi có tối đa bao nhiêu ngày để gửi yêu cầu trả hàng kể từ lúc trạng thái cập nhật 'Lấy hàng thành công' mà tôi chưa bấm nhận hàng?", "metadata_filter": None, "gold_answer": "20 ngày kể từ lúc đơn hàng được cập nhật trạng thái “Lấy hàng thành công” và bạn không bấm “Đã nhận được hàng”.", "source_file": "return-refund-policy.md", "answer_markers": ["20 ngày", "Lấy hàng thành công"]},
    {"id": "Q3", "type": "condition", "query": "Sản phẩm của tôi cần đáp ứng các điều kiện cơ bản nào để được bảo hành?", "metadata_filter": None, "gold_answer": "Còn thời hạn bảo hành (dựa trên tem/phiếu bảo hành/hoặc thời điểm kích hoạt bảo hành điện tử); còn tem/phiếu bảo hành; sản phẩm bị lỗi kỹ thuật không phải do lỗi của Người Mua.", "source_file": "buyer-warranty-policy.md", "answer_markers": ["Còn thời hạn bảo hành", "Còn tem/phiếu bảo hành", "lỗi kỹ thuật"]},
    {"id": "Q4", "type": "process", "query": "Đối với khiếu nại không phải là Trả Hàng/Hoàn Tiền, Shopee xử lý vụ việc trong thời hạn bao lâu kể từ khi nhận đủ thông tin từ các bên?", "metadata_filter": None, "gold_answer": "Shopee yêu cầu các bên tranh chấp cung cấp đầy đủ thông tin/tài liệu liên quan đến vụ việc, và đưa ra hướng giải quyết trong vòng 07 ngày làm việc kể từ ngày nhận được đầy đủ các thông tin/tài liệu có liên quan; vụ việc phức tạp có thể kéo dài hơn.", "source_file": "dispute-process.md", "answer_markers": ["07 ngày làm việc", "đầy đủ các thông tin/tài liệu"]},
    {"id": "Q5", "type": "listing", "query": "Hãy liệt kê tất cả các lý do mà tôi có thể dùng để gửi yêu cầu Trả hàng/Hoàn tiền trên Shopee.", "metadata_filter": None, "gold_answer": "Chưa nhận được hàng; thiếu hàng; Người bán gửi sai hàng; hàng lỗi, không hoạt động; khác với mô tả; hàng đã qua sử dụng; hàng giả/nhái; đổi ý (sản phẩm còn nguyên tem, nhãn mác, bao bì).", "source_file": "return-refund-policy.md", "answer_markers": ["Chưa nhận được hàng", "Thiếu hàng", "Người bán gửi sai hàng", "Hàng lỗi, không hoạt động", "Khác với mô tả", "Hàng đã qua sử dụng", "Hàng giả/nhái", "Đổi ý"]},
]


def build_chunker(strategy: str):
    if strategy == "FixedSizeChunker":
        return FixedSizeChunker(chunk_size=500, overlap=50)
    if strategy == "SentenceChunker":
        return SentenceChunker(max_sentences_per_chunk=3)
    if strategy == "RecursiveChunker":
        return RecursiveChunker(chunk_size=500)
    if strategy == "HeadingAwarePolicyChunker":
        from src.chunking import HeadingAwarePolicyChunker
        return HeadingAwarePolicyChunker()
    raise ValueError(f"Unknown strategy: {strategy}")


def strategy_details(strategy: str) -> tuple[str, str]:
    return {
        "FixedSizeChunker": ("FixedSizeChunker", "FixedSizeChunker(chunk_size=500, overlap=50)"),
        "SentenceChunker": ("SentenceChunker", "SentenceChunker(max_sentences_per_chunk=3)"),
        "RecursiveChunker": ("RecursiveChunker", "RecursiveChunker(chunk_size=500)"),
        "HeadingAwarePolicyChunker": ("HeadingAwarePolicyChunker", "HeadingAwarePolicyChunker()"),
    }[strategy]


def parse_document(path: Path) -> tuple[dict[str, str], str]:
    parts = path.read_text(encoding="utf-8").split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"Missing frontmatter in {path}")
    return dict(re.findall(r"^(\w+):\s*(.+)$", parts[1], re.MULTILINE)), parts[2].strip()


def load_documents(chunker) -> tuple[list[Document], int]:
    documents = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        metadata, body = parse_document(path)
        for index, chunk in enumerate(chunker.chunk(body)):
            documents.append(Document(id=f"{path.stem}#{index}", content=chunk, metadata={**metadata, "doc_id": path.stem, "chunk_index": index}))
    return documents, len({document.metadata["doc_id"] for document in documents})


def evaluate_retrieval(
    results: list[dict], markers: list[str], source_file: str
) -> tuple[int, int | None, int, int]:
    """Score evidence across top-3 chunks from the frozen gold source."""
    expected_markers = [marker.casefold() for marker in markers]
    expected_doc_id = Path(source_file).stem
    first_evidence_rank = None
    source_contents = []

    for rank, result in enumerate(results, start=1):
        if result["metadata"].get("doc_id") != expected_doc_id:
            continue
        content = result["content"].casefold()
        source_contents.append(content)
        if first_evidence_rank is None and any(marker in content for marker in expected_markers):
            first_evidence_rank = rank

    combined = "\n".join(source_contents)
    matched = sum(marker in combined for marker in expected_markers)
    total = len(expected_markers)
    if matched == total:
        score = 2 if first_evidence_rank == 1 else 1
    elif first_evidence_rank is not None:
        score = 1
    else:
        score = 0
    return score, first_evidence_rank, matched, total


def print_results(results: list[dict]) -> None:
    for rank, result in enumerate(results, start=1):
        snippet = result["content"][:500].rstrip()
        print(f"\nTop {rank}\nscore: {result['score']:.4f}\ndoc_id: {result['metadata']['doc_id']}\naudience: {result['metadata'].get('audience')}\ncontent: {snippet}")


def print_query(spec: dict, results: list[dict], title: str | None = None, metadata_filter: dict | None = None) -> tuple[int, int | None]:
    print("\n" + "=" * 60)
    print(title or spec["id"])
    print(f"Query: {spec['query']}\nFilter: {metadata_filter}\nGold answer: {spec['gold_answer']}\nGold source: {spec['source_file']}")
    print_results(results)
    score, rank, matched, total = evaluate_retrieval(
        results, spec["answer_markers"], spec["source_file"]
    )
    print(f"Relevant evidence found: {f'Yes, first marker rank {rank}' if rank else 'No'}")
    print(f"Gold-marker coverage: {matched}/{total} across gold-source chunks in top-{TOP_K}")
    print("Agent answer: not evaluated in this shared retrieval benchmark.")
    print(f"Retrieval score: {score}/2")
    return score, rank


def ab_observation(unfiltered_rank: int | None, filtered_rank: int | None) -> str:
    if filtered_rank and (not unfiltered_rank or filtered_rank < unfiltered_rank):
        return "improved"
    return "unchanged" if filtered_rank == unfiltered_rank else "worse"


def main() -> None:
    strategy_name, chunker_name = strategy_details(STRATEGY)
    documents, document_count = load_documents(build_chunker(STRATEGY))
    embedder = LocalEmbedder()
    store = EmbeddingStore(collection_name="lab7_shared_benchmark", embedding_fn=embedder)
    store.add_documents(documents)
    average_length = sum(len(document.content) for document in documents) / len(documents)

    print("=" * 60 + "\nLAB 7 BENCHMARK\n" + "=" * 60)
    print(f"Strategy: {strategy_name}\nChunker: {chunker_name}\nEmbedder: {embedder._backend_name}\nCorpus: {CORPUS_DIR}\nDocuments: {document_count}\nChunks: {len(documents)}\nTop-K: {TOP_K}\nBenchmark queries: {len(GOLDEN_SET)}\n" + "=" * 60)

    q1 = GOLDEN_SET[0]
    unfiltered = store.search(q1["query"], top_k=TOP_K)
    filtered = store.search_with_filter(q1["query"], top_k=TOP_K, metadata_filter=q1["metadata_filter"])
    _, unfiltered_rank = print_query(q1, unfiltered, "Q1 — UNFILTERED", None)
    q1_score, filtered_rank = print_query(q1, filtered, "Q1 — FILTERED audience=seller", q1["metadata_filter"])
    observation = ab_observation(unfiltered_rank, filtered_rank)
    print(f"Q1 metadata filter: {observation} (unfiltered rank={unfiltered_rank}, filtered rank={filtered_rank})")

    scores = [(q1["id"], q1_score)]
    for spec in GOLDEN_SET[1:]:
        score, _ = print_query(spec, store.search_with_filter(spec["query"], top_k=TOP_K, metadata_filter=spec["metadata_filter"]), metadata_filter=spec["metadata_filter"])
        scores.append((spec["id"], score))

    total = sum(score for _, score in scores)
    weakest_id, weakest_score = min(scores, key=lambda item: item[1])
    weakest = next(spec for spec in GOLDEN_SET if spec["id"] == weakest_id)
    print("\n" + "=" * 60 + "\nSUMMARY")
    print(f"Strategy: {strategy_name}\nChunker parameters: {chunker_name}\nEmbedding model: {embedder._backend_name}\nDocuments: {document_count}\nChunks: {len(documents)}\nAverage chunk length: {average_length:.2f}")
    for query_id, score in scores:
        print(f"{query_id} score: {score}/2")
    print(f"Total retrieval score: {total}/10\nMetadata A/B:\nunfiltered: first evidence rank {unfiltered_rank}\nfiltered: first evidence rank {filtered_rank}\nobservation: {observation}")
    print(f"Failure case:\nquery: {weakest_id} — {weakest['query']}\nwhat went wrong: content audit score was {weakest_score}/2.\nlikely reason: top-3 did not contain every frozen answer marker across gold-source chunks.\npossible improvement: inspect heading/context boundaries in a separate experiment; do not tune this frozen benchmark.")


if __name__ == "__main__":
    main()
