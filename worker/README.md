# Worker "xin mã mời qua email" (api.swoonflicks.com/invite)

Form trên `/invite/`, `/invite/rs-boost/`, `/es/invite/rs-boost/`, `/pt/invite/rs-boost/` gửi email người xin → Worker này kiểm Turnstile,
chặn spam bằng KV, rồi gửi mã RS Boost qua Resend. Mã **không** còn in trong HTML (build.py chỉ in form khi `_src/config.json` → `gate.endpoint` có giá trị).

Lắp ráp từ: [Cloudflare Workers](https://developers.cloudflare.com/workers/) (free: 100.000 request/ngày), [Workers KV](https://developers.cloudflare.com/kv/platform/pricing/) (free: 100.000 đọc + 1.000 ghi/ngày),
[Turnstile](https://developers.cloudflare.com/turnstile/plans/) (free, 20 widget), [Resend](https://resend.com/pricing) (free: 3.000 mail/tháng, 100/ngày, 3 domain).
Không dùng MailChannels: API free cho Workers đã tắt 30/06/2024 ([thông báo](https://blog.mailchannels.com/important-update-mailchannels-email-sending-api-for-cloudflare-workers-to-be-terminated/)).

## Sếp cần làm, theo thứ tự (khoảng 20 phút, chưa tính chờ DNS)

Cần: tài khoản Cloudflare (đã có, zone swoonflicks.com), Node 18+ trên máy nhà, tài khoản Resend (tạo mới, free).

1. **Resend → Domains → Add domain**: nhập `send.swoonflicks.com` (Resend khuyên gửi từ subdomain). Resend hiện 3 record; thêm vào Cloudflare DNS (thread Domain giữ Cloudflare):
   - MX `send` → `feedback-smtp.<region>.amazonses.com`, priority 10
   - TXT `send` → `v=spf1 include:amazonses.com ~all`
   - TXT `resend._domainkey` → `p=...` (DKIM), **Proxy: DNS only**
   Nguồn record: https://resend.com/docs/dashboard/domains/cloudflare. Bấm Verify trên Resend, chờ xanh (thường vài phút, DNS có thể tới vài giờ).
   Khuyến nghị thêm TXT `_dmarc` → `v=DMARC1; p=none; rua=mailto:admin@swoonflicks.com` cho deliverability (chưa xác minh Resend bắt buộc).
2. **Resend → API Keys → Create**: quyền "Sending access", domain `send.swoonflicks.com`. Chép key (`re_...`), chỉ dán vào bước 6. Không dán vào chat/repo/OneDrive.
3. **Cloudflare → Turnstile → Add widget**: hostname `swoonflicks.com`, mode Managed. Được **Site key** (công khai) + **Secret key** (bí mật).
   - Site key dán vào `_src/config.json` → `"gate": {"turnstile": "0x4AAAA..."}` rồi build lại site.
   - Secret key dùng ở bước 6.
4. Trên máy nhà: `cd hub/site/worker` (bản sao repo swoonflicks), `npm install`, `npx wrangler login` (mở trình duyệt, bấm Allow).
5. `npx wrangler kv namespace create INVITES` → in ra `id = "..."`; dán vào `wrangler.toml` chỗ `REPLACE_WITH_KV_NAMESPACE_ID`.
6. Đặt bí mật (gõ xong Enter, dán key, Enter):
   ```
   npx wrangler secret put RESEND_API_KEY
   npx wrangler secret put TURNSTILE_SECRET
   ```
7. `npx wrangler deploy` → Worker chạy ở `https://api.swoonflicks.com` (Cloudflare tự tạo DNS + cert cho custom domain vì zone đã ở Cloudflare,
   nguồn https://developers.cloudflare.com/workers/configuration/routing/custom-domains/). Kiểm: mở `https://api.swoonflicks.com/health` phải ra `{"ok":true}`.
8. Thử thật: mở trang `/invite/rs-boost/` bản staging, nhập Gmail của sếp, bấm gửi, xem mail tới (kể cả thư mục spam). Resend → Emails thấy log từng mail.

Thứ tự deploy site: Worker lên trước (bước 7), rồi mới "Go deploy" site; nếu site lên trước, form báo lỗi "Something went wrong" cho tới khi Worker có.

## Tuỳ chỉnh (trong `wrangler.toml`, không cần sửa code)

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `INVITE_CODE` | mã RS Boost hiện tại | Mã gửi đi. Đổi mã = sửa đây + `wrangler deploy`, không cần build site |
| `MAIL_FROM` | `Swoonflicks <invite@send.swoonflicks.com>` | Phải thuộc domain đã verify trên Resend |
| `MAIL_REPLY_TO` | `partner@swoonflicks.com` | Người xin bấm Reply thì về Gmail sếp (forward đã có) |
| `ALLOWED_ORIGINS` | swoonflicks.com, www | Trang nào được gọi API |
| `MAX_PER_EMAIL` / `MAX_PER_IP` | 2 / 6 mỗi 24h | Chống spam; quá thì form báo "đã xin hôm nay" |

Chữ trong email: `src/mail.js` (EN/ES/PT). Bản EN–VI để duyệt: `docs/invite-email-gate/email-copy.md`.

## Xem danh sách người đã xin mã

Mỗi lần gửi thành công, Worker ghi 1 key `lead:<thời điểm>:<id>` = `{"email","lang","page","country"}` vào KV (không hết hạn).
```
npx wrangler kv key list --binding INVITES --prefix lead: | more
npx wrangler kv key get --binding INVITES "lead:2026-10-15T03:00:00.000Z:abc123"
```
Xoá theo yêu cầu người dùng: `npx wrangler kv key delete --binding INVITES "<key>"`. Trang /privacy/ đã ghi mục "Invite code emails".

## Chạy thử tại máy

`npm test` (9 test: template 3 ngữ, CORS, giới hạn, Turnstile, lỗi Resend; không cần mạng).
`npx wrangler dev` + `.dev.vars` (chép từ `.dev.vars.example`) để chạy local; form trên site trỏ tới `http://localhost:8787/invite` nếu muốn thử end-to-end.

## Rủi ro đã biết

- Mã vẫn lộ được: ai cũng xin được, và mã vẫn nằm trong lịch sử git/trang cũ đã index. Cổng email là cảm giác "được mời riêng" + gom email, không phải bảo mật.
- Deliverability: domain mới gửi, chưa có uy tín. Giữ DKIM/SPF/DMARC đủ, gửi ít, nội dung không hứa tiền. Mail có thể vào Promotions của Gmail.
- Free Resend 100 mail/ngày: vượt thì Worker trả 502, form báo lỗi. Resend dashboard có cảnh báo.
- Turnstile để trống (`gate.turnstile` rỗng) thì Worker vẫn nhận form nhưng chỉ còn giới hạn IP/email chống spam. Nên bật trước khi chạy ads vào trang này.
