# Nguồn sinh site (bản sao để review)

Site này là output của `build.py`. Bản gốc nằm trên máy nhà (`short-drama/hub/`); build còn đọc `ke/shelf.csv` và thư mục phim local (poster, mô tả), nên không chạy được trên cloud.

- Sửa giao diện: `site.css` (build nhúng inline vào mọi trang), `template.html`.
- Sửa HTML/JS sinh ra: `build.py`. Tracking: `t.js` (copy thành `/assets/t.js`).
- Đừng sửa HTML đã build: lần build sau sẽ đè. Sửa ở đây, máy nhà chép về `hub/` rồi build lại.
- Trang guide (`/invite/rs-boost/`, bản `/es/` `/pt/`, `/guides/...`): mỗi trang 1 file `_src/guides/*.json`, build tự sinh trang + BreadcrumbList/WebPage/FAQPage, hreflang, sitemap, llms.txt. Khối code lấy từ `config.json` "invite" theo `code` = tên program. Không ghi số coin/hoa hồng nếu không có link trong `sources`.
- IndexNow: key ở `config.json` "indexnow", build ghi `<key>.txt` ra gốc. Sau mỗi deploy chạy `indexnow.py` (chép về `hub/` như build.py).
