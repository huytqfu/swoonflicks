# Lô 3: đầu vào cho 5 trang phim mới (19/10/2026)

Mỗi phim 1 file spec `_src/lo3/<slug>.json`. Điền đủ, xoá `_draft` và `_todo`, rồi sinh cả lô một lần:

```
for f in _src/lo3/*.json; do python3 _src/new_film.py "$f" --write || echo "LỖI: $f"; done
python3 _src/new_film.py --check            # lint lại toàn bộ content
python3 _src/tests/new_film_test.py && node _src/tests/ads-links.test.js
```

`new_film.py` **từ chối** spec còn `"TODO"` hoặc `"_draft": true` (không ghi gì). Cách tool lọc chữ: xem `_src/new-film.md`.

## Từng trường lấy ở đâu

| Trường | Bắt buộc | Lấy ở đâu | Ghi chú |
|---|---|---|---|
| `slug` | có | tên phim viết thường, nối `-` | trùng thư mục trang `/<slug>/`; build cắt hậu tố id `-xxxxxx` của thư mục phim |
| `title` | có | tên phim **chính thức** trên trang DramaCPS / app | tiêu đề ad trên Meta có thể là hook, không phải tên phim |
| `synopsis` | có | mô tả phim trên DramaCPS (`info.json` của thư mục phim máy nhà), **chép nguyên** | là căn cứ chống bịa: tên riêng, con số trong chữ trang phải có ở đây |
| `network` | nên có | app của link DramaCPS | không hiện trên trang; dùng để lọc tên network |
| `genre` | nên có | chọn trong nhóm có sẵn ở `GENRE` (build.py): Fantasy, Family, Revenge, Romance, Royal, Sci-Fi | thiếu thì phim biến mất khi lọc thể loại |
| `drama_url` | có | DramaCPS → link "Drama URL" của phim | link organic, vào cột `link` của `ke/shelf.csv` (máy nhà) |
| `app_home_url` | không | DramaCPS → link "App Home" cùng cặp | chỉ dùng cho `ads_links` khi đã chốt chạy ads phim đó |
| số tập | **không ghi** | — | trang không hiện số tập; tool chặn "48 episodes", "episode 3" |
| `poster` | có (máy nhà) | ảnh dọc 3:4 của phim | máy nhà lưu thành `banner.jpg` trong thư mục phim; thiếu thì build bỏ phim |
| `trailer_url` | không | mp4 tập 1 trên DramaCPS | máy nhà đẩy lên R2 (`make_episodes.py`); `trailer-dates.json` chỉ điền ngày thật (`Last-Modified`) |
| `sources.episodes` / `sources.app` | không | URL trang phim chính thức trên app | trang cụ thể, không phải trang chủ; không có thì `null` |
| `intro`, `why`, `faq` | không | người viết, bám synopsis | thiếu thì trang chỉ có FAQ "where to watch" + "about" + synopsis |
| `seo_title`, `seo_description` | không | tự sinh nếu thiếu | title ≤60, desc ≤155; mẫu `<tên>: Where to Watch` cho tên ≤44 ký tự, `<tên>: Watch` ≤53, tên trơn ≤60; tên dài hơn 60 thì phải điền `seo_title` tay |

Luật trang phim (tool tự kiểm): không chữ "free", không tên network, không số tập, không chi tiết vũ khí, không tên riêng / con số ngoài synopsis, title ≤60, description ≤155.

## 10 file nháp ShortMax hiện có (A27, 19/10)

Top 10 bão hoà thấp của `side-hustle/short-drama/lo3-saturation-2026-10-19.md` (claude-work-brain, nhánh `claude/lo3-saturation-2026-10-19`, mục 3). `network` = ShortMax theo tag upload, chưa đối chiếu app. 5 spec NetShort cũ chuyển sang `_old/` (không xoá).

| File | Tên (ký tự) | Còn thiếu |
|---|---|---|
| `from-fat-girl-to-beauty-queen.json` | 29 | synopsis, cặp link, poster |
| `i-taught-the-dragon-how-to-court-now-he-s-completely-mine.json` | 58 | như trên; seo_title tự rút về `<tên>` trơn |
| `they-called-me-a-fool-until-i-saved-the-mafia-don.json` | 50 | như trên; seo_title rút về `<tên>: Watch` |
| `too-fat-for-you-watch-me-marry-the-billionaire.json` | 47 | như trên; seo_title rút về `<tên>: Watch` |
| `heiress-in-disguise.json` | 19 | như trên |
| `the-mafia-heiress-returns.json` | 25 | như trên |
| `revenge-of-the-billionaire-s-hidden-wife.json` | 40 | như trên |
| `rise-of-the-forgotten-god-from-trash-to-shocking-the-gods.json` | 58 | như trên; seo_title rút về `<tên>` trơn |
| `my-billionaire-ex-s-revenge.json` | 27 | như trên |
| `forbidden-by-the-moon.json` | 21 | như trên |

- **Synopsis: 0/10 có nguồn chính thức.** WebSearch 19/10 cho từng tên (kèm "ShortMax") không ra trang chính thức nào có synopsis đúng tên; `_source` để `null`, `synopsis` = TODO. Vài kết quả chỉ là tên gần hoặc bản tiếng Tây Ban Nha khác tên, không dùng.
- `genre` điền theo tên phim, **chưa xác minh**; sửa khi có synopsis.
- Tên lấy từ tiêu đề upload YouTube; tên chính thức trên DramaCPS / app chưa xác minh.
