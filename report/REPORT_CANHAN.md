# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Đình Duy
**Nhóm:** Nova
**Ngày:** 20/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.
**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector gần cùng hướng nên hai đoạn thường có ý nghĩa gần nhau. Điểm cao không chứng minh hai câu giống hệt nhau, nhưng nó là tín hiệu tốt để lấy các đoạn liên quan trước.

**Ví dụ có độ tương tự CAO:**
- Câu A: Người mua có thể đổi sản phẩm trong vòng 7 ngày.
- Câu B: Khách hàng được trả hàng trong một tuần.
- Tại sao tương đồng: Cả hai đều nói về quyền đổi/trả hàng và cùng thời hạn, chỉ dùng từ khác nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Người mua có thể đổi sản phẩm trong vòng 7 ngày.
- Câu B: Python dùng thụt lề để xác định khối lệnh.
- Tại sao khác: Một câu nói về chính sách thương mại điện tử, câu kia nói về cú pháp lập trình.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine so hướng của vector nên ít bị ảnh hưởng bởi độ lớn vector. Điều này hợp với embedding vì ta thường cần so mức gần nhau về nghĩa; khi embedding đã chuẩn hóa như `MockEmbedder`, dot product cũng tương đương cosine để xếp hạng.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23`.
> Đáp án: 23 chunks. Tôi đã kiểm tra bằng `FixedSizeChunker(chunk_size=500, overlap=50)` trên chuỗi 10,000 ký tự và nhận được 23.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`, nên số chunk tăng lên 25. Overlap lớn giữ thêm ngữ cảnh ở ranh giới chunk, nhưng step nhỏ hơn nên tốn thêm lưu trữ và số lần embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` để tách sau dấu câu nên dấu `.`, `!`, `?` vẫn nằm trong câu. Sau đó tôi strip và gom tối đa N câu vào một chunk; text rỗng trả về `[]`. Cách này đơn giản cho lab, nên các trường hợp như `Dr.`, `v.v.` hoặc số thập phân `3.14` vẫn có thể bị tách chưa đúng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử lần lượt paragraph, dòng, câu, từ và cuối cùng là ký tự. Base case là text rỗng, hoặc text đã ngắn hơn `chunk_size`; đoạn còn dài sẽ gọi lại với separator nhỏ hơn. Các mảnh nhỏ được ghép lại gần ngưỡng kích thước để không tạo quá nhiều chunk ngắn; nếu không còn separator thì hard-split theo ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được lưu thành một record in-memory gồm id, content, metadata copy và embedding. Khi search, query được embed một lần rồi lấy dot product với embedding đã lưu, sort giảm dần và trả tối đa `top_k`. Mock embeddings của lab đã normalize nên dot product dùng được để xếp hạng.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi lọc metadata trước rồi mới xếp hạng, vì lọc sau top-k có thể bỏ lỡ kết quả đúng thuộc nhóm metadata cần tìm. Metadata được copy và thêm `doc_id` mặc định từ `Document.id`; delete giữ lại các record có `doc_id` khác nên xóa hết mọi chunk của cùng tài liệu nguồn.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent gọi `store.search(question, top_k)` rồi tạo context đánh số `[1]`, `[2]` với source và content của từng kết quả. Prompt yêu cầu chỉ dùng context, không bịa, và nói rõ khi context chưa đủ; sau đó nó gọi `llm_fn` đã được inject. Nếu không có kết quả, agent trả thông báo rõ ràng mà không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v
============================= test session starts ==============================
collected 42 items

tests/test_solution.py .......................................... [100%]

============================== 42 passed in 0.05s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
