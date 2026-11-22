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
          store[id] = 0; save(); paint(btn);
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
      store[id] = v + 1; save(); paint(btn);
      buzz(store[id] === tgt ? 45 : 10);
    });
  });

  var rst = document.getElementById('reset');
  if (rst) {
    if (!counters.length) rst.hidden = true;
    rst.addEventListener('click', function () {
      store = {}; save();
      counters.forEach(paint);
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
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault(); prompt_ = e;
    if (ib) ib.hidden = false;
  });
  if (ib) ib.addEventListener('click', function () {
    if (!prompt_) return;
    prompt_.prompt();
    prompt_.userChoice.then(function () { prompt_ = null; ib.hidden = true; });
  });
  window.addEventListener('appinstalled', function () {
    prompt_ = null; if (ib) ib.hidden = true;
  });
})();
