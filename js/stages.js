/**
 * 俠客棧 — 墨點江湖舞台（v0.5.7：場景江湖事件／命中停頓／藏書熱點／坐客去重）
 * Hub 480×270：場景分層、小二／俠客 spritesheet；戰鬥 400×180：attack／hurt／parry 幀
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
    serve:  [6, 7, 8],
    attack: [9, 10, 11, 12], // 俠客攻擊；xiaoer 同幀位＝wipe（見下）
    wipe:   [9, 10, 11, 12], // 僅 xiaoer：抹枱（唔係 attack）
    hurt:   [13, 14],
    parry:  [15, 16, 17]
  };

  const SHEET_IDS = ['qingyi', 'tiezhang', 'langren', 'qinshi', 'xiaoer'];
  const LAYER_ORDER = ['hub_wall', 'hub_floor', 'hub_furniture', 'hub_counter'];
  const LAYER_TOP = ['hub_lanterns'];

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
    hit_ring: { frames: 3 }
  };

  /** 資產快取戳：跟 GAME.version 對齊，確保 v1.2.1 精靈表換檔後瀏覽器重拉 */
  const ASSET_VER = (typeof global !== 'undefined' && global.WuxiaData && global.WuxiaData.GAME && global.WuxiaData.GAME.version)
    ? global.WuxiaData.GAME.version
    : '0.5.7';

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
      jobs.push(loadImg('assets/sprites/' + id + '.png').then(function (img) {
        if (img) Assets.sheets[id] = img;
      }));
    });
    ['boss_heifeng', 'boss_xieyi'].forEach(function (id) {
      jobs.push(loadImg('assets/sprites/' + id + '_combat.png').then(function (img) {
        if (img) Assets.bosses[id] = img;
      }));
    });
    jobs.push(loadImg('assets/sprites/guest_sit.png').then(function (img) {
      if (img) Assets.sheets.guest_sit = img;
    }));
    jobs.push(loadImg('assets/sprites/guest_walk.png').then(function (img) {
      if (img) Assets.sheets.guest_walk = img;
    }));
    LAYER_ORDER.concat(LAYER_TOP).forEach(function (name) {
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

  function drawSheetFrame(ctx, img, frameIndex, dx, dy, opts) {
    if (!img) return false;
    const o = opts || {};
    const scale = o.scale || 1;
    const flip = !!o.flip;
    const dw = FRAME * scale;
    const dh = FRAME * scale;
    const sx = (frameIndex | 0) * FRAME;
    const ox = Math.round(dx);
    const oy = Math.round(dy);
    ctx.save();
    if (o.alpha != null) ctx.globalAlpha = o.alpha;
    if (flip) {
      ctx.translate(ox + dw, oy);
      ctx.scale(-1, 1);
      ctx.drawImage(img, sx, 0, FRAME, FRAME, 0, 0, dw, dh);
    } else {
      ctx.drawImage(img, sx, 0, FRAME, FRAME, ox, oy, dw, dh);
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
    const bx = Math.round(clamp(x - tw / 2, 4, 480 - tw - 4));
    const by = Math.round(clamp(y, 4, 240));
    ctx.globalAlpha = clamp(life, 0, 1);
    drawRect(ctx, bx, by, tw, 14, C.night);
    drawRect(ctx, bx + 1, by + 1, tw - 2, 12, C.paper);
    drawPixelText(ctx, t, bx + 4, by + 3, C.ink);
    ctx.globalAlpha = 1;
  }

  // ——— 客棧 Hub 舞台（v0.5.7 · Hub v1.3 · 480×270） ———
  const InnStage = (function () {
    const W = 480;
    const H = 270;
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
    let guestX = 40;
    let guestY = 175;
    let guestStride = 0;
    let idleBlink = 0;
    let hoverId = null;
    let hotspotHandler = null;
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
    let xiaoer = { x: 220, y: 175, tx: 220, ty: 175, mode: 'idle', tick: 0, flip: false, actionTicks: 0, destAct: 'idle' };
    let guestFrame = 0;       // guest_sit 幀 0–5（入座後）
    let guestIndex = 0;       // guest_walk 0–3（對齊 sit 0–3）
    let guestLocal = 0;       // guest_walk local 0–7
    let guestFlip = false;
    let guestSeated = false;
    let seatTarget = { x: 228, y: 188 };
    let seatOccupiedKey = null; // 進場佔用嘅座位 key，畫坐客時跳過
    const PHASE_MS = { enter: 1800, serve: 1800, pay: 1400, leave: 1600 };
    const ALL_SEATS = [
      { x: 54, y: 198, key: 'a' }, { x: 108, y: 206, key: 'b' }, { x: 168, y: 212, key: 'c' },
      { x: 248, y: 214, key: 'd' }, { x: 318, y: 200, key: 'e' }, { x: 378, y: 208, key: 'f' }
    ];

    // Hub v1.3 熱點對齊 assets/scenes/README.md（480×270）
    const HOTSPOTS = [
      { id: 'door',     label: '大門·出巡',   x: 6,   y: 82,  w: 48,  h: 68, open: 'combat' },
      { id: 'board',    label: '告示·江湖',   x: 108, y: 92,  w: 44,  h: 28, open: 'story' },
      { id: 'books',    label: '書架·藏書',   x: 108, y: 120, w: 40,  h: 42, open: 'library' },
      { id: 'counter',  label: '櫃檯·經營',   x: 153, y: 163, w: 184, h: 57, open: 'inn' },
      { id: 'map',      label: '地圖·據點',   x: 362, y: 91,  w: 46,  h: 53, open: 'outposts' },
      { id: 'heroes',   label: '俠客席·養成', x: 338, y: 178, w: 72,  h: 34, open: 'heroes' },
      { id: 'tableA',   label: '雅座·小費',   x: 48,  y: 198, w: 86,  h: 46, open: 'table' },
      { id: 'tableB',   label: '雅座·加急',   x: 200, y: 208, w: 86,  h: 46, open: 'table' },
      { id: 'tableC',   label: '雅座·小費',   x: 318, y: 192, w: 90,  h: 48, open: 'table' }
    ];

    // 走廊 195–275,160–250 ＋ 枱間抹枱點
    const XIAOER_WAYPOINTS = [
      { x: 210, y: 168, act: 'idle' },   // 走廊上
      { x: 240, y: 200, act: 'wipe' },   // 中枱
      { x: 255, y: 220, act: 'wipe' },   // 走廊下
      { x: 200, y: 155, act: 'serve' },  // 櫃前
      { x: 90,  y: 200, act: 'wipe' },   // 左枱
      { x: 340, y: 198, act: 'wipe' },   // 右枱近俠客席
      { x: 280, y: 175, act: 'serve' },  // 走廊中
      { x: 190, y: 148, act: 'idle' }    // 櫃後
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
        '<canvas class="px-stage hub-canvas" width="480" height="270" aria-label="客棧內部主場景" tabindex="0"></canvas>' +
        '<div class="stage-caption" id="inn-stage-cap">客棧內部 · 點擊場景熱點開啟功能</div>';
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
    function setTipHandler(fn) { tipHandler = typeof fn === 'function' ? fn : null; }
    function setAmbientHeroes(ids) {
      ambientHeroes = Array.isArray(ids) && ids.length ? ids.slice(0, 4) : ['qingyi'];
    }
    function setInnTitle(name) { innTitle = name || '俠客棧'; }
    function setAmbientChange(fn) { ambientHandler = typeof fn === 'function' ? fn : null; }

    function showBubble(text, x, y, life) {
      const b = { text: text, x: x == null ? 220 : x, y: y == null ? 120 : y, life: life == null ? 1 : life };
      bubble = b;
      bubbles.push(Object.assign({}, b));
      if (bubbles.length > 5) bubbles.shift();
    }

    function pushBubble(text, x, y, life) {
      bubbles.push({ text: text, x: x == null ? 220 : x, y: y == null ? 120 : y, life: life == null ? 1 : life });
      if (bubbles.length > 6) bubbles.shift();
    }

    /** 場景化江湖事件：Hub 內多泡泡＋短暫行人演出（唔淨對話面板） */
    function playSceneEvent(def) {
      if (!def || !def.beats || !def.beats.length) return;
      const walkers = (def.walkers || [
        { id: 'langren', x: 40, y: 170, tx: 120, ty: 178 },
        { id: 'qingyi', x: 160, y: 178, tx: 100, ty: 172 }
      ]).map(function (w) {
        return {
          id: w.id || 'langren',
          x: w.x, y: w.y,
          tx: w.tx != null ? w.tx : w.x,
          ty: w.ty != null ? w.ty : w.y,
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
        done: false
      };
      if (def.caption) setCaption(def.caption);
    }

    function updateSceneEvent(now) {
      if (!sceneEvt || sceneEvt.done) return;
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
            ? sceneEvt.walkers[beat.walker].x + 10
            : (beat.x != null ? beat.x : 200);
          const wy = beat.walker != null && sceneEvt.walkers[beat.walker]
            ? sceneEvt.walkers[beat.walker].y - 16
            : (beat.y != null ? beat.y : 120);
          pushBubble(beat.line, wx, wy, beat.life != null ? beat.life : 1.15);
        }
        if (beat.move && sceneEvt.walkers[beat.move.i]) {
          const w = sceneEvt.walkers[beat.move.i];
          if (beat.move.tx != null) w.tx = beat.move.tx;
          if (beat.move.ty != null) w.ty = beat.move.ty;
        }
        if (beat.end) {
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
      if (rumorText) showBubble('傳聞：' + rumorText, 240, 28, 1.2);
    }

    function greetXiaoer(line) {
      const msg = line || '客官裏面請！';
      showBubble(msg, xiaoer.x + 16, xiaoer.y - 18, 1.15);
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
      return df >= 0.55 && df < 0.92;
    }

    function isNight() { return isNightNow(performance.now()); }

    function maybeEmitAmbient(now) {
      const night = isNightNow(now);
      if (lastNightFlag === night) return;
      lastNightFlag = night;
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
        const tip = 1 + Math.floor(Math.random() * 4);
        tipBurst = { x: cx, y: cy, life: 24, max: 24, amt: tip };
        floatLabel = { text: '+' + tip + '賞', x: cx - 8, y: cy - 10, life: 1 };
        if (tipHandler) tipHandler(tip, 'rush');
        setCaption('雅座加賞 ' + tip + ' 兩');
        return;
      }
      const tip = 1 + Math.floor(Math.random() * 3);
      tipBurst = { x: cx, y: cy, life: 28, max: 28, amt: tip };
      floatLabel = { text: '+' + tip + '賞', x: cx - 8, y: cy - 12, life: 1 };
      coinAlpha = 1;
      coinY = 0;
      if (tipHandler) tipHandler(tip, 'table');
      setCaption('雅座客人賞銀 ' + tip + ' 兩');
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
      // guest_walk：guestIndex 0–3＝teal／robe-red／ink-soft／violet（對齊 guest_sit 0–3）
      guestIndex = Math.floor(Math.random() * 4);
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
        return !(Math.abs(g.x - pick.x) < 8 && Math.abs(g.y - pick.y) < 8);
      });
      guestX = 28;
      guestY = 168;
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
      showBubble('客官裏面請！', xiaoer.x + 10, xiaoer.y - 16, 1);
      xiaoer.mode = 'walk';
      xiaoer.tx = 160;
      xiaoer.ty = 175;
      xiaoer.destAct = 'idle';
    }

    function seedSeated() {
      // 只放 2–3 位常駐坐客，留空位畀進場動畫，避免重疊
      seatedGuests = [
        { x: 54, y: 198, robe: C.teal, frame: 0, key: 'a' },
        { x: 248, y: 214, robe: C.violet, frame: 3, key: 'd' },
        { x: 378, y: 208, robe: C.mist, frame: 5, key: 'f' }
      ];
      seatOccupiedKey = null;
    }

    function dayFactor(now) {
      return (now / 90000) % 1;
    }

    function skyTintFactor(now) {
      const df = dayFactor(now);
      let skyT = 0;
      if (df < 0.25) skyT = df / 0.25 * 0.3;
      else if (df < 0.55) skyT = 0.3 + (df - 0.25) / 0.3 * 0.4;
      else if (df < 0.75) skyT = 0.7 + (df - 0.55) / 0.2 * 0.3;
      else skyT = 1 - (df - 0.75) / 0.25 * 0.85;
      return skyT;
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
        drawRect(ctx, 14, 108, 36, 42, C.cream);
        ctx.globalAlpha = 1;
      } else {
        ctx.globalAlpha = 0.25;
        drawRect(ctx, 14, 108, 36, 42, C.night);
        ctx.globalAlpha = 1;
      }
      // 匾額標題條（覆蓋字畫區上方中央）
      const tw = Math.min(160, 16 + innTitle.length * 14);
      drawRect(ctx, (W - tw) / 2, 4, tw, 12, C.inkSoft);
      drawRect(ctx, (W - tw) / 2 + 2, 6, tw - 4, 8, C.blood);
      drawPixelText(ctx, innTitle, (W - tw) / 2 + 8, 6, C.cream);
      return true;
    }

    function drawLanternsAndNight(now) {
      const img = Assets.layers.hub_lanterns;
      if (img) ctx.drawImage(img, 0, 0);
      const skyT = skyTintFactor(now);
      if (skyT > 0.55) {
        ctx.globalAlpha = (skyT - 0.55) * 0.28;
        drawRect(ctx, 0, 0, W, H, C.night);
        ctx.globalAlpha = 1;
      }
    }

    function drawBgFallback(now) {
      const skyT = skyTintFactor(now);
      const skyCol = lerpColor(C.sky, C.night, clamp((skyT - 0.35) / 0.65, 0, 1));
      const wallCol = lerpColor(C.wood, C.night, clamp((skyT - 0.5) / 0.5 * 0.35, 0, 0.35));
      drawRect(ctx, 0, 0, W, 100, wallCol);
      drawRect(ctx, 0, 0, W, 22, C.night);
      drawRect(ctx, 0, 96, W, 6, C.inkSoft);
      drawRect(ctx, 28, 32, 54, 42, skyCol);
      drawRect(ctx, 0, 102, W, H - 102, C.loess);
      drawRect(ctx, 150, 155, 180, 36, C.wood);
      drawRect(ctx, 12, 102, 48, 55, C.night);
    }

    function drawHotspotHints() {
      HOTSPOTS.forEach(function (h) {
        const on = hoverId === h.id;
        const isTable = h.open === 'table';
        if (on) {
          ctx.globalAlpha = isTable ? 0.32 : 0.38;
          drawRect(ctx, h.x, h.y, h.w, h.h, isTable ? C.jadeBright : C.gold);
          ctx.globalAlpha = 1;
          drawRect(ctx, h.x, h.y, h.w, 2, C.cream);
          drawRect(ctx, h.x, h.y + h.h - 2, h.w, 2, C.cream);
          drawRect(ctx, h.x, h.y, 2, h.h, C.cream);
          drawRect(ctx, h.x + h.w - 2, h.y, 2, h.h, C.cream);
          drawPixelText(ctx, h.label, h.x + 4, Math.max(8, h.y - 12), C.cream);
        } else if (!isTable) {
          // 主熱點：半透明提示框，易睇易點
          ctx.globalAlpha = 0.16;
          drawRect(ctx, h.x, h.y, h.w, h.h, C.gold);
          ctx.globalAlpha = 0.7;
          drawRect(ctx, h.x, h.y, h.w, 1, C.cream);
          drawRect(ctx, h.x, h.y + h.h - 1, h.w, 1, C.cream);
          drawRect(ctx, h.x, h.y, 1, h.h, C.cream);
          drawRect(ctx, h.x + h.w - 1, h.y, 1, h.h, C.cream);
          ctx.globalAlpha = 0.85;
          drawRect(ctx, h.x + 2, h.y + 2, 5, 5, C.gold);
          ctx.globalAlpha = 1;
        } else {
          ctx.globalAlpha = 0.35;
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
        xiaoer.tx = seatTarget.x - 28;
        xiaoer.ty = seatTarget.y - 6;
        xiaoer.destAct = 'serve';
        if (Math.abs(xiaoer.x - xiaoer.tx) < 3 && Math.abs(xiaoer.y - xiaoer.ty) < 3) {
          xiaoer.mode = 'serve';
        } else {
          xiaoer.mode = 'walk';
        }
        xiaoer.actionTicks = 0;
      } else if (phase === 'enter') {
        // 迎客：走廊中段靠門
        xiaoer.tx = 160;
        xiaoer.ty = 175;
        xiaoer.destAct = 'idle';
        xiaoer.mode = 'walk';
        xiaoer.actionTicks = 0;
      } else if (phase === 'pay') {
        xiaoer.tx = 220;
        xiaoer.ty = 168;
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
        if (Math.abs(dx) > 1.2) {
          xiaoer.x += clamp(dx, -1.05, 1.05);
        } else {
          xiaoer.y += clamp(dy, -0.85, 0.85);
          xiaoer.x += clamp(dx, -0.6, 0.6);
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
        // 門→走廊→座位；guest_walk local：0–3 walk｜4–5 approach｜6 彎腰｜7 坐定
        guestX = 28 + u * (seatTarget.x - 28);
        guestY = 168 + u * (seatTarget.y - 168);
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
          showBubble('請用茶。', xiaoer.x + 8, xiaoer.y - 14, 0.9);
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
          floatLabel = { text: '+' + payAmt + '兩', x: 250, y: 130, life: 1 };
          playHubSfx('pay');
          setCaption(guestName + ' 付銀 ' + payAmt + ' 兩');
        }
      } else if (phase === 'pay') {
        const dur = PHASE_MS.pay;
        coinY = Math.min(28, elapsed / 22);
        coinAlpha = clamp(1 - elapsed / (dur * 0.9), 0, 1);
        if (floatLabel) {
          floatLabel.y = (floatLabel.y0 != null ? floatLabel.y0 : 130) - elapsed / 50;
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
        guestX = seatTarget.x + u * (28 - seatTarget.x);
        guestY = seatTarget.y + u * (168 - seatTarget.y);
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
          floatLabel.y = (floatLabel.y || 140) - 0.4;
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
        drawRect(ctx, 150, 145, 180, 50, C.gold);
        ctx.globalAlpha = 1;
      }

      // 坐客：guest_sit v1.2；進場佔用位唔畫，避免重疊
      seatedGuests.forEach(function (g, gi) {
        if (seatOccupiedKey && g.key === seatOccupiedKey) return;
        if (phase !== 'idle' && Math.abs(g.x - guestX) < 10 && Math.abs(g.y - guestY) < 10) return;
        const gsheet = Assets.sheets.guest_sit;
        if (gsheet) {
          const fi = (typeof g.frame === 'number') ? (g.frame % 6) : (gi % 6);
          drawSheetFrame(ctx, gsheet, fi, g.x, g.y - 4, { scale: 1 });
        } else {
          drawFigure(ctx, g.x, g.y, { robe: g.robe, accent: C.gold, skin: C.skin, hair: C.inkSoft }, { scale: 1 });
        }
      });

      // 小二：idle／walk／serve／wipe（wipe＝幀 9–12，唔當 attack）
      const xeAnim = xiaoer.mode === 'walk' ? 'walk'
        : (xiaoer.mode === 'serve' ? 'serve'
          : (xiaoer.mode === 'wipe' ? 'wipe' : 'idle'));
      drawActor('xiaoer', xiaoer.x, xiaoer.y, xeAnim, xiaoer.tick, {
        flip: xiaoer.flip,
        scale: 1,
        speed: xeAnim === 'wipe' ? 9 : undefined
      });

      // 俠客閒逛（場景事件進行中略收，避免同事件行人撞疊）
      if (!sceneEvt) {
        ambientHeroes.forEach(function (hid, i) {
          const baseX = 55 + i * 36;
          const walk = Math.sin((walkerPhase + i * 40) / 30) * 22;
          const x = baseX + walk;
          const y = 175 + (i % 2) * 8;
          const flipping = Math.cos((walkerPhase + i * 40) / 30) < 0;
          drawActor(hid, x, y, 'walk', walkerPhase + i * 12, { flip: flipping, scale: 1 });
        });
      }

      // 場景事件行人
      if (sceneEvt && sceneEvt.walkers) {
        sceneEvt.walkers.forEach(function (w) {
          drawActor(w.id, w.x, w.y, 'walk', w.tick, { flip: w.flip, scale: 1 });
        });
      }

      // 進場客人：guest_walk（absIndex=guestIndex*8+local）→ 入座後 guest_sit 同色加杯
      if (phase !== 'idle') {
        if (guestSeated || phase === 'serve' || phase === 'pay') {
          const gsheet = Assets.sheets.guest_sit;
          if (gsheet) {
            drawSheetFrame(ctx, gsheet, guestFrame % 6, guestX, guestY - 4, { scale: 1 });
          } else {
            const robe = guestKind === 'stay' ? C.inkSoft : C.mist;
            drawFigure(ctx, guestX, guestY, { robe: robe, accent: C.gold, skin: C.skin, hair: C.inkSoft }, { scale: 1.1 });
          }
        } else {
          const gwalk = Assets.sheets.guest_walk;
          const absIndex = guestIndex * 8 + (guestLocal % 8);
          if (gwalk) {
            drawSheetFrame(ctx, gwalk, absIndex, guestX, guestY - 4, { scale: 1, flip: guestFlip, alpha: 1 });
          } else {
            const robe = guestKind === 'stay' ? C.inkSoft : C.mist;
            drawFigure(ctx, guestX, guestY, { robe: robe, accent: C.gold, skin: C.skin, hair: C.inkSoft }, {
              stride: guestLocal % 2,
              scale: 1.15
            });
          }
        }
      } else if (idleBlink < 25) {
        drawRect(ctx, 18, 150, 10, 22, C.inkSoft);
      }

      if (layered) drawLanternsAndNight(now);

      if ((phase === 'pay' || tipBurst) && coinAlpha > 0) {
        const cx = tipBurst ? tipBurst.x : 270;
        const cy = (tipBurst ? tipBurst.y : 160) - coinY;
        drawRect(ctx, cx, cy, 7, 7, C.gold);
        drawRect(ctx, cx + 1, cy + 1, 2, 2, C.cream);
        ctx.globalAlpha = tipBurst ? tipBurst.life / tipBurst.max : coinAlpha;
        drawRect(ctx, (tipBurst ? tipBurst.x - 20 : 230), (tipBurst ? tipBurst.y - 10 : 148), 7, 7, C.gold);
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
      setHotspotHandler, setTipHandler, setAmbientHeroes, setInnTitle,
      setAmbientChange, isNight, setRumor, greetXiaoer, showBubble, playSceneEvent,
      HOTSPOTS, getPhase: function () { return phase; },
      isScenePlaying: function () { return !!(sceneEvt && !sceneEvt.done); }
    };
  })();

  // ——— 戰鬥舞台 400×180 ———
  const CombatStage = (function () {
    const W = 400;
    const H = 180;
    let canvas = null;
    let ctx = null;
    let wrapEl = null;
    let raf = 0;
    let running = false;
    let units = [];
    let fx = [];
    let shake = 0;
    let anims = {};
    let tick = 0;
    let hitStop = 0;       // 命中停頓幀（凍結動畫推進）
    let screenFlash = 0;   // 全屏閃白

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
      const baseX = side === 'ally' ? 48 : 300;
      const gap = n <= 1 ? 0 : (n === 2 ? 42 : 36);
      const start = baseX - ((n - 1) * gap) / 2;
      return list.map((u, i) => {
        const x = start + i * gap;
        const y = 108 + (i % 2) * 8;
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
      wrapEl.innerHTML = '<canvas class="px-stage" width="400" height="180" aria-label="戰鬥舞台"></canvas>';
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
        next.push({
          id: u.id,
          name: u.name,
          side: 'ally',
          hp: u.hp,
          maxHp: u.maxHp,
          shield: u.shield || 0,
          heroId: u.id,
          x: prev && !anims[u.id] ? prev.x : slot.x,
          y: slot.y,
          ox: slot.x,
          oy: slot.y,
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
        else if (u.name && u.name.indexOf('黑風寨主') >= 0) heroId = 'boss_heifeng';
        else if (u.name && u.name.indexOf('邪醫') >= 0) heroId = 'boss_xieyi';
        next.push({
          id: u.id,
          name: u.name,
          side: 'enemy',
          hp: u.hp,
          maxHp: u.maxHp,
          shield: u.shield || 0,
          heroId: heroId,
          x: prev && !anims[u.id] ? prev.x : slot.x,
          y: slot.y,
          ox: slot.x,
          oy: slot.y,
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

      if (evt.kind === 'heal' || evt.kind === 'shield') {
        if (atk) {
          fx.push({ kind: 'text', text: evt.kind === 'heal' ? ('+' + (evt.heal || 0)) : '盾', x: atk.x + 4, y: atk.y - 8, life: 36, max: 36, color: C.jadeBright });
          atk.flash = 14;
        }
        if (evt.skillName) {
          fx.push({ kind: 'burst', x: (atk ? atk.x : 40) + 6, y: (atk ? atk.y : 80) + 4, life: 22, max: 22, color: C.jade });
          if (atk) {
            fx.push({
              kind: 'trail', x0: atk.x + 6, y0: atk.y + 6, x1: atk.x + 6, y1: atk.y - 10,
              life: 22, max: 22, color: C.jadeBright
            });
          }
        }
        return;
      }

      if (atk && (evt.kind === 'hit' || evt.kind === 'skill' || evt.kind === 'miss' || evt.kind === 'parry')) {
        const dir = atk.side === 'ally' ? 1 : -1;
        anims[atk.id] = { kind: 'lunge', t: 0, dur: 64, dir: dir };
        if (evt.skillName) {
          fx.push({ kind: 'burst', x: atk.x + 6, y: atk.y + 4, life: 24, max: 24, color: evt.kind === 'skill' ? C.cinnabarBright : C.gold });
          fx.push({ kind: 'text', text: '「' + evt.skillName + '」', x: atk.x - 12, y: atk.y - 20, life: 58, max: 58, color: C.gold });
        }
        if (tgt && (evt.kind === 'hit' || evt.kind === 'skill')) {
          fx.push({
            kind: 'trail',
            x0: atk.x + (dir > 0 ? 14 : -2),
            y0: atk.y + 6,
            x1: tgt.x + 6,
            y1: tgt.y + 6,
            life: 28, max: 28,
            color: evt.kind === 'skill' ? C.cinnabarBright : C.cream
          });
          spawnBladeFx(atk, tgt, evt.kind === 'skill');
        } else if (evt.kind === 'parry' || evt.kind === 'miss') {
          // 揮空／招架亦見刀弧
          spawnBladeFx(atk, tgt, false);
        }
      }

      if (evt.kind === 'miss' && tgt) {
        anims[tgt.id] = { kind: 'dodge', t: 0, dur: 40, dir: tgt.side === 'ally' ? -1 : 1 };
        fx.push({ kind: 'text', text: '閃', x: tgt.x + 2, y: tgt.y - 6, life: 30, max: 30, color: C.sky });
        hitStop = Math.max(hitStop, 4);
        return;
      }

      if (evt.kind === 'parry' && tgt) {
        anims[tgt.id] = { kind: 'parry', t: 0, dur: 52, dir: tgt.side === 'ally' ? -1 : 1 };
        tgt.flash = 16;
        if (atk) atk.flash = Math.max(atk.flash || 0, 8);
        fx.push({ kind: 'text', text: '架', x: tgt.x + 2, y: tgt.y - 6, life: 34, max: 34, color: C.gold });
        fx.push({ kind: 'slash', x: tgt.x, y: tgt.y + 2, life: 20, max: 20, color: C.gold });
        // 招架火花軌跡：攻防之間＋外彈
        if (atk) {
          const mx = (atk.x + tgt.x) / 2 + 4;
          const my = (atk.y + tgt.y) / 2 + 4;
          fx.push({
            kind: 'trail',
            x0: atk.x + 8, y0: atk.y + 6,
            x1: tgt.x + 4, y1: tgt.y + 4,
            life: 26, max: 26, color: C.gold
          });
          fx.push({
            kind: 'trail',
            x0: mx, y0: my,
            x1: mx + (tgt.side === 'ally' ? -18 : 18), y1: my - 14,
            life: 20, max: 20, color: C.cream
          });
          fx.push({ kind: 'burst', x: mx, y: my, life: 16, max: 16, color: C.gold });
          if (!pushFxSheet('parry_flash', mx - 8, my - 8, { dur: 14, scale: 1.1 })) {
            fx.push({ kind: 'sparks', x: mx, y: my, n: 9, life: 20, max: 20, color: C.gold });
            fx.push({
              kind: 'arc', x: mx, y: my, dir: atk.side === 'ally' ? 1 : -1,
              r: 16, start: -0.6, end: 0.6, life: 14, max: 14,
              color: C.gold, tipColor: C.cream
            });
          }
        }
        screenFlash = Math.max(screenFlash, 5);
        hitStop = Math.max(hitStop, 10);
        shake = Math.max(shake, 2.2);
        return;
      }

      if ((evt.kind === 'hit' || evt.kind === 'skill') && tgt) {
        const dmg = evt.damage || 0;
        const heavy = evt.kind === 'skill';
        anims[tgt.id] = { kind: 'hit', t: 0, dur: heavy ? 64 : 56, dir: tgt.side === 'ally' ? -1 : 1, heavy: heavy };
        tgt.flash = heavy ? 26 : 20;
        fx.push({ kind: 'text', text: '-' + dmg, x: tgt.x + 2, y: tgt.y - 4, life: 52, max: 52, color: C.cinnabarBright });
        fx.push({ kind: 'slash', x: tgt.x + 4, y: tgt.y + 4, life: 18, max: 18, color: C.cream });
        fx.push({ kind: 'burst', x: tgt.x + 6, y: tgt.y + 8, life: 12, max: 12, color: C.cream });
        // spark／hit_ring 已由 spawnBladeFx 處理；無 sheet 時補 canvas
        if (!Assets.fx.spark) {
          fx.push({ kind: 'sparks', x: tgt.x + 8, y: tgt.y + 10, n: heavy ? 8 : 5, life: heavy ? 18 : 12, max: heavy ? 18 : 12, color: C.cinnabarBright });
        }
        screenFlash = Math.max(screenFlash, heavy ? 9 : 6);
        hitStop = Math.max(hitStop, heavy ? 12 : 8);
        shake = Math.max(shake, heavy ? 6.2 : 3.8);
      }

      if (evt.kind === 'ko' && tgt) {
        fx.push({ kind: 'text', text: '倒', x: tgt.x + 2, y: tgt.y - 8, life: 44, max: 44, color: C.blood });
        shake = Math.max(shake, 7);
        screenFlash = Math.max(screenFlash, 10);
        hitStop = Math.max(hitStop, 14);
        anims[tgt.id] = { kind: 'hit', t: 0, dur: 48, dir: tgt.side === 'ally' ? -1 : 1, heavy: true };
        tgt.flash = 28;
      }
    }

    function drawBg() {
      drawRect(ctx, 0, 0, W, 85, C.sky);
      drawRect(ctx, 0, 55, 70, 40, C.mtn);
      drawRect(ctx, 50, 48, 80, 46, C.jade);
      drawRect(ctx, 250, 52, 90, 42, C.mtn);
      drawRect(ctx, 310, 42, 70, 52, C.jade);
      drawRect(ctx, 0, 85, W, 22, C.loess);
      drawRect(ctx, 0, 107, W, 73, C.wood);
      for (let i = 0; i < 10; i++) {
        drawRect(ctx, 12 + i * 40, 114, 18, 3, C.woodLight);
      }
      drawRect(ctx, 196, 92, 6, 6, C.cinnabar);
      drawRect(ctx, 194, 100, 10, 2, C.ink);
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
      let flash = u.flash > 0;
      let pose = 'idle';
      let animName = 'idle';
      let frameOverride = null;
      if (an) {
        const p = an.t / an.dur;
        if (an.kind === 'lunge') {
          if (p < 0.25) {
            const w = p / 0.25;
            dx = u.ox - an.dir * 8 * w;
            arm = 0;
            pose = 'idle';
            frameOverride = ANIM.attack[0];
          } else if (p < 0.55) {
            const sp = (p - 0.25) / 0.3;
            dx = u.ox + an.dir * (8 + 20 * sp);
            arm = 1;
            pose = 'strike';
            frameOverride = ANIM.attack[1 + Math.min(2, Math.floor(sp * 3))];
          } else {
            const rp = (p - 0.55) / 0.45;
            dx = u.ox + an.dir * 28 * (1 - rp);
            arm = rp < 0.4 ? 1 : 0;
            pose = rp < 0.35 ? 'strike' : 'idle';
            frameOverride = rp < 0.35 ? ANIM.attack[3] : ANIM.idle[0];
          }
          animName = poseToAnim(pose);
        } else if (an.kind === 'hit') {
          const heavy = an.heavy ? 1.35 : 1;
          if (p < 0.2) {
            dx = u.ox + an.dir * 3 * (p / 0.2) * heavy;
            pose = 'hurt';
            flash = true;
          } else if (p < 0.55) {
            const mid = (p - 0.2) / 0.35;
            dx = u.ox + an.dir * (3 + 12 * mid) * heavy;
            dy = u.oy - 3 * Math.sin(mid * Math.PI);
            pose = 'hurt';
            flash = true;
          } else {
            const back = (p - 0.55) / 0.45;
            dx = u.ox + an.dir * 15 * (1 - back) * heavy;
            pose = 'hurt';
          }
          animName = 'hurt';
          frameOverride = ANIM.hurt[p < 0.5 ? 0 : 1];
        } else if (an.kind === 'dodge') {
          const amp = Math.sin(p * Math.PI);
          dx = u.ox + an.dir * 14 * amp;
          dy = u.oy - 6 * amp;
          animName = 'walk';
        } else if (an.kind === 'parry') {
          const amp = Math.sin(p * Math.PI);
          dx = u.ox + an.dir * 4 * amp;
          pose = 'parry';
          flash = p > 0.2 && p < 0.55;
          animName = 'parry';
          frameOverride = ANIM.parry[Math.min(2, Math.floor(p * 3))];
        }
      } else {
        frameOverride = ANIM.idle[Math.floor(tick / 18) % 2];
      }

      if (u.dead) ctx.globalAlpha = 0.35;

      const flip = u.side === 'enemy';
      const sheet = Assets.sheets[u.heroId];
      const bossImg = Assets.bosses[u.heroId];
      let drew = false;
      if (sheet) {
        const fi = frameOverride != null ? frameOverride : animFrame(animName, tick, 8);
        drew = drawSheetFrame(ctx, sheet, fi, dx - 4, dy - 4, {
          scale: 1.15,
          flip: flip,
          alpha: flash ? 0.95 : (u.dead ? 0.35 : 1)
        });
        if (drew && flash) {
          ctx.globalAlpha = 0.55;
          drawRect(ctx, dx - 2, dy - 2, 28, 30, C.cream);
          ctx.globalAlpha = 1;
        }
      } else if (bossImg) {
        ctx.save();
        if (flash) ctx.globalAlpha = 0.95;
        if (flip) {
          ctx.translate(dx + 28, dy - 2);
          ctx.scale(-1, 1);
          ctx.drawImage(bossImg, 0, 0, 32, 32, 0, 0, 36, 36);
        } else {
          ctx.drawImage(bossImg, 0, 0, 32, 32, dx - 4, dy - 2, 36, 36);
        }
        ctx.restore();
        drew = true;
      }
      if (!drew) {
        drawFigure(ctx, dx, dy, pal, {
          weapon: weaponFor(u.heroId),
          arm: arm,
          flash: flash,
          pose: pose,
          scale: 1.15
        });
      }
      ctx.globalAlpha = 1;

      const bw = 32;
      const pct = u.maxHp > 0 ? clamp(u.hp / u.maxHp, 0, 1) : 0;
      drawRect(ctx, dx - 8, dy - 8, bw, 4, C.night);
      drawRect(ctx, dx - 8, dy - 8, Math.round(bw * pct), 4, u.side === 'ally' ? C.jadeBright : C.cinnabarBright);
      drawRect(ctx, dx - 8, dy - 8, bw, 1, C.ink);
      if (u.shield > 0) {
        drawRect(ctx, dx - 8, dy - 10, Math.min(bw, 4 + Math.round(u.shield / u.maxHp * bw)), 2, C.sky);
      }
      drawPixelText(ctx, u.name.slice(0, 4), dx - 6, dy + 28, C.cream);
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
      const steps = 10;
      for (let i = 0; i < steps; i++) {
        const tt = i / (steps - 1);
        const ang = start + (end - start) * tt;
        const x = cx + Math.cos(ang) * r * dir;
        const y = cy + Math.sin(ang) * r * 0.55;
        ctx.globalAlpha = a * (0.25 + 0.75 * tt);
        const col = (i >= steps - 3) ? (f.tipColor || C.cream) : (f.color || C.cinnabarBright);
        const sz = i >= steps - 2 ? 4 : (2 + Math.round(tt * 2));
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

    function spawnBladeFx(atk, tgt, heavy) {
      if (!atk) return;
      const dir = atk.side === 'ally' ? 1 : -1;
      const ax = atk.x + (dir > 0 ? 10 : -2);
      const ay = atk.y + 2;
      // 優先用 slash.png 精靈；冇檔先 canvas 弧
      const usedSlash = pushFxSheet('slash', ax, ay, {
        flip: dir < 0,
        dur: heavy ? 22 : 16,
        scale: heavy ? 1.15 : 1
      });
      if (!usedSlash) {
        fx.push({
          kind: 'arc',
          x: atk.x + (dir > 0 ? 12 : 0), y: atk.y + 8,
          dir: dir,
          r: heavy ? 28 : 22,
          start: -1.05 * dir,
          end: 0.7 * dir,
          life: heavy ? 26 : 18,
          max: heavy ? 26 : 18,
          color: heavy ? C.cinnabarBright : C.cinnabar,
          tipColor: C.cream
        });
      }
      if (tgt) {
        const hx = tgt.x + 4;
        const hy = tgt.y + 4;
        const usedSpark = pushFxSheet('spark', hx, hy, { dur: heavy ? 16 : 12 });
        if (!usedSpark) {
          fx.push({
            kind: 'sparks',
            x: tgt.x + 8, y: tgt.y + 10,
            n: heavy ? 8 : 5,
            life: heavy ? 18 : 12,
            max: heavy ? 18 : 12,
            color: C.cinnabarBright
          });
        }
        pushFxSheet('hit_ring', hx - 2, hy - 2, { dur: 12 });
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
      fx = fx.filter((f) => {
        if (!frozen) {
          f.life -= 1;
          if (f.kind === 'fxsheet') f.t = (f.t || 0) + 1;
          if (f.kind === 'text') f.y -= 0.32;
        }
        return f.life > 0;
      });
      if (shake > 0) shake = Math.max(0, shake - (frozen ? 0.04 : 0.16));
      if (wrapEl) {
        const amp = Math.min(8, shake * 1.4);
        const sx = shake > 0 ? (Math.round(shake * 2) % 2 === 0 ? amp : -amp) : 0;
        const sy = shake > 0 ? (Math.round(shake * 3) % 2 === 0 ? amp * 0.5 : -amp * 0.5) : 0;
        wrapEl.style.transform = 'translate(' + Math.round(sx) + 'px,' + Math.round(sy) + 'px)';
      }

      ctx.clearRect(0, 0, W, H);
      drawBg();
      const sorted = units.slice().sort((a, b) => a.y - b.y);
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
          const sc = f.scale || 1;
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
          drawPixelText(ctx, f.text, f.x, f.y, f.color || C.cream);
        } else if (f.kind === 'burst') {
          drawRect(ctx, f.x - 5, f.y - 5, 12, 12, f.color || C.gold);
          drawRect(ctx, f.x - 2, f.y - 2, 6, 6, C.cream);
        } else if (f.kind === 'slash') {
          // 十字刃光＋斜切（墨點硬邊）
          drawRect(ctx, f.x - 2, f.y + 4, 18, 2, f.color || C.cream);
          drawRect(ctx, f.x + 6, f.y - 4, 2, 16, f.color || C.cinnabarBright);
          drawRect(ctx, f.x, f.y, 12, 2, C.cinnabarBright);
          drawRect(ctx, f.x + 2, f.y + 6, 10, 2, C.cream);
        }
        ctx.globalAlpha = 1;
      });

      // 命中全屏閃白（短、硬邊像素感）
      if (screenFlash > 0) {
        ctx.globalAlpha = Math.min(0.55, screenFlash / 10);
        drawRect(ctx, 0, 0, W, H, C.cream);
        ctx.globalAlpha = 1;
      }
    }

    function resetIdle() {
      units = [];
      fx = [];
      anims = {};
      shake = 0;
      hitStop = 0;
      screenFlash = 0;
      if (wrapEl) wrapEl.style.transform = '';
    }

    return { mount, destroy, isMounted, sync, playAction, resetIdle, W, H };
  })();

  global.WuxiaStages = {
    Inn: InnStage,
    Combat: CombatStage,
    COLORS: C,
    Assets: Assets
  };
})(typeof window !== 'undefined' ? window : globalThis);
