# Audit chất lượng click: site -> link CPS (17/10/2026)

Câu hỏi: click thật từ người xem có ra tới link CPS sạch không, GA4/pixel có đếm đúng không, và site có khiến bot bấm link CPS hàng loạt không. Chỉ đọc code trên `main` (412e0f6), không chạy site, không đổi code. Dòng tham chiếu là của `_src/` (bản `assets/` giống hệt).

## Tóm tắt

| # | Câu hỏi | Kết luận | Mức chắc |
|---|---|---|---|
| 1 | Mọi chỗ ra link affiliate có bắn sự kiện kèm tên phim? | Có. Mọi `<a>` trỏ CPS đều có `data-aff`, `data-film`, `data-app`, `data-title` (quét toàn bộ `*.html`: không anchor CPS nào thiếu). Tự nhảy hết tập free bắn tay `ClickAffiliate` rồi đợi 150ms. | Đọc code |
| 2 | Link CPS có bị sửa? | Không. `href` là URL CPS gốc, không thêm tham số, không `encodeURI`, không cloak; `t.js` chỉ đọc `a.href`. | Đọc code |
| 3 | Site có khiến bot bấm CPS hàng loạt? | Không có bằng chứng. 508/540 click (94%) 04-14/10 có nguồn `direct`; chỉ 7/540 mang referrer `swoonflicks.com`. | Số liệu DramaCPS + suy luận |

## 1. Sự kiện

- `t.js:133-138`: listener `click` pha capture bắt mọi `a[data-aff]`, gửi `ClickAffiliate` kèm `film`, `title`, `app`, `placement`, `link_url`, `episode`. Sang GA4 là `click_affiliate`, Meta là custom `ClickAffiliate`, TikTok là `ClickButton` (`t.js:72-74`).
- Tự nhảy: `reel.js:156` bắn tay, `reel.js:158` nhảy sau 150ms. Chỉ chạy sau khi khách bấm play (`gest = true` ở `reel.js:56`/`203`) và lướt hết tập free (`reel.js:136`), nên crawler không bấm gì thì không tự nhảy.
- Số anchor CPS: trang một nút `go/*` 2 anchor/trang (poster + nút), trang bio `ig|tt|th|x|fb|yt` 14 anchor/trang, trang phim 1 anchor. Tất cả có `rel="nofollow sponsored noopener"` (`build.py:196,269,283`).

Lỗ hổng đo (đều là **suy luận từ code, chưa đo thực tế**):
- Khách ở múi giờ châu Âu, trống hoặc `Etc/*` (VPN, UTC) chưa bấm Accept thì pixel chưa tải, sự kiện xếp hàng rồi bỏ (`t.js:30-34`, `t.js:114`). Hệ quả: GA4 sẽ ít thấy bot headless (không múi giờ), nhưng cũng mất khách thật dùng VPN chưa chấp nhận cookie.
- Bấm giữa chuột / giữ lâu mở tab mới không sinh `click` nên không đếm (cần thêm `auxclick`).
- Tự nhảy chỉ đợi 150ms; nếu gtag.js/pixel chưa tải xong lúc khách tới màn khoá thì beacon có thể mất. Hiếm vì khách đã xem tập free.
- Phải kiểm trong GA4 DebugView xem có `click_affiliate` thật ở site live không; repo không chứng minh được.

## 2. Link CPS

- 11 mã `r.reelsgo.tv/<code>` và 3 link `reelslink.com/cps/<code>` (RS Boost) trong HTML đều khớp mã trong `ke/shelf.csv` của repo `claude-work-brain` (đối chiếu 11 mã DramaCPS).
- Không có `referrerpolicy` hay `<meta name="referrer">`, nên trình duyệt dùng mặc định `strict-origin-when-cross-origin`: DramaCPS thấy referrer `swoonflicks.com` nếu khách bấm từ site. Đây là cách để tách click từ site khỏi click từ link thô.
- Trình duyệt trong app (IG, TikTok, Threads) mất cookie/phiên khi sang store là hành vi của app, **repo không kiểm chứng được**.

## 3. Bot

Số từ `claude-work-brain/side-hustle/short-drama/ke/evidence-zero-order-2026-10-16/dcps-daily-detailed-stats.json`, cộng 04-14/10:

| Nguồn (referrer) | Click |
|---|---|
| direct | 508 |
| m.facebook.com / l.facebook.com / facebook.com | 8 / 6 / 3 |
| **swoonflicks.com** | **7** |
| youtube.com / t.co / reelmuan.co | 3 / 3 / 2 |
| Tổng | 540 |

(File `zero-order-2026-10-16.md` ghi direct ~486; JSON cho 508, tao lấy JSON.)

- Hub swoonflicks.com mới lên 13/10 (`HUB-ATA-DRAMA.md` mục 5 #9), trong khi cụm bất thường đã có từ 05-06/10 (88 click một link ngày 05/10). Cụm đó không thể đến từ HTML của site.
- Suy luận (chưa chứng minh được, dashboard không có IP): link CPS thô dán ở caption/comment các nền (FB comment, X, YT mô tả) bị trình quét link của nền hoặc tool xem trước gọi, nên ra `direct` + thiết bị `other` + US.
- Chặn rẻ cho phần HTML của site, **chưa áp**, vì nút ra CPS trực tiếp là luật của sếp và không có bằng chứng bot đến từ site: (a) `noindex,nofollow` thay `noindex,follow` cho `go/*`, bio và hub (`build.py:109`); (b) gắn `href` CPS lúc `pointerdown`/`focus` thay vì có sẵn trong HTML. Cả hai không ngăn được trình quét link thô ở mạng xã hội. (b) hỏng với người tắt JS và làm mất "copy link"; không đáng làm trước khi có số.

## Việc nên làm tiếp (không phải code)
1. Xem GA4 DebugView / Realtime ở site live: có `click_affiliate` kèm `film` khi tự bấm trên điện thoại thật.
2. So `click_affiliate` GA4 với click DramaCPS của cùng ngày từ 16/10 trở đi (GA4 mới đo từ 16/10).
3. Với link thô ở caption/comment: thử đổi sang link qua `ig.|tt.swoonflicks.com` hoặc trang `go/*` để click đi qua site và có referrer; so lại tỷ lệ `other`.
