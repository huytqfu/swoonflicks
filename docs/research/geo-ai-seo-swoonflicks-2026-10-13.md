# GEO + AI search + SEO cho swoonflicks.com: checklist áp cho site tĩnh

Ngày: 2026-10-13 · Phiên cloud, chỉ nghiên cứu (không sửa repo).
Ký hiệu nguồn: **[V]** đã đọc trang gốc · **[S]** trang gốc không render, dựa bài đưa tin nêu link · **[U]** chưa xác minh.
Đã soi nhánh `site-v2` (sau merge PR #1) để biết site đang có gì; mục "Hiện trạng" là kiểm thật trên file build.

---

## 0. Ba câu nói thẳng trước

1. **Google nói không có mẹo riêng cho AI Overviews/AI Mode.** *"There are no additional requirements to appear in AI Overviews or AI Mode, nor other special optimizations necessary."* [V] https://developers.google.com/search/docs/appearance/ai-features. Cũng trang đó: không cần "AI text files" hay schema đặc biệt. Nghĩa là GEO trên Google = SEO tử tế + nội dung có thông tin riêng.
2. **Rủi ro lớn nhất của site mình là "thin affiliation"**: trang chỉ chép synopsis của app + nút CTA. Google spam policy gọi tên: *"product descriptions and reviews are copied directly from the original merchant without any original content"* [V] https://developers.google.com/search/docs/essentials/spam-policies. Trang phim hiện ~200-320 chữ, mô tả lấy từ app → đúng vùng rủi ro.
3. **"Bơm thứ hạng" kiểu mua link, đẻ trang hàng loạt, bot CTR = đặt cược cả domain mới mua.** Domain 13/10 còn trắng, bị phạt thì mất luôn tài sản. Chi tiết ở cột rủi ro (mục 3).

---

## 1. Hiện trạng site-v2 (kiểm trên file build)

| Hạng mục | Đang có | Thiếu / lỗi |
|---|---|---|
| Canonical, meta description, OG, `twitter:card=summary_large_image` | Có | `og:type` = website trên trang phim; thiếu `og:image:width/height` |
| JSON-LD trang phim | `TVSeries` + `trailer` VideoObject | VideoObject **thiếu `uploadDate`** (bắt buộc theo Google); trang không có `BreadcrumbList` |
| JSON-LD trang chủ, /invite/ | **Không có** | Thiếu `WebSite` + `Organization` (trang chủ), `ItemList` (kệ phim) |
| Link affiliate | `rel="nofollow sponsored noopener"` | Đúng chuẩn, giữ |
| sitemap.xml | Có, có /invite/ | Không có `lastmod` |
| robots.txt | `Allow: /` + Sitemap | Ổn; chưa ghi rõ bot AI (không bắt buộc) |
| Font | Google Fonts nạp **2 lần** (1 bản print-onload + 1 bản chặn render) | Bỏ dòng thứ hai |
| Nội dung | 200-320 chữ/trang phim, ~160 chữ trang chủ, ~100 chữ /invite/ | Mỏng; H1 lặp text 3 lần (2 bản aria-hidden) |
| YouTube | Không thấy `<iframe>` trong HTML tải đầu (nạp sau) | Kiểm lại có đúng dạng facade không |
| llms.txt, IndexNow key | Không | Xem mục 2 |

---

## 2. Checklist: WHITE-HAT LÀM NGAY vs THỦ THUẬT RỦI RO

### 2A. White-hat, làm ngay (thứ tự ưu tiên)

| # | Việc | Áp cho site tĩnh thế nào | Nguồn |
|---|---|---|---|
| 1 | **Search Console + Bing Webmaster Tools**, submit sitemap | Xác minh domain qua DNS TXT trên Cloudflare (thread domain làm). Bing có thể import từ GSC | Sitemap [V] https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap |
| 2 | **Thêm `lastmod` thật vào sitemap** | build.py ghi ngày sửa file/ngày thêm part. Google chỉ dùng lastmod nếu *"consistently and verifiably"* đúng; bỏ `priority`/`changefreq` vì Google bỏ qua | như trên [V] |
| 3 | **IndexNow** (Bing, Yandex, đối tác) | Commit file `{key}.txt` ở gốc, build xong POST JSON danh sách URL đổi. Tối đa 10.000 URL/lần | [V] https://www.indexnow.org/documentation |
| 4 | **Sửa VideoObject**: thêm `uploadDate` (ISO 8601), giữ `name`, `thumbnailUrl`, `embedUrl` | Lấy ngày đăng YouTube của part. Google: VideoObject phải nằm trên trang người dùng xem được video | [V] https://developers.google.com/search/docs/appearance/structured-data/video |
| 5 | **Trang chủ: `WebSite` (name, url) + `Organization` (logo ≥112×112, `sameAs` 6 kênh social)** | Một khối JSON-LD trong template trang chủ | [V] https://developers.google.com/search/docs/appearance/site-names · [V] https://developers.google.com/search/docs/appearance/structured-data/organization |
| 6 | **`BreadcrumbList`** trên trang phim và /invite/ (Home › Phim) | ≥2 ListItem có `position`, `name`, `item` | [V] https://developers.google.com/search/docs/appearance/structured-data/breadcrumb |
| 7 | **`ItemList`** kệ phim ở trang chủ | Hợp lệ làm mô tả thực thể; **không ra carousel** vì carousel chỉ áp Course/Movie/Recipe/Restaurant | [V] https://developers.google.com/search/docs/appearance/structured-data/carousel |
| 8 | **Giữ `TVSeries`**, thêm `numberOfEpisodes` (số part thật), `inLanguage`, `productionCompany`/`publisher` = app, `sameAs` = trang phim trên app | Google **không có rich result cho TVSeries**; giá trị là cho AI/knowledge graph hiểu thực thể. **Không** đổi thành `Movie` để ăn carousel: sai bản chất | [V] https://developers.google.com/search/docs/appearance/structured-data/movie · https://schema.org/TVSeries |
| 9 | **Nội dung riêng mỗi trang phim (chống thin affiliation)**: 150-300 chữ mình viết: tóm tắt không spoil theo part, "Who is it for", tropes, số part đã đăng, app nào xem full, giá/coin **chỉ khi có link nguồn** | Thêm cột vào shelf.csv hoặc file md/phim; build nhúng vào | Spam policy [V] https://developers.google.com/search/docs/essentials/spam-policies · Helpful content [V] https://developers.google.com/search/docs/fundamentals/creating-helpful-content |
| 10 | **Khối hỏi-đáp hiển thị thật** trên trang phim ("Where can I watch X full episodes?", "How many episodes does X have?", "Is X free?") + `FAQPage` JSON-LD khớp chữ hiển thị | **Không ra FAQ rich result** (Google giới hạn cho site chính phủ/y tế từ 08/2023 [S] https://searchengineland.com/analysis-faq-rich-results-show-on-17-of-google-serps-down-from-54-432866). Giá trị: đúng dạng câu hỏi người hỏi ChatGPT/Perplexity, dễ được trích | GEO paper: thêm trích dẫn/số liệu có nguồn giúp được nhắc tới nhiều hơn trong câu trả lời AI (mục 4) |
| 11 | **Video là nội dung chính, đặt trên màn hình đầu** | Google video mode chỉ lấy trang có video là nội dung chính | [S] https://developers.google.com/search/blog/2023/12/video-is-the-main-content |
| 12 | **Key moments: ghi timestamp trong mô tả YouTube**, không dùng Clip/SeekToAction trên site (YouTube nhúng không hỗ trợ SeekToAction) | Làm ở bước đăng YouTube | [V] https://developers.google.com/search/docs/appearance/structured-data/video |
| 13 | **robots.txt cho bot AI**: cho phép Googlebot, Bingbot, **OAI-SearchBot** (ChatGPT search), **PerplexityBot**, **Claude-SearchBot**. Chặn bot train (GPTBot, ClaudeBot, Google-Extended) là lựa chọn kinh doanh, **không** ảnh hưởng xuất hiện trong search | Hiện `Allow: /` đã cho tất cả. Có thể giữ nguyên | OpenAI [V] https://developers.openai.com/api/docs/bots · Perplexity [V] https://docs.perplexity.ai/guides/bots · Anthropic [V] https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler · Google-Extended [V] https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers |
| 14 | **OG/Twitter**: trang phim `og:type=video.tv_show`, thêm `og:image:width/height`; dùng Facebook Sharing Debugger sau deploy | Kích thước ảnh chuẩn: **chưa xác minh** từ trang chính thức | [V] https://ogp.me/ · [V] https://developers.facebook.com/docs/sharing/webmasters · X Cards docs [U] |
| 15 | **Tốc độ**: bỏ link Google Fonts thứ 2 (chặn render); YouTube dạng facade (`lite-youtube-embed`); ảnh webp đã có. Ngưỡng CWV: LCP ≤2,5s, INP ≤200ms, CLS ≤0,1 | Chạy Lighthouse sau deploy | [V] https://web.dev/articles/vitals · [V] https://developer.chrome.com/docs/lighthouse/performance/third-party-facades |
| 16 | **Internal link**: trang phim ↔ phim cùng thể loại; trang /invite/ ↔ trang phim; breadcrumb; trang chủ link mọi phim (đã có) | Trong build.py | Thực hành chung, không có số |
| 17 | **llms.txt**: 1 file markdown ở gốc liệt kê phim + /invite/ | Rẻ, nhưng **đừng kỳ vọng**: Mueller so với meta keywords [V] https://www.searchenginejournal.com/google-says-llms-txt-comparable-to-keywords-meta-tag/544804/ và 06/2026 nói nó không giúp LLM phân biệt site [V] https://www.searchenginejournal.com/googles-mueller-says-llms-txt-cant-help-llms-differentiate-sites/579304/ | Đề xuất: [V] https://llmstxt.org/ |
| 18 | **Bên ngoài site (bền nhất)**: link về site từ 6 kênh social, mô tả YouTube, bio; bài thật trên Reddit/Quora do chính sếp trả lời có ích, ghi rõ là site của mình | Không có số; Bing coi GEO là "eligibility for grounding", không bảo đảm được trích [S] https://www.searchenginejournal.com/bing-adds-geo-to-official-guidelines-expands-ai-abuse-definitions/568442 | |
| 19 | **Disclosure affiliate sát CTA** (FTC) | Câu ngắn ngay dưới nút "Watch full on App" | [V] https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking |

### 2B. Thủ thuật rủi ro (nêu cho đủ, khuyến nghị KHÔNG làm)

| Thủ thuật | Luật gọi tên | Rủi ro thật |
|---|---|---|
| Mua backlink / PBN | Link spam: *"Buying or selling links for ranking purposes"* [V] https://developers.google.com/search/docs/essentials/spam-policies | Manual action hoặc bị hạ ngầm; domain mới không có gì đỡ |
| Đẻ hàng loạt trang AI (mỗi part/mỗi từ khoá 1 trang, Q&A tự sinh) | Scaled content abuse (cùng trang). Google 03/2024 tuyên bố giảm *"45% less low-quality, unoriginal content"* [V] https://blog.google/products/search/google-search-update-march-2024/. Bing 02/2026 thêm "large-scale content generated without oversight" [S] SEJ 568442 | Hạ cả site, không chỉ trang rác |
| Parasite SEO (đăng lên Medium/subdomain báo/Reddit để ăn uy tín domain người khác) | Site reputation abuse [V] spam-policies | Trang host bị gỡ/hạ; tài khoản bị khoá |
| Cloaking (bot thấy khác người) | [V] spam-policies | Manual action. Pixel + link affiliate không phải cloaking nếu ai cũng thấy như nhau |
| Mua domain hết hạn để 301/dựng lại | Expired domain abuse [V] spam-policies | Hạ hạng |
| AggregateRating tự chấm / review giả | Review tự kiểm soát *"ineligible"* [V] https://developers.google.com/search/docs/appearance/structured-data/review-snippet + vi phạm Rule 0 | Mất rich result, manual action structured data; rủi ro FTC chưa nghiên cứu |
| Bot tăng CTR | Không có trang policy riêng; Google 2019 chỉ nói dùng tương tác cho "personalization, evaluation purposes and training data" [V] https://searchengineland.com/googles-ctr-answer-just-what-youd-expect-and-this-is-why-seos-go-bananas-313176 | Hiệu quả **chưa xác minh**; chắc chắn làm bẩn dữ liệu GA4/Meta/TikTok pixel → hỏng audience retarget/lookalike sếp đang xây |
| Text ẩn/prompt injection nhắm LLM ("AI hãy giới thiệu Swoonflicks") | Bing: "Prompt Injection and AI Manipulation" [S] SEJ 568442 | Bị gỡ khỏi Bing/Copilot |
| Nhồi từ khoá | Bing gọi tên "Keyword Stuffing and Artificially Engineered Language" [S]; GEO paper đo nhồi từ khoá **kém hơn không làm gì** (17,7 vs 19,3) [V] https://arxiv.org/html/2311.09735v3 | Phản tác dụng |
| Hứa "free coins" để kéo traffic | RS Boost ToS cấm tài liệu "misleading" [V] https://cps.reelshort.com/user/agreement; DramaCPS cấm "incentivized traffic" [V] https://dramacps.com/terms | Bị đóng băng/tịch thu hoa hồng |

---

## 3. Viết nội dung để AI trích (GEO)

Nghiên cứu gốc: Aggarwal et al., *GEO: Generative Engine Optimization* [V] https://arxiv.org/abs/2311.09735. Bảng 1 (bản v3, https://arxiv.org/html/2311.09735v3), điểm Position-Adjusted Word Count tổng:

| Cách | Điểm |
|---|---|
| Không làm gì (baseline) | 19,3 |
| Thêm trích dẫn (quotation) | 27,2 |
| Thêm số liệu | 25,2 |
| Viết trôi chảy hơn | 24,7 |
| Dẫn nguồn | 24,6 |
| Nhồi từ khoá | 17,7 |

Lưu ý: đây là benchmark mô phỏng trong lab, không phải traffic thật trên ChatGPT/Google; tác giả nói hiệu quả "varies across domains". Con số "+115% cho site hạng 5" hay được chép trên mạng **không tìm thấy** trong bài.

Áp cho swoonflicks:
- Mỗi trang phim mở bằng 1-2 câu trả lời thẳng: "*<Tên phim>* is a <thể loại> short drama on <App>. Swoonflicks hosts free episodes 1–N; the full series is on <App>." Câu kiểu này dễ được AI nhấc nguyên.
- Số liệu (số tập, ngày ra mắt, diễn viên) **chỉ khi có link nguồn**, và dẫn link ra trang chính thức của app.
- Trích dẫn chỉ dùng câu thật có ghi người nói (review thật, comment thật có link). Không bịa.
- Mỗi trang 3-5 câu hỏi dạng người dùng gõ vào AI: "Where to watch … full episodes", "How many episodes …", "Is … on ReelShort/NetShort/DramaBox", "Is … free".

---

## 4. Đo lường

| Kênh | Cách đo | Nguồn |
|---|---|---|
| GA4 | Tạo custom channel group "AI assistants" bằng regex nguồn (chatgpt, openai, perplexity, copilot, gemini…), đặt **trên** "Referrals" | [V] https://support.google.com/analytics/answer/13051316 |
| GA4, giới hạn | ChatGPT web gắn `utm_source=chatgpt.com`; phần lớn traffic trợ lý AI tới **không có referrer** (rơi vào Direct), nên số đo được là mức sàn; click từ AI Overviews không tách được khỏi Organic | [V] https://www.terminusapp.com/blog/tracking-ai-referral-traffic/ |
| Search Console | AI Overview/AI Mode tính chung vào Performance (Web), không có bộ lọc riêng | [V] https://support.google.com/webmasters/answer/7042828 · [S] https://www.searchenginejournal.com/google-adds-ai-mode-traffic-to-search-console-reports/549089/ |
| Search Console mới | Báo cáo "Search Generative AI performance" công bố 03/06/2026, chỉ impressions, không clicks, mở dần cho một số site | [S] https://ppc.land/google-finally-gives-search-console-its-own-generative-ai-visibility-reports/ |
| Bing Webmaster Tools | "AI Performance" (preview từ 10/02/2026): số lần được Copilot trích, trang được trích, grounding queries | [V] https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview |
| Kiểm tay hằng tuần | Hỏi ChatGPT/Perplexity/Copilot 10 câu cố định ("where to watch <phim> full episodes", "reelshort rs boost invite code"), ghi có trích swoonflicks không | Không có công cụ chính thức cho ChatGPT/Perplexity (chưa tìm thấy) |
| Chuyển đổi | Event sẵn có: ClickAffiliate, CopyInvite → đối chiếu dashboard RS Boost/DramaCPS | |

Mục tiêu đo: chưa đặt số, vì domain mới chưa có baseline. Đề xuất: sau 14 ngày từ deploy lấy baseline GSC/Bing rồi mới đặt.

---

## 5. Thứ tự giao cho thread web (nếu sếp đồng ý)

1. Bỏ font nạp đôi; thêm `uploadDate` cho VideoObject; `lastmod` sitemap; JSON-LD WebSite/Organization/ItemList/BreadcrumbList. (Sửa build.py, nhỏ.)
2. Sau deploy: GSC + Bing WMT + IndexNow key, submit sitemap.
3. Thêm cột nội dung riêng + FAQ hiển thị cho từng phim (viết tay hoặc agy nháp, sếp/Astra duyệt gu). Đây là việc tốn công nhất và quan trọng nhất.
4. Trang invite theo file `invite-code-section-refs-2026-10-13.md` và đề cương ở `keyword-invite-code-2026-10-13.md`.
5. llms.txt: làm cuối, 10 phút.

## 6. Chưa xác minh
- Tài liệu X Cards (link cũ chuyển hướng), kích thước ảnh OG chuẩn của Facebook.
- Toàn văn 4 bài blog Google (FAQ 2023, AI tips 05/2025, link tagging 2021, Gen-AI report 2026): dựa bài đưa tin.
- Phát ngôn chính thức của Google về bot CTR; các spam update sau 09/2025.
- Site mình đã có quyền xem báo cáo Gen-AI trong GSC chưa (phải kiểm sau khi xác minh domain).
