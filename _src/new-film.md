# Thêm phim mới: `new_film.py`

Sinh `_src/content/<slug>.json` + `<slug>.seo.json` đúng schema từ 1 file spec, và tự lọc luật nội dung. Không cần build, chạy được trên cloud.

```
python3 _src/new_film.py spec.json            # kiểm + in kết quả, không ghi
python3 _src/new_film.py spec.json --write    # ghi (file đã có: chỉ bổ sung khoá còn thiếu / đang null, không đè)
python3 _src/new_film.py --check [slug ...]   # lint file content đang có, synopsis lấy từ trang đã build
python3 _src/tests/new_film_test.py           # test trên synopsis mẫu
```

## Spec (mẫu: `_src/new-film.sample.json`)

| Khoá | Bắt buộc | Dùng vào |
|---|---|---|
| `slug`, `title`, `synopsis` (gốc, chép nguyên) | có | tên file, FAQ, seo, căn cứ chống bịa |
| `network` | nên có | thêm vào bộ lọc tên network |
| `genre` | nên có | keywords, mô tả seo tự sinh; dòng GENRE cho build.py |
| `sources.episodes`, `sources.app` | không | URL trang phim chính thức (phải là trang cụ thể, không phải trang chủ). Không có thì để `null` |
| `sources.note` | không | ghi chú nguồn |
| `seo_title`, `seo_description` | không | thiếu thì tự sinh: `<title>: Where to Watch` (≤60), câu đầu synopsis + `Where to watch.` (≤155) |
| `intro`, `why`, `faq` | không | chữ người viết; thiếu thì bỏ trống (build vẫn chạy). Script **không** viết hộ |
| `about` | không | đáp án "What is … about?"; thiếu thì lấy tối đa 3 câu đầu synopsis (bỏ câu cụt "…") |
| `keywords` | không | thêm vào keywords tự sinh |
| `drama_url`, `app_home_url`, `trailer_url`, `poster` | không | không ghi vào content; script in ra **việc máy nhà** (shelf.csv, GENRE, ads_links, R2, banner.jpg) |

## Luật lọc (lỗi thì không ghi)

- Chữ "free"; tên network (danh sách trong script + `network` của spec); số tập (`48 episodes`, `episode 3`, `dozens of episodes`).
- Từ vũ khí: sword, blade, dagger, knife, gun, pistol, rifle, bomb… (trừ khi nằm trong tên phim).
- Chống bịa: tên riêng viết hoa giữa câu và mọi con số phải có trong synopsis, tên phim hoặc tên phim khác trên site. Đây là lọc thô: diễn giải sai ý (vd đổi động cơ nhân vật) script không bắt được, người duyệt vẫn phải đọc.
- `seo.title` ≤60 và không có chữ episode; `seo.description` ≤155.
- Keywords có chữ cấm: lỗi khi sinh mới; với file cũ (`--check`) chỉ cảnh báo, vì build không đọc keywords và khách không thấy.
