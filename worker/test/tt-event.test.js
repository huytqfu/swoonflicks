import { test } from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

const env = (over = {}) => ({ ALLOWED_ORIGINS: "https://swoonflicks.com,https://www.swoonflicks.com", TIKTOK_PIXEL_ID: "PIX", ...over });
const ctx = { waitUntil: (p) => p };
const post = (body, origin = "https://swoonflicks.com") => new Request("https://api.swoonflicks.com/tt-event", {
  method: "POST", headers: { "Content-Type": "application/json", Origin: origin, "CF-Connecting-IP": "1.2.3.4", "User-Agent": "UA" }, body: JSON.stringify(body) });
const ev = { event: "ViewContent", event_id: "e1", url: "https://swoonflicks.com/watch/x/", content_id: "x", ttclid: "C1", timestamp: Math.floor(Date.now() / 1000) };

let sent = [];
globalThis.fetch = async (url, init) => { sent.push({ url: String(url), headers: init.headers, body: JSON.parse(init.body) }); return new Response(JSON.stringify({ code: 0 }), { status: 200 }); };

test("tt-event forwards with ip, ua, ttclid, same event_id", async () => {
  sent = [];
  const r = await worker.fetch(post(ev), env({ TIKTOK_EVENTS_TOKEN: "tok" }), ctx);
  assert.equal(r.status, 200);
  await new Promise((r) => setTimeout(r, 10));
  assert.equal(sent.length, 1);
  assert.equal(sent[0].url, "https://business-api.tiktok.com/open_api/v1.3/event/track/");
  assert.equal(sent[0].headers["Access-Token"], "tok");
  const d = sent[0].body.data[0];
  assert.equal(sent[0].body.event_source_id, "PIX");
  assert.deepEqual([d.event, d.event_id, d.user.ip, d.user.user_agent, d.user.ttclid, d.page.url], ["ViewContent", "e1", "1.2.3.4", "UA", "C1", ev.url]);
});
test("tt-event: wrong origin 403, bad event 400, foreign url 400, no token 202, rate limit 429", async () => {
  sent = [];
  assert.equal((await worker.fetch(post(ev, "https://evil.com"), env(), ctx)).status, 403);
  assert.equal((await worker.fetch(post({ ...ev, event: "Purchase" }), env(), ctx)).status, 400);
  assert.equal((await worker.fetch(post({ ...ev, url: "https://evil.com/" }), env(), ctx)).status, 400);
  assert.equal((await worker.fetch(post(ev), env(), ctx)).status, 202);
  assert.equal((await worker.fetch(post(ev), env({ TIKTOK_EVENTS_TOKEN: "t", TT_LIMIT: { limit: async () => ({ success: false }) } }), ctx)).status, 429);
  assert.equal(sent.length, 0);
});
