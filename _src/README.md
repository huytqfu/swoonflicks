# Nguồn sinh site (bản sao để review)

Site này là output của `build.py`. Bản gốc nằm trên máy nhà (`short-drama/hub/`); build còn đọc `ke/shelf.csv` và thư mục phim local (poster, mô tả), nên không chạy được trên cloud.

- Sửa giao diện: `site.css` (build nhúng inline vào mọi trang), `template.html`.
- Sửa HTML/JS sinh ra: `build.py`. Tracking: `t.js` (copy thành `/assets/t.js`).
- Google Ads conversion: điền `gads` (`AW-…`) và `gads_label` trong `config.json`. Thiếu một trong hai thì build không đưa ra trang, HTML y như cũ. Có đủ thì mỗi lần bấm link CPS (`ClickAffiliate`) bắn thêm `conversion` tới `AW-…/label`, `transaction_id` = event_id, gửi kiểu beacon nên không giữ cú nhảy app.
- Đừng sửa HTML đã build: lần build sau sẽ đè. Sửa ở đây, máy nhà chép về `hub/` rồi build lại.
- Trang guide (`/invite/rs-boost/`, bản `/es/` `/pt/`, `/guides/...`): mỗi trang 1 file `_src/guides/*.json`, build tự sinh trang + BreadcrumbList/WebPage/FAQPage, hreflang, sitemap, llms.txt. Khối code lấy từ `config.json` "invite" theo `code` = tên program. Không ghi số coin/hoa hồng nếu không có link trong `sources`. Tuỳ chọn `"watch": [slug...]` (+ `watch_h2`): lưới poster ra thẳng link CPS gốc cùng tab, bắn ClickAffiliate placement=guide.
- IndexNow: key ở `config.json` "indexnow", build ghi `<key>.txt` ra gốc. Sau mỗi deploy chạy `indexnow.py` (chép về `hub/` như build.py).
- Link ads riêng: `config.json` "ads_links" = {slug: link DramaCPS riêng cho Google Ads}. Có thì build thêm `data-ads-href` vào nút ra app của phim đó; `t.js` đổi `href` sang link ads khi phiên có `gclid` hoặc `utm_source=google&utm_medium=cpc` (cờ `sf_paid` giữ cả phiên), và gửi `link_kind=ads|organic` trong `ClickAffiliate`. Rỗng = không đổi gì. Test: `node _src/tests/ads-links.test.js`.
- Trailer VideoObject: `trailer-dates.json` map `slug` → ngày đăng thật của tập 1 trên R2, ISO 8601 (vd `{"dragons-bow-to-the-trash": "2026-10-15"}`, lấy từ header `Last-Modified` của file mp4). Slug có ngày hợp lệ thì JSON-LD có `trailer` kèm `uploadDate`; không có hoặc sai định dạng thì build **bỏ** khối `trailer` (TVSeries còn lại vẫn hợp lệ). Không điền ngày đoán.
- Guide: `"films": [slug...]` = thẻ phim link **nội bộ** sang trang `/<slug>/` (khối "More dramas" cuối guide), khác `"watch"` ra thẳng link CPS.
- Thêm phim mới: `new_film.py` sinh `content/<slug>.json` + `.seo.json` từ 1 file spec, tự lọc luật nội dung; `--check` lint file đang có. Xem `new-film.md`. Test: `python3 _src/tests/new_film_test.py`.
