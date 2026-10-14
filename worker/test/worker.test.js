import { test } from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

function kv() {
  const m = new Map();
  return { m, get: async (k) => m.get(k) ?? null, put: async (k, v) => { m.set(k, v); } };
}
const env = (over = {}) => ({
  INVITE_CODE: "jCsNUgQuecHY", INVITE_PROGRAM: "RS Boost", SIGNUP_URL: "https://cps.reelshort.com/user/register",
  MAIL_FROM: "Swoonflicks <invite@send.swoonflicks.com>", MAIL_REPLY_TO: "partner@swoonflicks.com",
  ALLOWED_ORIGINS: "https://swoonflicks.com", MAX_PER_EMAIL: "2", MAX_PER_IP: "6", RESEND_API_KEY: "re_test", INVITES: kv(), ...over
});
const ctx = { waitUntil: (p) => p };
const post = (body, origin = "https://swoonflicks.com") => new Request("https://api.swoonflicks.com/invite", {
  method: "POST", headers: { "Content-Type": "application/json", Origin: origin, "CF-Connecting-IP": "1.2.3.4" }, body: JSON.stringify(body) });

let sent = [];
globalThis.fetch = async (url, init) => {
  if (String(url).startsWith("https://api.resend.com/emails")) { sent.push({ headers: init.headers, body: JSON.parse(init.body) }); return new Response(JSON.stringify({ id: "x" }), { status: 200 }); }
  if (String(url).includes("turnstile")) return new Response(JSON.stringify({ success: init.body.get("response") === "good" }), { status: 200 });
  throw new Error("unexpected fetch " + url);
};

test("happy path sends one email with code, 200 ok", async () => {
  sent = []; const e = env();
  const r = await worker.fetch(post({ email: "Creator@Example.com", lang: "es", page: "/es/invite/rs-boost/" }), e, ctx);
  assert.equal(r.status, 200); assert.deepEqual(await r.json(), { ok: true });
  assert.equal(sent.length, 1);
  assert.equal(sent[0].body.to[0], "creator@example.com");
  assert.ok(sent[0].body.html.includes("jCsNUgQuecHY"));
  assert.ok(sent[0].body.subject.startsWith("Tu código"));
  assert.ok(sent[0].headers["Idempotency-Key"].startsWith("invite-"));
  assert.equal(r.headers.get("Access-Control-Allow-Origin"), "https://swoonflicks.com");
  await new Promise((r) => setTimeout(r, 10));
  assert.ok([...e.INVITES.m.keys()].some((k) => k.startsWith("lead:")));
});
test("bad email 400, wrong origin 403, options 204", async () => {
  assert.equal((await worker.fetch(post({ email: "nope" }), env(), ctx)).status, 400);
  assert.equal((await worker.fetch(post({ email: "a@b.co" }, "https://evil.com"), env(), ctx)).status, 403);
  const o = await worker.fetch(new Request("https://api.swoonflicks.com/invite", { method: "OPTIONS", headers: { Origin: "https://swoonflicks.com" } }), env(), ctx);
  assert.equal(o.status, 204);
});
test("rate limit per email: 3rd request in a day is 429", async () => {
  sent = []; const e = env();
  for (let i = 0; i < 2; i++) { assert.equal((await worker.fetch(post({ email: "x@y.co" }), e, ctx)).status, 200); await new Promise((r) => setTimeout(r, 5)); }
  assert.equal((await worker.fetch(post({ email: "x@y.co" }), e, ctx)).status, 429);
  assert.equal(sent.length, 2);
});
test("turnstile enforced when secret set", async () => {
  const e = env({ TURNSTILE_SECRET: "s" });
  assert.equal((await worker.fetch(post({ email: "a@b.co", token: "bad" }), e, ctx)).status, 403);
  assert.equal((await worker.fetch(post({ email: "a@b.co", token: "good" }), e, ctx)).status, 200);
});
test("resend failure -> 502", async () => {
  const f = globalThis.fetch; globalThis.fetch = async () => new Response("boom", { status: 500 });
  try { assert.equal((await worker.fetch(post({ email: "a@b.co" }), env(), ctx)).status, 502); } finally { globalThis.fetch = f; }
});
