# Cổng email cho mã mời RS Boost (2026-10-14)

Sếp Huy 14/10 09:31: "về mã giới thiệu tao muốn làm cơ chế điền mail vào và gửi qua mail cho nó để thể hiện là mã giới thiệu này quý lắm... y chang kiểu drama partner đang làm".

## Drama Partner làm thế nào (đã xem lại 14/10, https://dramapartner.com/en/rsboost-invite-code/)
- Tiêu đề khối: "Where should we send your RS Boost starter kit?". Hứa: "You'll receive the invitation code, the official registration link, and a short setup checklist in one automatic email."
- Form: ô Email (+ ô Company), nút "Send my invite code →". Dòng tin cậy: "One requested email. No newsletter, no password request, and you can use the guide without registering."
- Không double opt-in, không nói gì về xác nhận sau khi bấm. Mã gọi là "Free", không nói "exclusive".
→ Mình làm giống phần lõi (1 email, mã + link đăng ký + checklist, không newsletter), thêm nhãn "By request only" và câu "We send the code personally" để ra cảm giác được mời riêng; bỏ ô Company (thừa, giảm tỉ lệ điền).

## So phương án nhận form + gửi mail (site tĩnh GitHub Pages, DNS trên Cloudflare)

| Phương án | Chi phí thật (nguồn) | Sếp phải làm | Rủi ro |
|---|---|---|---|
| **A. Cloudflare Worker + Resend + Turnstile + KV (CHỌN)** | Workers free 100.000 req/ngày ([pricing](https://developers.cloudflare.com/workers/platform/pricing/)); KV free 1.000 ghi/ngày ([pricing](https://developers.cloudflare.com/kv/platform/pricing/)); Turnstile free 20 widget ([plans](https://developers.cloudflare.com/turnstile/plans/)); Resend free 3.000 mail/tháng, 100/ngày, 3 domain ([pricing](https://resend.com/pricing)), Pro $20/tháng 50.000 mail | Tạo tài khoản Resend, 3 DNS record, 1 API key, 1 widget Turnstile, chạy 3 lệnh wrangler (worker/README.md) | Vượt 100 mail/ngày thì form lỗi; domain gửi mới, dễ vào Promotions |
| B. Cloudflare Email Service (gửi từ Worker, cùng nhà) | Chỉ trên Workers Paid $5/tháng; 3.000 mail/tháng kèm, thêm $0,35/1.000 ([pricing](https://developers.cloudflare.com/email-service/platform/pricing/)); Email Sending đang beta ([docs](https://developers.cloudflare.com/email-service/)) | Như A nhưng không cần Resend; mất $5/tháng | Beta; tốn tiền ngay cả khi 0 lead |
| C. Brevo form + automation (không code) | Free 300 mail/ngày ([pricing](https://www.brevo.com/pricing/)); trang pricing không hiện giá Starter, gỡ logo Brevo là tính năng trả phí → **chưa xác minh** automation có trong free | Tạo tài khoản, dựng form + workflow trên Brevo, nhúng iframe/script vào trang | Form mang logo Brevo, không theo brand; mail "Brevo" dễ bị coi là newsletter |
| D. Formspree | Free 50 submission/tháng, **không có autoresponse** (chỉ gói trả phí) ([plans](https://formspree.io/plans)) | – | Không gửi được mã về cho người xin → loại |
| E. MailChannels free cho Workers | Đã tắt 30/06/2024 ([thông báo](https://blog.mailchannels.com/important-update-mailchannels-email-sending-api-for-cloudflare-workers-to-be-terminated/)) | – | Loại |

Vì sao A: $0 khi chưa có lead, brand tự vẽ 100%, domain đã ở Cloudflare nên api.swoonflicks.com tự có DNS + cert, Turnstile chặn bot miễn phí, mã đổi được trong 1 biến không cần build lại site.

## Những gì đã build (nhánh này)
- `_src/build.py` + `site.css`: khối code → form "By request only" (EN/ES/PT), trạng thái gửi/đã gửi/lỗi/đã xin hôm nay; JS gọi Worker; event `RequestInvite`; Turnstile chỉ nạp khi có site key. `window.SF` giờ chỉ còn ID tracking (trước đây in cả config "invite" ra mọi trang → mã lộ trong HTML dù giấu khối code).
- `_src/config.json` → `gate.endpoint` (api.swoonflicks.com/invite), `gate.turnstile` (trống, sếp dán site key). Xoá endpoint = quay về hiện mã như cũ.
- `_src/guides/rs-boost-invite-code*.json` + `how-to-join-rs-boost.json`: bỏ mọi câu "shown here, no email"; thêm FAQ "Why by email" / "How fast" (SEO vẫn đủ chữ; mã không còn trong HTML).
- Privacy: mục "Invite code emails".
- `worker/`: Worker + template mail 3 ngữ + 9 test + README cắm key.

## Chưa làm / chờ sếp
- Chưa deploy Worker, chưa có tài khoản Resend/Turnstile (cần sếp, xem worker/README.md).
- Chưa build site thật (build chạy trên máy nhà); preview ở docs/invite-email-gate/preview-*.png render từ build.py với dữ liệu phim rỗng.
- Chưa test deliverability thật (Gmail/Outlook). Chưa có double opt-in (Drama Partner cũng không; thêm bước xác nhận chỉ làm mất người).
