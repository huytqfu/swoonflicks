// POST /tt-event: site gửi sự kiện, Worker thêm ip / user_agent rồi đẩy sang TikTok Events API 2.0.
// Endpoint + khung payload (event_source, event_source_id, data[].user/page/properties, test_event_code):
// https://docs.tealium.com/server-side-connectors/tiktok-events-connector · https://forge-kit.ai/docs/integrations/tiktok
// ttclid nằm ở user.ttclid (Events 2.0): https://www.rudderstack.com/docs/destinations/streaming-destinations/tiktok-ads/cloud-mode/
// event_id phải trùng event_id pixel gửi để TikTok khử trùng. Token: secret TIKTOK_EVENTS_TOKEN (wrangler secret put).
const TT_URL = "https://business-api.tiktok.com/open_api/v1.3/event/track/";
const EVENTS = new Set(["Pageview", "ViewContent", "ClickButton", "CompleteRegistration", "SubmitForm", "Contact", "Subscribe", "Search"]);
const SITE_RE = /^https:\/\/(www\.)?swoonflicks\.com(\/|$)/;

export async function ttEvent(req, env, ctx) {
  let b;
  try { b = await req.json(); } catch { return [400, { error: "bad_request" }]; }
  const event = String(b.event || ""), eventId = String(b.event_id || "").slice(0, 128), pageUrl = String(b.url || "");
  if (!EVENTS.has(event) || !eventId || !SITE_RE.test(pageUrl)) return [400, { error: "bad_event" }];
  const ip = req.headers.get("CF-Connecting-IP") || "";
  if (env.TT_LIMIT) { const { success } = await env.TT_LIMIT.limit({ key: ip }); if (!success) return [429, { error: "rate_limited" }]; }
  if (!env.TIKTOK_EVENTS_TOKEN) return [202, { ok: true, forwarded: false }];

  const now = Math.floor(Date.now() / 1000), ts = Math.floor(Number(b.timestamp) || now);
  const user = { ip, user_agent: req.headers.get("User-Agent") || "" };
  if (b.ttclid) user.ttclid = String(b.ttclid).slice(0, 512);
  if (b.ttp) user.ttp = String(b.ttp).slice(0, 256);
  const page = { url: pageUrl.slice(0, 2048) };
  if (b.referrer) page.referrer = String(b.referrer).slice(0, 2048);
  const properties = b.content_id ? { content_id: String(b.content_id).slice(0, 128), content_type: "product" } : {};
  const payload = {
    event_source: "web",
    event_source_id: env.TIKTOK_PIXEL_ID,
    data: [{ event, event_time: Math.abs(ts - now) > 7 * 86400 ? now : ts, event_id: eventId, user, page, properties }],
  };
  if (env.TIKTOK_TEST_CODE) payload.test_event_code = env.TIKTOK_TEST_CODE;

  const send = fetch(TT_URL, { method: "POST", headers: { "Access-Token": env.TIKTOK_EVENTS_TOKEN, "content-type": "application/json" }, body: JSON.stringify(payload) })
    .then((r) => r.json()).then((j) => { if (j.code !== 0) console.log("tt-event loi", event, j.code, j.message); })
    .catch((e) => console.log("tt-event fetch loi", String(e)));
  ctx.waitUntil(send);
  return [200, { ok: true, forwarded: true }];
}
