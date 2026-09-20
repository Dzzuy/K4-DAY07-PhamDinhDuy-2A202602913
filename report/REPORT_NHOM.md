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

| Thành viên | Chiến lược | Điểm truy xuất (/10) | Điểm mạnh dự kiến | Điểm yếu dự kiến |
|---|---|---:|---|---|
| Phạm Quốc Đạt | FixedSizeChunker | PENDING CP6 | Đơn giản, kích thước ổn định, baseline rõ ràng | Có thể cắt giữa câu/điều khoản |
| Phạm Đình Duy | SentenceChunker | PENDING CP6 | Giữ ranh giới câu, context tự nhiên | Chunk có thể dài không đều |
| Nguyễn Hữu Chương | RecursiveChunker | PENDING CP6 | Tôn trọng nhiều ranh giới tự nhiên | Có thể tạo nhiều chunk nhỏ |
| Võ Trường An | HeadingAwarePolicyChunker | PENDING CP6 | Domain-aware, giữ cấu trúc heading/section | Phụ thuộc chất lượng heading; cần fallback cho section dài |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **PENDING CP6.** Nhóm chỉ kết luận sau khi cả 4 thành viên chạy cùng 5 benchmark queries trên cùng corpus và cùng cấu hình retrieval. Không chọn “winner” trước khi có kết quả thực nghiệm.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> Bộ 5 query dùng chung cho mọi thành viên. Gold answer đều trích từ corpus đã freeze. Q5 dùng `metadata_filter={"audience": "seller"}`; query không ghi buyer/seller để việc lọc metadata có ý nghĩa.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk/document chứa thông tin |
|---|---|---|---|
| 1 | Đối với đơn hàng do Người bán tự vận chuyển, nếu Người mua không bấm “Đã nhận được hàng”, thời hạn tối đa để gửi yêu cầu Trả hàng/Hoàn tiền là bao lâu kể từ lúc đơn hàng được cập nhật “Lấy hàng thành công”? | 20 ngày kể từ lúc đơn hàng được cập nhật trạng thái “Lấy hàng thành công”. | `return-refund-policy.md` — §1.2 |
| 2 | Ba điều kiện bảo hành cơ bản mà Shopee khuyến cáo Người Mua cần đáp ứng là gì? | Còn thời hạn bảo hành; còn tem/phiếu bảo hành; sản phẩm bị lỗi kỹ thuật không phải do lỗi của Người Mua. | `buyer-warranty-policy.md` — Điều kiện bảo hành |
| 3 | Khi đăng bán sản phẩm trên Shopee, Người Bán phải điền những thông tin nào liên quan đến nguồn gốc và bảo hành? | Điền đầy đủ nguồn gốc, xuất xứ, thuộc tính sản phẩm và chế độ bảo hành (nếu có) theo yêu cầu của mỗi ngành hàng. | `seller-listing-policy.md` — C.4 Thông tin mô tả |
| 4 | Với tranh chấp không phải khiếu nại Trả hàng/Hoàn tiền, Shopee đưa ra hướng giải quyết trong bao lâu sau khi nhận đủ thông tin/tài liệu? | Trong vòng 07 ngày làm việc kể từ ngày nhận đầy đủ thông tin/tài liệu liên quan; vụ việc có nhiều thông tin hoặc tình tiết phức tạp có thể kéo dài hơn. | `dispute-process.md` — Bước 3 |
| 5 | Khi phát sinh nhu cầu bảo hành sản phẩm trên Shopee thì cần làm gì? | Người Bán có trách nhiệm tiếp nhận bảo hành sản phẩm/dịch vụ cho Người Mua theo cam kết trong Chính sách bảo hành của Người Bán và/hoặc nhà sản xuất. Thông tin Chính sách bảo hành phải được đăng tải trong phần mô tả sản phẩm/dịch vụ trên Shopee. | `seller-warranty-policy.md` — §4; filter `audience=seller` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm theo `docs/SCORING.md`: **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---|---|---|---|
| 1 | PENDING CP5 | PENDING CP6 | PENDING CP6 | |
| 2 | PENDING CP5 | PENDING CP6 | PENDING CP6 | |
| 3 | PENDING CP5 | PENDING CP6 | PENDING CP6 | |
| 4 | PENDING CP5 | PENDING CP6 | PENDING CP6 | |
| 5 | PENDING CP5 | PENDING CP6 | PENDING CP6 | Metadata A/B required |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **PENDING CP6.** Nhóm sẽ so sánh filtered vs unfiltered trên query metadata đã chốt ở CP5 và chỉ kết luận từ kết quả thực tế.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> **PENDING CP6/CP7.** Sẽ chọn từ kết quả benchmark thực tế, metadata A/B và failure analysis.

**Bài học rút ra khi so sánh trong nhóm:**
> **PENDING CP6/CP7.** Chỉ tổng kết sau khi 4 strategy chạy cùng benchmark.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> **PENDING CP7.**

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|---|---|
| Lựa chọn tài liệu (Document Set Quality) | PENDING CP7 / 10 |
| Thiết kế chiến lược (Strategy Design) | PENDING CP7 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | PENDING CP7 / 10 |
| Thuyết trình (Demo) | PENDING CP7 / 5 |
| **Tổng phần nhóm** | **PENDING CP7 / 40** |
