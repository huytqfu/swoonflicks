/* Player lướt dọc trang phim (build copy sang /assets/reel.js). Mỗi .sl là 1 màn; .fr = tập có video, .lk.st = tập free chưa có nguồn,
   .gate = màn khoá (tập trả phí đầu), .info = giới thiệu.
   - Vào màn tập free: lần đầu bấm play, sau đó lướt tới đâu tự phát tới đó; chỉ 1 video sống 1 lúc.
   - Hết video tự lướt sang tập kế; đã bấm xem và lướt hết tập free rồi lướt tiếp tới màn trả phí đầu thì nhảy thẳng link app, không đếm ngược (sếp 14/10 02:28).
     Chưa xem hết tập free (hoặc phim không có tập nào phát được) thì màn khoá chỉ đứng yên với nút, không tự nhảy (sếp 15/10).
   - Ra link app (tự nhảy, nút, ô tập trong lưới) thì nhớ tập đó; khách quay lại site thì nhảy về màn khoá, hiện "Continue Episode N on <app>".
   - Nguồn: yt = Shorts kênh mình (API, đọc được tiến độ + hết video); rs = iframe chính chủ RS Boost (không đọc được gì, khách tự lướt).
   - Sự kiện qua SFT (t.js): VideoPlay, VideoProgress (chỉ YouTube đọc được), ClickAffiliate (t.js tự bắt a[data-aff]; tự nhảy bắn tay, placement auto). */
(function (W, D) {
  var B = D.body.dataset, feed = D.querySelector('.rl'), S = [].slice.call(D.querySelectorAll('.rl > .sl')), ct = D.querySelector('.rt .ct'),
    gate = D.querySelector('.sl.gate'), dlg = D.querySelector('.eps'), link = gate && gate.querySelector('.unl'),
    act = null, gest = false, hold = false, done = false, FR = D.querySelectorAll('.rl > .sl.fr'), lastFr = FR[FR.length - 1], P = null, cur = '', marks = {}, tick, KEY = 'sf_cont',
    RM = W.matchMedia && matchMedia('(prefers-reduced-motion:reduce)').matches;
  if (!feed) return;
  function T(n, p) { if (W.SFT) SFT.track(n, Object.assign({ film: B.film, title: B.title, app: B.app }, p || {})) }
  function go(s, instant) { if (s) feed.scrollTo({ top: s.offsetTop, behavior: instant || RM ? 'auto' : 'smooth' }) }

  // ---- phát video ----
  function stop(s) {
    clearInterval(tick);
    if (P && P.destroy) { try { P.destroy() } catch (e) {} }
    P = null;
    if (!s) return;
    s.classList.remove('on-air');
    [].forEach.call(s.querySelectorAll('.stg iframe,.stg .vh,.stg .err'), function (x) { x.remove() });
  }
  function ytApi(cb) {
    if (W.YT && YT.Player) return cb();
    var prev = W.onYouTubeIframeAPIReady;
    W.onYouTubeIframeAPIReady = function () { if (prev) prev(); cb() };
    if (!D.querySelector('script[src*="iframe_api"]')) {
      var x = D.createElement('script'); x.src = 'https://www.youtube.com/iframe_api'; x.onerror = function () { fail(act) }; D.head.appendChild(x);
    }
  }
  function fail(s) {
    if (!s || !s.classList.contains('fr')) return;
    stop(s);
    var p = D.createElement('p'); p.className = 'err';
    p.style.cssText = 'position:absolute;left:16px;right:16px;bottom:90px;text-align:center;color:#fff;font:600 14px system-ui;text-shadow:0 1px 4px #000';
    p.innerHTML = 'Could not load this episode. <button type="button" style="color:inherit;background:none;border:0;text-decoration:underline;font:inherit;min-height:44px">Retry</button>';
    p.querySelector('button').onclick = function () { play(s) };
    s.querySelector('.stg').appendChild(p);
  }
  function play(s) {
    gest = true;
    stop(s);
    var k = s.dataset.k, v = s.dataset.v, ep = s.dataset.ep, stg = s.querySelector('.stg');
    cur = v; s.classList.add('on-air');
    if (k === 'yt') {
      var h = D.createElement('div'); h.className = 'vh'; stg.appendChild(h);
      ytApi(function () {
        if (act !== s) return;
        P = new YT.Player(h, { host: 'https://www.youtube-nocookie.com', videoId: v,
          playerVars: { autoplay: 1, playsinline: 1, rel: 0, modestbranding: 1 },
          events: {
            onReady: function (e) { var f = e.target.getIframe(); f.title = B.title + ' episode ' + ep; e.target.playVideo() },
            onError: function () { fail(s) },
            onStateChange: function (x) {
              if (x.data === 1) {
                if (!marks[v + 'p']) { marks[v + 'p'] = 1; T('VideoPlay', { video_id: v, episode: +ep, platform: 'youtube' }) }
                clearInterval(tick);
                tick = setInterval(function () {
                  if (!P || !P.getDuration) return;
                  var d = P.getDuration(), t = P.getCurrentTime(); if (!d) return;
                  [25, 50, 75, 95].forEach(function (m) {
                    if (!marks[v + m] && t / d * 100 >= m) { marks[v + m] = 1; T('VideoProgress', { video_id: v, episode: +ep, percent: m, platform: 'youtube' }) }
                  });
                }, 1000);
              } else clearInterval(tick);
              if (x.data === 0) next(s);
            } } });
      });
    } else {
      // rs: iframe chính chủ RS Boost (url có cps_id + code của sếp); khách bấm play trong khung, không đọc được tiến độ nên không bắn VideoPlay
      if (!/^https:\/\/www\.reelshort\.com\//.test(v)) return fail(s);
      var f = D.createElement('iframe');
      f.src = v;
      f.title = B.title + ' episode ' + ep; f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen'; f.setAttribute('allowfullscreen', '');
      stg.appendChild(f);
    }
  }
  function next(s) {
    var n = S[S.indexOf(s) + 1];
    go(n);
  }

  // ---- màn đang xem ----
  function activate(s) {
    if (act === s) return;
    var prev = act; act = s; stop(prev);
    D.body.classList.toggle('at-info', s.classList.contains('info'));
    var n = s.dataset.ep;
    ct.textContent = n && s.classList.contains('fr') ? 'EP ' + n : '';  // không lộ tổng / số tập free (sếp 15/10)
    if (s === lastFr && gest) done = true;  // đã bấm xem và lướt tới tập free cuối
    if (s !== gate) hold = false; else if (!hold && done && !D.querySelector('.sl.st')) jump();
    if (s.classList.contains('fr') && gest) play(s);
  }
  if ('IntersectionObserver' in W) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (x) { if (x.isIntersecting) activate(x.target) }) }, { root: feed, threshold: 0.6 });
    S.forEach(function (s) { io.observe(s) });
  }
  S.forEach(function (s) { var b = s.querySelector('.play'); if (b) b.onclick = function () { act = s; play(s) } });

  // hết tập free: chạm màn trả phí đầu là nhảy thẳng link CPS gốc (sếp 14/10 02:28: không đếm ngược, không chờ).
  // Khách quay lại site thì đứng ở màn này với dòng "Continue Episode N on <app>" (hold), lướt ra rồi vào lại mới nhảy tiếp.
  function jump() {
    if (!link) return;
    hold = true;
    T('ClickAffiliate', { placement: 'auto', link_url: link.href, episode: +link.dataset.ep || undefined });
    remember(link.dataset.ep);
    setTimeout(function () { location.href = link.href }, 150);
  }

  // ---- nhớ tập đã ra app, quay lại thì nói rõ đang xem tiếp ở app nào ----
  function remember(ep) { try { localStorage.setItem(KEY, JSON.stringify({ film: B.film, ep: ep || '', t: Date.now() })) } catch (e) {} }
  D.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-aff]');
    if (a && a.dataset.film === B.film) remember(a.dataset.ep);
  }, true);
  function back(jump) {
    var c; try { c = JSON.parse(localStorage.getItem(KEY) || 'null') } catch (e) {}
    if (!c || c.film !== B.film || Date.now() - c.t > 7 * 864e5 || !gate) return;
    hold = true;
    // tập free chưa có nguồn (màn .st) thì hiện ở chính màn đó; tập trả phí thì đổi số tập của màn khoá
    var ep = +c.ep, at = gate;
    S.forEach(function (s) { if (s.classList.contains('st') && ep >= +s.dataset.ep && ep <= +s.dataset.last) at = s });
    if (at === gate && ep && ep >= +gate.dataset.ep) {
      gate.dataset.ep = ep; link.dataset.ep = ep;
    }
    [].forEach.call(D.querySelectorAll('.cont'), function (x) { x.hidden = true });
    var box = at.querySelector('.cont');
    box.textContent = (ep ? 'Continue Episode ' + ep : 'Continue watching') + ' on ' + B.app;
    box.hidden = false;
    if (jump) go(at, true);
  }
  back(true);
  W.addEventListener('pageshow', function (e) { if (e.persisted) back(true) });
  D.addEventListener('visibilitychange', function () {
    if (D.hidden) { if (P && P.pauseVideo) P.pauseVideo() } else back(false);
  });

  // ---- lưới đủ tập ----
  function openEps() {
    if (!dlg) return;
    [].forEach.call(dlg.querySelectorAll('.ti'), function (t) { t.classList.toggle('cur', !!act && (t.dataset.go || t.dataset.ep) === act.dataset.ep) });
    dlg.showModal ? dlg.showModal() : dlg.setAttribute('open', '');
  }
  function closeEps() { dlg.close ? dlg.close() : dlg.removeAttribute('open') }
  [].forEach.call(D.querySelectorAll('.eps-o'), function (b) { b.onclick = openEps });
  if (dlg) {
    dlg.querySelector('.x').onclick = closeEps;
    dlg.addEventListener('click', function (e) {
      if (e.target === dlg) return closeEps();
      var t = e.target.closest('[data-go]');
      if (!t) return;
      gest = true; closeEps();
      var s = feed.querySelector('.sl.fr[data-ep="' + t.dataset.go + '"]');
      if (s === act) play(s); else go(s);
    });
  }

  // ---- bàn phím (desktop) ----
  D.addEventListener('keydown', function (e) {
    if (dlg && dlg.open || /INPUT|TEXTAREA/.test(e.target.tagName) || !act || act.classList.contains('info')) return;
    var i = S.indexOf(act);
    if (e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === 'j') { e.preventDefault(); go(S[i + 1]) }
    else if (e.key === 'ArrowUp' || e.key === 'PageUp' || e.key === 'k') { e.preventDefault(); go(S[i - 1]) }
  });
})(window, document);
