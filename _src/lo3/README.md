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

## 7 phim ShortMax đã sinh content (A28, 19/10)

Spec do PC điền (synopsis + cặp link DramaCPS); content sinh bằng `new_film.py --write`. 10 spec nháp A27 và 5 spec NetShort ở `_old/`.

| Phim | Slug | Genre | Nguồn synopsis | SEO title / desc |
|---|---|---|---|---|
| His Childhood Friend Ruined My Car, I Ruined His Empire | `his-childhood-friend-ruined-my-car-i-ruined-his-empire` | Revenge, Romance | [DramaCPS](https://dramacps.com/dashboard/materials?source=shortmax&q=660602) | 55 / 134 |
| I Raised the Wrong Fiancé | `i-raised-the-wrong-fianc` | Romance | [DramaCPS](https://dramacps.com/dashboard/materials?source=shortmax&q=662399) | 41 / 125 |
| My Family Sold Me for $7 Million. I Owned Their Building | `my-family-sold-me-for-7-million-i-owned-their-building` | Family, Revenge | [DramaCPS](https://dramacps.com/dashboard/materials?source=shortmax&q=662357) | 56 / 142 |
| Reborn, I Ditched the Faithless Crown Prince | `reborn-i-ditched-the-faithless-crown-prince` | Royal, Romance | [DramaCPS](https://dramacps.com/dashboard/materials?source=shortmax&q=660348) | 60 / 114 |
| Reborn, I Refused to Pay for Her Lies | `reborn-i-refused-to-pay-for-her-lies` | Family, Revenge | [DramaCPS](https://dramacps.com/dashboard/materials?source=shortmax&q=664454) | 53 / 150 |
| Scrap Lace, Broken Vows | `scrap-lace-broken-vows` | Revenge, Romance | [DramaCPS](https://dramacps.com/dashboard/materials?source=shortmax&q=660461) | 39 / 147 |
| The Plus-Size Fiancée Both Brothers Wanted | `the-plus-size-fianc-e-both-brothers-wanted` | Romance | [DramaCPS](https://dramacps.com/dashboard/materials?source=shortmax&q=660385) | 58 / 140 |

- Genre chọn từ nhóm có sẵn của `GENRE` theo synopsis; dòng `GENRE` trong build.py (khoá `<slug>-<id>`) máy nhà thêm.
- Scrap Lace: tên gốc DramaCPS có dấu phẩy toàn góc (`，`), spec đổi thành `, `.
- Poster: cloud không tải được `cover_url` (img.reelhunter.xyz bị chặn) → máy nhà tải, đưa về 3:4, lưu `banner.jpg`.
