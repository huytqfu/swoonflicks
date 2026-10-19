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

## 5 file nháp hiện có

Lấy từ `ke/lo3/network-ads-films-2026-10-19.md` (claude-work-brain, nhánh `claude/lo3-network-ads-2026-10-19`). File đó **không có phim ShortMax nào** (không tìm thấy page ShortMax chính chủ); 5 tên dưới đây là phim có tên rõ trên các page suy luận là NetShort, xếp theo số ad.

| File | Tín hiệu (file nguồn) | Còn thiếu |
|---|---|---|
| `my-succubus-glow-up.json` | page Netshorts chính chủ 19 ad + 9 ad page farm | synopsis, cặp link DramaCPS, poster, genre; kiểm 18+ |
| `the-dragonless-beggar-commands-nine-dragons.json` | page Netshorts 13 ad | như trên |
| `the-mafia-bosses-max-level-nanny.json` | 12 ad / 9 page farm | như trên |
| `my-spells-can-evolve-endlessly.json` | 8 ad / 8 page farm | như trên |
| `blind-heiress-exposes-husband-at-banquet-shatters-ipo-dreams.json` | 2 ad / 1 page | như trên; có thể là hook, không phải tên phim; tên 61 ký tự nên phải điền `seo_title` |

Chưa xác minh cho cả 5: phim có trên DramaCPS không, network thật của từng phim, tên chính thức.
