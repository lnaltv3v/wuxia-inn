/**
 * 俠客棧 — WuxiaAudio（墨點江湖聽覺）
 * Web Audio 預載 assets/audio/sfx|bgm/*.ogg；缺失則 oscillator／noise 合成後備。
 * 戰鬥／Hub 掛接由開發主理人接入；本模組只提供 API 與建議 mapping。
 * 無外部依賴。
 */
(function (global) {
  'use strict';

  var BASE = 'assets/audio/';
  var SFX_DIR = BASE + 'sfx/';
  var BGM_DIR = BASE + 'bgm/';

  /** 戰鬥 onAction kind → 建議音效 id 列表 */
  var ACTION_MAP = {
    hit: ['sword_slash', 'hit'],
    skill: ['sword_slash', 'hit'],
    miss: [],
    parry: ['parry'],
    heal: [],
    shield: [],
    ko: ['hit'],
    windup: ['sword_slash'],
    strike: ['sword_slash'],
    clash: ['parry', 'hit'],
    recover: []
  };

  /** Hub phase → 建議音效 id（開發可於 phase 切換時呼叫） */
  var HUB_MAP = {
    enter: ['door_wood', 'footstep'],
    serve: ['tea_pour'],
    pay: ['coin'],
    leave: ['door_wood', 'footstep'],
    sit: ['guest_sit']
  };

  var SFX_IDS = [
    'door_wood', 'footstep', 'tea_pour', 'coin', 'sword_slash',
    'parry', 'hit', 'guest_sit', 'victory', 'defeat', 'ui_click'
  ];
  var BGM_IDS = ['bgm_inn', 'bgm_inn_day', 'bgm_inn_night', 'bgm_combat'];

  var ctx = null;
  var master = null;
  var sfxGain = null;
  var bgmGain = null;
  var unlocked = false;
  var muted = false;
  var masterVol = 0.85;
  var buffers = Object.create(null); // id -> AudioBuffer
  var synthReady = Object.create(null); // id -> true（合成後備標記）
  var currentBgmId = null;
  var bgmSource = null;
  var bgmStartAt = 0;
  var preloadPromise = null;

  function ensureCtx() {
    if (ctx) return ctx;
    var AC = global.AudioContext || global.webkitAudioContext;
    if (!AC) return null;
    ctx = new AC();
    master = ctx.createGain();
    master.gain.value = muted ? 0 : masterVol;
    master.connect(ctx.destination);
    sfxGain = ctx.createGain();
    sfxGain.gain.value = 1;
    sfxGain.connect(master);
    bgmGain = ctx.createGain();
    bgmGain.gain.value = 0.45;
    bgmGain.connect(master);
    return ctx;
  }

  function applyMute() {
    if (!master) return;
    master.gain.value = muted ? 0 : masterVol;
  }

  function unlock() {
    ensureCtx();
    if (!ctx) return Promise.resolve(false);
    var p = ctx.state === 'suspended' ? ctx.resume() : Promise.resolve();
    return p.then(function () {
      unlocked = ctx.state === 'running';
      return unlocked;
    }).catch(function () {
      return false;
    });
  }

  function pathFor(id) {
    if (BGM_IDS.indexOf(id) >= 0) return BGM_DIR + id + '.ogg';
    return SFX_DIR + id + '.ogg';
  }

  function decodeArrayBuffer(ab) {
    return new Promise(function (resolve, reject) {
      ensureCtx();
      if (!ctx) return reject(new Error('no AudioContext'));
      // Safari 舊式 callback／新式 Promise 皆顧
      var ret = ctx.decodeAudioData(ab, function (buf) { resolve(buf); }, function (err) { reject(err || new Error('decode')); });
      if (ret && typeof ret.then === 'function') ret.then(resolve, reject);
    });
  }

  function fetchBuffer(id) {
    var url = pathFor(id);
    return fetch(url, { cache: 'force-cache' })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.arrayBuffer();
      })
      .then(decodeArrayBuffer)
      .then(function (buf) {
        buffers[id] = buf;
        return buf;
      });
  }

  /* ---------- 合成後備（同 id，無外部樣本） ---------- */

  function makeBuffer(seconds, fillFn) {
    ensureCtx();
    var sr = ctx.sampleRate;
    var n = Math.max(1, Math.floor(seconds * sr));
    var buf = ctx.createBuffer(1, n, sr);
    var d = buf.getChannelData(0);
    fillFn(d, sr, n);
    return buf;
  }

  function synthSfx(id) {
    ensureCtx();
    if (!ctx) return null;
    var buf = null;
    if (id === 'door_wood') {
      buf = makeBuffer(0.55, function (d, sr, n) {
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          var f = 180 + 90 * Math.sin(2 * Math.PI * 3.2 * t) + 40 * t;
          var sq = 0.35 * Math.sin(2 * Math.PI * f * t) * Math.exp(-3.2 * t);
          var kn = t < 0.04 ? 0.4 * (Math.random() * 2 - 1) * (1 - t / 0.04) : 0;
          if (t > 0.38 && t < 0.42) kn += 0.3 * (Math.random() * 2 - 1);
          d[i] = Math.tanh(sq + kn);
        }
      });
    } else if (id === 'footstep') {
      buf = makeBuffer(0.18, function (d, sr, n) {
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          d[i] = Math.tanh(0.7 * Math.sin(2 * Math.PI * 90 * t) * Math.exp(-28 * t)
            + 0.3 * (Math.random() * 2 - 1) * Math.exp(-40 * t));
        }
      });
    } else if (id === 'tea_pour') {
      buf = makeBuffer(0.7, function (d, sr, n) {
        var lp = 0;
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          var raw = Math.random() * 2 - 1;
          lp = lp * 0.55 + raw * 0.45;
          var hiss = (raw - lp) * 0.5;
          var amp = (0.15 + 0.5 * (0.5 + 0.5 * Math.sin(2 * Math.PI * 2.5 * t)))
            * Math.min(1, t / 0.08) * Math.min(1, (0.7 - t) / 0.12);
          d[i] = Math.tanh(hiss * amp);
        }
      });
    } else if (id === 'coin') {
      buf = makeBuffer(0.35, function (d, sr, n) {
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          var a = Math.exp(-9 * t);
          var s = 0.45 * Math.sin(2 * Math.PI * 2100 * t)
            + 0.28 * Math.sin(2 * Math.PI * 3150 * t)
            + 0.18 * Math.sin(2 * Math.PI * 4200 * t);
          d[i] = Math.tanh(s * a);
        }
      });
    } else if (id === 'sword_slash') {
      buf = makeBuffer(0.32, function (d, sr, n) {
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          var f = 800 + 2400 * Math.exp(-18 * t);
          d[i] = Math.tanh(
            (Math.random() * 2 - 1) * 0.45 * Math.exp(-10 * t)
            + 0.3 * Math.sin(2 * Math.PI * f * t) * Math.exp(-14 * t)
          );
        }
      });
    } else if (id === 'parry') {
      buf = makeBuffer(0.28, function (d, sr, n) {
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          var a = Math.exp(-16 * t);
          var s = 0.5 * Math.sin(2 * Math.PI * 1650 * t)
            + 0.35 * Math.sin(2 * Math.PI * 2450 * t)
            + 0.15 * (Math.random() * 2 - 1) * Math.exp(-40 * t);
          d[i] = Math.tanh(s * a);
        }
      });
    } else if (id === 'hit') {
      buf = makeBuffer(0.28, function (d, sr, n) {
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          d[i] = Math.tanh(
            0.75 * Math.sin(2 * Math.PI * 110 * t) * Math.exp(-22 * t)
            + 0.35 * (Math.random() * 2 - 1) * Math.exp(-30 * t)
          );
        }
      });
    } else if (id === 'guest_sit') {
      buf = makeBuffer(0.4, function (d, sr, n) {
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          d[i] = Math.tanh(
            0.3 * Math.sin(2 * Math.PI * (140 + 30 * Math.sin(12 * t)) * t) * Math.exp(-6 * t)
            + 0.1 * (Math.random() * 2 - 1) * Math.exp(-8 * t)
          );
        }
      });
    } else if (id === 'victory') {
      var notesV = [261.63, 329.63, 392.0, 440.0, 523.25];
      buf = makeBuffer(0.85, function (d, sr, n) {
        for (var ni = 0; ni < notesV.length; ni++) {
          var start = Math.floor(ni * 0.12 * sr);
          var f0 = notesV[ni];
          for (var j = 0; j < Math.floor(0.28 * sr); j++) {
            if (start + j >= n) break;
            var t = j / sr;
            d[start + j] += 0.4 * Math.sin(2 * Math.PI * f0 * t) * Math.exp(-4.5 * t);
          }
        }
        for (var i = 0; i < n; i++) d[i] = Math.tanh(d[i]);
      });
    } else if (id === 'defeat') {
      var notesD = [392.0, 329.63, 261.63, 196.0];
      buf = makeBuffer(0.94, function (d, sr, n) {
        for (var ni = 0; ni < notesD.length; ni++) {
          var start = Math.floor(ni * 0.16 * sr);
          var f0 = notesD[ni];
          for (var j = 0; j < Math.floor(0.35 * sr); j++) {
            if (start + j >= n) break;
            var t = j / sr;
            d[start + j] += 0.45 * Math.sin(2 * Math.PI * f0 * t) * Math.exp(-3.2 * t);
          }
        }
        for (var i = 0; i < n; i++) d[i] = Math.tanh(d[i]);
      });
    } else if (id === 'ui_click') {
      buf = makeBuffer(0.08, function (d, sr, n) {
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          d[i] = 0.4 * Math.sin(2 * Math.PI * 880 * t) * Math.exp(-55 * t);
        }
      });
    } else if (id === 'bgm_inn' || id === 'bgm_inn_day' || id === 'bgm_inn_night') {
      var night = id === 'bgm_inn_night';
      var root = night ? 146.83 : 196.0;
      var secs = night ? 8 : 8; // 短循環後備（完整曲用 ogg）
      var melody = [0, 2, 4, 2, 3, 1, 0, 2];
      var scale = [0, 2, 4, 7, 9];
      function pent(r, deg) {
        var o = Math.floor(deg / 5), d = ((deg % 5) + 5) % 5;
        return r * Math.pow(2, (scale[d] + 12 * o) / 12);
      }
      buf = makeBuffer(secs, function (d, sr, n) {
        var beat = 0.7;
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          var edge = Math.min(1, t / 0.4, (secs - t) / 0.4);
          var mi = Math.floor(t / beat) % melody.length;
          var mf = pent(root, melody[mi]);
          var s = 0.06 * Math.sin(2 * Math.PI * root * 0.5 * t)
            + 0.08 * Math.sin(2 * Math.PI * mf * t);
          d[i] = Math.tanh(s * edge * (night ? 0.8 : 0.95));
        }
      });
    } else if (id === 'bgm_combat') {
      var riff = [0, 0, 1, 0, 3, 2, 0, 1];
      var scaleC = [0, 2, 4, 7, 9];
      var rootC = 110;
      function pentC(r, deg) {
        var o = Math.floor(deg / 5), d = ((deg % 5) + 5) % 5;
        return r * Math.pow(2, (scaleC[d] + 12 * o) / 12);
      }
      buf = makeBuffer(8, function (d, sr, n) {
        var beat = 0.28;
        for (var i = 0; i < n; i++) {
          var t = i / sr;
          var edge = Math.min(1, t / 0.3, (8 - t) / 0.3);
          var bi = Math.floor(t / beat) % riff.length;
          var f = pentC(rootC, riff[bi]);
          var pulse = (t % beat) < beat * 0.35 ? 1 : 0.35;
          var s = 0.12 * Math.sin(2 * Math.PI * f * t) * pulse
            + 0.04 * Math.sin(2 * Math.PI * rootC * 0.5 * t);
          if (bi % 2 === 1 && (t % beat) < 0.05) s += 0.08 * (Math.random() * 2 - 1);
          d[i] = Math.tanh(s * edge);
        }
      });
    }
    if (buf) {
      buffers[id] = buf;
      synthReady[id] = true;
    }
    return buf;
  }

  function ensureBuffer(id) {
    if (buffers[id]) return Promise.resolve(buffers[id]);
    return fetchBuffer(id).catch(function () {
      var b = synthSfx(id);
      if (!b) throw new Error('no buffer for ' + id);
      return b;
    });
  }

  function preload() {
    if (preloadPromise) return preloadPromise;
    ensureCtx();
    var ids = SFX_IDS.concat(BGM_IDS);
    preloadPromise = Promise.all(ids.map(function (id) {
      return ensureBuffer(id).catch(function () {
        synthSfx(id);
      });
    })).then(function () { return true; });
    return preloadPromise;
  }

  function play(id, opts) {
    opts = opts || {};
    ensureCtx();
    if (!ctx) return null;
    if (ctx.state === 'suspended') unlock();
    var buf = buffers[id];
    if (!buf) {
      // 懶載：觸發預載後用合成即播
      ensureBuffer(id).then(function () {
        play(id, opts);
      }).catch(function () {});
      buf = synthSfx(id);
      if (!buf) return null;
    }
    var src = ctx.createBufferSource();
    src.buffer = buf;
    var g = ctx.createGain();
    var vol = typeof opts.volume === 'number' ? opts.volume : 1;
    g.gain.value = vol;
    src.connect(g);
    g.connect(sfxGain);
    if (typeof opts.playbackRate === 'number') src.playbackRate.value = opts.playbackRate;
    try {
      src.start(0);
    } catch (e) { /* ignore */ }
    return src;
  }

  function stopBgm() {
    if (bgmSource) {
      try { bgmSource.stop(0); } catch (e) { /* ignore */ }
      try { bgmSource.disconnect(); } catch (e2) { /* ignore */ }
      bgmSource = null;
    }
    currentBgmId = null;
  }

  function setBgm(id) {
    if (id == null || id === false) {
      stopBgm();
      return;
    }
    if (id === currentBgmId && bgmSource) return;
    ensureCtx();
    if (!ctx) return;
    if (ctx.state === 'suspended') unlock();

    function startWith(buf) {
      stopBgm();
      if (!buf) return;
      var src = ctx.createBufferSource();
      src.buffer = buf;
      src.loop = true;
      src.connect(bgmGain);
      try {
        src.start(0);
      } catch (e) { return; }
      bgmSource = src;
      currentBgmId = id;
      bgmStartAt = ctx.currentTime;
    }

    if (buffers[id]) {
      startWith(buffers[id]);
    } else {
      ensureBuffer(id).then(startWith).catch(function () {
        startWith(synthSfx(id));
      });
    }
  }

  function setMuted(m) {
    muted = !!m;
    applyMute();
  }

  function setMasterVolume(v) {
    masterVol = Math.max(0, Math.min(1, Number(v) || 0));
    applyMute();
  }

  var api = {
    unlock: unlock,
    resume: unlock,
    play: play,
    setMuted: setMuted,
    setMasterVolume: setMasterVolume,
    setBgm: setBgm,
    stopBgm: stopBgm,
    preload: preload,
    get ready() { return preload(); },
    get muted() { return muted; },
    get masterVolume() { return masterVol; },
    get currentBgm() { return currentBgmId; },
    get unlocked() { return unlocked; },
    ACTION_MAP: ACTION_MAP,
    HUB_MAP: HUB_MAP,
    SFX_IDS: SFX_IDS.slice(),
    BGM_IDS: BGM_IDS.slice()
  };

  global.WuxiaAudio = api;
})(typeof window !== 'undefined' ? window : this);
