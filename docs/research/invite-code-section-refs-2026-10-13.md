# Mục "Invite code" cho swoonflicks.com: khảo partner + đề xuất bố cục

Ngày: 2026-10-13 · Phiên cloud (chỉ nghiên cứu, không sửa repo).
Nguồn: WebSearch/WebFetch. Quote lấy qua công cụ fetch có tóm tắt, **cần mở trình duyệt đối chiếu từng chữ trước khi trích lại công khai.**
Không bịa code, không bịa mức thưởng. Số nào không có link bài cụ thể = "chưa xác minh".

---

## 0. Ba điều phải biết trước khi dựng

1. **Code RS Boost là code của CREATOR, không phải code xem phim.** Form đăng ký RS Boost có ô "Bind invitation code" (https://cps.reelshort.com/user/register). Người mới bind code của mình → mình thành upline. ToS RS Boost mục IV.2: *"If you successfully introduce other users to join this promotion, your ratio of CPS may be raised."* (https://cps.reelshort.com/user/agreement). Tăng bao nhiêu: **chưa xác minh** (ToS chỉ ghi "may be raised").
   → Khách của mục này là **người muốn làm affiliate/creator**, không phải người xem muốn coin. Trang /invite/ thread web đã dựng (nhánh site-v2, code jCsNUgQuecHY) đang đúng hướng này.
2. **DramaCPS không có mã mời** (sếp xác nhận 13/10). Đường duy nhất của DramaCPS là link CPS gốc. ToS DramaCPS mục 7 cấm "unofficial redirects, intermediate pages" chen vào tracking (https://dramacps.com/terms) → link CPS để nguyên, không bọc shortener/redirect của mình.
3. **App ReelShort có ô "Invitation Code" riêng cho người xem** (Profile/Me → Invitation Code → Redeem), theo blog chính thức https://www.reelshort.com/fandom/reelshort-invitation-code-01-25-1a2b555/ (08/10/2026). Bài **không nêu số coin**. Code RS Boost có nhập được vào ô này không: **chưa xác minh**. Đừng ghi lên site là "nhập code này được coin".

---

## 1. Bảng khảo 8 trang/kênh

| # | URL | Ai chạy | Cách trình bày | CTA (quote) | Thưởng trang tự ghi | Disclosure | Đánh giá |
|---|---|---|---|---|---|---|---|
| 1 | https://www.reelshort.com/fandom/reelshort-invitation-code-01-25-1a2b555/ | ReelShort (blog chính thức) | Hướng dẫn 4 bước nhập code, không liệt kê code | n/a | "free bonus coins", không số | n/a | **Link tới trang này** thay vì tự viết hướng dẫn viewer |
| 2 | https://dramapartner.com/en/rsboost-invite-code/ | DramaPartner (bán tool AI recap) | Code RS Boost **giấu sau form email**, 4 bước đăng ký, cảnh báo "cannot be unbound", rồi upsell tool | "Send my invite code →" | "Free ReelShort RS Boost invite code · delivered by email" | Chỉ link footer "Affiliate disclosure" | Đối thủ trực tiếp. Điểm yếu: email gate, không FAQ, không schema, chỉ en/zh |
| 3 | https://shortdramapartner.com/blog/how-to-get-reelshort-invitation-code | "Drama Affiliate Program" (độc lập) | Form email xin code, có FAQ | "Get My Free Invitation Code", "Request Code" | "up to 30%", "$500 to $10,000+ per month" (**không nguồn**) | Gián tiếp ("we earn a small bonus on your activity") | Claim thu nhập không nguồn: **đừng bắt chước** |
| 4 | https://www.wethrift.com/codes/reelshort.com | Wethrift (coupon) | Thẻ "BEST CODE RIGHT NOW" + nút "Copy Code", bảng xếp hạng code, độ tươi, ngày | "Use code [code] to save on your order at ReelShort." | "11%" (số của Wethrift, chưa xác minh) | "We earn no commission and show no ads here." | Mẫu UI nút copy + ngày kiểm tra đáng học |
| 5 | https://linktr.ee/Good.drama | Ẩn danh | ~60 nút, mỗi phim một link reelslink.com/cps | "For more exciting episodes, click the link below" | "Search 76307 on reelshort to get 50 coins" (chưa xác minh) | Không | Mẫu link-in-bio phổ biến, **thiếu disclosure** |
| 6 | https://linktr.ee/reeldrama1 | "Reel Drama 1 Official" | 100+ nút theo phim, đi qua short.inbeidou.ai | "Choose a movie from Collections /ReelShort/GoodShort/DramaBox/" | Không | Không | Như trên |
| 7 | https://linktr.ee/Dramashort | "DramaShort Official" | ~150 nút, 9+ domain redirect, khối "drama codes" không giải thích | "Next part is here! If the link doesn't redirect, please open it in a browser." | Không | Không | Rối, nhiều redirect: không theo |
| 8 | https://fleekio.com/streaming/redeem-dramabox-gift-code/ | Không tác giả | Code che "????", link thiếu | "Copy this code: ????" | "1,000 gifts" (không định nghĩa) | Không | **Trang mồi.** Ví dụ thứ phải tránh |

NetShort: không tìm được trang invite code thật nào; kết quả toàn spam trên subdomain bị chiếm. DramaBox/NetShort: không tìm được trang help chính thức về redeem code.

---

## 2. Luật chính thức áp vào mục này

| Luật | Nguồn | Áp cho swoonflicks |
|---|---|---|
| RS Boost III.2: *"You may upload or disseminate the Advertising Materials and the advertising Links to online media you choose"* | https://cps.reelshort.com/user/agreement | Đăng code/link lên site riêng **không bị cấm** |
| RS Boost III.3(3)(a): cấm tài liệu "fake, fraudulent or misleading"; III.4(2): cấm "dark patterns, fraudulent clicks" | như trên | Không hứa coin/thu nhập. Không nút giả, không đếm ngược giả |
| RS Boost III.3(3)(c): không đổi/che trademark | như trên | Logo ReelShort để nguyên nếu dùng |
| RS Boost III.4(5): không "crawl, deep-link to, or scrape" | như trên | Chỉ dùng link RS Boost tự sinh |
| RS Boost III.5: vi phạm → thu hồi quyền, đóng băng tài khoản và tiền chưa trả | như trên | Rủi ro thật nếu claim lố |
| DramaCPS mục 6: cấm "misleading promotion methods ... or incentivized traffic" trừ khi được duyệt bằng văn bản | https://dramacps.com/terms | Không "xem phim nhận coin" |
| DramaCPS mục 7: cấm "unofficial redirects, intermediate pages" | như trên | Link CPS để nguyên |
| DramaCPS mục 5/9: gian lận → tịch thu toàn bộ hoa hồng chưa trả + truy thu | như trên | |
| FTC: disclosure đặt **sát** khuyến nghị; "Paid link" cạnh link là đủ; nút "buy now" không đủ; disclosure một lần ở trang chủ hay link ẩn trong footer không đủ | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking | Ghi disclosure ngay dưới khối code |
| FTC: luật Mỹ áp dụng nếu nội dung có thể ảnh hưởng người tiêu dùng Mỹ | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | Khán giả chính là Mỹ → áp |

Chưa đọc được: FAQ/campaign rule RS Boost (sau đăng nhập), câu trả lời Help Center DramaCPS (https://dramacps.com/help, nạp động). Hai ToS **không nói gì** về chạy ads, bid từ khoá thương hiệu, coupon site.

---

## 3. Trang /invite/ hiện tại (site-v2, đã merge PR #1)

Đang có: H1 "Invitation codes", 1 thẻ RS Boost: mô tả 1 câu, code `jCsNUgQuecHY`, nút Copy (bắn event CopyInvite), nút "Sign up for RS Boost", disclosure chung ở footer.
Khoảng cách so với đề xuất bên dưới:
- Chưa có các bước đăng ký, cảnh báo "bind xong không gỡ được", FAQ, schema, ngày cập nhật. Thân bài ~100 từ, quá mỏng để lên top.
- Disclosure nằm footer, chưa sát khối code (FTC nói footer không đủ).
- Title "Invitation codes · Swoonflicks" chưa chứa từ khoá "RS Boost invite code" / "ReelShort invitation code".

## 4. Đề xuất bố cục (mobile-first, một cột)

URL: giữ `/invite/` làm trang tổng, thêm `/invite/rs-boost/` làm trang đích SEO (chi tiết từ khoá ở file keyword-invite-code-2026-10-13.md).

```
[Header gọn]  ‹ All dramas
H1: ReelShort RS Boost invite code (updated <ngày kiểm>)
1 câu: "Joining RS Boost as a creator? Paste this code in the 'Bind invitation code' box at sign-up."

┌ THẺ CODE (dính trên màn hình đầu, không cần cuộn) ─────┐
│  RS Boost invitation code                               │
│  [ jCsNUgQuecHY ]   [ Copy ]  → đổi thành "Copied ✓"     │
│  [ Open RS Boost sign-up ]  (link cps.reelshort.com)     │
│  "Last checked: <ngày>"                                  │
│  Disclosure 1 dòng: "This is our referral code. If you   │
│  join with it, we may get a better commission rate from  │
│  ReelShort. It costs you nothing."                       │
└─────────────────────────────────────────────────────────┘

H2: How to use the code (4 bước, có ảnh chụp màn hình form của sếp)
   1 Open cps.reelshort.com → Register
   2 Fill email / password
   3 Paste code in "Bind invitation code"
   4 Verify email, then log in
   ⚠ "A bound code cannot be changed later" (theo dramapartner, nên tự xác nhận trên form)

H2: Who RS Boost is for (2-3 dòng, không số thu nhập)
H2: FAQ (5-6 câu, chữ thật trên trang + FAQPage JSON-LD)
   - Is the RS Boost invite code free?  → Yes. Never pay for a code.
   - Is this the same as the in-app ReelShort invitation code? → No… (link bài chính thức ReelShort)
   - Does DramaCPS need an invite code? → No, DramaCPS has none.
   - Can I change the code after sign-up? …
   - Do I get free coins with this code? → No. (trung thực, chặn hiểu lầm)
H2: Just want to watch? → 3 thẻ phim từ kệ (link nội bộ /<slug>/)
[Footer: disclosure đầy đủ + privacy]
```

Ghi chú UI:
- Code dùng font mono cỡ lớn, có `user-select: all` để bấm giữ là chọn hết (trên mobile nút copy đôi khi bị chặn clipboard).
- Nút Copy giữ event `CopyInvite`; thêm event `ClickSignup` cho nút đăng ký để đo tỉ lệ copy → bấm.
- Không email gate (khác 2 đối thủ): người tìm "invite code" muốn code ngay, đây là lợi thế UX của mình.
- Không hiển thị bất kỳ con số thu nhập/hoa hồng nào.
- Mục DramaCPS (nếu muốn): 1 thẻ nhỏ "DramaCPS doesn't use invite codes, sign up directly" + link CPS/ref gốc nếu sếp có link giới thiệu chính thức (chưa xác minh DramaCPS có chương trình giới thiệu creator).

## 5. Sếp cần cung cấp / kiểm

| Việc | Vì sao |
|---|---|
| Chụp form đăng ký RS Boost (ô "Bind invitation code") | Ảnh bước 3, và xác nhận ô bắt buộc hay tuỳ chọn |
| Trong dashboard RS Boost: xem code mời có trang thống kê người được mời / mức CPS tăng không | IV.2 chỉ ghi "may be raised"; biết số thật mới đáng đầu tư SEO mạnh |
| Xác nhận code `jCsNUgQuecHY` còn đúng (thread web đã đưa vào site) | Tránh đăng code chết |
| Có link giới thiệu creator của DramaCPS không | Nếu không có thì bỏ thẻ DramaCPS khỏi /invite/ |

## 6. Chưa làm / chưa xác minh
- Mức tăng CPS khi mời được người, số coin của invitation code viewer: chưa xác minh.
- Trang TikTok /discover bị chặn fetch; không thấy thread Reddit liên quan.
- Chưa đọc trang Affiliate disclosure của dramapartner (https://dramapartner.com/en/affiliate-disclosure/).
- Không sửa repo; thread web dựng theo bố cục trên nếu sếp đồng ý.
