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

**Ngưỡng đã chốt trước khi xem điểm:** cao `>= 0.50`, thấp `< 0.50`. Điểm được tính bằng `compute_similarity()` với đúng backend CP6 là `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Người mua có thể yêu cầu bảo hành khi sản phẩm còn thời hạn bảo hành. | Khách hàng được đề nghị bảo hành nếu hàng vẫn còn hạn. | cao | 0.6939 (cao) | Có |
| 2 | Người bán phải công khai chế độ bảo hành trong mô tả sản phẩm. | Khi đăng sản phẩm, người bán cần ghi thông tin bảo hành ở phần mô tả. | cao | 0.8377 (cao) | Có |
| 3 | Shopee xử lý tranh chấp trong vòng 07 ngày làm việc. | Python dùng thụt lề để xác định khối lệnh. | thấp | 0.1419 (thấp) | Có |
| 4 | Đơn do người bán tự vận chuyển có thể yêu cầu hoàn tiền sau 20 ngày. | Nếu không bấm đã nhận hàng, thời hạn trả hàng là 20 ngày từ lúc lấy hàng thành công. | cao | 0.8229 (cao) | Có |
| 5 | Người bán phải điền nguồn gốc và xuất xứ của sản phẩm. | Người mua cần gửi khiếu nại trong ứng dụng Shopee. | thấp | 0.3547 (thấp) | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 2 cao nhất (0.8377), đúng vì cả hai nói rõ nghĩa vụ công khai bảo hành trong mô tả. Cặp 5 vẫn thấp hơn ngưỡng nhưng không gần 0, vì cả hai đều thuộc bối cảnh Shopee; embedding nhận ra một ít ngữ cảnh chung nhưng vẫn phân biệt hành động khác nhau. Điều này cho thấy cosine không chỉ so từ giống nhau mà còn phản ánh hướng nghĩa tổng thể.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm retrieval | Có evidence liên quan không? | Grounding từ retrieved context |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Quyền/trách nhiệm bảo hành trên sàn (A/B seller) | Top-1 là chính sách chung của Người Bán (0.6014); chunk có đủ gold answer ở rank 3 khi filter seller. | 1 / 2 | Có | Không có LLM; evidence rank 3 đủ để grounding gold answer. |
| 2 | Thời hạn trả hàng đơn tự vận chuyển | `return-refund-policy` (0.8726): có mốc 20 ngày và “Lấy hàng thành công”. | 2 / 2 | Có | Không có LLM; evidence rank 1 đủ để trả lời 20 ngày. |
| 3 | Ba điều kiện bảo hành | `buyer-warranty-policy` (0.6306): nói chi phí/liên hệ bảo hành, thiếu ba điều kiện. | 0 / 2 | Không | Không có LLM; top-3 không chứa đủ ba conditions của gold answer. |
| 4 | Thời hạn xử lý tranh chấp | `dispute-process` (0.8307): nêu 07 ngày làm việc sau khi đủ thông tin/tài liệu. | 2 / 2 | Có | Không có LLM; evidence rank 1 đủ để trả lời gold answer. |
| 5 | Danh sách lý do Trả hàng/Hoàn tiền | `return-refund-process` (0.6830): hướng dẫn cung cấp bằng chứng, không liệt kê các lý do. | 0 / 2 | Không | Không có LLM; top-3 không chứa đầy đủ danh sách lý do. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5

**SentenceChunker retrieval score:** 5 / 10 (Q1 rank 3 = 1 điểm; Q2/Q4 rank 1 = 2 điểm; Q3/Q5 = 0). Shared bench không đánh giá `KnowledgeBaseAgent` hoặc LLM.

**Embedding backend:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` qua `LocalEmbedder`.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Một document đúng vẫn chưa đủ: phải nhìn đúng chunk có chứa câu trả lời. Metadata filter cũng chỉ giảm tập ứng viên; nó không tự làm embedding hiểu đúng câu hỏi. Vì thế benchmark cần giữ corpus và query cố định rồi ghi cả nội dung chunk, không chỉ ghi doc_id.

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
