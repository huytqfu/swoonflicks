import { test } from "node:test";
import assert from "node:assert/strict";
import { buildMail } from "../src/mail.js";

for (const lang of ["en", "es", "pt"]) {
  test(`mail ${lang} contains code, signup link, no raw html in text`, () => {
    const m = buildMail({ lang, program: "RS Boost", code: "ABC123xyz", signup: "https://cps.reelshort.com/user/register", page: "/invite/rs-boost/" });
    assert.ok(m.subject.includes("RS Boost"));
    assert.ok(m.html.includes("ABC123xyz") && m.text.includes("ABC123xyz"));
    assert.ok(m.html.includes("https://cps.reelshort.com/user/register") && m.text.includes("https://cps.reelshort.com/user/register"));
    assert.ok(m.html.includes("https://api.swoonflicks.com/img/mail-logo.png"));
    assert.ok(!/<[a-z]/.test(m.text));
    assert.ok(!/\bfree episodes?\b|\bep(isode)? \d+ free\b/i.test(m.html));  // không lộ số tập free
  });
}
test("escapes html in inputs", () => {
  const m = buildMail({ lang: "en", program: "<b>x</b>", code: "<script>", signup: "https://x.y/?a=1&b=2", page: "/invite/" });
  assert.ok(!m.html.includes("<script>") && m.html.includes("&lt;script&gt;"));
});
