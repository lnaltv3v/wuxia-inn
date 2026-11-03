/**
 * 俠客棧 — 墨點江湖舞台（v0.9.1：場景化預熱＋鏡頭減震＋r2 精靈／960×540）
 * Hub 面板開仍呼吸；熱點墨框／硃標；戰鬥 shake 下調；招名飄字；戰場分層
 */
(function (global) {
  'use strict';

  const C = {
    ink: '#1A1510',
    inkSoft: '#3D3226',
    night: '#2A2218',
    paper: '#E8D5A8',
    paperLight: '#F4E6C4',
    cream: '#FFF8EE',
    cinnabar: '#A61B1B',
    cinnabarBright: '#C42B2B',
    gold: '#C9A227',
    loess: '#B8860B',
    jade: '#2F6B4F',
    jadeBright: '#3D8F66',
    wood: '#5C4030',
    woodLight: '#8B6914',
    sky: '#6A9AB8',
    mtn: '#4A7A58',
    mist: '#8A7A60',
    skin: '#E8C4A0',
    skinDark: '#C09070',
    teal: '#2A6A6A',
    tealBright: '#4A9A9A',
    robeRed: '#A04040',
    violet: '#5A4060',
    blood: '#8B2942'
  };

  const HERO_COLORS = {
    qingyi:   { robe: C.teal, accent: C.tealBright, skin: C.skin, hair: C.ink },
    tiezhang: { robe: C.robeRed, accent: C.jadeBright, skin: C.skin, hair: C.inkSoft },
    langren:  { robe: C.inkSoft, accent: C.cinnabarBright, skin: C.skinDark, hair: C.ink },
    qinshi:   { robe: C.paperLight, accent: C.violet, skin: C.skin, hair: C.ink },
    enemy:    { robe: C.blood, accent: C.cinnabar, skin: C.skinDark, hair: C.ink },
    staff:    { robe: C.wood, accent: C.gold, skin: C.skin, hair: C.ink },
    guest:    { robe: C.mist, accent: C.gold, skin: C.skin, hair: C.inkSoft },
    default:  { robe: C.wood, accent: C.gold, skin: C.skin, hair: C.ink }
  };

  const FRAME = 32;
  const ANIM = {
    idle:   [0, 1],
    walk:   [2, 3, 4, 5],
    // v0.9：6–8 = windup（舊稱 serve）；Hub 小二暫共用幀位播斟茶
    windup: [6, 7, 8],
    serve:  [6, 7, 8],
    attack: [9, 10, 11, 12], // strike；xiaoer 同幀位＝wipe
    strike: [9, 10, 11, 12],
    wipe:   [9, 10, 11, 12],
    hurt:   [13, 14],
    parry:  [15, 16, 17]
  };

  const SHEET_IDS = ['qingyi', 'tiezhang', 'langren', 'qinshi', 'xiaoer'];
  const LAYER_ORDER = ['hub_wall', 'hub_floor', 'hub_furniture', 'hub_counter'];
  // z: … → 角色 → lanterns → fg（夜用 hub_lanterns_night）
  const LAYER_TOP = ['hub_lanterns'];
  const LAYER_FG = ['hub_fg'];
  const LAYER_NIGHT = ['hub_lanterns_night'];
  /** 戰鬥場分層（可選 PNG；缺則程式畫硬邊後備） */
  const BATTLE_LAYERS = ['battle_sky', 'battle_mid', 'battle_ground', 'battle_props'];

  const Assets = {
    sheets: {},
    bosses: {},
    layers: {},
    fx: {},
    ready: false,
    failed: false
  };
  const FX_SHEETS = {
    slash: { frames: 6 },
    spark: { frames: 5 },
    parry_flash: { frames: 4 },
    hit_ring: { frames: 3 },
    clash: { frames: 6 }
  };

  /** 資產快取戳：跟 GAME.version 對齊，確保 v1.2.1 精靈表換檔後瀏覽器重拉 */
  const ASSET_VER = (typeof global !== 'undefined' && global.WuxiaData && global.WuxiaData.GAME && global.WuxiaData.GAME.version)
    ? global.WuxiaData.GAME.version
    : '0.8.3';

  function loadImg(src) {
    return new Promise(function (resolve) {
      const img = new Image();
      img.decoding = 'async';
      img.onload = function () { resolve(img); };
      img.onerror = function () { resolve(null); };
      const sep = src.indexOf('?') >= 0 ? '&' : '?';
      img.src = src + sep + 'v=' + encodeURIComponent(ASSET_VER);
    });
  }

  function bootAssets() {
    const jobs = [];
    SHEET_IDS.forEach(function (id) {
      // 優先 64px 精靈表（1152×64）；未到則用 32px + Hub CHAR_SCALE=2
      jobs.push(loadImg('assets/sprites/64/' + id + '.png').then(function (img64) {
        if (img64) {
          Assets.sheets[id] = img64;
          Assets.sheetNative = Assets.sheetNative || {};
          Assets.sheetNative[id] = 64;
          return null;
        }
        return loadImg('assets/sprites/' + id + '.png').then(function (img) {
          if (img) {
            Assets.sheets[id] = img;
            Assets.sheetNative = Assets.sheetNative || {};
            Assets.sheetNative[id] = 32;
          }
        });
      }));
    });
    ['boss_heifeng', 'boss_xieyi', 'boss_xueying'].forEach(function (id) {
      jobs.push(loadImg('assets/sprites/64/' + id + '_combat.png').then(function (img64) {
        if (img64) { Assets.bosses[id] = img64; return null; }
        return loadImg('assets/sprites/' + id + '_combat.png').then(function (img) {
          if (img) Assets.bosses[id] = img;
        });
      }));
    });
    Assets.sheetNative = Assets.sheetNative || {};
    jobs.push(loadImg('assets/sprites/64/guest_sit.png').then(function (img64) {
      if (img64) {
        Assets.sheets.guest_sit = img64;
        Assets.sheetNative.guest_sit = 64;
        return null;
      }
      return loadImg('assets/sprites/guest_sit.png').then(function (img) {
        if (img) { Assets.sheets.guest_sit = img; Assets.sheetNative.guest_sit = img.height || 32; }
      });
    }));
    jobs.push(loadImg('assets/sprites/64/guest_walk.png').then(function (img64) {
      if (img64) {
        Assets.sheets.guest_walk = img64;
        Assets.sheetNative.guest_walk = 64;
        return null;
      }
      return loadImg('assets/sprites/guest_walk.png').then(function (img) {
        if (img) { Assets.sheets.guest_walk = img; Assets.sheetNative.guest_walk = img.height || 32; }
      });
    }));

    LAYER_ORDER.concat(LAYER_TOP).concat(LAYER_FG).concat(LAYER_NIGHT).concat(BATTLE_LAYERS).forEach(function (name) {
      jobs.push(loadImg('assets/scenes/' + name + '.png').then(function (img) {
        if (img) Assets.layers[name] = img;
      }));
    });
    Object.keys(FX_SHEETS).forEach(function (id) {
      jobs.push(loadImg('assets/sprites/fx/' + id + '.png').then(function (img) {
        if (img) Assets.fx[id] = img;
      }));
    });
    Promise.all(jobs).then(function () {
      Assets.ready = !!(Assets.layers.hub_wall && Assets.sheets.xiaoer);
      Assets.failed = !Assets.ready;
    });
  }
  bootAssets();

  function clamp(n, a, b) { return Math.max(a, Math.min(b, n)); }

  function drawRect(ctx, x, y, w, h, color) {
    ctx.fillStyle = color;
    ctx.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h));
  }

  function lerpColor(a, b, t) {
    const pa = parseInt(a.slice(1), 16);
    const pb = parseInt(b.slice(1), 16);
    const ar = (pa >> 16) & 255, ag = (pa >> 8) & 255, ab = pa & 255;
    const br = (pb >> 16) & 255, bg = (pb >> 8) & 255, bb = pb & 255;
    const r = Math.round(ar + (br - ar) * t);
    const g = Math.round(ag + (bg - ag) * t);
    const bl = Math.round(ab + (bb - ab) * t);
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + bl).toString(16).slice(1);
  }

  function animFrame(name, tick, speed) {
    const frames = ANIM[name] || ANIM.idle;
    const sp = speed || 8;
    return frames[Math.floor(tick / sp) % frames.length];
  }

  function sheetNativeSize(img) {
    if (!img) return FRAME;
    if (img.height === 64 || img.height === 48) return img.height;
    return FRAME;
  }

  function drawSheetFrame(ctx, img, frameIndex, dx, dy, opts) {
    if (!img) return false;
    const o = opts || {};
    const native = o.frameSize || sheetNativeSize(img);
    const scale = o.scale || 1;
    const flip = !!o.flip;
    const dw = native * scale;
    const dh = native * scale;
    const sx = (frameIndex | 0) * native;
    const ox = Math.round(dx);
    const oy = Math.round(dy);
    ctx.save();
    if (o.alpha != null) ctx.globalAlpha = o.alpha;
    if (flip) {
      ctx.translate(ox + dw, oy);
      ctx.scale(-1, 1);
      ctx.drawImage(img, sx, 0, native, native, 0, 0, dw, dh);
    } else {
      ctx.drawImage(img, sx, 0, native, native, ox, oy, dw, dh);
    }
    ctx.restore();
    return true;
  }

  /** 極簡 12×16 剪影小人（素材未載入時後備） */
  function drawFigure(ctx, x, y, pal, opts) {
    const o = opts || {};
    const scale = o.scale || 1;
    const flash = o.flash;
    const robe = flash ? C.cream : pal.robe;
    const skin = flash ? C.cream : pal.skin;
    const hair = flash ? C.mist : pal.hair;
    const accent = flash ? C.gold : pal.accent;
    const ox = Math.round(x);
    const oy = Math.round(y);
    const s = scale;
    const pose = o.pose || 'idle';

    drawRect(ctx, ox + 2 * s, oy + 15 * s, 8 * s, 2 * s, C.ink);
    drawRect(ctx, ox + 3 * s, oy + 0 * s, 6 * s, 2 * s, hair);
    drawRect(ctx, ox + 2 * s, oy + 2 * s, 8 * s, 2 * s, hair);
    drawRect(ctx, ox + 3 * s, oy + 3 * s, 6 * s, 4 * s, skin);
    drawRect(ctx, ox + 4 * s, oy + 4 * s, 1 * s, 1 * s, C.ink);
    drawRect(ctx, ox + 7 * s, oy + 4 * s, 1 * s, 1 * s, C.ink);
    drawRect(ctx, ox + 2 * s, oy + 7 * s, 8 * s, 6 * s, robe);
    drawRect(ctx, ox + 2 * s, oy + 7 * s, 8 * s, 1 * s, accent);

    let armSwing = o.arm || 0;
    let leftArmY = 8;
    let rightArmY = 8;
    let leftArmH = 4;
    let rightArmH = 4;
    if (pose === 'parry') {
      armSwing = 0;
      leftArmY = 5;
      rightArmY = 6;
      leftArmH = 5;
      rightArmH = 4;
      drawRect(ctx, ox + (-1) * s, oy + 5 * s, 3 * s, 2 * s, accent);
    } else if (pose === 'strike') {
      armSwing = 2;
      rightArmY = 6;
    } else if (pose === 'hurt') {
      armSwing = -1;
    }

    drawRect(ctx, ox + (0 + armSwing) * s, oy + leftArmY * s, 2 * s, leftArmH * s, robe);
    drawRect(ctx, ox + (10 - armSwing) * s, oy + rightArmY * s, 2 * s, rightArmH * s, robe);
    drawRect(ctx, ox + (0 + armSwing) * s, oy + (leftArmY + leftArmH - 1) * s, 2 * s, 1 * s, skin);
    drawRect(ctx, ox + (10 - armSwing) * s, oy + (rightArmY + rightArmH - 1) * s, 2 * s, 1 * s, skin);

    const stride = o.stride || 0;
    drawRect(ctx, ox + (3 - stride) * s, oy + 13 * s, 2 * s, 3 * s, C.inkSoft);
    drawRect(ctx, ox + (7 + stride) * s, oy + 13 * s, 2 * s, 3 * s, C.inkSoft);

    if (o.weapon === 'sword') {
      if (pose === 'strike') {
        drawRect(ctx, ox + 12 * s, oy + 2 * s, 8 * s, 1 * s, accent);
        drawRect(ctx, ox + 11 * s, oy + 1 * s, 2 * s, 3 * s, C.gold);
      } else if (pose === 'parry') {
        drawRect(ctx, ox + (-2) * s, oy + 3 * s, 1 * s, 8 * s, accent);
        drawRect(ctx, ox + (-3) * s, oy + 2 * s, 3 * s, 1 * s, C.gold);
      } else {
        drawRect(ctx, ox + 11 * s, oy + 4 * s, 1 * s, 9 * s, accent);
        drawRect(ctx, ox + 10 * s, oy + 3 * s, 3 * s, 1 * s, C.gold);
      }
    } else if (o.weapon === 'blade') {
      if (pose === 'strike') {
        drawRect(ctx, ox + 12 * s, oy + 3 * s, 9 * s, 2 * s, accent);
        drawRect(ctx, ox + 11 * s, oy + 2 * s, 2 * s, 4 * s, C.woodLight);
      } else if (pose === 'parry') {
        drawRect(ctx, ox + (-3) * s, oy + 4 * s, 2 * s, 7 * s, accent);
      } else {
        drawRect(ctx, ox + 11 * s, oy + 3 * s, 2 * s, 8 * s, accent);
        drawRect(ctx, ox + 10 * s, oy + 2 * s, 4 * s, 1 * s, C.woodLight);
      }
    } else if (o.weapon === 'fist') {
      drawRect(ctx, ox + (-1 + armSwing) * s, oy + 9 * s, 3 * s, 2 * s, skin);
      drawRect(ctx, ox + (10 - armSwing) * s, oy + 9 * s, 3 * s, 2 * s, skin);
    } else if (o.weapon === 'qin') {
      drawRect(ctx, ox + 1 * s, oy + 9 * s, 10 * s, 2 * s, accent);
      drawRect(ctx, ox + 2 * s, oy + 8 * s, 8 * s, 1 * s, C.ink);
    } else if (o.weapon === 'club') {
      if (pose === 'strike') {
        drawRect(ctx, ox + 12 * s, oy + 4 * s, 7 * s, 2 * s, C.mist);
      } else {
        drawRect(ctx, ox + 11 * s, oy + 5 * s, 2 * s, 7 * s, C.mist);
        drawRect(ctx, ox + 10 * s, oy + 4 * s, 4 * s, 1 * s, C.cinnabar);
      }
    } else if (o.weapon === 'tray') {
      drawRect(ctx, ox + 10 * s, oy + 7 * s, 5 * s, 1 * s, C.woodLight);
      drawRect(ctx, ox + 11 * s, oy + 5 * s, 3 * s, 2 * s, C.cinnabarBright);
    }
  }

  function drawPixelText(ctx, text, x, y, color) {
    ctx.fillStyle = color || C.cream;
    ctx.font = '8px monospace';
    ctx.textBaseline = 'top';
    ctx.fillText(String(text), Math.round(x), Math.round(y));
  }

  function drawBubble(ctx, text, x, y, life) {
    if (!text || life <= 0) return;
    const t = String(text);
    const tw = Math.min(200, 8 + t.length * 6);
    const bx = Math.round(clamp(x - tw / 2, 4, 960 - tw - 4));
    const by = Math.round(clamp(y, 4, 500));
    ctx.globalAlpha = clamp(life, 0, 1);
    drawRect(ctx, bx, by, tw, 18, C.night);
    drawRect(ctx, bx + 1, by + 1, tw - 2, 16, C.paper);
    drawPixelText(ctx, t, bx + 4, by + 4, C.ink);
    ctx.globalAlpha = 1;
  }

  // ——— 客棧 Hub 舞台（v0.7.0 · Hub 960×540 · 橋接放大場景） ———
  const InnStage = (function () {
    const W = 960;
    const H = 540;
    /** Hub 角色顯示：優先原生 64（scale=1）；僅缺檔時 32×2 橋接 */
    const CHAR_SCALE = 1;
    const HS = 2; // 舊 480 座標倍率
    function hubScaleFor(id) {
      const n = Assets.sheetNative && Assets.sheetNative[id];
      if (n === 64) return 1;
      if (n === 32) return 2; // 橋接
      // guest sheets: height 64 → 1
      const img = Assets.sheets[id];
      if (img && img.height === 64) return 1;
      if (img && img.height === 32) return 2;
      return CHAR_SCALE;
    }
    const PHASES = { idle: 1, enter: 1, serve: 1, pay: 1, leave: 1 };

    let canvas = null;
    let ctx = null;
    let wrapEl = null;
    let raf = 0;
    let running = false;
    let phase = 'idle';
    let t0 = 0;
    let guestName = '過路客';
    let payAmt = 0;
    let guestKind = 'meal';
    let queue = [];
    let coinY = 0;
    let coinAlpha = 0;
    let floatLabel = null;
    let staffArm = 0;
    let guestX = 80;
    let guestY = 350;
    let guestStride = 0;
    let idleBlink = 0;
    let hoverId = null;
    let selectedHotspotId = null; // sheet 打開時對應熱點高亮
    let hotspotHandler = null;
    let hintHandler = null;
    let choiceHandler = null;
    let tipHandler = null;
    let ambientHeroes = ['qingyi'];
    let innTitle = '俠客棧';
    let walkerPhase = 0;
    let seatedGuests = [];
    let doorOpen = 0;
    let tipBurst = null;
    let accelerateFlash = 0;
    let ambientHandler = null;
    let lastNightFlag = null;
    let lastFootstepAt = 0;
    let bubble = null; // { text, x, y, life } 主泡泡（兼容舊 API）
    let bubbles = [];  // 多泡泡：場景事件氣氛
    let rumorText = '';
    let sceneEvt = null; // { beats, i, t0, walkers }
    let xiaoer = { x: 440, y: 350, tx: 440, ty: 350, mode: 'idle', tick: 0, flip: false, actionTicks: 0, destAct: 'idle' };
    let guestFrame = 0;       // guest_sit 幀 0–5（入座後）
    let guestIndex = 0;       // guest_walk 0–5（對齊 sit 0–5：含 jade／wood-hat）
    let guestLocal = 0;       // guest_walk local 0–7
    let guestFlip = false;
    let guestSeated = false;
    let seatTarget = { x: 456, y: 376 };
    let seatOccupiedKey = null; // 進場佔用嘅座位 key，畫坐客時跳過
    const PHASE_MS = { enter: 1400, serve: 1600, pay: 1200, leave: 1300 };
    const ALL_SEATS = [
      { x: 108, y: 396, key: 'a' }, { x: 216, y: 412, key: 'b' }, { x: 336, y: 424, key: 'c' },
      { x: 496, y: 428, key: 'd' }, { x: 636, y: 400, key: 'e' }, { x: 756, y: 416, key: 'f' }
    ];

    // Hub v2.0 熱點（960×540＝舊錨點 ×2；場景 PNG 暫 nearest 橋接）
    const HOTSPOTS = [
      { id: 'door',     label: '大門·出巡',   x: 12,  y: 164, w: 96,  h: 136, open: 'combat' },
      { id: 'board',    label: '告示·江湖',   x: 216, y: 184, w: 88,  h: 56,  open: 'story' },
      { id: 'books',    label: '書架·藏書',   x: 216, y: 224, w: 80,  h: 100, open: 'library' },
      { id: 'counter',  label: '櫃檯·經營',   x: 306, y: 326, w: 368, h: 114, open: 'inn' },
      { id: 'map',      label: '地圖·據點',   x: 724, y: 182, w: 92,  h: 106, open: 'outposts' },
      { id: 'heroes',   label: '俠客席·養成', x: 676, y: 356, w: 144, h: 68,  open: 'heroes' },
      { id: 'tableA',   label: '雅座·小費',   x: 96,  y: 396, w: 172, h: 92,  open: 'table' },
      { id: 'tableB',   label: '雅座·加急',   x: 400, y: 416, w: 172, h: 92,  open: 'table' },
      { id: 'tableC',   label: '雅座·小費',   x: 636, y: 384, w: 180, h: 96,  open: 'table' }
    ];

    // 走廊 390–550,320–500 ＋ 枱間抹枱點（×2）
    const XIAOER_WAYPOINTS = [
      { x: 440, y: 340, act: 'idle' },
      { x: 472, y: 404, act: 'wipe' },
      { x: 500, y: 456, act: 'wipe' },
      { x: 410, y: 316, act: 'serve' },
      { x: 172, y: 404, act: 'wipe' },
      { x: 664, y: 392, act: 'wipe' },
      { x: 536, y: 356, act: 'serve' },
      { x: 376, y: 300, act: 'idle' },
      { x: 470, y: 376, act: 'wipe' }
    ];

    function mount(host) {
      if (!host) return;
      if (canvas && canvas.isConnected && running && host.contains(canvas.closest('.stage-wrap') || canvas)) {
        return;
      }
      host.innerHTML = '';
      const wrap = document.createElement('div');
      wrap.className = 'stage-wrap inn-stage-wrap hub-stage-wrap';
      wrap.innerHTML =
        '<canvas class="px-stage hub-canvas" width="960" height="540" aria-label="客棧內部主場景" tabindex="0"></canvas>' +
        '<div class="stage-caption stage-caption-slim" id="inn-stage-cap" hidden>客棧內部</div>';
      host.appendChild(wrap);
      wrapEl = wrap;
      canvas = wrap.querySelector('canvas');
      ctx = canvas.getContext('2d');
      ctx.imageSmoothingEnabled = false;
      running = true;
      t0 = performance.now();
      if (!PHASES[phase]) phase = 'idle';
      canvas.addEventListener('mousemove', onMove);
      canvas.addEventListener('mouseleave', () => { hoverId = null; });
      canvas.addEventListener('click', onClick);
      canvas.addEventListener('touchstart', onTouch, { passive: true });
      cancelAnimationFrame(raf);
      seedSeated();
      loop(performance.now());
      if (phase === 'idle' && queue.length) startNext();
    }

    function destroy() {
      running = false;
      cancelAnimationFrame(raf);
      if (canvas) {
        canvas.removeEventListener('mousemove', onMove);
        canvas.removeEventListener('click', onClick);
        canvas.removeEventListener('touchstart', onTouch);
      }
      canvas = null;
      ctx = null;
      wrapEl = null;
    }

    function isMounted() { return !!canvas && running && canvas.isConnected; }

    function setCaption(text) {
      const el = document.getElementById('inn-stage-cap');
      if (el) el.textContent = text;
    }

    function setHotspotHandler(fn) { hotspotHandler = typeof fn === 'function' ? fn : null; }
    function setSelectedHotspot(id) { selectedHotspotId = id || null; }
    function setHintHandler(fn) { hintHandler = typeof fn === 'function' ? fn : null; }
    function setChoiceHandler(fn) { choiceHandler = typeof fn === 'function' ? fn : null; }
    function setTipHandler(fn) { tipHandler = typeof fn === 'function' ? fn : null; }
    function setAmbientHeroes(ids) {
      ambientHeroes = Array.isArray(ids) && ids.length ? ids.slice(0, 4) : ['qingyi'];
    }
    function setInnTitle(name) { innTitle = name || '俠客棧'; }
    function setAmbientChange(fn) { ambientHandler = typeof fn === 'function' ? fn : null; }

    function showBubble(text, x, y, life) {
      const b = { text: text, x: x == null ? 440 : x, y: y == null ? 240 : y, life: life == null ? 1 : life };
      bubble = b;
      bubbles.push(Object.assign({}, b));
      if (bubbles.length > 3) bubbles.shift();
    }

    function pushBubble(text, x, y, life) {
      bubbles.push({ text: text, x: x == null ? 440 : x, y: y == null ? 240 : y, life: life == null ? 1 : life });
      if (bubbles.length > 3) bubbles.shift();
    }

    /** 場景化江湖事件：Hub 內多泡泡＋短暫行人演出（唔淨對話面板） */
    function playSceneEvent(def) {
      if (!def || !def.beats || !def.beats.length) return;
      const walkers = (def.walkers || [
        { id: 'langren', x: 80, y: 340, tx: 240, ty: 356 },
        { id: 'qingyi', x: 320, y: 356, tx: 200, ty: 344 }
      ]).map(function (w) {
        // 兼容舊 480 座標資料：若明顯落在左半舊格則 ×2
        let sx = w.x, sy = w.y, stx = w.tx != null ? w.tx : w.x, sty = w.ty != null ? w.ty : w.y;
        const looksLegacy = Math.max(sx, sy, stx, sty) <= 280;
        if (looksLegacy) { sx *= HS; sy *= HS; stx *= HS; sty *= HS; }
        return {
          id: w.id || 'langren',
          x: sx, y: sy,
          tx: stx,
          ty: sty,
          flip: !!w.flip,
          tick: 0
        };
      });
      sceneEvt = {
        id: def.id || 'scene',
        beats: def.beats.slice(),
        i: 0,
        t0: performance.now(),
        walkers: walkers,
        done: false,
        awaitChoice: false,
        choices: def.choices || null,
        caption: def.caption || '',
        interactive: !!def.interactive
      };
      if (def.caption) setCaption(def.caption);
    }

    function resolveSceneChoice(choiceId) {
      if (!sceneEvt || !sceneEvt.awaitChoice) return null;
      const choices = sceneEvt.choices || [];
      let picked = null;
      for (let i = 0; i < choices.length; i++) {
        if (choices[i].id === choiceId) { picked = choices[i]; break; }
      }
      if (!picked && choices.length) picked = choices[0];
      sceneEvt.awaitChoice = false;
      sceneEvt.done = true;
      if (picked && picked.resultLine) {
        pushBubble(picked.resultLine, 440, 220, 1.6);
        setCaption(picked.resultLine);
      }
      const out = picked;
      setTimeout(function () { sceneEvt = null; }, 900);
      return out;
    }

    function updateSceneEvent(now) {
      if (!sceneEvt || sceneEvt.done) return;
      if (sceneEvt.awaitChoice) return;
      const elapsed = now - sceneEvt.t0;
      // 行人緩移
      sceneEvt.walkers.forEach(function (w) {
        const dx = w.tx - w.x;
        const dy = w.ty - w.y;
        if (Math.abs(dx) > 0.4 || Math.abs(dy) > 0.4) {
          w.x += dx * 0.04;
          w.y += dy * 0.04;
          w.flip = dx < 0;
          w.tick += 1;
        } else {
          w.tick += 1;
        }
      });
      while (sceneEvt.i < sceneEvt.beats.length && elapsed >= sceneEvt.beats[sceneEvt.i].at) {
        const beat = sceneEvt.beats[sceneEvt.i];
        sceneEvt.i += 1;
        if (beat.caption) setCaption(beat.caption);
        if (beat.line) {
          const wx = beat.walker != null && sceneEvt.walkers[beat.walker]
            ? sceneEvt.walkers[beat.walker].x + 20
            : (beat.x != null ? beat.x * (beat.x <= 280 ? HS : 1) : 400);
          const wy = beat.walker != null && sceneEvt.walkers[beat.walker]
            ? sceneEvt.walkers[beat.walker].y - 32
            : (beat.y != null ? beat.y * (beat.y <= 280 ? HS : 1) : 240);
          pushBubble(beat.line, wx, wy, beat.life != null ? beat.life : 1.15);
        }
        if (beat.move && sceneEvt.walkers[beat.move.i]) {
          const w = sceneEvt.walkers[beat.move.i];
          let mtx = beat.move.tx, mty = beat.move.ty;
          if (mtx != null && mtx <= 280) mtx *= HS;
          if (mty != null && mty <= 280) mty *= HS;
          if (mtx != null) w.tx = mtx;
          if (mty != null) w.ty = mty;
        }
        if (beat.prompt && sceneEvt.choices && sceneEvt.choices.length) {
          sceneEvt.awaitChoice = true;
          sceneEvt.done = false;
          setCaption(sceneEvt.caption || '掌櫃，如何處置？');
          if (choiceHandler) {
            try { choiceHandler(sceneEvt.choices, sceneEvt); } catch (e) { /* ignore */ }
          }
        } else if (beat.end) {
          sceneEvt.done = true;
          setTimeout(function () {
            if (sceneEvt && sceneEvt.done) sceneEvt = null;
          }, 600);
        }
      }
      if (sceneEvt.i >= sceneEvt.beats.length && !sceneEvt.done) {
        sceneEvt.done = true;
        setTimeout(function () { sceneEvt = null; }, 800);
      }
    }

    function setRumor(text) {
      rumorText = text || '';
      if (rumorText) showBubble('傳聞：' + rumorText, 480, 56, 1.2);
    }

    function greetXiaoer(line) {
      const msg = line || '客官裏面請！';
      showBubble(msg, xiaoer.x + 32, xiaoer.y - 36, 1.15);
      setCaption('小二：' + msg);
    }

    function playHubSfx(phaseKey) {
      if (typeof WuxiaAudio === 'undefined' || !WuxiaAudio) return;
      try {
        const map = WuxiaAudio.HUB_MAP || {};
        const ids = map[phaseKey] || [];
        ids.forEach(function (id) { WuxiaAudio.play(id); });
      } catch (e) { /* ignore */ }
    }

    function playSfx(id, opts) {
      if (typeof WuxiaAudio === 'undefined' || !WuxiaAudio || !id) return;
      try { WuxiaAudio.play(id, opts); } catch (e) { /* ignore */ }
    }

    function isNightNow(now) {
      const df = dayFactor(now != null ? now : performance.now());
      return df >= 0.52 && df < 0.86;
    }

    function isNight() { return isNightNow(performance.now()); }

    function maybeEmitAmbient(now) {
      const night = isNightNow(now);
      if (lastNightFlag === night) return;
      lastNightFlag = night;
      if (night) {
        setCaption('夜色漸濃，燈籠點起——夜客小費更豪爽');
        pushBubble('掌燈時分', 480, 72, 1.2);
      } else {
        setCaption('天光破曉，客棧再開門營業');
        pushBubble('晨光入棧', 480, 72, 1.1);
      }
      if (ambientHandler) {
        try { ambientHandler(night); } catch (e) { /* ignore */ }
      }
    }

    function canvasPos(evt) {
      const rect = canvas.getBoundingClientRect();
      const sx = canvas.width / rect.width;
      const sy = canvas.height / rect.height;
      const cx = (evt.clientX != null ? evt.clientX : (evt.touches && evt.touches[0].clientX)) - rect.left;
      const cy = (evt.clientY != null ? evt.clientY : (evt.touches && evt.touches[0].clientY)) - rect.top;
      return { x: cx * sx, y: cy * sy };
    }

    function hitTest(x, y) {
      for (let i = HOTSPOTS.length - 1; i >= 0; i--) {
        const h = HOTSPOTS[i];
        if (x >= h.x && x <= h.x + h.w && y >= h.y && y <= h.y + h.h) return h;
      }
      return null;
    }

    function onMove(evt) {
      const p = canvasPos(evt);
      const h = hitTest(p.x, p.y);
      hoverId = h ? h.id : null;
      if (canvas) canvas.style.cursor = h ? 'pointer' : 'default';
      if (hintHandler) {
        try { hintHandler(h); } catch (e) { /* ignore */ }
      }
    }

    function handleHotspot(h) {
      if (!h) return;
      if (h.open === 'table') {
        onTableInteract(h);
        return;
      }
      if (hotspotHandler) hotspotHandler(h.open, h);
    }

    function onClick(evt) {
      const p = canvasPos(evt);
      handleHotspot(hitTest(p.x, p.y));
    }

    function onTouch(evt) {
      if (!evt.touches || !evt.touches[0]) return;
      const p = canvasPos(evt.touches[0]);
      const h = hitTest(p.x, p.y);
      hoverId = h ? h.id : null;
      handleHotspot(h);
    }

    function onTableInteract(h) {
      const cx = h.x + h.w / 2;
      const cy = h.y + 8;
      if (phase === 'enter' || phase === 'serve') {
        const elapsed = performance.now() - t0;
        const target = phase === 'enter' ? PHASE_MS.enter : PHASE_MS.serve;
        t0 = performance.now() - Math.max(elapsed, target - 180);
        accelerateFlash = 18;
        floatLabel = { text: '加急上菜!', x: cx - 20, y: cy, life: 1 };
        setCaption('雅座催單——小二加快斟茶…');
        return;
      }
      if (phase === 'pay') {
        const mul = getTipMul();
        const tip = Math.max(1, Math.round((1 + Math.floor(Math.random() * 4)) * mul));
        tipBurst = { x: cx, y: cy, life: 24, max: 24, amt: tip };
        floatLabel = { text: '+' + tip + '賞', x: cx - 8, y: cy - 10, life: 1 };
        if (tipHandler) tipHandler(tip, 'rush');
        setCaption((isNight() ? '夜客加賞 ' : '雅座加賞 ') + tip + ' 兩');
        return;
      }
      const mul = getTipMul();
      const tip = Math.max(1, Math.round((1 + Math.floor(Math.random() * 3)) * mul));
      tipBurst = { x: cx, y: cy, life: 28, max: 28, amt: tip };
      floatLabel = { text: '+' + tip + '賞', x: cx - 8, y: cy - 12, life: 1 };
      coinAlpha = 1;
      coinY = 0;
      if (tipHandler) tipHandler(tip, 'table');
      setCaption((isNight() ? '夜客賞銀 ' : '雅座客人賞銀 ') + tip + ' 兩');
    }

    function enqueueGuest(guest, pay) {
      queue.push({ guest: guest || { name: '過路客', kind: 'meal' }, pay: pay || 0 });
      if (phase === 'idle') startNext();
    }

    function playGuest(guest, pay) { enqueueGuest(guest, pay); }

    function startNext() {
      if (!queue.length) {
        phase = 'idle';
        doorOpen = 0;
        seatOccupiedKey = null;
        setCaption(innTitle + ' · 點擊場景熱點 · 雅座可催單／小費');
        return;
      }
      const job = queue.shift();
      guestName = job.guest.name || '過路客';
      guestKind = job.guest.kind || 'meal';
      payAmt = job.pay || 0;
      // guest_walk：guestIndex 0–5＝teal／robe-red／ink-soft／violet／jade／wood-hat（對齊 guest_sit）
      guestIndex = Math.floor(Math.random() * 6);
      guestFrame = guestIndex; // 入座後切同色 sit（有杯）
      guestLocal = 0;
      // 揀空位，避免同常駐坐客重疊
      const taken = {};
      seatedGuests.forEach(function (g) { if (g.key) taken[g.key] = true; });
      const free = ALL_SEATS.filter(function (s) { return !taken[s.key]; });
      const pick = free.length ? free[Math.floor(Math.random() * free.length)] : ALL_SEATS[guestIndex % ALL_SEATS.length];
      seatTarget = { x: pick.x, y: pick.y };
      seatOccupiedKey = pick.key;
      // 若仍撞到（後備），暫時移開該格常駐客
      seatedGuests = seatedGuests.filter(function (g) {
        return !(Math.abs(g.x - pick.x) < 16 && Math.abs(g.y - pick.y) < 16);
      });
      guestX = 56;
      guestY = 336;
      guestStride = 0;
      guestFlip = false;
      guestSeated = false;
      staffArm = 0;
      coinAlpha = 0;
      floatLabel = null;
      phase = 'enter';
      doorOpen = 1;
      t0 = performance.now();
      lastFootstepAt = 0;
      playHubSfx('enter');
      setCaption(guestName + ' 推門進場…');
      showBubble('客官裏面請！', xiaoer.x + 20, xiaoer.y - 32, 1);
      xiaoer.mode = 'walk';
      xiaoer.tx = 320;
      xiaoer.ty = 350;
      xiaoer.destAct = 'idle';
    }

    function seedSeated() {
      // 只放 2–3 位常駐坐客，留空位畀進場動畫，避免重疊
      seatedGuests = [
        { x: 108, y: 396, robe: C.teal, frame: 0, key: 'a' },
        { x: 216, y: 412, robe: C.jadeBright, frame: 4, key: 'b' },
        { x: 496, y: 428, robe: C.violet, frame: 3, key: 'd' },
        { x: 756, y: 416, robe: C.wood, frame: 5, key: 'f' }
      ];
      seatOccupiedKey = null;
    }

    /** 全日循環約 64 秒；夜間窗加長，方便睇到 lanterns_night */
    function dayFactor(now) {
      return (now / 64000) % 1;
    }

    function skyTintFactor(now) {
      const df = dayFactor(now);
      let skyT = 0;
      // 晨 0–0.18 → 日 0.18–0.42 → 昏 0.42–0.52 → 夜 0.52–0.86 → 黎明 0.86–1
      if (df < 0.18) skyT = 0.15 + (df / 0.18) * 0.25;
      else if (df < 0.42) skyT = 0.4 + ((df - 0.18) / 0.24) * 0.15;
      else if (df < 0.52) skyT = 0.55 + ((df - 0.42) / 0.1) * 0.25;
      else if (df < 0.86) skyT = 0.8 + ((df - 0.52) / 0.34) * 0.2;
      else skyT = 1.0 - ((df - 0.86) / 0.14) * 0.75;
      return skyT;
    }

    function dayPhaseName(now) {
      const df = dayFactor(now != null ? now : performance.now());
      if (df < 0.18) return 'dawn';
      if (df < 0.42) return 'day';
      if (df < 0.52) return 'dusk';
      if (df < 0.86) return 'night';
      return 'dawn';
    }

    /** 營業小費倍率：日平、昏略高、夜最高（酒客多） */
    function getTipMul(now) {
      const phase = dayPhaseName(now);
      if (phase === 'night') return 1.55;
      if (phase === 'dusk') return 1.3;
      if (phase === 'dawn') return 0.85;
      return 1.0;
    }

    function drawBgLayers(now) {
      const hasLayers = Assets.layers.hub_wall && Assets.layers.hub_floor;
      if (!hasLayers) {
        drawBgFallback(now);
        return false;
      }
      LAYER_ORDER.forEach(function (name) {
        const img = Assets.layers[name];
        if (img) ctx.drawImage(img, 0, 0);
      });
      // 門開合：左門加暗／亮
      if (doorOpen > 0.2) {
        ctx.globalAlpha = 0.35 * doorOpen;
        drawRect(ctx, 28, 216, 72, 84, C.cream);
        ctx.globalAlpha = 1;
      } else {
        ctx.globalAlpha = 0.25;
        drawRect(ctx, 28, 216, 72, 84, C.night);
        ctx.globalAlpha = 1;
      }
      // 匾額標題條（覆蓋字畫區上方中央）
      const tw = Math.min(320, 32 + innTitle.length * 28);
      drawRect(ctx, (W - tw) / 2, 8, tw, 24, C.inkSoft);
      drawRect(ctx, (W - tw) / 2 + 4, 12, tw - 8, 16, C.blood);
      drawPixelText(ctx, innTitle, (W - tw) / 2 + 16, 14, C.cream);
      return true;
    }

    function drawLanternsAndNight(now) {
      const night = isNightNow(now);
      const dayImg = Assets.layers.hub_lanterns;
      const nightImg = Assets.layers.hub_lanterns_night;
      const img = night && nightImg ? nightImg : dayImg;
      if (img) ctx.drawImage(img, 0, 0);
      const skyT = skyTintFactor(now);
      // 夜：加深天色罩＋窗／燈硬光斑，令 lanterns_night 更明顯
      if (night) {
        ctx.globalAlpha = 0.16 + Math.min(0.14, (skyT - 0.75) * 0.35);
        drawRect(ctx, 0, 0, W, H, C.night);
        ctx.globalAlpha = 1;
        // 硬邊燈暈（盤內色，唔用柔邊）
        const glows = [
          { x: 144, y: 96, w: 36, h: 28 },
          { x: 440, y: 80, w: 44, h: 32 },
          { x: 720, y: 104, w: 36, h: 28 }
        ];
        glows.forEach(function (g) {
          ctx.globalAlpha = 0.22;
          drawRect(ctx, g.x, g.y, g.w, g.h, C.gold);
          ctx.globalAlpha = 0.12;
          drawRect(ctx, g.x - 2, g.y - 2, g.w + 4, g.h + 4, C.cinnabarBright);
          ctx.globalAlpha = 1;
        });
      } else if (skyT > 0.55) {
        ctx.globalAlpha = (skyT - 0.55) * 0.22;
        drawRect(ctx, 0, 0, W, H, C.night);
        ctx.globalAlpha = 1;
      }
    }

    function drawForeground() {
      const fg = Assets.layers.hub_fg;
      if (fg) ctx.drawImage(fg, 0, 0);
    }

    function drawBgFallback(now) {
      const skyT = skyTintFactor(now);
      const skyCol = lerpColor(C.sky, C.night, clamp((skyT - 0.35) / 0.65, 0, 1));
      const wallCol = lerpColor(C.wood, C.night, clamp((skyT - 0.5) / 0.5 * 0.35, 0, 0.35));
      drawRect(ctx, 0, 0, W, 200, wallCol);
      drawRect(ctx, 0, 0, W, 44, C.night);
      drawRect(ctx, 0, 192, W, 12, C.inkSoft);
      drawRect(ctx, 56, 64, 108, 84, skyCol);
      drawRect(ctx, 0, 204, W, H - 204, C.loess);
      drawRect(ctx, 300, 310, 360, 72, C.wood);
      drawRect(ctx, 24, 204, 96, 110, C.night);
    }

    function drawHotspotHints() {
      HOTSPOTS.forEach(function (h) {
        const on = hoverId === h.id;
        const sel = selectedHotspotId === h.id;
        const isTable = h.open === 'table';
        const active = on || sel;
        if (active) {
          // 墨框＋硃角標（唔靠大文字板）
          const fill = isTable ? C.jadeBright : (sel ? C.cinnabar : C.gold);
          ctx.globalAlpha = on ? 0.22 : 0.14;
          drawRect(ctx, h.x, h.y, h.w, h.h, fill);
          ctx.globalAlpha = 1;
          drawRect(ctx, h.x, h.y, h.w, 3, C.ink);
          drawRect(ctx, h.x, h.y + h.h - 3, h.w, 3, C.ink);
          drawRect(ctx, h.x, h.y, 3, h.h, C.ink);
          drawRect(ctx, h.x + h.w - 3, h.y, 3, h.h, C.ink);
          // 硃紅角標
          const mark = sel ? C.cinnabarBright : C.cinnabar;
          drawRect(ctx, h.x - 1, h.y - 1, 10, 10, mark);
          drawRect(ctx, h.x + h.w - 9, h.y - 1, 10, 10, mark);
          drawRect(ctx, h.x - 1, h.y + h.h - 9, 10, 10, C.ink);
          drawRect(ctx, h.x + h.w - 9, h.y + h.h - 9, 10, 10, C.ink);
          // 僅 hover 時短字（選中唔再疊大標）
          if (on) {
            const short = (h.label || '').split('·')[0];
            if (short) {
              drawRect(ctx, h.x + 4, Math.max(8, h.y - 16), Math.min(72, 8 + short.length * 10), 12, C.ink);
              drawPixelText(ctx, short, h.x + 6, Math.max(10, h.y - 14), C.cream);
            }
          }
        } else if (!isTable) {
          // 常駐：淡墨角＋1px 框，無大字
          ctx.globalAlpha = 0.55;
          drawRect(ctx, h.x, h.y, h.w, 1, C.inkSoft);
          drawRect(ctx, h.x, h.y + h.h - 1, h.w, 1, C.inkSoft);
          drawRect(ctx, h.x, h.y, 1, h.h, C.inkSoft);
          drawRect(ctx, h.x + h.w - 1, h.y, 1, h.h, C.inkSoft);
          ctx.globalAlpha = 0.85;
          drawRect(ctx, h.x + 2, h.y + 2, 6, 6, C.cinnabar);
          ctx.globalAlpha = 1;
        } else {
          ctx.globalAlpha = 0.4;
          drawRect(ctx, h.x + 2, h.y + 2, 4, 4, C.jade);
          ctx.globalAlpha = 1;
        }
      });
    }

    function weaponFor(id) {
      if (id === 'qingyi') return 'sword';
      if (id === 'tiezhang') return 'fist';
      if (id === 'langren') return 'blade';
      if (id === 'qinshi') return 'qin';
      return null;
    }

    function pickXiaoerWaypoint() {
      return XIAOER_WAYPOINTS[Math.floor(Math.random() * XIAOER_WAYPOINTS.length)];
    }

    function updateXiaoer(now) {
      xiaoer.tick += 1;
      if (phase === 'serve') {
        // 走到客人座旁斟茶
        xiaoer.tx = seatTarget.x - 56;
        xiaoer.ty = seatTarget.y - 12;
        xiaoer.destAct = 'serve';
        if (Math.abs(xiaoer.x - xiaoer.tx) < 3 && Math.abs(xiaoer.y - xiaoer.ty) < 3) {
          xiaoer.mode = 'serve';
        } else {
          xiaoer.mode = 'walk';
        }
        xiaoer.actionTicks = 0;
      } else if (phase === 'enter') {
        // 迎客：走廊中段靠門
        xiaoer.tx = 320;
        xiaoer.ty = 350;
        xiaoer.destAct = 'idle';
        xiaoer.mode = 'walk';
        xiaoer.actionTicks = 0;
      } else if (phase === 'pay') {
        xiaoer.tx = 440;
        xiaoer.ty = 336;
        xiaoer.destAct = 'idle';
        if (Math.abs(xiaoer.x - xiaoer.tx) > 3) xiaoer.mode = 'walk';
        else xiaoer.mode = 'idle';
      } else if (xiaoer.tick % 180 === 0 && phase === 'idle') {
        const wp = pickXiaoerWaypoint();
        xiaoer.tx = wp.x;
        xiaoer.ty = wp.y;
        xiaoer.destAct = wp.act || 'idle';
        xiaoer.mode = 'walk';
        xiaoer.actionTicks = 0;
      } else if (Math.abs(xiaoer.x - xiaoer.tx) < 2 && Math.abs(xiaoer.y - xiaoer.ty) < 2) {
        if (xiaoer.mode === 'walk') {
          xiaoer.mode = xiaoer.destAct || 'idle';
          xiaoer.actionTicks = 0;
        } else if (xiaoer.mode === 'wipe' || xiaoer.mode === 'serve' || xiaoer.mode === 'idle') {
          xiaoer.actionTicks = (xiaoer.actionTicks || 0) + 1;
          const hold = xiaoer.mode === 'wipe' ? 90 : (xiaoer.mode === 'serve' ? 70 : 110);
          if (xiaoer.actionTicks > hold && Math.random() < 0.04) {
            const wp = pickXiaoerWaypoint();
            xiaoer.tx = wp.x;
            xiaoer.ty = wp.y;
            xiaoer.destAct = wp.act || 'idle';
            xiaoer.mode = 'walk';
            xiaoer.actionTicks = 0;
          }
        }
      }
      const dx = xiaoer.tx - xiaoer.x;
      const dy = xiaoer.ty - xiaoer.y;
      if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) {
        // 先橫後直，走走廊感
        if (Math.abs(dx) > 2.4) {
          xiaoer.x += clamp(dx, -2.1, 2.1);
        } else {
          xiaoer.y += clamp(dy, -1.7, 1.7);
          xiaoer.x += clamp(dx, -1.2, 1.2);
        }
        xiaoer.flip = dx < 0;
        if (phase !== 'serve' || Math.abs(dx) > 3 || Math.abs(dy) > 3) {
          xiaoer.mode = 'walk';
        }
      }
    }

    function drawActor(sheetId, x, y, animName, tick, opts) {
      const o = opts || {};
      const sheet = Assets.sheets[sheetId];
      const fi = animFrame(animName, tick, o.speed || (animName === 'walk' ? 7 : 10));
      if (sheet && drawSheetFrame(ctx, sheet, fi, x, y, { scale: o.scale || 1, flip: o.flip, alpha: o.alpha })) {
        return;
      }
      const pal = HERO_COLORS[sheetId] || HERO_COLORS.default;
      drawFigure(ctx, x + 8, y + 4, pal, {
        weapon: weaponFor(sheetId),
        stride: animName === 'walk' ? (Math.floor(tick / 8) % 2) : 0,
        pose: animName === 'serve' ? 'idle' : 'idle',
        arm: animName === 'serve' ? 1 : 0,
        scale: o.scale || 1.1
      });
    }

    function loop(now) {
      if (!running || !ctx || !canvas || !canvas.isConnected) return;
      raf = requestAnimationFrame(loop);
      const elapsed = now - t0;
      idleBlink = (idleBlink + 1) % 90;
      walkerPhase = (walkerPhase + 1) % 240;
      if (accelerateFlash > 0) accelerateFlash -= 1;
      if (bubble) {
        bubble.life -= 0.008;
        if (bubble.life <= 0) bubble = null;
      }
      bubbles = bubbles.filter(function (b) {
        b.life -= 0.007;
        return b.life > 0;
      });
      updateSceneEvent(now);

      maybeEmitAmbient(now);
      updateXiaoer(now);

      if (phase === 'enter') {
        const dur = PHASE_MS.enter;
        doorOpen = clamp(1 - Math.abs(elapsed - dur * 0.35) / (dur * 0.55), 0.15, 1);
        const u = Math.min(1, elapsed / dur);
        // 門→走廊中段→座位（避開 v1.4 密家具）；guest_walk local：0–3 walk｜4–5 approach｜6 彎腰｜7 坐定
        const midX = 470, midY = 364;
        let pathX, pathY;
        if (seatTarget.x <= 280) {
          // 左座：直入
          pathX = 56 + u * (seatTarget.x - 56);
          pathY = 336 + u * (seatTarget.y - 336);
        } else if (u < 0.42) {
          const u1 = u / 0.42;
          pathX = 56 + u1 * (midX - 56);
          pathY = 336 + u1 * (midY - 336);
        } else {
          const u2 = (u - 0.42) / 0.58;
          pathX = midX + u2 * (seatTarget.x - midX);
          pathY = midY + u2 * (seatTarget.y - midY);
        }
        guestX = pathX;
        guestY = pathY;
        guestFlip = false;
        guestSeated = false;
        if (u < 0.62) guestLocal = Math.floor((elapsed / 160) % 4);           // walk 0–3
        else if (u < 0.78) guestLocal = 4 + Math.floor(((u - 0.62) / 0.16) * 2) % 2; // approach 4–5
        else if (u < 0.9) guestLocal = 6;                                     // 彎腰
        else guestLocal = 7;                                                  // 坐定無杯
        guestStride = guestLocal;
        if (elapsed - lastFootstepAt > 280 && u < 0.75) {
          lastFootstepAt = elapsed;
          playSfx('footstep', { volume: 0.45 });
        }
        if (elapsed >= dur) {
          phase = 'serve';
          t0 = now;
          guestX = seatTarget.x;
          guestY = seatTarget.y;
          guestSeated = true;
          guestLocal = 7;
          guestStride = 0;
          doorOpen = 0.08;
          playHubSfx('sit');
          playHubSfx('serve');
          setCaption('小二斟茶遞水…');
          showBubble('請用茶。', xiaoer.x + 16, xiaoer.y - 28, 0.9);
        }
      } else if (phase === 'serve') {
        const dur = PHASE_MS.serve;
        doorOpen = Math.max(0, doorOpen - 0.02);
        staffArm = Math.floor(elapsed / 220) % 2;
        xiaoer.mode = 'serve';
        if (elapsed >= dur) {
          phase = 'pay';
          t0 = now;
          staffArm = 0;
          coinAlpha = 1;
          coinY = 0;
          floatLabel = { text: '+' + payAmt + '兩', x: 500, y: 260, life: 1 };
          playHubSfx('pay');
          setCaption(guestName + ' 付銀 ' + payAmt + ' 兩');
        }
      } else if (phase === 'pay') {
        const dur = PHASE_MS.pay;
        coinY = Math.min(28, elapsed / 22);
        coinAlpha = clamp(1 - elapsed / (dur * 0.9), 0, 1);
        if (floatLabel) {
          floatLabel.y = (floatLabel.y0 != null ? floatLabel.y0 : 260) - elapsed / 50;
          floatLabel.life = clamp(1 - elapsed / dur, 0, 1);
        }
        if (elapsed >= dur) {
          phase = 'leave';
          t0 = now;
          floatLabel = null;
          doorOpen = 0.9;
          lastFootstepAt = 0;
          playHubSfx('leave');
          setCaption(guestName + ' 推門告辭');
        }
      } else if (phase === 'leave') {
        const dur = PHASE_MS.leave;
        doorOpen = clamp(0.3 + Math.sin(Math.min(1, elapsed / dur) * Math.PI) * 0.7, 0.2, 1);
        const u = Math.min(1, elapsed / dur);
        guestSeated = false;
        guestX = seatTarget.x + u * (56 - seatTarget.x);
        guestY = seatTarget.y + u * (336 - seatTarget.y);
        guestFlip = true;
        // 離場：先 approach 起身感 → walk
        if (u < 0.18) guestLocal = 5;
        else if (u < 0.28) guestLocal = 4;
        else guestLocal = Math.floor((elapsed / 150) % 4);
        guestStride = guestLocal;
        if (elapsed - lastFootstepAt > 280 && elapsed < dur * 0.85) {
          lastFootstepAt = elapsed;
          playSfx('footstep', { volume: 0.4 });
        }
        if (elapsed >= dur) startNext();
      } else {
        doorOpen = Math.max(0, doorOpen - 0.03);
        if (floatLabel) {
          floatLabel.life = Math.max(0, (floatLabel.life || 1) - 0.02);
          floatLabel.y = (floatLabel.y || 280) - 0.8;
          if (floatLabel.life <= 0) floatLabel = null;
        }
      }

      if (tipBurst) {
        tipBurst.life -= 1;
        if (tipBurst.life <= 0) tipBurst = null;
      }

      ctx.clearRect(0, 0, W, H);
      const layered = drawBgLayers(now);

      if (accelerateFlash > 0) {
        ctx.globalAlpha = accelerateFlash / 30;
        drawRect(ctx, 300, 290, 360, 100, C.gold);
        ctx.globalAlpha = 1;
      }

      // 坐客：guest_sit v1.2；進場佔用位唔畫，避免重疊
      seatedGuests.forEach(function (g, gi) {
        if (seatOccupiedKey && g.key === seatOccupiedKey) return;
        if (phase !== 'idle' && Math.abs(g.x - guestX) < 20 && Math.abs(g.y - guestY) < 20) return;
        const gsheet = Assets.sheets.guest_sit;
        if (gsheet) {
          const fi = (typeof g.frame === 'number') ? (g.frame % 6) : (gi % 6);
          drawSheetFrame(ctx, gsheet, fi, g.x, g.y - 8, { scale: hubScaleFor('guest_sit') });
        } else {
          drawFigure(ctx, g.x, g.y, { robe: g.robe, accent: C.gold, skin: C.skin, hair: C.inkSoft }, { scale: hubScaleFor('guest_sit') });
        }
      });

      // 小二：idle／walk／serve／wipe（wipe＝幀 9–12，唔當 attack）
      const xeAnim = xiaoer.mode === 'walk' ? 'walk'
        : (xiaoer.mode === 'serve' ? 'serve'
          : (xiaoer.mode === 'wipe' ? 'wipe' : 'idle'));
      drawActor('xiaoer', xiaoer.x, xiaoer.y, xeAnim, xiaoer.tick, {
        flip: xiaoer.flip,
        scale: hubScaleFor('xiaoer'),
        speed: xeAnim === 'wipe' ? 9 : undefined
      });

      // 俠客閒逛（場景事件進行中略收，避免同事件行人撞疊）
      if (!sceneEvt) {
        ambientHeroes.forEach(function (hid, i) {
          const baseX = 110 + i * 72;
          const walk = Math.sin((walkerPhase + i * 40) / 30) * 44;
          const x = baseX + walk;
          const y = 350 + (i % 2) * 16;
          const flipping = Math.cos((walkerPhase + i * 40) / 30) < 0;
          drawActor(hid, x, y, 'walk', walkerPhase + i * 12, { flip: flipping, scale: hubScaleFor(hid) });
        });
      }

      // 場景事件行人
      if (sceneEvt && sceneEvt.walkers) {
        sceneEvt.walkers.forEach(function (w) {
          drawActor(w.id, w.x, w.y, 'walk', w.tick, { flip: w.flip, scale: hubScaleFor(w.id) });
        });
      }

      // 進場客人：guest_walk（absIndex=guestIndex*8+local）→ 入座後 guest_sit 同色加杯
      if (phase !== 'idle') {
        if (guestSeated || phase === 'serve' || phase === 'pay') {
          const gsheet = Assets.sheets.guest_sit;
          if (gsheet) {
            drawSheetFrame(ctx, gsheet, guestFrame % 6, guestX, guestY - 8, { scale: hubScaleFor('guest_sit') });
          } else {
            const robe = guestKind === 'stay' ? C.inkSoft : C.mist;
            drawFigure(ctx, guestX, guestY, { robe: robe, accent: C.gold, skin: C.skin, hair: C.inkSoft }, { scale: hubScaleFor('guest_sit') });
          }
        } else {
          const gwalk = Assets.sheets.guest_walk;
          const absIndex = guestIndex * 8 + (guestLocal % 8);
          if (gwalk) {
            drawSheetFrame(ctx, gwalk, absIndex, guestX, guestY - 8, { scale: hubScaleFor('guest_walk'), flip: guestFlip, alpha: 1 });
          } else {
            const robe = guestKind === 'stay' ? C.inkSoft : C.mist;
            drawFigure(ctx, guestX, guestY, { robe: robe, accent: C.gold, skin: C.skin, hair: C.inkSoft }, {
              stride: guestLocal % 2,
              scale: hubScaleFor('guest_walk')
            });
          }
        }
      } else if (idleBlink < 25) {
        drawRect(ctx, 36, 300, 20, 44, C.inkSoft);
      }

      if (layered) {
        drawLanternsAndNight(now);
        drawForeground(); // z6 最前景（角色／燈籠之後）
      }

      if ((phase === 'pay' || tipBurst) && coinAlpha > 0) {
        const cx = tipBurst ? tipBurst.x : 540;
        const cy = (tipBurst ? tipBurst.y : 320) - coinY;
        drawRect(ctx, cx, cy, 14, 14, C.gold);
        drawRect(ctx, cx + 2, cy + 2, 4, 4, C.cream);
        ctx.globalAlpha = tipBurst ? tipBurst.life / tipBurst.max : coinAlpha;
        drawRect(ctx, (tipBurst ? tipBurst.x - 40 : 460), (tipBurst ? tipBurst.y - 20 : 296), 14, 14, C.gold);
        ctx.globalAlpha = 1;
      }
      if (floatLabel && floatLabel.life > 0) {
        ctx.globalAlpha = floatLabel.life;
        drawPixelText(ctx, floatLabel.text, floatLabel.x, floatLabel.y, C.gold);
        ctx.globalAlpha = 1;
      }
      if (tipBurst) {
        const a = tipBurst.life / tipBurst.max;
        ctx.globalAlpha = a;
        drawRect(ctx, tipBurst.x - 2, tipBurst.y - (28 - tipBurst.life), 6, 6, C.gold);
        ctx.globalAlpha = 1;
      }

      bubbles.forEach(function (b) {
        drawBubble(ctx, b.text, b.x, b.y, b.life);
      });
      if (bubble && !bubbles.length) drawBubble(ctx, bubble.text, bubble.x, bubble.y, bubble.life);

      drawHotspotHints();
    }

    return {
      mount, destroy, isMounted, playGuest, enqueueGuest,
      setHotspotHandler, setSelectedHotspot, setTipHandler, setAmbientHeroes, setInnTitle,
      setAmbientChange, isNight, getTipMul, dayPhaseName, setRumor, greetXiaoer, showBubble, playSceneEvent, resolveSceneChoice, setHintHandler, setChoiceHandler,
      HOTSPOTS, getPhase: function () { return phase; },
      isScenePlaying: function () { return !!(sceneEvt && !sceneEvt.done); }
    };
  })();

  // ——— 戰鬥舞台 960×540（原生對齊 Hub；角色 64×2） ———
  const CombatStage = (function () {
    const W = 960;
    const H = 540;
    /** 戰鬥角色顯示：64→×2（128）；32 橋接→×4；禁止非整數倍 */
    const CHAR_SCALE_64 = 2;
    const CHAR_SCALE_32 = 4;
    let canvas = null;
    let ctx = null;
    let wrapEl = null;
    let raf = 0;
    let running = false;
    let units = [];
    let fx = [];
    let shake = 0;
    let shakeFine = 0;     // 細震層（高頻、短）
    let zoomPulse = 0;     // 整數像素縮放脈衝（>0 時略放大，保持 pixelated）
    let anims = {};
    let tick = 0;
    let hitStop = 0;       // 命中停頓幀（凍結動畫推進）
    let screenFlash = 0;   // 全屏閃白
    let speedMul = 1;      // 對齊戰鬥速度：縮短動畫／hit-stop wall-clock

    function setSpeedMul(mul) {
      let m = Number(mul);
      if (!(m > 0)) m = 1;
      if (m < 0.5) m = 0.5;
      if (m > 2) m = 2;
      speedMul = Math.round(m * 2) / 2;
      return speedMul;
    }
    function getSpeedMul() { return speedMul; }
    function scaleDur(frames) {
      return Math.max(6, Math.round(frames / speedMul));
    }
    function scaleStop(n) {
      return Math.max(3, Math.round(n / speedMul));
    }

    /** v0.9.1 鏡頭：細震→中震分層（全面約半至六成，KO／clash 都唔好太晃） */
    function bumpCamera(tier) {
      // tier: 'light' | 'mid' | 'heavy' | 'ko' | 'clash'
      if (tier === 'light') {
        shakeFine = Math.max(shakeFine, 1.1);
        shake = Math.max(shake, 1.4);
      } else if (tier === 'mid') {
        shakeFine = Math.max(shakeFine, 1.8);
        shake = Math.max(shake, 2.8);
        zoomPulse = Math.max(zoomPulse, 3);
      } else if (tier === 'heavy') {
        shakeFine = Math.max(shakeFine, 2.4);
        shake = Math.max(shake, 4.0);
        zoomPulse = Math.max(zoomPulse, 4);
      } else if (tier === 'clash') {
        shakeFine = Math.max(shakeFine, 2.5);
        shake = Math.max(shake, 3.6);
        zoomPulse = Math.max(zoomPulse, 4);
      } else if (tier === 'ko') {
        shakeFine = Math.max(shakeFine, 2.8);
        shake = Math.max(shake, 5.0);
        zoomPulse = Math.max(zoomPulse, 5);
      }
    }

    function weaponFor(id) {
      if (id === 'qingyi') return 'sword';
      if (id === 'tiezhang') return 'fist';
      if (id === 'langren') return 'blade';
      if (id === 'qinshi') return 'qin';
      if (id && String(id).indexOf('boss') >= 0) return 'blade';
      return 'club';
    }

    function palFor(u) {
      if (u.side === 'enemy') return HERO_COLORS.enemy;
      return HERO_COLORS[u.heroId] || HERO_COLORS.default;
    }

    function layoutSlots(list, side) {
      const n = list.length;
      const baseX = side === 'ally' ? 96 : 600;
      const gap = n <= 1 ? 0 : (n === 2 ? 84 : 72);
      const start = baseX - ((n - 1) * gap) / 2;
      return list.map((u, i) => {
        const x = start + i * gap;
        const y = 270 + (i % 2) * 20;
        return { x, y };
      });
    }

    function mount(host) {
      if (!host) return;
      if (canvas && canvas.isConnected && running && host.contains(canvas.closest('.stage-wrap') || canvas)) {
        return;
      }
      const existing = host.querySelector('.combat-stage-wrap canvas.px-stage');
      if (existing && existing.width === W) {
        wrapEl = existing.closest('.stage-wrap');
        canvas = existing;
        ctx = canvas.getContext('2d');
        ctx.imageSmoothingEnabled = false;
        running = true;
        cancelAnimationFrame(raf);
        loop();
        return;
      }
      host.innerHTML = '';
      wrapEl = document.createElement('div');
      wrapEl.className = 'stage-wrap combat-stage-wrap';
      wrapEl.innerHTML = '<canvas class="px-stage" width="960" height="540" aria-label="戰鬥舞台"></canvas>';
      host.appendChild(wrapEl);
      canvas = wrapEl.querySelector('canvas');
      ctx = canvas.getContext('2d');
      ctx.imageSmoothingEnabled = false;
      running = true;
      units = [];
      fx = [];
      shake = 0;
      anims = {};
      cancelAnimationFrame(raf);
      loop();
    }

    function destroy() {
      running = false;
      cancelAnimationFrame(raf);
      canvas = null;
      ctx = null;
      wrapEl = null;
    }

    function isMounted() { return !!canvas && running && canvas.isConnected; }

    function sync(unitSnap) {
      if (!unitSnap) return;
      const allies = unitSnap.filter((u) => u.side === 'ally');
      const enemies = unitSnap.filter((u) => u.side === 'enemy');
      const aSlots = layoutSlots(allies, 'ally');
      const eSlots = layoutSlots(enemies, 'enemy');
      const next = [];
      allies.forEach((u, i) => {
        const prev = units.find((p) => p.id === u.id);
        const slot = aSlots[i];
        const tx = (u.x != null) ? u.x : slot.x;
        const ty = (u.y != null) ? u.y : slot.y;
        // 平滑跟上邏輯座標；攻擊動畫中暫用 ox 作基準
        let x = tx;
        let y = ty;
        if (prev && !anims[u.id]) {
          x = prev.x + (tx - prev.x) * 0.45;
          y = prev.y + (ty - prev.y) * 0.45;
          if (Math.abs(tx - x) < 1.6) x = tx;
          if (Math.abs(ty - y) < 1.6) y = ty;
        } else if (prev && anims[u.id]) {
          x = prev.x;
          y = prev.y;
        }
        next.push({
          id: u.id,
          name: u.name,
          side: 'ally',
          hp: u.hp,
          maxHp: u.maxHp,
          shield: u.shield || 0,
          heroId: u.id,
          intent: u.intent || 'hold',
          combatState: u.combatState || u.intent || 'idle',
          telegraph: !!u.telegraph,
          ranged: !!u.ranged,
          engage: !!u.engage,
          contact: !!u.contact,
          invuln: u.invuln || 0,
          x: x,
          y: y,
          ox: tx,
          oy: ty,
          flash: prev ? prev.flash : 0,
          dead: u.hp <= 0
        });
      });
      enemies.forEach((u, i) => {
        const prev = units.find((p) => p.id === u.id);
        const slot = eSlots[i];
        let heroId = 'enemy';
        if (u.id && String(u.id).indexOf('boss_heifeng') >= 0) heroId = 'boss_heifeng';
        else if (u.id && String(u.id).indexOf('boss_xieyi') >= 0) heroId = 'boss_xieyi';
        else if (u.id && String(u.id).indexOf('boss_xueying') >= 0) heroId = 'boss_xueying';
        else if (u.name && u.name.indexOf('黑風寨主') >= 0) heroId = 'boss_heifeng';
        else if (u.name && u.name.indexOf('邪醫') >= 0) heroId = 'boss_xieyi';
        else if (u.name && u.name.indexOf('血影樓主') >= 0) heroId = 'boss_xueying';
        const tx = (u.x != null) ? u.x : slot.x;
        const ty = (u.y != null) ? u.y : slot.y;
        let x = tx;
        let y = ty;
        if (prev && !anims[u.id]) {
          x = prev.x + (tx - prev.x) * 0.45;
          y = prev.y + (ty - prev.y) * 0.45;
          if (Math.abs(tx - x) < 1.6) x = tx;
          if (Math.abs(ty - y) < 1.6) y = ty;
        } else if (prev && anims[u.id]) {
          x = prev.x;
          y = prev.y;
        }
        next.push({
          id: u.id,
          name: u.name,
          side: 'enemy',
          hp: u.hp,
          maxHp: u.maxHp,
          shield: u.shield || 0,
          heroId: heroId,
          intent: u.intent || 'hold',
          combatState: u.combatState || u.intent || 'idle',
          telegraph: !!u.telegraph,
          ranged: !!u.ranged,
          engage: !!u.engage,
          contact: !!u.contact,
          invuln: u.invuln || 0,
          x: x,
          y: y,
          ox: tx,
          oy: ty,
          flash: prev ? prev.flash : 0,
          dead: u.hp <= 0
        });
      });
      units = next;
    }

    function playAction(evt) {
      if (!evt) return;
      const atk = units.find((u) => u.id === evt.attackerId);
      const tgt = units.find((u) => u.id === evt.targetId);

      // v0.8：讀招 telegraph
      if (evt.kind === 'windup' && atk) {
        const dir = atk.side === 'ally' ? 1 : -1;
        anims[atk.id] = { kind: 'windup', t: 0, dur: scaleDur(48), dir: dir, ranged: !!evt.ranged };
        atk.flash = Math.max(atk.flash || 0, 12);
        // 讀招 telegraph：金點＋雙層短刀光預兆（比 v0.8.0 更明顯）
        fx.push({
          kind: 'burst', x: atk.x + (dir > 0 ? 22 : -8), y: atk.y + 6,
          life: scaleDur(26), max: scaleDur(26), color: evt.skillName ? C.gold : C.cream
        });
        fx.push({
          kind: 'burst', x: atk.x + (dir > 0 ? 10 : 4), y: atk.y - 8,
          life: scaleDur(18), max: scaleDur(18), color: C.gold
        });
        pushFxSheet('slash', atk.x + (dir > 0 ? 8 : -16), atk.y - 6, {
          flip: dir < 0, dur: scaleDur(18), scale: 1.05
        });
        pushFxSheet('slash', atk.x + (dir > 0 ? 18 : -22), atk.y + 4, {
          flip: dir < 0, dur: scaleDur(14), scale: 0.9
        });
        // v0.9：windup 招名淡出（弱）
        const wuName = evt.skillName ? ('「' + evt.skillName + '」') : '讀招';
        fx.push({
          kind: 'text', text: wuName,
          x: atk.x - 10, y: atk.y - 44, life: scaleDur(42), max: scaleDur(42),
          color: evt.skillName ? C.gold : C.mist,
          soft: true
        });
        return;
      }

      if (evt.kind === 'strike' && atk) {
        const dir = atk.side === 'ally' ? 1 : -1;
        const dx = tgt ? Math.abs(tgt.x - atk.x) : 80;
        const reach = evt.ranged
          ? Math.min(24, Math.max(8, dx * 0.15))
          : Math.min(68, Math.max(28, dx * 0.72 + 12));
        anims[atk.id] = { kind: 'lunge', t: 0, dur: scaleDur(evt.ranged ? 40 : 52), dir: dir, ranged: !!evt.ranged, reach: reach };
        spawnBladeFx(atk, tgt, false, false);
        // v0.9：strike 招名強顯（跟狀態）
        const sn = evt.skillName ? ('「' + evt.skillName + '」') : '判定';
        fx.push({
          kind: 'text', text: sn,
          x: atk.x - 14, y: atk.y - 52, life: scaleDur(50), max: scaleDur(50),
          color: evt.skillName ? C.cinnabarBright : C.cream,
          strong: true
        });
        return;
      }

      if (evt.kind === 'recover' && atk) {
        if (anims[atk.id] && anims[atk.id].kind === 'windup') delete anims[atk.id];
        return;
      }

      if (evt.kind === 'clash') {
        const mx = evt.ax != null ? evt.ax : ((atk && tgt) ? (atk.x + tgt.x) / 2 : 480);
        const my = evt.ay != null ? evt.ay : ((atk && tgt) ? (atk.y + tgt.y) / 2 : 320);
        pushFxSheet('clash', mx - 16, my - 14, { dur: scaleDur(24), scale: 1.7 });
        pushFxSheet('slash', mx - 10, my - 8, { dur: scaleDur(16), scale: 1.25 });
        pushFxSheet('spark', mx - 8, my - 8, { dur: scaleDur(18), scale: 1.45 });
        fx.push({ kind: 'burst', x: mx, y: my, life: scaleDur(18), max: scaleDur(18), color: C.gold });
        fx.push({ kind: 'text', text: '撞刃', x: mx - 16, y: my - 28, life: scaleDur(38), max: scaleDur(38), color: C.gold });
        screenFlash = Math.max(screenFlash, 9);
        hitStop = Math.max(hitStop, scaleStop(16));
        bumpCamera('clash');
        if (atk) atk.flash = Math.max(atk.flash || 0, 14);
        if (tgt) tgt.flash = Math.max(tgt.flash || 0, 14);
        return;
      }

      if (evt.kind === 'heal' || evt.kind === 'shield') {
        if (atk) {
          fx.push({ kind: 'text', text: evt.kind === 'heal' ? ('+' + (evt.heal || 0)) : '盾', x: atk.x + 8, y: atk.y - 16, life: 36, max: 36, color: C.jadeBright });
          atk.flash = 14;
        }
        if (evt.skillName) {
          fx.push({ kind: 'burst', x: (atk ? atk.x : 80) + 12, y: (atk ? atk.y : 200) + 8, life: 22, max: 22, color: C.jade });
          if (atk) {
            fx.push({
              kind: 'trail', x0: atk.x + 12, y0: atk.y + 12, x1: atk.x + 12, y1: atk.y - 20,
              life: 22, max: 22, color: C.jadeBright
            });
          }
        }
        return;
      }

      if (atk && (evt.kind === 'hit' || evt.kind === 'skill' || evt.kind === 'miss' || evt.kind === 'parry')) {
        const dir = atk.side === 'ally' ? 1 : -1;
        const alreadyLunging = anims[atk.id] && anims[atk.id].kind === 'lunge';
        // v0.8：strike 事件已開 lunge；命中事件只補目標／VFX，避免重播亂揮
        if (!alreadyLunging) {
          const dx = tgt ? Math.abs((tgt.x) - (atk.x)) : 80;
          const lungeDur = scaleDur(evt.ranged ? 48 : (dx > 80 ? 56 : 48));
          const reach = evt.ranged
            ? Math.min(24, Math.max(8, dx * 0.15))
            : Math.min(68, Math.max(28, dx * 0.72 + 12));
          anims[atk.id] = { kind: 'lunge', t: 0, dur: lungeDur, dir: dir, ranged: !!evt.ranged, reach: reach };
        }
        if (evt.skillName && !alreadyLunging) {
          fx.push({ kind: 'burst', x: atk.x + 12, y: atk.y + 8, life: 24, max: 24, color: evt.kind === 'skill' ? C.cinnabarBright : C.gold });
          fx.push({ kind: 'text', text: '「' + evt.skillName + '」', x: atk.x - 24, y: atk.y - 40, life: 58, max: 58, color: C.gold });
        }
        const bossBoost = (atk.heroId && String(atk.heroId).indexOf('boss') >= 0)
          || (tgt && tgt.heroId && String(tgt.heroId).indexOf('boss') >= 0);
        if (tgt && (evt.kind === 'hit' || evt.kind === 'skill')) {
          fx.push({
            kind: 'trail',
            x0: atk.x + (dir > 0 ? 28 : -4),
            y0: atk.y + 12,
            x1: tgt.x + 12,
            y1: tgt.y + 12,
            life: 28, max: 28,
            color: evt.kind === 'skill' ? C.cinnabarBright : C.cream
          });
          if (!alreadyLunging || evt.clash) spawnBladeFx(atk, tgt, evt.kind === 'skill', bossBoost);
          else {
            // 判定幀補一層火花／hit_ring
            pushFxSheet('spark', tgt.x, tgt.y, { dur: scaleDur(14), scale: evt.kind === 'skill' ? 1.35 : 1.15 });
            pushFxSheet('hit_ring', tgt.x - 4, tgt.y - 4, { dur: scaleDur(12), scale: 1.2 });
          }
        } else if (evt.kind === 'parry') {
          spawnBladeFx(atk, tgt, false, bossBoost);
        } else if (evt.kind === 'miss' && !evt.whiff) {
          spawnBladeFx(atk, tgt, false, bossBoost);
        }
      }

      if (evt.kind === 'miss') {
        if (evt.whiff && atk) {
          // 揮空：弱刀風（短弧、低 alpha 感）
          const dir = atk.side === 'ally' ? 1 : -1;
          fx.push({
            kind: 'arc', x: atk.x + (dir > 0 ? 28 : -8), y: atk.y + 16, dir: dir,
            r: 36, start: -0.85 * dir, end: 0.55 * dir,
            life: scaleDur(14), max: scaleDur(14),
            color: C.mist, tipColor: C.cream, weak: true
          });
          pushFxSheet('slash', atk.x + (dir > 0 ? 20 : -24), atk.y, {
            flip: dir < 0, dur: scaleDur(12), scale: 0.75
          });
          fx.push({ kind: 'text', text: '空', x: atk.x + 8, y: atk.y - 20, life: scaleDur(28), max: scaleDur(28), color: C.mist });
          bumpCamera('light');
          hitStop = Math.max(hitStop, scaleStop(4));
          return;
        }
        if (tgt) {
          anims[tgt.id] = { kind: 'dodge', t: 0, dur: scaleDur(52), dir: tgt.side === 'ally' ? -1 : 1 };
          fx.push({ kind: 'text', text: '閃', x: tgt.x + 4, y: tgt.y - 12, life: scaleDur(30), max: scaleDur(30), color: C.sky });
          hitStop = Math.max(hitStop, scaleStop(5));
          bumpCamera('light');
        }
        return;
      }

      if (evt.kind === 'parry' && tgt) {
        anims[tgt.id] = { kind: 'parry', t: 0, dur: scaleDur(52), dir: tgt.side === 'ally' ? -1 : 1 };
        if (atk) anims[atk.id] = { kind: 'parry', t: 0, dur: scaleDur(40), dir: atk.side === 'ally' ? 1 : -1 };
        tgt.flash = 16;
        if (atk) atk.flash = Math.max(atk.flash || 0, 10);
        fx.push({ kind: 'text', text: '架', x: tgt.x + 4, y: tgt.y - 12, life: scaleDur(34), max: scaleDur(34), color: C.gold });
        fx.push({ kind: 'slash', x: tgt.x, y: tgt.y + 4, life: scaleDur(20), max: scaleDur(20), color: C.gold });
        // 招架對撞：clash 接觸點＋parry_flash（可錯 0–1 tick）
        if (atk) {
          const mx = (atk.x + tgt.x) / 2 + 4;
          const my = (atk.y + tgt.y) / 2 + 4;
          fx.push({
            kind: 'trail',
            x0: atk.x + 8, y0: atk.y + 6,
            x1: tgt.x + 4, y1: tgt.y + 4,
            life: scaleDur(26), max: scaleDur(26), color: C.gold
          });
          fx.push({
            kind: 'trail',
            x0: mx, y0: my,
            x1: mx + (tgt.side === 'ally' ? -18 : 18), y1: my - 14,
            life: scaleDur(20), max: scaleDur(20), color: C.cream
          });
          fx.push({ kind: 'burst', x: mx, y: my, life: scaleDur(16), max: scaleDur(16), color: C.gold });
          // clash one-shot 喺接觸點
          const clashOk = pushFxSheet('clash', mx - 16, my - 14, { dur: scaleDur(18), scale: 1.35 });
          // parry_flash 錯後 1 tick（delay 用 delayed fx）
          fx.push({ kind: 'fxdelay', wait: 1, id: 'parry_flash', x: mx - 10, y: my - 10, dur: scaleDur(16), scale: 1.3 });
          fx.push({ kind: 'fxdelay', wait: 1, id: 'spark', x: mx - 8, y: my - 8, dur: scaleDur(12), scale: 1.1 });
          const f1 = pushFxSheet('parry_flash', atk.x - 4, atk.y - 6, { dur: scaleDur(16), scale: 1.15, flip: atk.side === 'enemy' });
          const f2 = pushFxSheet('parry_flash', tgt.x - 4, tgt.y - 6, { dur: scaleDur(16), scale: 1.2, flip: tgt.side === 'enemy' });
          if (!clashOk && !f1 && !f2) {
            fx.push({ kind: 'sparks', x: mx, y: my, n: 12, life: scaleDur(22), max: scaleDur(22), color: C.gold });
            fx.push({
              kind: 'arc', x: mx, y: my, dir: atk.side === 'ally' ? 1 : -1,
              r: 18, start: -0.7, end: 0.7, life: scaleDur(16), max: scaleDur(16),
              color: C.gold, tipColor: C.cream
            });
          }
        }
        screenFlash = Math.max(screenFlash, 7);
        hitStop = Math.max(hitStop, scaleStop(16));
        bumpCamera('mid');
        return;
      }

      if ((evt.kind === 'hit' || evt.kind === 'skill') && tgt) {
        const dmg = evt.damage || 0;
        const heavy = evt.kind === 'skill';
        const meleeContact = !evt.ranged && (evt.contact || true);
        anims[tgt.id] = {
          kind: 'hit', t: 0, dur: scaleDur(heavy ? 64 : 56),
          dir: tgt.side === 'ally' ? -1 : 1, heavy: heavy,
          knock: meleeContact ? (heavy ? 28 : 20) : (heavy ? 16 : 10)
        };
        tgt.flash = heavy ? 26 : 20;
        fx.push({ kind: 'text', text: '-' + dmg, x: tgt.x + 4, y: tgt.y - 24, life: scaleDur(56), max: scaleDur(56), color: C.cinnabarBright });
        fx.push({ kind: 'slash', x: tgt.x + 8, y: tgt.y + 8, life: scaleDur(18), max: scaleDur(18), color: C.cream });
        fx.push({ kind: 'burst', x: tgt.x + 12, y: tgt.y + 16, life: scaleDur(14), max: scaleDur(14), color: C.cream });
        // 近身：spark／hit_ring 分層（錯開）
        if (meleeContact && atk) {
          const mx = (atk.x + tgt.x) / 2 - 8;
          const my = (atk.y + tgt.y) / 2 - 10;
          const dir = atk.side === 'ally' ? 1 : -1;
          pushFxSheet('clash', mx, my, { dur: scaleDur(heavy ? 20 : 16), scale: heavy ? 1.5 : 1.32 });
          pushFxSheet('hit_ring', mx + 2, my + 2, { dur: scaleDur(heavy ? 16 : 12), scale: heavy ? 1.4 : 1.22 });
          fx.push({ kind: 'fxdelay', wait: 1, id: 'spark', x: mx + 4, y: my + 4, dur: scaleDur(14), scale: heavy ? 1.35 : 1.2 });
          fx.push({ kind: 'fxdelay', wait: 2, id: 'spark', x: mx - dir * 10, y: my - 6, dur: scaleDur(12), scale: 1.05 });
          fx.push({ kind: 'fxdelay', wait: 1, id: 'hit_ring', x: mx - 6, y: my - 4, dur: scaleDur(10), scale: 0.95 });
          fx.push({
            kind: 'arc', x: mx, y: my, dir: dir,
            r: heavy ? 48 : 38, start: -1.05 * dir, end: 0.85 * dir,
            life: scaleDur(heavy ? 22 : 16), max: scaleDur(heavy ? 22 : 16),
            color: heavy ? C.cinnabarBright : C.cream, tipColor: C.gold
          });
        }
        fx.push({ kind: 'sparks', x: tgt.x + 8, y: tgt.y + 10, n: heavy ? 14 : 9, life: scaleDur(heavy ? 22 : 14), max: scaleDur(heavy ? 22 : 14), color: C.cinnabarBright });
        screenFlash = Math.max(screenFlash, heavy ? 10 : 7);
        hitStop = Math.max(hitStop, scaleStop(heavy ? 18 : 13));
        bumpCamera(heavy ? 'heavy' : 'mid');
      }

      if (evt.kind === 'ko' && tgt) {
        fx.push({ kind: 'text', text: '倒', x: tgt.x + 2, y: tgt.y - 20, life: scaleDur(48), max: scaleDur(48), color: C.blood });
        pushFxSheet('hit_ring', tgt.x - 8, tgt.y, { dur: scaleDur(18), scale: 1.55 });
        fx.push({ kind: 'sparks', x: tgt.x + 8, y: tgt.y + 12, n: 16, life: scaleDur(26), max: scaleDur(26), color: C.blood });
        screenFlash = Math.max(screenFlash, 12);
        hitStop = Math.max(hitStop, scaleStop(20));
        bumpCamera('ko');
        anims[tgt.id] = { kind: 'hit', t: 0, dur: scaleDur(48), dir: tgt.side === 'ally' ? -1 : 1, heavy: true, knock: 32 };
        tgt.flash = 28;
      }
    }

    /** 戰鬥場背景：遠山／地面／木樁旗分層；優先 battle_* PNG，否則硬邊程式畫 */
    function drawBattleProc() {
      // sky
      drawRect(ctx, 0, 0, W, 280, C.sky);
      [[40, 36, 120, 18], [90, 48, 80, 12], [280, 28, 140, 16], [420, 50, 100, 14],
       [560, 34, 160, 18], [720, 44, 110, 12], [820, 30, 90, 16]].forEach(function (b) {
        drawRect(ctx, b[0], b[1], b[2], b[3], C.cream);
        drawRect(ctx, b[0] + 8, b[1] + 10, Math.max(8, b[2] - 20), 8, C.paper);
      });
      drawRect(ctx, 860, 50, 36, 36, C.gold);
      drawRect(ctx, 866, 56, 24, 24, C.sky);
      // mountains (narrowing bands)
      function mountain(bx, py, width, height, col) {
        for (let i = 0; i < height; i++) {
          const t = i / Math.max(1, height - 1);
          const half = Math.max(2, Math.round((width / 2) * (1 - t * 0.92)));
          drawRect(ctx, bx + Math.round(width / 2) - half, py + i, half * 2, 2, col);
        }
      }
      mountain(-40, 130, 280, 150, C.mtn);
      mountain(160, 110, 320, 170, C.jade);
      mountain(400, 125, 300, 155, C.mtn);
      mountain(620, 100, 340, 180, C.jade);
      mountain(780, 135, 260, 145, C.mtn);
      drawRect(ctx, 0, 250, W, 30, C.mist);
      for (let x = 0; x < W; x += 48) drawRect(ctx, x, 258, 28, 8, C.paper);
      // ground
      drawRect(ctx, 0, 270, W, 50, C.loess);
      drawRect(ctx, 0, 310, W, 16, C.woodLight);
      drawRect(ctx, 0, 320, W, 220, C.wood);
      for (let i = 0; i < 14; i++) {
        const x = 20 + i * 70;
        drawRect(ctx, x, 348, 48, 10, C.woodLight);
        drawRect(ctx, x + 4, 358, 40, 4, C.inkSoft);
      }
      drawRect(ctx, 400, 360, 160, 70, C.inkSoft);
      drawRect(ctx, 408, 368, 144, 54, '#5A4A32');
      drawRect(ctx, 420, 380, 120, 30, C.wood);
      drawRect(ctx, 470, 390, 20, 10, C.gold);
      drawRect(ctx, 0, 400, 80, 80, C.night);
      drawRect(ctx, 880, 400, 80, 80, C.night);
      // stakes + flags
      function stake(x, y, h, flag, side) {
        drawRect(ctx, x, y, 8, h, C.wood);
        drawRect(ctx, x + 2, y, 4, h, C.woodLight);
        drawRect(ctx, x - 2, y + h - 6, 12, 8, C.inkSoft);
        if (!flag) return;
        const fy = y + 8;
        if (side === 'L') {
          drawRect(ctx, x + 8, fy, 40, 28, C.cinnabar);
          drawRect(ctx, x + 8, fy, 40, 6, C.cinnabarBright);
          drawRect(ctx, x + 12, fy + 10, 20, 10, C.cream);
        } else {
          drawRect(ctx, x - 40, fy, 40, 28, C.cinnabar);
          drawRect(ctx, x - 40, fy, 40, 6, C.cinnabarBright);
          drawRect(ctx, x - 32, fy + 10, 20, 10, C.gold);
        }
      }
      [[36, 250, 95, true, 'L'], [90, 244, 99, false, 'L'], [150, 238, 103, true, 'L'],
       [870, 250, 95, true, 'R'], [810, 244, 99, false, 'R'], [750, 238, 103, true, 'R']
      ].forEach(function (s) { stake(s[0], s[1], s[2], s[3], s[4]); });
      [280, 480, 680].forEach(function (x) {
        drawRect(ctx, x, 290, 6, 40, C.wood);
        drawRect(ctx, x - 4, 286, 14, 6, C.ink);
      });
      drawRect(ctx, 44, 268, 110, 3, C.inkSoft);
      drawRect(ctx, 760, 268, 110, 3, C.inkSoft);
      [200, 740].forEach(function (x) {
        drawRect(ctx, x, 300, 6, 50, C.wood);
        drawRect(ctx, x - 6, 292, 18, 14, C.cinnabarBright);
        drawRect(ctx, x - 2, 296, 10, 6, C.gold);
      });
    }

    function drawBg() {
      // z-order：sky → mid → ground → props（之後 loop 先畫單位／VFX）
      // 中央站位留白約 x 300–660、y 336–440（精修場景）
      const hasSky = !!Assets.layers.battle_sky;
      if (hasSky) {
        ctx.imageSmoothingEnabled = false;
        BATTLE_LAYERS.forEach(function (name) {
          const img = Assets.layers[name];
          if (img) ctx.drawImage(img, 0, 0, W, H);
        });
        // 若缺 props 層仍補一點旗／樁，避免太空
        if (!Assets.layers.battle_props) {
          drawRect(ctx, 40, 250, 8, 90, C.wood);
          drawRect(ctx, 48, 258, 36, 24, C.cinnabar);
          drawRect(ctx, 900, 250, 8, 90, C.wood);
          drawRect(ctx, 860, 258, 36, 24, C.cinnabar);
        }
      } else {
        drawBattleProc();
      }
    }

    function drawMeleeRing(u) {
      if (!u || u.dead || u.ranged) return;
      const FIELD = (global.WuxiaCombat && global.WuxiaCombat.FIELD) || { meleeRange: 58, contactRange: 38 };
      const r = (FIELD.meleeRange || 58) * 0.5;
      const cx = u.x + 16;
      const cy = u.y + 52;
      const st = u.combatState || u.intent || '';
      const active = u.engage || u.contact || u.telegraph || st === 'approach' || st === 'windup' || st === 'strike' || st === 'hold' || st === 'idle';
      if (!active && !(u.invuln > 0)) return;
      const a = u.telegraph ? 0.7 : ((u.contact || u.engage) ? 0.55 : (u.invuln > 0 ? 0.5 : 0.22));
      ctx.globalAlpha = a;
      const col = u.invuln > 0 ? C.sky : (u.side === 'ally' ? C.jadeBright : C.cinnabarBright);
      for (let i = 0; i < 16; i++) {
        const ang = (i / 16) * Math.PI * 2;
        const x = cx + Math.cos(ang) * r;
        const y = cy + Math.sin(ang) * r * 0.38;
        drawRect(ctx, x, y, 3, 3, col);
      }
      if (u.contact || u.engage) {
        ctx.globalAlpha = Math.min(0.85, a + 0.25);
        const bw = u.contact ? 28 : 24;
        const bh = u.contact ? 40 : 32;
        drawRect(ctx, u.x + 16 - bw / 2, u.y + 12, bw, 3, C.cream);
        drawRect(ctx, u.x + 16 - bw / 2, u.y + 12 + bh, bw, 3, C.cream);
        drawRect(ctx, u.x + 16 - bw / 2, u.y + 12, 3, bh, col);
        drawRect(ctx, u.x + 16 + bw / 2 - 3, u.y + 12, 3, bh, col);
        if (u.contact) {
          drawRect(ctx, u.x + 10, u.y + 28, 12, 8, C.gold);
        }
      }
      ctx.globalAlpha = 1;
    }

    function poseToAnim(pose) {
      if (pose === 'strike') return 'attack';
      if (pose === 'hurt') return 'hurt';
      if (pose === 'parry') return 'parry';
      return 'idle';
    }

    function drawUnit(u) {
      const pal = palFor(u);
      let dx = u.x;
      let dy = u.y;
      const an = anims[u.id];
      let arm = 0;
      let flash = u.flash > 0 || (u.invuln > 0);
      let pose = 'idle';
      let animName = 'idle';
      let frameOverride = null;
      if (an) {
        const p = an.t / an.dur;
        if (an.kind === 'lunge') {
          const reach = an.reach != null ? an.reach : 56;
          const back = an.ranged ? 8 : 16;
          if (p < 0.25) {
            const w = p / 0.25;
            dx = u.ox - an.dir * back * w;
            arm = 0;
            pose = 'idle';
            frameOverride = ANIM.attack[0];
          } else if (p < 0.55) {
            const sp = (p - 0.25) / 0.3;
            dx = u.ox + an.dir * (back * 0.4 + reach * sp);
            arm = 1;
            pose = 'strike';
            frameOverride = ANIM.attack[1 + Math.min(2, Math.floor(sp * 3))];
          } else {
            const rp = (p - 0.55) / 0.45;
            dx = u.ox + an.dir * reach * (1 - rp);
            arm = rp < 0.4 ? 1 : 0;
            pose = rp < 0.35 ? 'strike' : 'idle';
            frameOverride = rp < 0.35 ? ANIM.attack[3] : ANIM.idle[0];
          }
          animName = poseToAnim(pose);
        } else if (an.kind === 'hit') {
          const knock = an.knock != null ? an.knock : (an.heavy ? 28 : 20);
          if (p < 0.18) {
            // 撞開：短推
            dx = u.ox + an.dir * knock * 0.35 * (p / 0.18);
            pose = 'hurt';
            flash = true;
          } else if (p < 0.5) {
            const mid = (p - 0.18) / 0.32;
            dx = u.ox + an.dir * knock * (0.35 + 0.65 * mid);
            dy = u.oy - 10 * Math.sin(mid * Math.PI);
            pose = 'hurt';
            flash = true;
          } else {
            // 彈回／摩擦收束
            const back = (p - 0.5) / 0.5;
            const ease = back * back;
            dx = u.ox + an.dir * knock * (1 - ease);
            pose = 'hurt';
          }
          animName = 'hurt';
          frameOverride = ANIM.hurt[p < 0.5 ? 0 : 1];
        } else if (an.kind === 'dodge') {
          const amp = Math.sin(p * Math.PI);
          dx = u.ox + an.dir * 52 * amp;
          dy = u.oy - 20 * amp;
          flash = p > 0.15 && p < 0.7;
          animName = 'walk';
        } else if (an.kind === 'parry') {
          const amp = Math.sin(p * Math.PI);
          dx = u.ox + an.dir * 20 * amp;
          dy = u.oy - 6 * amp;
          pose = 'parry';
          flash = p > 0.15 && p < 0.65;
          animName = 'parry';
          frameOverride = ANIM.parry[Math.min(2, Math.floor(p * 3))];
        } else if (an.kind === 'windup') {
          dx = u.ox - an.dir * (6 + 4 * Math.sin(p * Math.PI));
          dy = u.oy - 4 * Math.sin(p * Math.PI);
          pose = 'idle';
          animName = 'windup';
          // v0.9：6→7→8 讀招，唔再用 parry／serve 茶盤感
          frameOverride = ANIM.windup[Math.min(2, Math.floor(p * 3))];
          flash = flash || (p > 0.15 && p < 0.9);
        }
      } else {
        const st = u.combatState || u.intent || 'idle';
        if (st === 'approach' || st === 'retreat' || st === 'strafe'
          || u.intent === 'approach' || u.intent === 'retreat' || u.intent === 'strafe') {
          animName = 'walk';
          frameOverride = ANIM.walk[Math.floor(tick / 8) % 4];
        } else if (st === 'windup') {
          animName = 'windup';
          frameOverride = ANIM.windup[Math.floor(tick / 8) % 3];
          flash = true;
        } else if (st === 'strike') {
          animName = 'strike';
          frameOverride = ANIM.strike[1 + (Math.floor(tick / 6) % 3)];
          pose = 'strike';
        } else if (st === 'recover') {
          // 收招偏 strike 尾幀 11–12，再回 idle
          animName = 'strike';
          frameOverride = ANIM.strike[2 + (Math.floor(tick / 10) % 2)];
        } else if (st === 'hurt') {
          animName = 'hurt';
          frameOverride = ANIM.hurt[Math.floor(tick / 8) % 2];
          pose = 'hurt';
          flash = true;
        } else if (st === 'parry') {
          animName = 'parry';
          frameOverride = ANIM.parry[Math.min(2, Math.floor(tick / 8) % 3)];
          pose = 'parry';
        } else if (st === 'dodge') {
          animName = 'walk';
          frameOverride = ANIM.walk[Math.floor(tick / 6) % 4];
        } else {
          frameOverride = ANIM.idle[Math.floor(tick / 18) % 2];
        }
      }

      if (u.dead) ctx.globalAlpha = 0.35;
      if (u.telegraph && !u.dead) {
        ctx.globalAlpha = 0.35;
        drawRect(ctx, dx - 10, dy - 10, 8, 8, C.gold);
        drawRect(ctx, dx + 100, dy - 10, 8, 8, C.gold);
        ctx.globalAlpha = u.dead ? 0.35 : 1;
      }

      const flip = u.side === 'enemy';
      const sheet = Assets.sheets[u.heroId];
      const bossImg = Assets.bosses[u.heroId];
      let drew = false;
      if (sheet) {
        const fi = frameOverride != null ? frameOverride : animFrame(animName, tick, 8);
        const sc = (sheet.height === 64) ? CHAR_SCALE_64 : ((sheet.height === 32) ? CHAR_SCALE_32 : CHAR_SCALE_64);
        const out = (sheet.height === 64 ? 64 : 32) * sc;
        const ox = dx - Math.round(out * 0.12);
        const oy = dy - Math.round(out * 0.12);
        drew = drawSheetFrame(ctx, sheet, fi, ox, oy, {
          scale: sc,
          flip: flip,
          alpha: flash ? 0.95 : (u.dead ? 0.35 : 1)
        });
        if (drew && flash) {
          ctx.globalAlpha = 0.55;
          drawRect(ctx, ox + 8, oy + 8, out - 16, out - 12, C.cream);
          ctx.globalAlpha = 1;
        }
      } else if (bossImg) {
        const bs = bossImg.height || 64;
        const sc = (bs === 64) ? CHAR_SCALE_64 : ((bs === 32) ? CHAR_SCALE_32 : CHAR_SCALE_64);
        const out = bs * sc;
        const ox = dx - Math.round(out * 0.12);
        const oy = dy - Math.round(out * 0.06);
        ctx.save();
        ctx.imageSmoothingEnabled = false;
        if (flash) ctx.globalAlpha = 0.95;
        if (flip) {
          ctx.translate(ox + out, oy);
          ctx.scale(-1, 1);
          ctx.drawImage(bossImg, 0, 0, bs, bs, 0, 0, out, out);
        } else {
          ctx.drawImage(bossImg, 0, 0, bs, bs, ox, oy, out, out);
        }
        ctx.restore();
        drew = true;
      }
      if (!drew) {
        // 通用敵／缺表：加厚色塊剪影（唔冒充精修）＋腳底影
        const isMob = u.side === 'enemy' && (!u.heroId || u.heroId === 'enemy');
        drawRect(ctx, dx + 8, dy + 108, 48, 8, C.ink);
        ctx.globalAlpha = 0.35;
        drawRect(ctx, dx + 4, dy + 112, 56, 6, C.night);
        ctx.globalAlpha = u.dead ? 0.35 : 1;
        drawFigure(ctx, dx, dy, pal, {
          weapon: weaponFor(u.heroId),
          arm: arm,
          flash: flash,
          pose: pose,
          scale: isMob ? 5 : 4,
          bulky: isMob
        });
        if (isMob) {
          // 寬肩／帽簷／腰帶／靴／武器塊：可讀剪影（腳本色塊≠精修成品）
          drawRect(ctx, dx - 4, dy + 18, 60, 14, pal.robe);
          drawRect(ctx, dx + 4, dy + 6, 44, 10, pal.hair || C.ink);
          drawRect(ctx, dx + 14, dy + 10, 6, 4, C.cream); // 帽簷高光 1 塊
          drawRect(ctx, dx + 8, dy + 46, 40, 8, pal.accent || C.cinnabar);
          drawRect(ctx, dx + 12, dy + 70, 14, 10, C.inkSoft); // 左靴
          drawRect(ctx, dx + 30, dy + 70, 14, 10, C.inkSoft); // 右靴
          drawRect(ctx, dx + 50, dy + 24, 22, 8, pal.accent || C.cinnabarBright); // 橫刀
          drawRect(ctx, dx + 48, dy + 22, 6, 12, C.woodLight); // 刀柄
        }
      }
      ctx.globalAlpha = 1;

      // 場內 HUD：厚血條＋外框＋狀態晶片（唔用大塊 HTML）
      const bw = 80;
      const bh = 10;
      const barX = dx - 10;
      const barY = dy - 28;
      const pct = u.maxHp > 0 ? clamp(u.hp / u.maxHp, 0, 1) : 0;
      drawRect(ctx, barX - 2, barY - 2, bw + 4, bh + 4, C.ink);
      drawRect(ctx, barX, barY, bw, bh, C.night);
      drawRect(ctx, barX, barY, Math.max(0, Math.round(bw * pct)), bh, u.side === 'ally' ? C.jadeBright : C.cinnabarBright);
      if (pct > 0 && pct < 1) drawRect(ctx, barX + Math.round(bw * pct) - 2, barY, 2, bh, C.cream);
      if (u.shield > 0) {
        drawRect(ctx, barX, barY - 6, Math.min(bw, 10 + Math.round(u.shield / u.maxHp * bw)), 4, C.sky);
      }
      // 狀態：W 讀招／S 出招／H 受傷／P 架／D 閃／! 接觸
      const st = u.combatState || u.intent || '';
      let chip = null;
      let chipCol = C.gold;
      if (st === 'windup' || u.telegraph) { chip = 'W'; chipCol = C.gold; }
      else if (st === 'strike') { chip = 'S'; chipCol = C.cinnabarBright; }
      else if (st === 'hurt') { chip = 'H'; chipCol = C.blood; }
      else if (st === 'parry') { chip = 'P'; chipCol = C.gold; }
      else if (st === 'dodge') { chip = 'D'; chipCol = C.sky; }
      else if (u.contact) { chip = '!'; chipCol = C.cream; }
      if (chip) {
        drawRect(ctx, barX + bw + 4, barY - 2, 14, 14, C.ink);
        drawRect(ctx, barX + bw + 6, barY, 10, 10, chipCol);
        drawPixelText(ctx, chip, barX + bw + 7, barY + 1, C.ink);
      }
      drawPixelText(ctx, u.name.slice(0, 4), dx - 4, dy + 118, C.cream);
      if (u.maxHp > 0) {
        drawPixelText(ctx, String(Math.max(0, Math.round(u.hp))), barX, barY - 12, u.side === 'ally' ? C.jadeBright : C.cinnabarBright);
      }
    }

    function drawTrail(f) {
      const a = f.life / f.max;
      const steps = 6;
      for (let i = 0; i < steps; i++) {
        const tt = i / (steps - 1);
        const x = f.x0 + (f.x1 - f.x0) * tt;
        const y = f.y0 + (f.y1 - f.y0) * tt;
        ctx.globalAlpha = a * (0.3 + 0.7 * tt);
        const sz = 2 + Math.round(3 * tt);
        drawRect(ctx, x, y, sz, Math.max(2, sz - 1), f.color || C.cream);
      }
      ctx.globalAlpha = 1;
    }

    /** 斬擊弧線／刀光（canvas 像素塊近似弧，硃紅／宣紙白） */
    function drawArc(f) {
      const a = f.life / f.max;
      const dir = f.dir || 1;
      const cx = f.x;
      const cy = f.y;
      const r = f.r || 22;
      const start = f.start != null ? f.start : (-0.9 * dir);
      const end = f.end != null ? f.end : (0.55 * dir);
      const steps = f.weak ? 8 : 14;
      for (let i = 0; i < steps; i++) {
        const tt = i / (steps - 1);
        const ang = start + (end - start) * tt;
        const x = cx + Math.cos(ang) * r * dir;
        const y = cy + Math.sin(ang) * r * 0.55;
        const baseA = f.weak ? 0.18 : 0.28;
        ctx.globalAlpha = a * (baseA + (f.weak ? 0.45 : 0.72) * tt);
        const col = (i >= steps - 3) ? (f.tipColor || C.cream) : (f.color || C.cinnabarBright);
        const sz = f.weak ? (i >= steps - 2 ? 3 : 2) : (i >= steps - 2 ? 5 : (2 + Math.round(tt * 3)));
        drawRect(ctx, x, y, sz, Math.max(2, sz - 1), col);
        if (i >= steps - 4) {
          drawRect(ctx, x - 1, y + 1, 2, 2, C.cream);
        }
      }
      ctx.globalAlpha = 1;
    }

    /** 招架／命中火花粒子 */
    function drawSparks(f) {
      const a = f.life / f.max;
      const n = f.n || 6;
      for (let i = 0; i < n; i++) {
        const ang = (i / n) * Math.PI * 2 + (1 - a) * 0.8;
        const dist = (1 - a) * (10 + (i % 3) * 4);
        const x = f.x + Math.cos(ang) * dist;
        const y = f.y + Math.sin(ang) * dist * 0.7;
        ctx.globalAlpha = a * (0.5 + 0.5 * ((i % 2)));
        drawRect(ctx, x, y, 2 + (i % 2), 2, (i % 2) ? C.cream : (f.color || C.cinnabarBright));
      }
      ctx.globalAlpha = 1;
    }

    function pushFxSheet(id, x, y, opts) {
      const o = opts || {};
      const meta = FX_SHEETS[id];
      const img = Assets.fx[id];
      if (!img || !meta) return false;
      const frames = meta.frames;
      const dur = o.dur != null ? o.dur : Math.max(10, frames * 3);
      fx.push({
        kind: 'fxsheet',
        id: id,
        x: x, y: y,
        frames: frames,
        t: 0,
        dur: dur,
        life: dur,
        max: dur,
        flip: !!o.flip,
        scale: o.scale || 1
      });
      return true;
    }

    function spawnBladeFx(atk, tgt, heavy, bossBoost) {
      if (!atk) return;
      const dir = atk.side === 'ally' ? 1 : -1;
      const boss = !!bossBoost || (atk.heroId && String(atk.heroId).indexOf('boss') >= 0)
        || (tgt && tgt.heroId && String(tgt.heroId).indexOf('boss') >= 0);
      const ax = atk.x + (dir > 0 ? 20 : -12);
      const ay = atk.y + 8;
      const sMul = boss ? 1.4 : 1;
      // 跟面向：多段 slash 沿揮砍方向拉開弧長
      const usedSlash = pushFxSheet('slash', ax, ay - 8, {
        flip: dir < 0,
        dur: heavy ? 20 : 14,
        scale: (heavy ? 1.35 : 1.15) * sMul
      });
      pushFxSheet('slash', ax + dir * 18, ay - 2, {
        flip: dir < 0,
        dur: heavy ? 26 : 18,
        scale: (heavy ? 1.55 : 1.32) * sMul
      });
      pushFxSheet('slash', ax + dir * 34, ay + 6, {
        flip: dir < 0,
        dur: heavy ? 18 : 14,
        scale: (heavy ? 1.28 : 1.1) * sMul
      });
      if (heavy || boss) {
        pushFxSheet('slash', ax + dir * 48, ay - 10, {
          flip: dir < 0,
          dur: 16,
          scale: (boss ? 1.65 : 1.35) * sMul
        });
      }
      // 永遠補 canvas 弧（同 sheet 疊加，弧更長跟面向）
      fx.push({
        kind: 'arc',
        x: atk.x + (dir > 0 ? 24 : -4), y: atk.y + 18,
        dir: dir,
        r: (heavy ? 52 : 40) * (boss ? 1.2 : 1),
        start: -1.25 * dir,
        end: 0.95 * dir,
        life: heavy ? 28 : 20,
        max: heavy ? 28 : 20,
        color: heavy ? C.cinnabarBright : C.cinnabar,
        tipColor: C.cream
      });
      fx.push({
        kind: 'arc',
        x: atk.x + (dir > 0 ? 30 : -8), y: atk.y + 10,
        dir: dir,
        r: (heavy ? 36 : 28) * (boss ? 1.15 : 1),
        start: -0.7 * dir,
        end: 1.05 * dir,
        life: heavy ? 22 : 16,
        max: heavy ? 22 : 16,
        color: C.cream,
        tipColor: C.gold
      });
      if (!usedSlash) { /* sheet 缺失時弧已足夠 */ }
      if (tgt) {
        const hx = tgt.x + 4;
        const hy = tgt.y + 8;
        pushFxSheet('spark', hx, hy, { dur: heavy ? 18 : 14, scale: (heavy ? 1.45 : 1.22) * sMul });
        pushFxSheet('spark', hx - dir * 8, hy - 6, { dur: heavy ? 14 : 10, scale: 1.1 * sMul });
        pushFxSheet('hit_ring', hx - 6, hy - 6, { dur: heavy ? 16 : 12, scale: (heavy ? 1.4 : 1.18) * sMul });
        fx.push({ kind: 'fxdelay', wait: 1, id: 'spark', x: hx + dir * 6, y: hy - 10, dur: scaleDur(12), scale: 1.15 * sMul });
        fx.push({ kind: 'fxdelay', wait: 1, id: 'hit_ring', x: hx - 2, y: hy + 2, dur: scaleDur(10), scale: 1.05 * sMul });
        if (boss) {
          pushFxSheet('spark', hx + dir * 8, hy - 12, { dur: 16, scale: 1.55 });
        }
        fx.push({
          kind: 'sparks',
          x: tgt.x + 10, y: tgt.y + 14,
          n: (heavy ? 14 : 9) + (boss ? 6 : 0),
          life: heavy ? 24 : 16,
          max: heavy ? 24 : 16,
          color: C.cinnabarBright
        });
        const mx = (atk.x + tgt.x) / 2 + 2;
        const my = (atk.y + tgt.y) / 2 + 6;
        pushFxSheet('spark', mx - 8, my - 8, { dur: 12, scale: 1.18 * sMul });
        fx.push({ kind: 'burst', x: mx, y: my, life: heavy ? 16 : 12, max: heavy ? 16 : 12, color: C.cream });
      }
    }

    function loop() {
      if (!running || !ctx || !canvas || !canvas.isConnected) return;
      raf = requestAnimationFrame(loop);
      tick += 1;

      const frozen = hitStop > 0;
      if (hitStop > 0) hitStop -= 1;
      if (screenFlash > 0) screenFlash -= 1;

      Object.keys(anims).forEach((id) => {
        if (!frozen) anims[id].t += 1;
        if (anims[id].t >= anims[id].dur) delete anims[id];
      });
      units.forEach((u) => {
        if (!frozen && u.flash > 0) u.flash -= 1;
        if (!anims[u.id]) {
          u.x = u.ox;
          u.y = u.oy;
        }
      });
      // 延遲觸發嘅 FX（clash 錯開 spark／parry_flash 0–1 tick）
      const spawned = [];
      fx.forEach((f) => {
        if (f.kind !== 'fxdelay') return;
        if (frozen) return;
        f.wait = (f.wait || 0) - 1;
        if (f.wait <= 0) {
          pushFxSheet(f.id, f.x, f.y, { dur: f.dur, scale: f.scale || 1, flip: f.flip });
          f.life = 0;
        }
      });
      fx = fx.filter((f) => {
        if (f.kind === 'fxdelay') return (f.life == null || f.life > 0) && (f.wait == null || f.wait > 0);
        // 定格單位，但刀光／火花／軌跡繼續播，先睇到碰撞
        const keepFx = f.kind === 'fxsheet' || f.kind === 'sparks' || f.kind === 'slash'
          || f.kind === 'arc' || f.kind === 'burst' || f.kind === 'trail';
        if (!frozen || keepFx) {
          f.life -= 1;
          if (f.kind === 'fxsheet') f.t = (f.t || 0) + 1;
          if (f.kind === 'text') f.y -= frozen ? 0.1 : 0.32;
        }
        return f.life > 0;
      });
      if (shake > 0) shake = Math.max(0, shake - (frozen ? 0.05 : 0.18));
      if (shakeFine > 0) shakeFine = Math.max(0, shakeFine - (frozen ? 0.08 : 0.28));
      if (zoomPulse > 0) zoomPulse = Math.max(0, zoomPulse - (frozen ? 0.15 : 0.45));
      if (wrapEl) {
        // 中震：wrap 位移；細震：更高頻、更短
        const amp = Math.min(7, shake * 1.35);
        const fine = Math.min(2.5, shakeFine * 0.95);
        const sx = (shake > 0 ? ((Math.round(shake * 2) % 2 === 0) ? amp : -amp) : 0)
          + (shakeFine > 0 ? ((tick % 2 === 0) ? fine : -fine) : 0);
        const sy = (shake > 0 ? ((Math.round(shake * 3) % 2 === 0) ? amp * 0.55 : -amp * 0.55) : 0)
          + (shakeFine > 0 ? ((tick % 3 === 0) ? fine * 0.6 : -fine * 0.4) : 0);
        wrapEl.style.transform = 'translate(' + Math.round(sx) + 'px,' + Math.round(sy) + 'px)';
      }

      ctx.clearRect(0, 0, W, H);
      // 整數像素 zoom pulse：以場心為準，放大 0／2／4 px 等效（scale 用整數偏移裁切感）
      const zPix = zoomPulse > 0 ? Math.min(4, Math.round(zoomPulse / 2) * 2) : 0;
      if (zPix > 0) {
        ctx.save();
        ctx.imageSmoothingEnabled = false;
        const zx = Math.round(zPix / 2);
        const zy = Math.round(zPix / 2);
        // 以中心放大：先平移再近似放大（用 drawImage 自身 canvas 太重；改為座標縮放整數）
        ctx.translate(-zx, -zy);
        // 無平滑：放大係透過多畫邊距錯覺；真正 scale 用整數 1+（zPix/W）近似唔穩，改用 clip 外擴
      }
      drawBg();
      const sorted = units.slice().sort((a, b) => a.y - b.y);
      sorted.forEach(drawMeleeRing);
      sorted.forEach(drawUnit);

      fx.forEach((f) => {
        const a = f.life / f.max;
        if (f.kind === 'fxsheet') {
          const img = Assets.fx[f.id];
          if (!img) return;
          const frames = f.frames || 1;
          const fi = Math.min(frames - 1, Math.floor((f.t || 0) / Math.max(1, f.dur / frames)));
          const dx = f.x;
          const dy = f.y;
          const sc = (f.scale || 1) * 2; // 960 場：VFX 整數倍放大
          const dw = 32 * sc;
          const dh = 32 * sc;
          ctx.save();
          ctx.imageSmoothingEnabled = false;
          ctx.globalAlpha = clamp(a * 1.1, 0, 1);
          if (f.flip) {
            ctx.translate(dx + dw, dy);
            ctx.scale(-1, 1);
            ctx.drawImage(img, fi * 32, 0, 32, 32, 0, 0, dw, dh);
          } else {
            ctx.drawImage(img, fi * 32, 0, 32, 32, dx, dy, dw, dh);
          }
          ctx.restore();
          ctx.globalAlpha = 1;
          return;
        }
        if (f.kind === 'trail') {
          drawTrail(f);
          return;
        }
        if (f.kind === 'arc') {
          drawArc(f);
          return;
        }
        if (f.kind === 'sparks') {
          drawSparks(f);
          return;
        }
        ctx.globalAlpha = clamp(a, 0, 1);
        if (f.kind === 'text') {
          let ta = a;
          if (f.soft) ta = a * a;           // 讀招：更快淡出
          if (f.strong) ta = Math.min(1, a * 1.25 + 0.15); // 判定：更醒目
          ctx.globalAlpha = clamp(ta, 0, 1);
          if (f.strong) {
            drawRect(ctx, f.x - 2, f.y - 1, Math.min(120, 8 + String(f.text).length * 7), 12, C.ink);
          }
          drawPixelText(ctx, f.text, f.x, f.y, f.color || C.cream);
          ctx.globalAlpha = 1;
        } else if (f.kind === 'burst') {
          drawRect(ctx, f.x - 5, f.y - 5, 12, 12, f.color || C.gold);
          drawRect(ctx, f.x - 2, f.y - 2, 6, 6, C.cream);
        } else if (f.kind === 'slash') {
          // 十字刃光＋斜切（墨點硬邊，加厚一輪）
          drawRect(ctx, f.x - 4, f.y + 3, 22, 3, f.color || C.cream);
          drawRect(ctx, f.x + 5, f.y - 6, 3, 20, f.color || C.cinnabarBright);
          drawRect(ctx, f.x - 1, f.y, 16, 2, C.cinnabarBright);
          drawRect(ctx, f.x + 1, f.y + 7, 14, 2, C.cream);
          drawRect(ctx, f.x + 10, f.y - 2, 8, 2, C.gold);
        }
        ctx.globalAlpha = 1;
      });

      // 命中全屏閃白（短、硬邊像素感）
      if (screenFlash > 0) {
        ctx.globalAlpha = Math.min(0.55, screenFlash / 10);
        drawRect(ctx, 0, 0, W, H, C.cream);
        ctx.globalAlpha = 1;
      }
      // zoom pulse：用整數像素外框／中心十字暗示「拉近」，避免非整數 CSS scale 糊邊
      if (zPix > 0) {
        const inset = zPix;
        ctx.globalAlpha = Math.min(0.45, zPix / 10);
        drawRect(ctx, inset, inset, W - inset * 2, 2, C.cream);
        drawRect(ctx, inset, H - inset - 2, W - inset * 2, 2, C.cream);
        drawRect(ctx, inset, inset, 2, H - inset * 2, C.cream);
        drawRect(ctx, W - inset - 2, inset, 2, H - inset * 2, C.cream);
        ctx.globalAlpha = 1;
        ctx.restore();
      }
    }

    function resetIdle() {
      units = [];
      fx = [];
      anims = {};
      shake = 0;
      shakeFine = 0;
      zoomPulse = 0;
      hitStop = 0;
      screenFlash = 0;
      if (wrapEl) wrapEl.style.transform = '';
    }

    return { mount, destroy, isMounted, sync, playAction, resetIdle, setSpeedMul, getSpeedMul, W, H };
  })();

  global.WuxiaStages = {
    Inn: InnStage,
    Combat: CombatStage,
    COLORS: C,
    Assets: Assets
  };
})(typeof window !== 'undefined' ? window : globalThis);
