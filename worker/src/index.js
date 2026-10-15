// swoonflicks-invite: nhận POST {email, lang, program, page, token} từ form trên swoonflicks.com,
// kiểm Turnstile, chặn spam bằng KV, gửi mã mời qua Resend (https://resend.com/docs/api-reference/emails/send-email).
// Trả: 200 {ok:true} · 400 {error:"bad_email"|"bad_request"} · 403 {error:"turnstile"} · 429 {error:"rate_limited"} · 502 {error:"send_failed"}
import { buildMail } from "./mail.js";
import { MAIL_LOGO_B64 } from "./mail-logo.js";
import { ttEvent } from "./tt-event.js";

const MAIL_LOGO = Uint8Array.from(atob(MAIL_LOGO_B64), (c) => c.charCodeAt(0));

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const LANGS = new Set(["en", "es", "pt"]);

export default {
  async fetch(req, env, ctx) {
    const origin = req.headers.get("Origin") || "";
    const allowed = (env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
    const cors = corsHeaders(origin, allowed);
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    const url = new URL(req.url);
    if (url.pathname === "/img/mail-logo.png") return new Response(MAIL_LOGO, { headers: { "content-type": "image/png", "cache-control": "public, max-age=86400" } });
    if (url.pathname === "/health") return json({ ok: true }, 200, cors);
    if (req.method === "POST" && url.pathname === "/tt-event") {
      if (!allowed.includes(origin)) return json({ error: "origin" }, 403, cors);
      const [st, out] = await ttEvent(req, env, ctx);
      return json(out, st, cors);
    }
    if (req.method !== "POST" || url.pathname !== "/invite") return json({ error: "not_found" }, 404, cors);
    if (allowed.length && !allowed.includes(origin)) return json({ error: "origin" }, 403, cors);

    let body;
    try { body = await req.json(); } catch { return json({ error: "bad_request" }, 400, cors); }
    const email = String(body.email || "").trim().toLowerCase();
    if (!EMAIL_RE.test(email) || email.length > 254) return json({ error: "bad_email" }, 400, cors);
    const lang = LANGS.has(body.lang) ? body.lang : "en";
    const page = /^\/[a-z0-9\-\/]*$/.test(body.page || "") ? body.page : "/invite/";
    const ip = req.headers.get("CF-Connecting-IP") || "0.0.0.0";

    // 1. Turnstile (bỏ qua khi chưa đặt secret, để thử nghiệm)
    if (env.TURNSTILE_SECRET) {
      const ok = await verifyTurnstile(env.TURNSTILE_SECRET, body.token, ip);
      if (!ok) return json({ error: "turnstile" }, 403, cors);
    }

    // 2. Giới hạn theo email + IP trong 24h (KV; không có binding thì bỏ qua)
    const kv = env.INVITES;
    const maxE = +env.MAX_PER_EMAIL || 2, maxI = +env.MAX_PER_IP || 6;
    if (kv) {
      const [ke, ki] = [`rl:e:${await sha(email)}`, `rl:i:${await sha(ip)}`];
      const [ce, ci] = await Promise.all([kv.get(ke), kv.get(ki)]);
      if ((+ce || 0) >= maxE || (+ci || 0) >= maxI) return json({ error: "rate_limited" }, 429, cors);
      ctx.waitUntil(Promise.all([
        kv.put(ke, String((+ce || 0) + 1), { expirationTtl: 86400 }),
        kv.put(ki, String((+ci || 0) + 1), { expirationTtl: 86400 })
      ]));
    }

    // 3. Gửi mail qua Resend
    const program = env.INVITE_PROGRAM || "RS Boost";
    const mail = buildMail({ lang, program, code: env.INVITE_CODE, signup: env.SIGNUP_URL, page });
    const day = new Date().toISOString().slice(0, 10);
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
        "Idempotency-Key": `invite-${day}-${await sha(email + lang)}`   // cùng người, cùng ngày, cùng ngôn ngữ = 1 mail
      },
      body: JSON.stringify({
        from: env.MAIL_FROM, to: [email], reply_to: env.MAIL_REPLY_TO || undefined,
        subject: mail.subject, html: mail.html, text: mail.text,
        tags: [{ name: "kind", value: "invite" }, { name: "lang", value: lang }]
      })
    });
    if (!res.ok) {
      console.log("resend error", res.status, (await res.text()).slice(0, 300));
      return json({ error: "send_failed" }, 502, cors);
    }

    // 4. Lưu người đã xin mã (để sếp xem danh sách / trả lời; xem README mục "Xem danh sách")
    if (kv) ctx.waitUntil(kv.put(`lead:${new Date().toISOString()}:${Math.random().toString(36).slice(2, 8)}`,
      JSON.stringify({ email, lang, page, country: req.cf?.country || "" })));
    return json({ ok: true }, 200, cors);
  }
};

async function verifyTurnstile(secret, token, ip) {
  if (!token) return false;
  const fd = new FormData();
  fd.append("secret", secret); fd.append("response", token); fd.append("remoteip", ip);
  try {
    const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: fd });
    const j = await r.json();
    return !!j.success;
  } catch { return false; }
}

async function sha(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].slice(0, 12).map((x) => x.toString(16).padStart(2, "0")).join("");
}

function corsHeaders(origin, allowed) {
  const h = { "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Max-Age": "86400", "Cache-Control": "no-store" };
  if (!allowed.length || allowed.includes(origin)) h["Access-Control-Allow-Origin"] = origin || "*";
  return h;
}

function json(obj, status, extra) {
  return new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", ...extra } });
}
