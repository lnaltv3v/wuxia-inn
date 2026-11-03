/**
 * 俠客棧 — 墨點江湖舞台（v0.5.1）
 * Hub 480×270：雅座／門／日夜色溫；戰鬥 400×180：多幀攻受、招架、技能軌跡
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

  /** 極簡 12×16 剪影小人（墨點江湖） */
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
    const pose = o.pose || 'idle'; // idle | parry | strike

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

  // ——— 客棧 Hub 舞台（v0.5.1 · 480×270） ———
  const InnStage = (function () {
    const W = 480;
    const H = 270;
    /** 狀態機：idle → enter → serve → pay → leave → idle */
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
    let guestX = 450;
    let guestY = 168;
    let guestStride = 0;
    let idleBlink = 0;
    let hoverId = null;
    let hotspotHandler = null;
    let tipHandler = null;
    let ambientHeroes = ['qingyi'];
    let innTitle = '俠客棧';
    let walkerPhase = 0;
    let seatedGuests = [];
    let doorOpen = 0; // 0..1
    let tipBurst = null;
    let accelerateFlash = 0;

    const HOTSPOTS = [
      { id: 'counter',  label: '櫃檯·經營',  x: 150, y: 145, w: 180, h: 55, open: 'inn' },
      { id: 'heroes',   label: '俠客席·養成', x: 20,  y: 175, w: 110, h: 70, open: 'heroes' },
      { id: 'door',     label: '大門·出巡',  x: 428, y: 90,  w: 52,  h: 115, open: 'combat' },
      { id: 'board',    label: '告示·江湖',  x: 355, y: 55,  w: 55,  h: 50, open: 'story' },
      { id: 'map',      label: '地圖·據點',  x: 20,  y: 55,  w: 70,  h: 55, open: 'outposts' },
      { id: 'books',    label: '書架·藏書',  x: 300, y: 55,  w: 45,  h: 55, open: 'inn' },
      { id: 'tableA',   label: '雅座·小費',  x: 28,  y: 188, w: 95,  h: 50, open: 'table' },
      { id: 'tableB',   label: '雅座·加急',  x: 118, y: 210, w: 90,  h: 48, open: 'table' },
      { id: 'tableC',   label: '雅座·小費',  x: 218, y: 192, w: 95,  h: 50, open: 'table' }
    ];

    function mount(host) {
      if (!host) return;
      // 已掛載且仍在 DOM：只確保 loop，避免 UI 重繪拆動畫
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

    /** 雅座：接客中則加速；閒置則小費演出 */
    function onTableInteract(h) {
      const cx = h.x + h.w / 2;
      const cy = h.y + 8;
      if (phase === 'enter' || phase === 'serve') {
        // 加速：把本階段推近結束
        const elapsed = performance.now() - t0;
        const target = phase === 'enter' ? 1100 : 1200;
        t0 = performance.now() - Math.max(elapsed, target - 180);
        accelerateFlash = 18;
        floatLabel = { text: '加急上菜!', x: cx - 20, y: cy, life: 1 };
        setCaption('雅座催單——店員加快斟茶…');
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
      // idle / leave：坐客小費
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
        setCaption(innTitle + ' · 點擊場景熱點 · 雅座可催單／小費');
        return;
      }
      const job = queue.shift();
      guestName = job.guest.name || '過路客';
      guestKind = job.guest.kind || 'meal';
      payAmt = job.pay || 0;
      guestX = 460;
      guestY = 168;
      guestStride = 0;
      staffArm = 0;
      coinAlpha = 0;
      floatLabel = null;
      phase = 'enter';
      doorOpen = 1;
      t0 = performance.now();
      setCaption(guestName + ' 推門進場…');
    }

    function seedSeated() {
      seatedGuests = [
        { x: 55, y: 200, robe: C.mist },
        { x: 95, y: 208, robe: C.inkSoft },
        { x: 250, y: 205, robe: C.wood }
      ];
    }

    function drawTable(tx, ty, tw) {
      drawRect(ctx, tx, ty, tw, 10, C.wood);
      drawRect(ctx, tx, ty, tw, 2, C.woodLight);
      drawRect(ctx, tx + 4, ty + 10, 4, 8, C.inkSoft);
      drawRect(ctx, tx + tw - 8, ty + 10, 4, 8, C.inkSoft);
      drawRect(ctx, tx - 10, ty + 4, 8, 6, C.woodLight);
      drawRect(ctx, tx + tw + 2, ty + 4, 8, 6, C.woodLight);
      // 茶杯點
      drawRect(ctx, tx + tw / 2 - 2, ty - 3, 4, 3, C.cream);
      drawRect(ctx, tx + tw / 2 - 1, ty - 4, 2, 1, C.cinnabarBright);
    }

    function dayFactor(now) {
      // 約 90 秒一循環：0 清晨 → 0.35 正午 → 0.7 黃昏 → 1 深夜
      return (now / 90000) % 1;
    }

    function drawBg(now) {
      const df = dayFactor(now);
      let skyT = 0;
      if (df < 0.25) skyT = df / 0.25 * 0.3;
      else if (df < 0.55) skyT = 0.3 + (df - 0.25) / 0.3 * 0.4;
      else if (df < 0.75) skyT = 0.7 + (df - 0.55) / 0.2 * 0.3;
      else skyT = 1 - (df - 0.75) / 0.25 * 0.85;

      const skyCol = lerpColor(C.sky, C.night, clamp((skyT - 0.35) / 0.65, 0, 1));
      const wallCol = lerpColor(C.wood, C.night, clamp((skyT - 0.5) / 0.5 * 0.35, 0, 0.35));
      const lanternGlow = skyT > 0.55 ? 1 : 0.35 + skyT * 0.4;

      drawRect(ctx, 0, 0, W, 100, wallCol);
      drawRect(ctx, 0, 0, W, 22, C.night);
      drawRect(ctx, 0, 96, W, 6, C.inkSoft);
      drawRect(ctx, 0, 98, W, 2, C.woodLight);

      // 左窗
      drawRect(ctx, 28, 32, 54, 42, skyCol);
      drawRect(ctx, 32, 52, 20, 22, C.mtn);
      drawRect(ctx, 48, 44, 24, 30, C.jade);
      drawRect(ctx, 28, 32, 54, 2, C.ink);
      drawRect(ctx, 28, 72, 54, 2, C.ink);
      drawRect(ctx, 28, 32, 2, 42, C.ink);
      drawRect(ctx, 80, 32, 2, 42, C.ink);
      drawRect(ctx, 54, 32, 2, 42, C.ink);
      drawRect(ctx, 28, 52, 54, 2, C.ink);

      // 右窗（近門）
      drawRect(ctx, 380, 32, 40, 42, skyCol);
      drawRect(ctx, 384, 50, 18, 24, C.mtn);
      drawRect(ctx, 380, 32, 40, 2, C.ink);
      drawRect(ctx, 380, 72, 40, 2, C.ink);
      drawRect(ctx, 380, 32, 2, 42, C.ink);
      drawRect(ctx, 418, 32, 2, 42, C.ink);

      // 燈籠＋夜光暈
      [[120, 26], [220, 26], [320, 26]].forEach(function (p) {
        if (lanternGlow > 0.6) {
          ctx.globalAlpha = 0.25 * lanternGlow;
          drawRect(ctx, p[0] - 4, p[1] + 4, 20, 22, C.gold);
          ctx.globalAlpha = 1;
        }
        drawRect(ctx, p[0], p[1], 12, 16, lanternGlow > 0.7 ? C.cinnabarBright : C.cinnabar);
        drawRect(ctx, p[0] + 2, p[1] - 2, 8, 2, C.gold);
        drawRect(ctx, p[0] + 4, p[1] + 16, 4, 4, C.gold);
        if (lanternGlow > 0.75) {
          drawRect(ctx, p[0] + 3, p[1] + 5, 6, 4, C.cream);
        }
      });

      drawRect(ctx, 24, 58, 62, 48, '#D4BC8A');
      drawRect(ctx, 28, 62, 54, 40, C.mtn);
      drawRect(ctx, 34, 70, 16, 10, C.jade);
      drawRect(ctx, 52, 78, 20, 12, C.loess);
      drawRect(ctx, 24, 54, 62, 4, C.inkSoft);

      drawRect(ctx, 302, 58, 42, 48, C.wood);
      drawRect(ctx, 306, 62, 8, 18, C.blood);
      drawRect(ctx, 316, 64, 8, 16, C.teal);
      drawRect(ctx, 326, 62, 8, 18, C.violet);
      drawRect(ctx, 306, 84, 34, 4, C.woodLight);
      drawRect(ctx, 306, 92, 34, 4, C.woodLight);

      drawRect(ctx, 358, 58, 50, 46, C.woodLight);
      drawRect(ctx, 362, 62, 42, 38, C.paper);
      drawRect(ctx, 366, 66, 34, 3, C.inkSoft);
      drawRect(ctx, 366, 72, 28, 3, C.mist);
      drawRect(ctx, 366, 78, 30, 3, C.cinnabar);
      drawRect(ctx, 366, 84, 22, 3, C.inkSoft);

      const tw = Math.min(160, 16 + innTitle.length * 14);
      drawRect(ctx, (W - tw) / 2, 6, tw, 14, C.inkSoft);
      drawRect(ctx, (W - tw) / 2 + 2, 8, tw - 4, 10, C.blood);

      drawRect(ctx, 0, 102, W, H - 102, C.loess);
      for (let i = 0; i < 14; i++) {
        drawRect(ctx, 10 + i * 34, 112 + (i % 3) * 8, 16, 3, C.woodLight);
      }

      drawTable(40, 195, 70);
      drawTable(230, 200, 70);
      drawTable(130, 220, 60);

      drawRect(ctx, 150, 155, 180, 36, C.wood);
      drawRect(ctx, 150, 155, 180, 5, C.woodLight);
      drawRect(ctx, 150, 186, 180, 5, C.inkSoft);
      drawRect(ctx, 220, 148, 14, 10, C.teal);
      drawRect(ctx, 224, 144, 6, 4, C.tealBright);
      drawRect(ctx, 245, 152, 8, 5, C.paperLight);
      drawRect(ctx, 260, 152, 8, 5, C.paperLight);
      drawRect(ctx, 170, 148, 16, 10, C.gold);
      drawRect(ctx, 172, 150, 12, 6, C.loess);

      // 大門：開合更明顯
      const openPx = Math.round(doorOpen * 18);
      // 門外夜景／天光
      drawRect(ctx, 432, 102, 48, 110, skyCol);
      if (skyT > 0.6) {
        ctx.globalAlpha = 0.4;
        drawRect(ctx, 436, 110, 40, 90, C.night);
        ctx.globalAlpha = 1;
      } else {
        drawRect(ctx, 440, 130, 14, 40, C.mtn);
        drawRect(ctx, 456, 140, 12, 30, C.jade);
      }
      // 門扇（左右拉開）
      drawRect(ctx, 432 - openPx, 102, 24, 110, C.night);
      drawRect(ctx, 436 - openPx, 106, 18, 102, C.inkSoft);
      drawRect(ctx, 456 + openPx, 102, 24, 110, C.night);
      drawRect(ctx, 458 + openPx, 106, 18, 102, C.inkSoft);
      if (doorOpen < 0.4) {
        drawRect(ctx, 452, 148, 6, 14, C.gold);
      } else {
        // 門檻光
        drawRect(ctx, 448, 200, 12, 6, C.gold);
        ctx.globalAlpha = 0.35;
        drawRect(ctx, 444, 180, 20, 30, C.cream);
        ctx.globalAlpha = 1;
      }
      // 門楣
      drawRect(ctx, 428, 96, 52, 8, C.woodLight);
      drawRect(ctx, 430, 90, 48, 6, C.inkSoft);

      // 夜間整體微暗罩（地板以上牆面）
      if (skyT > 0.65) {
        ctx.globalAlpha = (skyT - 0.65) * 0.35;
        drawRect(ctx, 0, 22, W, 80, C.night);
        ctx.globalAlpha = 1;
      }
    }

    function drawHotspotHints() {
      HOTSPOTS.forEach(function (h) {
        const on = hoverId === h.id;
        const isTable = h.open === 'table';
        if (on) {
          ctx.globalAlpha = isTable ? 0.28 : 0.35;
          drawRect(ctx, h.x, h.y, h.w, h.h, isTable ? C.jadeBright : C.gold);
          ctx.globalAlpha = 1;
          drawRect(ctx, h.x, h.y, h.w, 2, C.cream);
          drawRect(ctx, h.x, h.y + h.h - 2, h.w, 2, C.cream);
          drawRect(ctx, h.x, h.y, 2, h.h, C.cream);
          drawRect(ctx, h.x + h.w - 2, h.y, 2, h.h, C.cream);
          drawPixelText(ctx, h.label, h.x + 4, Math.max(8, h.y - 12), C.cream);
        } else {
          ctx.globalAlpha = isTable ? 0.4 : 0.55;
          drawRect(ctx, h.x + 2, h.y + 2, 4, 4, isTable ? C.jade : C.gold);
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

    function loop(now) {
      if (!running || !ctx || !canvas || !canvas.isConnected) return;
      raf = requestAnimationFrame(loop);
      const elapsed = now - t0;
      idleBlink = (idleBlink + 1) % 90;
      walkerPhase = (walkerPhase + 1) % 240;
      if (accelerateFlash > 0) accelerateFlash -= 1;

      // —— 狀態機 ——
      if (phase === 'enter') {
        doorOpen = clamp(1 - Math.abs(elapsed - 400) / 700, 0.15, 1);
        guestX = 460 - Math.min(1, elapsed / 1100) * 200;
        guestY = 168;
        guestStride = Math.floor(elapsed / 120) % 2;
        if (elapsed >= 1100) {
          phase = 'serve';
          t0 = now;
          guestX = 260;
          guestStride = 0;
          doorOpen = 0.08;
          setCaption('店員斟茶遞水…');
        }
      } else if (phase === 'serve') {
        doorOpen = Math.max(0, doorOpen - 0.02);
        staffArm = Math.floor(elapsed / 180) % 2;
        if (elapsed >= 1200) {
          phase = 'pay';
          t0 = now;
          staffArm = 0;
          coinAlpha = 1;
          coinY = 0;
          floatLabel = { text: '+' + payAmt + '兩', x: 250, y: 130, life: 1 };
          setCaption(guestName + ' 付銀 ' + payAmt + ' 兩');
        }
      } else if (phase === 'pay') {
        coinY = Math.min(28, elapsed / 18);
        coinAlpha = clamp(1 - elapsed / 900, 0, 1);
        if (floatLabel) {
          floatLabel.y = (floatLabel.y0 != null ? floatLabel.y0 : 130) - elapsed / 40;
          floatLabel.life = clamp(1 - elapsed / 1000, 0, 1);
        }
        if (elapsed >= 1000) {
          phase = 'leave';
          t0 = now;
          floatLabel = null;
          doorOpen = 0.9;
          setCaption(guestName + ' 推門告辭');
        }
      } else if (phase === 'leave') {
        doorOpen = clamp(0.3 + Math.sin(Math.min(1, elapsed / 1000) * Math.PI) * 0.7, 0.2, 1);
        guestX = 260 + Math.min(1, elapsed / 1000) * 210;
        guestStride = Math.floor(elapsed / 120) % 2;
        if (elapsed >= 1000) startNext();
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
      drawBg(now);

      if (accelerateFlash > 0) {
        ctx.globalAlpha = accelerateFlash / 30;
        drawRect(ctx, 150, 145, 180, 50, C.gold);
        ctx.globalAlpha = 1;
      }

      seatedGuests.forEach(function (g) {
        drawFigure(ctx, g.x, g.y, { robe: g.robe, accent: C.gold, skin: C.skin, hair: C.inkSoft }, { scale: 1 });
      });

      const staffPal = HERO_COLORS.staff;
      const staffX = phase === 'serve' ? 188 + staffArm * 2 : 182;
      drawFigure(ctx, staffX, 128, staffPal, {
        weapon: phase === 'serve' ? 'tray' : null,
        arm: staffArm,
        scale: 1.15
      });

      ambientHeroes.forEach(function (hid, i) {
        const pal = HERO_COLORS[hid] || HERO_COLORS.default;
        const baseX = 30 + i * 28;
        const walk = Math.sin((walkerPhase + i * 40) / 30) * 18;
        const stride = Math.floor((walkerPhase + i * 20) / 20) % 2;
        const y = 178 + (i % 2) * 6;
        drawFigure(ctx, baseX + walk, y, pal, {
          weapon: weaponFor(hid),
          stride: stride,
          scale: 1.1
        });
      });

      if (phase !== 'idle') {
        const robe = guestKind === 'stay' ? C.inkSoft : C.mist;
        drawFigure(ctx, guestX, guestY, { robe: robe, accent: C.gold, skin: C.skin, hair: C.inkSoft }, {
          stride: guestStride,
          scale: 1.15
        });
      } else if (idleBlink < 25) {
        // 門外剪影暗示有人經過
        drawRect(ctx, 448, 175, 10, 22, C.inkSoft);
      }

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

      drawHotspotHints();
    }

    return {
      mount, destroy, isMounted, playGuest, enqueueGuest,
      setHotspotHandler, setTipHandler, setAmbientHeroes, setInnTitle,
      HOTSPOTS, getPhase: function () { return phase; }
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
      // 若 host 內已有我們的 wrap（被父層重新插入），重綁引用
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
        next.push({
          id: u.id,
          name: u.name,
          side: 'enemy',
          hp: u.hp,
          maxHp: u.maxHp,
          shield: u.shield || 0,
          heroId: 'enemy',
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
          fx.push({ kind: 'text', text: evt.kind === 'heal' ? ('+' + (evt.heal || 0)) : '盾', x: atk.x + 4, y: atk.y - 8, life: 20, max: 20, color: C.jadeBright });
          atk.flash = 6;
        }
        if (evt.skillName) {
          fx.push({ kind: 'burst', x: (atk ? atk.x : 40) + 6, y: (atk ? atk.y : 80) + 4, life: 12, max: 12, color: C.jade });
          if (atk) {
            fx.push({
              kind: 'trail', x0: atk.x + 6, y0: atk.y + 6, x1: atk.x + 6, y1: atk.y - 10,
              life: 12, max: 12, color: C.jadeBright
            });
          }
        }
        return;
      }

      if (atk && (evt.kind === 'hit' || evt.kind === 'skill' || evt.kind === 'miss' || evt.kind === 'parry')) {
        const dir = atk.side === 'ally' ? 1 : -1;
        // 多幀攻擊：蓄勢→斬出→回收
        anims[atk.id] = { kind: 'lunge', t: 0, dur: 16, dir: dir };
        if (evt.skillName) {
          fx.push({ kind: 'burst', x: atk.x + 6, y: atk.y + 4, life: 14, max: 14, color: evt.kind === 'skill' ? C.cinnabarBright : C.gold });
          fx.push({ kind: 'text', text: evt.skillName, x: atk.x - 4, y: atk.y - 14, life: 22, max: 22, color: C.cream });
        }
        if (tgt && (evt.kind === 'hit' || evt.kind === 'skill')) {
          fx.push({
            kind: 'trail',
            x0: atk.x + (dir > 0 ? 14 : -2),
            y0: atk.y + 6,
            x1: tgt.x + 6,
            y1: tgt.y + 6,
            life: 12, max: 12,
            color: evt.kind === 'skill' ? C.cinnabarBright : C.cream
          });
        }
      }

      if (evt.kind === 'miss' && tgt) {
        anims[tgt.id] = { kind: 'dodge', t: 0, dur: 14, dir: tgt.side === 'ally' ? -1 : 1 };
        fx.push({ kind: 'text', text: '閃', x: tgt.x + 2, y: tgt.y - 6, life: 16, max: 16, color: C.sky });
        return;
      }

      if (evt.kind === 'parry' && tgt) {
        anims[tgt.id] = { kind: 'parry', t: 0, dur: 14, dir: tgt.side === 'ally' ? -1 : 1 };
        tgt.flash = 5;
        fx.push({ kind: 'text', text: '架', x: tgt.x + 2, y: tgt.y - 6, life: 16, max: 16, color: C.gold });
        fx.push({ kind: 'slash', x: tgt.x, y: tgt.y + 2, life: 8, max: 8, color: C.gold });
        shake = Math.max(shake, 1.5);
        return;
      }

      if ((evt.kind === 'hit' || evt.kind === 'skill') && tgt) {
        const dmg = evt.damage || 0;
        // 多幀受擊：頓挫→擊退→回位
        anims[tgt.id] = { kind: 'hit', t: 0, dur: 14, dir: tgt.side === 'ally' ? -1 : 1, heavy: evt.kind === 'skill' };
        tgt.flash = 10;
        fx.push({ kind: 'text', text: '-' + dmg, x: tgt.x + 2, y: tgt.y - 4, life: 24, max: 24, color: C.cinnabarBright });
        fx.push({ kind: 'slash', x: tgt.x + 4, y: tgt.y + 4, life: 10, max: 10, color: C.cream });
        shake = Math.max(shake, evt.kind === 'skill' ? 5.5 : 3.2);
      }

      if (evt.kind === 'ko' && tgt) {
        fx.push({ kind: 'text', text: '倒', x: tgt.x + 2, y: tgt.y - 8, life: 26, max: 26, color: C.blood });
        shake = Math.max(shake, 6);
        anims[tgt.id] = { kind: 'hit', t: 0, dur: 18, dir: tgt.side === 'ally' ? -1 : 1, heavy: true };
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

    function drawUnit(u) {
      const pal = palFor(u);
      let dx = u.x;
      let dy = u.y;
      const an = anims[u.id];
      let arm = 0;
      let flash = u.flash > 0;
      let pose = 'idle';
      if (an) {
        const p = an.t / an.dur;
        if (an.kind === 'lunge') {
          // 幀：0–25% 蓄勢後拉、25–55% 斬出、55–100% 回收
          if (p < 0.25) {
            const w = p / 0.25;
            dx = u.ox - an.dir * 8 * w;
            arm = 0;
            pose = 'idle';
          } else if (p < 0.55) {
            const sp = (p - 0.25) / 0.3;
            dx = u.ox + an.dir * (8 + 20 * sp);
            arm = 1;
            pose = 'strike';
          } else {
            const rp = (p - 0.55) / 0.45;
            dx = u.ox + an.dir * 28 * (1 - rp);
            arm = rp < 0.4 ? 1 : 0;
            pose = rp < 0.35 ? 'strike' : 'idle';
          }
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
        } else if (an.kind === 'dodge') {
          const amp = Math.sin(p * Math.PI);
          dx = u.ox + an.dir * 14 * amp;
          dy = u.oy - 6 * amp;
        } else if (an.kind === 'parry') {
          const amp = Math.sin(p * Math.PI);
          dx = u.ox + an.dir * 4 * amp;
          pose = 'parry';
          flash = p > 0.2 && p < 0.55;
        }
      }
      if (u.dead) ctx.globalAlpha = 0.35;
      drawFigure(ctx, dx, dy, pal, {
        weapon: weaponFor(u.heroId),
        arm: arm,
        flash: flash,
        pose: pose,
        scale: 1.15
      });
      ctx.globalAlpha = 1;

      const bw = 32;
      const pct = u.maxHp > 0 ? clamp(u.hp / u.maxHp, 0, 1) : 0;
      drawRect(ctx, dx - 8, dy - 8, bw, 4, C.night);
      drawRect(ctx, dx - 8, dy - 8, Math.round(bw * pct), 4, u.side === 'ally' ? C.jadeBright : C.cinnabarBright);
      drawRect(ctx, dx - 8, dy - 8, bw, 1, C.ink);
      if (u.shield > 0) {
        drawRect(ctx, dx - 8, dy - 10, Math.min(bw, 4 + Math.round(u.shield / u.maxHp * bw)), 2, C.sky);
      }
      drawPixelText(ctx, u.name.slice(0, 4), dx - 6, dy + 20, C.cream);
    }

    function drawTrail(f) {
      const a = f.life / f.max;
      const steps = 6;
      for (let i = 0; i < steps; i++) {
        const t = i / (steps - 1);
        const x = f.x0 + (f.x1 - f.x0) * t;
        const y = f.y0 + (f.y1 - f.y0) * t;
        ctx.globalAlpha = a * (0.3 + 0.7 * t);
        const sz = 2 + Math.round(3 * t);
        drawRect(ctx, x, y, sz, Math.max(2, sz - 1), f.color || C.cream);
      }
      ctx.globalAlpha = 1;
    }

    function loop() {
      if (!running || !ctx || !canvas || !canvas.isConnected) return;
      raf = requestAnimationFrame(loop);

      Object.keys(anims).forEach((id) => {
        anims[id].t += 1;
        if (anims[id].t >= anims[id].dur) delete anims[id];
      });
      units.forEach((u) => {
        if (u.flash > 0) u.flash -= 1;
        if (!anims[u.id]) {
          u.x = u.ox;
          u.y = u.oy;
        }
      });
      fx = fx.filter((f) => {
        f.life -= 1;
        if (f.kind === 'text') f.y -= 0.7;
        return f.life > 0;
      });
      if (shake > 0) shake = Math.max(0, shake - 0.28);
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
        if (f.kind === 'trail') {
          drawTrail(f);
          return;
        }
        ctx.globalAlpha = clamp(a, 0, 1);
        if (f.kind === 'text') {
          drawPixelText(ctx, f.text, f.x, f.y, f.color || C.cream);
        } else if (f.kind === 'burst') {
          drawRect(ctx, f.x - 5, f.y - 5, 12, 12, f.color || C.gold);
          drawRect(ctx, f.x - 2, f.y - 2, 6, 6, C.cream);
        } else if (f.kind === 'slash') {
          drawRect(ctx, f.x, f.y, 14, 2, f.color || C.cream);
          drawRect(ctx, f.x + 3, f.y - 4, 2, 10, f.color || C.cream);
          drawRect(ctx, f.x - 2, f.y + 3, 10, 2, f.color || C.mist);
        }
        ctx.globalAlpha = 1;
      });
    }

    function resetIdle() {
      units = [];
      fx = [];
      anims = {};
      shake = 0;
      if (wrapEl) wrapEl.style.transform = '';
    }

    return { mount, destroy, isMounted, sync, playAction, resetIdle, W, H };
  })();

  global.WuxiaStages = {
    Inn: InnStage,
    Combat: CombatStage,
    COLORS: C
  };
})(typeof window !== 'undefined' ? window : globalThis);
