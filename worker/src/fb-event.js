// POST /fb-event: site gửi sự kiện, Worker thêm ip / user_agent rồi đẩy sang Meta Conversions API.
// Endpoint + payload: https://developers.facebook.com/docs/marketing-api/conversions-api/using-the-api
// user_data (client_ip_address, client_user_agent, fbp, fbc): https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/customer-information-parameters
// event_id phải trùng eventID pixel gửi để Meta khử trùng. Token: secret META_CAPI_TOKEN, gửi trong body (không đặt trên URL để khỏi lọt log).
const EVENTS = new Set(["PageView", "ViewContent", "Lead", "CompleteRegistration", "Contact", "Subscribe", "Search", "ClickAffiliate"]); // ClickAffiliate = custom event của site
const SITE_RE = /^https:\/\/(www\.)?swoonflicks\.com(\/|$)/;

export async function fbEvent(req, env, ctx) {
  let b;
  try { b = await req.json(); } catch { return [400, { error: "bad_request" }]; }
  const event = String(b.event || ""), eventId = String(b.event_id || "").slice(0, 128), pageUrl = String(b.url || "");
  if (!EVENTS.has(event) || !eventId || !SITE_RE.test(pageUrl)) return [400, { error: "bad_event" }];
  const ip = req.headers.get("CF-Connecting-IP") || "";
  if (env.TT_LIMIT) { const { success } = await env.TT_LIMIT.limit({ key: "fb:" + ip }); if (!success) return [429, { error: "rate_limited" }]; }
  if (!env.META_CAPI_TOKEN) return [202, { ok: true, forwarded: false }];

  const now = Math.floor(Date.now() / 1000), ts = Math.floor(Number(b.timestamp) || now);
  const user_data = { client_ip_address: ip, client_user_agent: req.headers.get("User-Agent") || "" };
  if (b.fbp) user_data.fbp = String(b.fbp).slice(0, 256);
  if (b.fbc) user_data.fbc = String(b.fbc).slice(0, 512);
  const custom_data = b.content_id ? { content_ids: [String(b.content_id).slice(0, 128)], content_type: "product" } : {};
  const payload = {
    data: [{ event_name: event, event_time: Math.abs(ts - now) > 7 * 86400 ? now : ts, event_id: eventId, action_source: "website",
      event_source_url: pageUrl.slice(0, 2048), user_data, custom_data }],
    access_token: env.META_CAPI_TOKEN,
  };
  if (env.META_TEST_CODE) payload.test_event_code = env.META_TEST_CODE;

  const url = `https://graph.facebook.com/${env.META_API_VERSION || "v24.0"}/${env.META_PIXEL_ID}/events`;
  const send = fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) })
    .then((r) => r.json()).then((j) => { if (j.error) console.log("fb-event loi", event, j.error.code, j.error.message); })
    .catch((e) => console.log("fb-event fetch loi", String(e)));
  ctx.waitUntil(send);
  return [200, { ok: true, forwarded: true }];
}
