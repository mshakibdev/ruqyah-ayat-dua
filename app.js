/* রুকইয়াহ — আয়াত ও দোয়া
   গোনার ঘর, আরবির আকার, স্ক্রিন জাগিয়ে রাখা, থিম, অফলাইন ও ইনস্টল */
(function () {
  'use strict';

  var PAGE = (location.pathname.split('/').pop() || 'index.html').replace('.html', '');
  var KEY  = 'rad-count-' + PAGE;

  /* ---------- ছোট সহায়ক ---------- */
  var BN = '০১২৩৪৫৬৭৮৯';
  function bn(n) {
    return String(n).replace(/\d/g, function (d) { return BN[+d]; });
  }
  function ls(fn, dflt) {
    try { return fn(); } catch (e) { return dflt; }
  }
  var toast = (function () {
    var el, t;
    return function (msg) {
      if (!el) {
        el = document.createElement('div');
        el.className = 'toast';
        document.body.appendChild(el);
      }
      el.textContent = msg;
      el.classList.add('show');
      clearTimeout(t);
      t = setTimeout(function () { el.classList.remove('show'); }, 1700);
    };
  })();
  function buzz(ms) {
    try { if (navigator.vibrate) navigator.vibrate(ms); } catch (e) {}
  }

  /* ---------- মেনু ---------- */
  (function () {
    var btn = document.getElementById('menubtn'),
        menu = document.getElementById('menu'),
        scrim = document.getElementById('scrim'),
        close = document.getElementById('menuclose');
    if (!btn || !menu || !scrim) return;

    var open = false, lastFocus = null;
    var narrow = function () { return matchMedia('(max-width: 899px)').matches; };

    function show() {
      if (open) return;
      open = true; lastFocus = document.activeElement;
      menu.hidden = false; scrim.hidden = false;
      // hidden সরানোর পর একটি ফ্রেম অপেক্ষা, নইলে ট্রানজিশন চলবে না
      requestAnimationFrame(function () {
        menu.classList.add('on'); scrim.classList.add('on');
      });
      btn.setAttribute('aria-expanded', 'true');
      if (narrow()) document.body.classList.add('locked');
      var first = menu.querySelector('a[aria-current="page"]') || menu.querySelector('a');
      if (first) first.focus({ preventScroll: true });
    }

    function hide(back) {
      if (!open) return;
      open = false;
      menu.classList.remove('on'); scrim.classList.remove('on');
      btn.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('locked');
      setTimeout(function () {
        if (!open) { menu.hidden = true; scrim.hidden = true; }
      }, 240);
      if (back) (lastFocus || btn).focus({ preventScroll: true });
    }

    btn.addEventListener('click', function () { open ? hide(true) : show(); });
    scrim.addEventListener('click', function () { hide(false); });
    if (close) close.addEventListener('click', function () { hide(true); });
    // লিঙ্কে চাপ দিলে পাতা বদলাবে — তার আগেই প্যানেল গুটিয়ে যাক
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) hide(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && open) { e.preventDefault(); hide(true); return; }
      if (e.key !== 'Tab' || !open) return;
      // খোলা থাকলে ফোকাস প্যানেলের ভেতরেই ঘুরবে
      var f = menu.querySelectorAll('a[href], button');
      if (!f.length) return;
      var a = f[0], z = f[f.length - 1];
      if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
      else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
    });
    addEventListener('resize', function () {
      if (open && !narrow()) document.body.classList.remove('locked');
    });
  })();

  /* ---------- ডেস্কটপ মেনুবার ---------- */
  (function () {
    var groups = [].slice.call(document.querySelectorAll('.dnav .dg'));
    if (!groups.length) return;
    var cur = null;

    function panel(g) { return g.querySelector('.dgp'); }
    function btn(g)   { return g.querySelector('.dgb'); }

    function close(g, back) {
      if (!g) return;
      panel(g).hidden = true;
      btn(g).setAttribute('aria-expanded', 'false');
      if (cur === g) cur = null;
      if (back) btn(g).focus({ preventScroll: true });
    }
    function closeAll(back) { var g = cur; cur = null; close(g, back); }

    function open(g) {
      if (cur === g) return;
      closeAll(false);
      panel(g).hidden = false;
      btn(g).setAttribute('aria-expanded', 'true');
      cur = g;
      // ডানদিকের প্যানেল যেন পর্দার বাইরে না যায়
      var pp = panel(g), r = pp.getBoundingClientRect();
      pp.style.left = (r.right > innerWidth - 12) ? 'auto' : '';
      pp.style.right = (r.right > innerWidth - 12) ? '-6px' : '';
    }

    groups.forEach(function (g) {
      var b = btn(g), pp = panel(g);
      b.addEventListener('click', function (e) {
        e.stopPropagation();
        cur === g ? closeAll(true) : open(g);
      });
      // একটা খোলা থাকলে পাশেরটায় মাউস নিলেই বদলে যাবে — মেনুবারের স্বাভাবিক আচরণ
      b.addEventListener('mouseenter', function () { if (cur && cur !== g) open(g); });
      b.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ') {
          e.preventDefault(); open(g);
          var a = pp.querySelector('a[aria-current="page"]') || pp.querySelector('a');
          if (a) a.focus({ preventScroll: true });
        }
      });
      pp.addEventListener('keydown', function (e) {
        var links = [].slice.call(pp.querySelectorAll('a'));
        var i = links.indexOf(document.activeElement);
        if (e.key === 'ArrowDown') { e.preventDefault(); (links[i + 1] || links[0]).focus(); }
        else if (e.key === 'ArrowUp') {
          e.preventDefault();
          i <= 0 ? b.focus() : links[i - 1].focus();
        }
      });
    });

    document.addEventListener('click', function (e) {
      if (cur && !e.target.closest('.dg')) closeAll(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && cur) { e.preventDefault(); closeAll(true); }
    });
    document.addEventListener('focusin', function (e) {
      if (cur && !e.target.closest('.dg')) closeAll(false);
    });
  })();

  /* ---------- গোনার ঘর ---------- */
  var store = ls(function () {
    return JSON.parse(localStorage.getItem(KEY) || '{}');
  }, {}) || {};

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {}
  }

  var counters = [].slice.call(document.querySelectorAll('.cnt[data-target]'));

  function paint(btn) {
    var id  = btn.dataset.id,
        tgt = +btn.dataset.target,
        v   = store[id] || 0;
    btn.querySelector('.cv').textContent = bn(v);
    btn.classList.toggle('full', v >= tgt);
    btn.setAttribute('aria-label', 'পড়া হয়েছে ' + bn(v) + ' বার, লক্ষ্য ' + bn(tgt));
    // কার্ডের সব ঘর পূর্ণ হলে কার্ডটি সম্পূর্ণ
    var card = btn.closest('.it');
    if (card) {
      var all = [].slice.call(card.querySelectorAll('.cnt[data-target]'));
      card.classList.toggle('done', all.length > 0 && all.every(function (b) {
        return (store[b.dataset.id] || 0) >= +b.dataset.target;
      }));
    }
  }

  counters.forEach(function (btn) {
    var id = btn.dataset.id, tgt = +btn.dataset.target;
    paint(btn);

    var held = false, timer = null;

    function startHold() {
      held = false;
      timer = setTimeout(function () {
        held = true;
        if (store[id]) {
          store[id] = 0; save(); paint(btn); chapters();
          buzz(28); toast('শূন্য করা হলো');
        }
      }, 450);
    }
    function endHold() { clearTimeout(timer); }

    btn.addEventListener('pointerdown', startHold);
    btn.addEventListener('pointerup', endHold);
    btn.addEventListener('pointerleave', endHold);
    btn.addEventListener('pointercancel', endHold);
    btn.addEventListener('contextmenu', function (e) { e.preventDefault(); });

    // 'বারের অধিক' হলে সংখ্যাটি সর্বনিম্ন — লক্ষ্য ছাড়িয়েও গোনা চলবে
    var open = btn.dataset.open === '1';

    btn.addEventListener('click', function () {
      if (held) { held = false; return; }          // চেপে ধরা ছিল — গোনা বাড়বে না
      var v = store[id] || 0;
      if (v >= tgt && !open) { toast('এটি শেষ হয়েছে — চেপে ধরে রাখলে শূন্য হবে'); return; }
      if (v >= 999) return;
      store[id] = v + 1; save(); paint(btn); chapters();
      buzz(store[id] === tgt ? 45 : 10);
    });
  });

  /* ---------- স্ক্রল নামালে টুলবার সরে যাবে ----------
     লম্বা পাতায় ভাসমান বোতামগুলো লেখার ওপর বসে থাকে; নিচে নামার সময়
     সরে যায়, থামলে বা উপরে উঠলে ফিরে আসে। */
  (function () {
    var tools = document.querySelector('.tools');
    if (!tools) return;
    var last = scrollY, idle = null;
    addEventListener('scroll', function () {
      var y = scrollY;
      if (y > last + 8 && y > 220) tools.classList.add('away');
      else if (y < last - 8) tools.classList.remove('away');
      last = y;
      clearTimeout(idle);
      idle = setTimeout(function () { tools.classList.remove('away'); }, 650);
    }, { passive: true });
  })();

  /* ---------- অধ্যায়ের অগ্রগতি ----------
     ৪১টি কার্ডের পাতায় কোন অধ্যায় কতটা হলো সেটা শিরোনামেই দেখানো হয়। */
  var chapters = (function () {
    var heads = [].slice.call(document.querySelectorAll('h2.ch'));
    if (!heads.length || !counters.length) return function () {};
    var groups = heads.map(function (h) {
      var cards = [], n = h.nextElementSibling;
      while (n && n.tagName !== 'H2') {
        if (n.classList.contains('it') && n.querySelector('.cnt[data-target]')) cards.push(n);
        n = n.nextElementSibling;
      }
      var tag = document.createElement('span');
      tag.className = 'cp';
      if (cards.length) h.appendChild(tag);
      return { cards: cards, tag: tag };
    });
    return function () {
      groups.forEach(function (g) {
        if (!g.cards.length) return;
        var done = g.cards.filter(function (c) { return c.classList.contains('done'); }).length;
        g.tag.textContent = done === g.cards.length
          ? '✓ ' + bn(g.cards.length) + 'টিই শেষ'
          : bn(done) + '/' + bn(g.cards.length) + ' শেষ';
      });
    };
  })();
  chapters();

  /* ---------- হোমের ফিল্টার ---------- */
  (function () {
    var q = document.getElementById('q');
    if (!q) return;
    var fx = document.getElementById('qx');
    var cards = [].slice.call(document.querySelectorAll('.tc[data-n]'));
    var heads = [].slice.call(document.querySelectorAll('h3.gh'));
    q.addEventListener('input', function () {
      var v = q.value.trim().toLowerCase();
      var hit = 0;
      cards.forEach(function (c) {
        var on = !v || c.dataset.n.toLowerCase().indexOf(v) !== -1;
        c.hidden = !on;
        if (on) hit++;
      });
      heads.forEach(function (h) {
        var grid = h.nextElementSibling, any = false, i;
        var kids = grid ? grid.children : [];
        for (i = 0; i < kids.length; i++) if (!kids[i].hidden) { any = true; break; }
        h.hidden = !any;
        if (grid) grid.hidden = !any;
      });
      if (fx) fx.hidden = hit !== 0;
    });
  })();

  var rst = document.getElementById('reset');
  if (rst) {
    if (!counters.length) rst.hidden = true;
    rst.addEventListener('click', function () {
      store = {}; save();
      counters.forEach(paint); chapters();
      toast('সব গোনা শূন্য করা হলো');
    });
  }

  /* ---------- আরবির আকার ---------- */
  var MIN = 19, MAX = 42, STEP = 3;
  function arsize(next) {
    var cur = parseInt(ls(function () { return localStorage.getItem('rad-ar'); }, null) || '25', 10);
    if (next != null) {
      cur = Math.max(MIN, Math.min(MAX, next));
      document.documentElement.style.setProperty('--arsize', cur + 'px');
      try { localStorage.setItem('rad-ar', cur); } catch (e) {}
      toast('আরবির আকার ' + bn(cur));
    }
    return cur;
  }
  var fp = document.getElementById('fplus'), fm = document.getElementById('fminus');
  if (fp) fp.addEventListener('click', function () { arsize(arsize() + STEP); });
  if (fm) fm.addEventListener('click', function () { arsize(arsize() - STEP); });

  /* ---------- স্ক্রিন জাগিয়ে রাখা ---------- */
  var wakeBtn = document.getElementById('wake'), lock = null, wantWake = false;

  function wakeOn() {
    if (!('wakeLock' in navigator)) return Promise.reject();
    return navigator.wakeLock.request('screen').then(function (l) {
      lock = l;
      l.addEventListener('release', function () { lock = null; });
    });
  }
  if (wakeBtn) {
    if (!('wakeLock' in navigator)) {
      wakeBtn.hidden = true;
    } else {
      wakeBtn.addEventListener('click', function () {
        if (wantWake) {
          wantWake = false;
          if (lock) { lock.release(); lock = null; }
          wakeBtn.classList.remove('on');
          toast('স্ক্রিন স্বাভাবিকভাবে নিভবে');
        } else {
          wakeOn().then(function () {
            wantWake = true;
            wakeBtn.classList.add('on');
            toast('পড়া শেষ না হওয়া পর্যন্ত স্ক্রিন জেগে থাকবে');
          }).catch(function () {
            toast('এই ব্রাউজারে সম্ভব নয়');
          });
        }
      });
      document.addEventListener('visibilitychange', function () {
        if (wantWake && !lock && document.visibilityState === 'visible') {
          wakeOn().catch(function () {});
        }
      });
    }
  }

  /* ---------- থিম ---------- */
  var tb = document.getElementById('tb');
  if (tb) tb.addEventListener('click', function () {
    var set = document.documentElement.getAttribute('data-theme');
    var dark = set ? set === 'dark'
                   : matchMedia('(prefers-color-scheme: dark)').matches;
    var next = dark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('rad-theme', next); } catch (e) {}
    var m = document.querySelector('meta[name="theme-color"]:not([media])');
    if (m) m.setAttribute('content', next === 'dark' ? '#101a20' : '#1b3a4b');
  });

  /* ---------- সার্ভিস ওয়ার্কার ---------- */
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () {});
    });
  }

  /* ---------- ইনস্টল ---------- */
  var ib = document.getElementById('install'), prompt_ = null;

  var installed = navigator.standalone === true ||
                  matchMedia('(display-mode: standalone)').matches ||
                  matchMedia('(display-mode: window-controls-overlay)').matches;
  if (installed && ib) ib.hidden = true;

  // ব্রাউজার নিজে ডায়ালগ দেখাতে না পারলে হাতে-কলমে পথটা বলে দিই
  function manual(why) {
    var ua = navigator.userAgent;
    var mobile = /Android|Mobile/i.test(ua);
    var steps = mobile
      ? 'ব্রাউজারের <b>মেনু (⋮)</b> খুলুন, তারপর <b>“Install app”</b> বা <b>“Add to Home screen”</b> বেছে নিন।'
      : 'অ্যাড্রেস বারের ডান পাশে <b>ইনস্টল আইকন (⊞)</b> আছে কিনা দেখুন, অথবা <b>মেনু (⋮)</b> → ' +
        '<b>“Cast, save and share”</b> → <b>“Install page as app”</b> (Edge-এ <b>“Apps” → “Install this site as an app”</b>)।';

    var box = document.getElementById('manualtip');
    if (!box) {
      box = document.createElement('div');
      box.id = 'manualtip'; box.className = 'iostip';
      box.innerHTML = '<div></div><button type="button" aria-label="বন্ধ করুন">&times;</button>';
      var w = document.querySelector('.wrap'), h = w && w.querySelector('header');
      if (h && h.nextSibling) w.insertBefore(box, h.nextSibling);
      else if (w) w.appendChild(box);
      box.querySelector('button').addEventListener('click', function () { box.remove(); });
    }
    box.querySelector('div').innerHTML = '<b>' + why + '</b> ' + steps;
    box.hidden = false;
    box.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault(); prompt_ = e;
    if (ib && !installed) ib.hidden = false;
  });

  if (ib) ib.addEventListener('click', function () {
    if (!prompt_) {
      manual('ব্রাউজার এখন ইনস্টলের ডায়ালগ দিতে পারছে না —');
      return;
    }
    var p = prompt_;
    prompt_ = null;                       // prompt() একবারই ডাকা যায়
    var choice;
    try { choice = p.prompt(); } catch (e) {
      manual('ইনস্টলের ডায়ালগ খোলা গেল না —'); return;
    }
    Promise.resolve(choice).then(function () { return p.userChoice; })
      .then(function (res) {
        if (res && res.outcome === 'accepted') {
          ib.hidden = true;
          toast('ইনস্টল হয়ে গেছে — হোম স্ক্রিনে দেখুন');
        } else {
          // বাতিল হলে বোতামটি থাকুক, যেন আবার চেষ্টা করা যায়
          toast('ইনস্টল বাতিল হয়েছে — আবার চাপ দিতে পারেন');
        }
      })
      .catch(function () { manual('ইনস্টল সম্পন্ন হয়নি —'); });
  });
  /* ---------- iOS: ইনস্টল বোতাম নেই, তাই হাতে-কলমে ইঙ্গিত ---------- */
  var tip = document.getElementById('iostip');
  if (tip) {
    var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
                (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    var isSafari = /^((?!chrome|android|crios|fxios|edgios).)*safari/i.test(navigator.userAgent);
    var standalone = navigator.standalone === true ||
                     matchMedia('(display-mode: standalone)').matches;
    var hid = ls(function () { return localStorage.getItem('rad-iostip'); }, null);
    if (isIOS && !standalone && !hid) {
      if (!isSafari) {
        // iOS-এ হোম স্ক্রিনে বসানো শুধু Safari-তেই সম্ভব — Edge/Chrome/Firefox সবই WebKit
        tip.querySelector('div').innerHTML =
          '<b>ফোনে অ্যাপের মতো রাখতে Safari লাগবে</b> — iPhone-এ এই সুবিধা অ্যাপল শুধু Safari-কেই দেয়। ' +
          'পাতাটি <b>Safari</b>-তে খুলে <b>Share</b> → <b>“Add to Home Screen”</b> করুন। ' +
          'এখানে পড়তে কোনো অসুবিধা নেই, শুধু ইনস্টল হবে না।';
      }
      tip.hidden = false;
    }
    tip.querySelector('button').addEventListener('click', function () {
      tip.hidden = true;
      try { localStorage.setItem('rad-iostip', '1'); } catch (e) {}
    });
  }

  window.addEventListener('appinstalled', function () {
    prompt_ = null; if (ib) ib.hidden = true;
  });
})();
