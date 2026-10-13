# _src/content — nội dung riêng cho trang phim

Mỗi phim 2 file, tên = slug trang (`/<slug>/`, slug = id phim bỏ đuôi hex, giống `build.py`).

## `<slug>.json` — nội dung hiển thị (build nhúng vào trang + FAQPage JSON-LD)

```json
{
  "intro": "2–3 câu tiếng Anh, giọng Swoonflicks, không chép synopsis của app",
  "why":   ["3–4 bullet: vì sao đáng xem / trope / hợp ai"],
  "faq":   [{"q": "Câu hỏi người xem hay gõ", "a": "Câu trả lời"}]
}
```

- Chữ thường (plain text), không HTML, không markdown. Build tự escape.
- `faq` 4–5 câu. JSON-LD `FAQPage` phải khớp đúng chữ hiển thị.
- Số tập / tập trả phí chỉ ghi khi có trên trang chính thức của app (URL ở file `.seo.json`). Không có thì bỏ hẳn câu đó, không đoán.
- Không hứa xem full miễn phí, không nhắc coin miễn phí hay mã mở khoá.

## `<slug>.seo.json` — meta, không hiển thị

```json
{
  "title": "≤60 ký tự, dùng cho <title> và og:title",
  "description": "≤155 ký tự, dùng cho meta description và og:description",
  "keywords": ["5–8 cụm từ khoá để tham khảo khi viết; không xuất ra meta keywords"],
  "sources": {"episodes": "URL trang app chính thức chứa số tập", "app": "URL trang phim trên app"},
  "checked": "YYYY-MM-DD ngày tra số tập"
}
```

`sources.episodes` = `null` nghĩa là chưa xác minh được số tập; FAQ khi đó không có câu số tập.
Số tập trên app có thể đổi: tra lại theo `checked` trước khi dùng lâu dài.
