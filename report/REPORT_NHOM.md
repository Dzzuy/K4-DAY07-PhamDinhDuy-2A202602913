# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nova  
**Thành viên:**  
- Phạm Đình Duy — 2A202602913  
- Phạm Quốc Đạt — 2A202602384  
- Võ Trường An — 2A20262656  
- Nguyễn Hữu Chương — 2A202602601  

**Ngày:** 20/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách bảo hành và hậu mãi Shopee dành cho Người Mua và Người Bán.

**Tại sao nhóm chọn chủ đề này?**
> Bộ dữ liệu gồm các chính sách công khai liên quan đến bảo hành, đăng bán, Shopee Mall, Trả hàng/Hoàn tiền, tranh chấp và Shopee Đảm Bảo. Các tài liệu có thông tin cho cả Người Mua và Người Bán, đồng thời nhiều chính sách dùng từ vựng gần nhau nhưng có quy trình, quyền và nghĩa vụ khác nhau. Vì vậy corpus phù hợp để so sánh các chiến lược chunking và kiểm tra tác dụng thực tế của metadata filter theo `audience`.

### Đóng góp thu thập và chuẩn hóa dữ liệu đến CP2

- **Phạm Đình Duy:** tham gia chọn phạm vi dữ liệu và các nguồn Shopee chính thức; phát hiện các trường hợp metadata/title không khớp nội dung được crawler lấy về; phối hợp làm sạch, chuẩn hóa lại corpus; thiết kế phân chia 4 chiến lược chunking khác nhau cho nhóm; phụ trách xây dựng bộ benchmark chung ở CP5.
- **Phạm Quốc Đạt:** sử dụng crawler được cung cấp trong repo để thu thập corpus ban đầu từ các nguồn công khai của Shopee.
- Corpus sau khi crawl được kiểm tra lại thủ công, làm sạch phần không liên quan và chuẩn hóa metadata trước khi dùng cho benchmark.
- Cả 4 thành viên sẽ sử dụng **cùng một corpus, cùng 5 benchmark queries, cùng gold answers và cùng cấu hình retrieval**, chỉ thay đổi chiến lược chunking để đảm bảo so sánh công bằng.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|---|---|---|---:|---|
| 1 | Chính sách bảo hành - trách nhiệm Người Bán | https://help.shopee.vn/portal/4/article/77245 | 2026-09-20 / not-stated | 2,337 | seller, warranty, shopee, vi |
| 2 | Chính sách bảo hành - quyền Người Mua | https://help.shopee.vn/portal/4/article/77245 | 2026-09-20 / not-stated | 3,292 | buyer, warranty, shopee, vi |
| 3 | Quy định về đăng bán sản phẩm trên Shopee | https://help.shopee.vn/portal/4/article/77246 | 2026-09-20 / not-stated | 2,175 | seller, listing-policy, shopee, vi |
| 4 | Điều khoản Dịch vụ Shopee Mall | https://help.shopee.vn/portal/4/article/77262 | 2026-09-20 / not-stated | 5,145 | both, mall-policy, shopee, vi |
| 5 | Những quy định chung về Trả hàng/Hoàn tiền của Shopee | https://help.shopee.vn/portal/4/article/188931 | 2026-09-20 / not-stated | 3,508 | buyer, return-refund, shopee, vi |
| 6 | Quy trình Shopee xử lý yêu cầu Trả hàng/Hoàn tiền | https://help.shopee.vn/portal/4/article/190242 | 2026-09-20 / not-stated | 3,026 | buyer, return-process, shopee, vi |
| 7 | Quy trình giải quyết tranh chấp/Xử lý khiếu nại | https://help.shopee.vn/portal/4/article/77265 | 2026-09-20 / 2024-03-15 | 2,933 | both, dispute, shopee, vi |
| 8 | Shopee Đảm Bảo là gì? | https://help.shopee.vn/portal/4/article/79314 | 2026-09-20 / not-stated | 1,642 | buyer, buyer-protection, shopee, vi |

**Tổng quan corpus (Corpus Summary):**
- Tổng số tài liệu: **8 file Markdown** từ **7 URL nguồn công khai**.
- Phân bố `audience`: **buyer 4, seller 2, both 2**.
- Article `77245` được tách thành hai document buyer/seller để metadata filter có tác dụng thực tế.
- CP2 validation: **PASS** — 8 file nằm trong yêu cầu 5–10; metadata đầy đủ; `doc_id` khớp filename; `sources.csv` khớp 1-1; có ít nhất 2 giá trị `audience`.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Corpus chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` trong metadata.
- [x] Mỗi tài liệu có `audience` (`buyer` / `seller` / `both`) và trường phân loại bổ sung.
- [x] Mỗi `doc_id` khớp tên file `.md` và `sources.csv`.
- [x] Dữ liệu crawler đã được đọc lại và làm sạch trước khi benchmark.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|---|---|---|---|
| `doc_id` | string | `buyer-warranty-policy` | Định danh ổn định giữa file, chunk, metadata và nguồn. |
| `title` | string | `Quy trình Shopee xử lý yêu cầu Trả hàng/Hoàn tiền` | Cho biết phạm vi document khi hiển thị kết quả retrieval. |
| `source_url` | URL/string | `https://help.shopee.vn/portal/4/article/190242` | Truy vết về nguồn chính sách gốc. |
| `retrieved_at` | date | `2026-09-20` | Theo dõi thời điểm dữ liệu được thu thập. |
| `document_version` | string/date | `2024-03-15` hoặc `not-stated` | Phân biệt phiên bản/ngày cập nhật khi nguồn có công bố. |
| `audience` | enum | `buyer`, `seller`, `both` | Metadata chính dùng cho A/B filtered vs unfiltered retrieval. |
| `category` | string | `return-refund` | Phân biệt các nhóm policy có từ vựng gần nhau. |
| `platform` | string | `shopee` | Giữ provenance theo nền tảng nếu corpus mở rộng. |
| `language` | string | `vi` | Xác nhận ngôn ngữ nguồn và query. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu. Corpus, 5 benchmark queries, gold answers, embedding backend, `top_k` và cách chấm được giữ giống nhau; chỉ chiến lược chunking thay đổi.

### Cấu hình benchmark dùng chung

- Corpus: `data/shopee-warranty/` (8 file Markdown; chỉ body được chunk).
- Embedder: `LocalEmbedder` — `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- Top-k: 3; gold set: 5 logical queries với full gold answers trong `bench.py`.
- Mỗi chunk giữ frontmatter gốc và thêm `doc_id=path.stem`. Q1 là A/B cùng một query, không tính thành hai câu.

### Phân tích đường cơ sở (Baseline Analysis)

Nhóm chạy `ChunkingStrategyComparator().compare()` trên ba tài liệu đại diện sau khi loại frontmatter:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|---|---|---:|---:|---|
| `seller-warranty-policy.md` | FixedSizeChunker (`fixed_size`) | 10 | 198.80 | Một phần; cắt theo ký tự nên có thể cắt giữa câu hoặc heading. |
| `seller-warranty-policy.md` | SentenceChunker (`by_sentences`) | 3 | 511.33 | Tốt ở ranh giới câu, nhưng chunk dài hơn. |
| `seller-warranty-policy.md` | RecursiveChunker (`recursive`) | 12 | 126.92 | Một phần; ưu tiên ranh giới tự nhiên nhưng heading ngắn có thể thành chunk riêng. |
| `return-refund-policy.md` | FixedSizeChunker (`fixed_size`) | 16 | 195.88 | Một phần; kích thước đều nhưng có thể cắt giữa câu. |
| `return-refund-policy.md` | SentenceChunker (`by_sentences`) | 7 | 338.71 | Giữ điều kiện và thời hạn theo câu khá tốt. |
| `return-refund-policy.md` | RecursiveChunker (`recursive`) | 18 | 130.94 | Giữ nhiều ranh giới nhỏ nhưng tạo nhiều chunk hơn. |
| `shopee-mall-terms.md` | FixedSizeChunker (`fixed_size`) | 25 | 196.96 | Độ dài đều nhưng không ưu tiên cấu trúc điều khoản. |
| `shopee-mall-terms.md` | SentenceChunker (`by_sentences`) | 7 | 530.00 | Giữ câu/điều khoản dài tốt hơn nhưng chunk lớn. |
| `shopee-mall-terms.md` | RecursiveChunker (`recursive`) | 24 | 153.58 | Giữ được nhiều newline/section boundary nhưng có thể sinh chunk nhỏ. |

### Chiến lược của từng thành viên

**Thành viên 1 — Phạm Quốc Đạt — 2A202602384**
- **Loại chiến lược:** `FixedSizeChunker`.
- **Mô tả & lý do chọn:** Đây là baseline đơn giản, dễ kiểm soát kích thước và chi phí embedding. Nhược điểm dự kiến là có thể cắt giữa câu hoặc điều khoản, vì vậy kết quả của Đạt tạo mốc so sánh với các chiến lược semantic/structure-aware.
- **Tham số benchmark:** sẽ ghi đúng cấu hình thực tế khi Đạt chạy CP5/CP6.

**Thành viên 2 — Phạm Đình Duy — 2A202602913**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`.
- **Mô tả & lý do chọn:** Giữ nguyên ranh giới câu nên tránh cắt điều khoản giữa câu. Ba câu/chunk là cấu hình trung gian nhằm giữ đủ context mà không gom quá nhiều policy khác nhau vào một chunk.
- **Code snippet:** dùng implementation `SentenceChunker` đã hoàn thành trong Phase 1.

**Thành viên 3 — Nguyễn Hữu Chương — 2A202602601**
- **Loại chiến lược:** `RecursiveChunker`.
- **Mô tả & lý do chọn:** Chiến lược ưu tiên các ranh giới tự nhiên như paragraph, newline, câu và khoảng trắng trước khi hard-split. Điều này phù hợp với policy dài có nhiều đoạn/điều khoản, đồng thời vẫn giới hạn kích thước chunk.
- **Tham số benchmark:** sẽ ghi đúng cấu hình thực tế khi Chương chạy CP5/CP6.

**Thành viên 4 — Võ Trường An — 2A20262656**
- **Loại chiến lược:** Custom `HeadingAwarePolicyChunker`.
- **Mô tả & lý do chọn:** Chunk theo heading/section của Markdown trước để giữ cấu trúc điều khoản gốc. Nếu một section quá dài, chiến lược có thể fallback sang chia nhỏ nhưng phải giữ heading đi kèm để chunk vẫn còn ngữ cảnh.
- **Code snippet:** **PENDING CP5** — phải dán implementation thực tế của An sau khi hoàn thành custom chunker; không tự tạo code giả trong report.

### So Sánh Giữa Các Thành Viên

| Thành viên        | Chiến lược                                    | Điểm truy xuất (/10) | Điểm mạnh dự kiến                                                                       | Điểm yếu dự kiến                                                                           |     |
| -------------------| -----------------------------------------------| ---------------------:| -----------------------------------------------------------------------------------------| --------------------------------------------------------------------------------------------| -----|
| Phạm Quốc Đạt     | FixedSizeChunker                              | PENDING CP6          | Đơn giản, kích thước ổn định, baseline rõ ràng                                          | Có thể cắt giữa câu/điều khoản                                                             |     |
| Phạm Đình Duy     | SentenceChunker (`max_sentences_per_chunk=3`) | 5 / 10               | Q2 và Q4 lấy answer-bearing chunk ở Top-1; Q1 metadata filter đưa gold chunk vào Top-3. | Q3 và Q5 không đưa chunk chứa đủ marker vàng vào Top-3.                                    |     |
| Nguyễn Hữu Chương | RecursiveChunker                              | 7/10                 | Tôn trọng nhiều ranh giới tự nhiên                                                      | Có trường hợp tiêu đề nằm ở chunk này, nội dung nằm ở chunk kia, gây mất ngữ cảnh nội dung |     |
| Võ Trường An      | HeadingAwarePolicyChunker                     | PENDING CP6          | Domain-aware, giữ cấu trúc heading/section                                              | Phụ thuộc chất lượng heading; cần fallback cho section dài                                 |     |

\* Kết quả của Duy dùng `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` qua LocalEmbedder trên 41 sentence chunks. Không dùng kết quả để chọn winner khi ba chiến lược còn lại chưa có kết quả cuối.

### Failure case quan sát từ SentenceChunker của Duy

**Query:** Q3 — Sản phẩm của tôi cần đáp ứng các điều kiện cơ bản nào để được bảo hành?

**Expected:** Chunk của `buyer-warranty-policy` có đủ “Còn thời hạn bảo hành”, “Còn tem/phiếu bảo hành” và “lỗi kỹ thuật”.

**Observed:** Top-3 trả về một chunk nói chi phí/liên hệ bảo hành, một chunk chính sách chung và một chunk trách nhiệm Người Bán; không có chunk chứa đủ ba điều kiện.

**Cause:** Chunk điều kiện cụ thể là các bullet ngắn, trong khi các chunk chính sách chung chứa nhiều từ “bảo hành” và “điều kiện” nên được semantic retrieval xếp cao hơn.

**Proposed fix:** Ở một thí nghiệm mới, giữ heading đi kèm chunk sau hoặc thử overlap câu nhỏ; không thay đổi corpus/query/cấu hình của benchmark CP6 này sau khi đã chấm.

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **PENDING CP6.** Nhóm chỉ kết luận sau khi cả 4 thành viên chạy cùng 5 benchmark queries trên cùng corpus và cùng cấu hình retrieval. Không chọn “winner” trước khi có kết quả thực nghiệm.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> Bộ 5 query dùng chung cho mọi thành viên. Gold answer đều trích từ corpus đã freeze. Q1 chạy A/B trên cùng query: unfiltered và `metadata_filter={"audience": "seller"}`; hai lượt vẫn chỉ tính là một logical query.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk/document chứa thông tin |
|---|---|---|---|
| 1 | Quyền và trách nhiệm của tôi đối với việc bảo hành sản phẩm trên sàn là gì? | Người Bán tiếp nhận bảo hành theo Chính sách bảo hành và đăng chính sách trong phần mô tả. | `seller-warranty-policy.md`; A/B `audience=seller` |
| 2 | Đơn tự vận chuyển có bao nhiêu ngày để yêu cầu trả hàng nếu chưa bấm nhận hàng? | 20 ngày từ “Lấy hàng thành công”. | `return-refund-policy.md` |
| 3 | Sản phẩm cần điều kiện cơ bản nào để được bảo hành? | Còn hạn; còn tem/phiếu; lỗi kỹ thuật không do Người Mua. | `buyer-warranty-policy.md` |
| 4 | Khiếu nại không phải Trả Hàng/Hoàn Tiền được xử lý bao lâu? | 07 ngày làm việc sau khi nhận đủ thông tin/tài liệu; vụ phức tạp có thể lâu hơn. | `dispute-process.md` |
| 5 | Các lý do gửi yêu cầu Trả hàng/Hoàn tiền là gì? | Chưa nhận, thiếu/sai hàng, lỗi/khác mô tả/đã dùng/giả nhái, hoặc đổi ý còn nguyên trạng. | `return-refund-policy.md` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm theo `docs/SCORING.md`: **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi                                                                         | Chiến lược tốt nhất cho câu này                                    | Có chunk liên quan trong top-3? | Ghi chú                                                                                                                                       |
| - | ------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Quyền và trách nhiệm của tôi đối với việc bảo hành sản phẩm trên sàn là gì?     | `RecursiveChunker` và `HeadingAwarePolicyChunker`                  | Có                              | Chương và An đều đưa answer-bearing chunk lên **Rank 2** khi dùng `audience=seller`; Duy đưa lên Rank 3.                                      |
| 2 | Đơn tự vận chuyển có bao nhiêu ngày để yêu cầu trả hàng nếu chưa bấm nhận hàng? | `SentenceChunker`, `RecursiveChunker`, `HeadingAwarePolicyChunker` | Có                              | Cả ba LocalEmbedder run đều lấy đúng chunk chứa **20 ngày** và “Lấy hàng thành công” ở **Top-1**, đạt 2/2.                                    |
| 3 | Sản phẩm cần điều kiện cơ bản nào để được bảo hành?                             | `RecursiveChunker` và `HeadingAwarePolicyChunker`                  | Có                              | Chương và An lấy đúng chunk chứa đủ 3 điều kiện ở **Top-1**, đạt 2/2. `SentenceChunker` của Duy không đưa chunk chứa đủ các marker vào Top-3. |
| 4 | Khiếu nại không phải Trả Hàng/Hoàn Tiền được xử lý bao lâu?                     | `SentenceChunker`, `RecursiveChunker`, `HeadingAwarePolicyChunker` | Có                              | Cả ba LocalEmbedder run đều đưa chunk `dispute-process` chứa **07 ngày làm việc** lên Top-1, đạt 2/2.                                         |
| 5 | Các lý do gửi yêu cầu Trả hàng/Hoàn tiền là gì?                                 | Chưa có chiến lược nào giải quyết đầy đủ                           | Không đủ                        | Cả ba LocalEmbedder run đều đạt 0/2 vì Top-3 không chứa đầy đủ 8 lý do của gold answer. Đây là failure case chung rõ nhất của benchmark.      |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Metadata filter có tác dụng rõ nhất ở **Q1**, là câu hỏi cố ý mơ hồ giữa quyền/trách nhiệm của Người Mua và Người Bán. Với `SentenceChunker` của Duy, answer-bearing chunk chuyển từ **không có trong Top-3** khi unfiltered sang **Rank 3** khi lọc `audience=seller`. Với `RecursiveChunker` của Chương, kết quả cải thiện từ **Rank 3 lên Rank 2**. Với `HeadingAwarePolicyChunker` của An, answer-bearing chunk giữ nguyên **Rank 2 → Rank 2**, nghĩa là filter không tăng hạng nhưng vẫn giới hạn candidate về đúng audience. Kết quả cho thấy metadata filter hữu ích nhất khi corpus có nhiều tài liệu dùng từ vựng giống nhau nhưng áp dụng cho các đối tượng khác nhau.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

> 1. **Chunking ảnh hưởng trực tiếp đến retrieval:** cùng corpus, cùng 5 query và cùng embedding model nhưng `SentenceChunker` đạt 5/10, trong khi `RecursiveChunker` và `HeadingAwarePolicyChunker` đạt 7/10.
> 2. **Metadata filter có giá trị thực tế:** ở Q1, filter `audience=seller` giúp `SentenceChunker` từ không có answer-bearing chunk trong Top-3 lên Rank 3 và giúp `RecursiveChunker` tăng từ Rank 3 lên Rank 2.
> 3. **Đúng document chưa có nghĩa là đủ câu trả lời:** Q5 cho thấy retrieval có thể tìm đúng chủ đề hoặc đúng document nhưng vẫn không chứa đầy đủ danh sách 8 lý do cần trả lời. Vì vậy nhóm đánh giá ở content-level thay vì chỉ kiểm tra `doc_id`.

**Bài học rút ra khi so sánh trong nhóm:**

> `FixedSizeChunker` đơn giản và kiểm soát kích thước tốt nhưng dễ cắt giữa điều khoản; kết quả hiện tại của Đạt chưa thể so sánh công bằng vì artifact vẫn dùng MockEmbedder. `SentenceChunker` giữ câu hoàn chỉnh và hoạt động tốt ở các câu hỏi Q2, Q4 nhưng gặp khó với danh sách bullet và thông tin phụ thuộc heading. `RecursiveChunker` giữ được nhiều ranh giới tự nhiên và đạt 7/10. `HeadingAwarePolicyChunker` cũng đạt 7/10, đồng thời giữ heading cha trong từng subchunk nên phù hợp với tài liệu policy có cấu trúc section rõ ràng. Không có chiến lược nào giải quyết tốt Q5, cho thấy chunking đơn thuần chưa đủ cho câu hỏi yêu cầu tổng hợp một danh sách dài.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nhóm sẽ giữ cấu trúc heading/section và các danh sách bullet quan trọng thành các đơn vị nguyên vẹn thay vì để chúng bị chia giữa nhiều chunk. Với các section dài, có thể bổ sung overlap hoặc cơ chế lấy thêm các chunk lân cận trong cùng section. Ngoài dense embedding, nhóm cũng có thể thử hybrid retrieval như BM25 + vector search để cải thiện các câu hỏi chứa con số, cụm từ chính xác hoặc danh sách nhiều mục. Metadata cũng có thể được mở rộng thêm các trường như `section_type`, `policy_type` hoặc `effective_date`.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                 | Điểm tự đánh giá |
| ---------------------------------------- | ---------------- |
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10          |
| Thiết kế chiến lược (Strategy Design)    | 15 / 15          |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10           |
| Thuyết trình (Demo)                      | 5 / 5            |
| **Tổng phần nhóm**                       | **37 / 40**      |
