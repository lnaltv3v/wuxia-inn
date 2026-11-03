/**
 * 俠客棧 — 墨點江湖舞台（v0.4.2）
 * 客棧接客 Canvas + 戰鬥對峙 Canvas；色盤跟 ART.md
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

    // 影
    drawRect(ctx, ox + 2 * s, oy + 15 * s, 8 * s, 2 * s, C.ink);
    // 髮
    drawRect(ctx, ox + 3 * s, oy + 0 * s, 6 * s, 2 * s, hair);
    drawRect(ctx, ox + 2 * s, oy + 2 * s, 8 * s, 2 * s, hair);
    // 臉
    drawRect(ctx, ox + 3 * s, oy + 3 * s, 6 * s, 4 * s, skin);
    drawRect(ctx, ox + 4 * s, oy + 4 * s, 1 * s, 1 * s, C.ink);
    drawRect(ctx, ox + 7 * s, oy + 4 * s, 1 * s, 1 * s, C.ink);
    // 袍
    drawRect(ctx, ox + 2 * s, oy + 7 * s, 8 * s, 6 * s, robe);
    drawRect(ctx, ox + 2 * s, oy + 7 * s, 8 * s, 1 * s, accent);
    // 臂
    const armSwing = o.arm || 0;
    drawRect(ctx, ox + (0 + armSwing) * s, oy + 8 * s, 2 * s, 4 * s, robe);
    drawRect(ctx, ox + (10 - armSwing) * s, oy + 8 * s, 2 * s, 4 * s, robe);
    drawRect(ctx, ox + (0 + armSwing) * s, oy + 11 * s, 2 * s, 1 * s, skin);
    drawRect(ctx, ox + (10 - armSwing) * s, oy + 11 * s, 2 * s, 1 * s, skin);
    // 腿
    const stride = o.stride || 0;
    drawRect(ctx, ox + (3 - stride) * s, oy + 13 * s, 2 * s, 3 * s, C.inkSoft);
    drawRect(ctx, ox + (7 + stride) * s, oy + 13 * s, 2 * s, 3 * s, C.inkSoft);
    // 武器
    if (o.weapon === 'sword') {
      drawRect(ctx, ox + 11 * s, oy + 4 * s, 1 * s, 9 * s, accent);
      drawRect(ctx, ox + 10 * s, oy + 3 * s, 3 * s, 1 * s, C.gold);
    } else if (o.weapon === 'blade') {
      drawRect(ctx, ox + 11 * s, oy + 3 * s, 2 * s, 8 * s, accent);
      drawRect(ctx, ox + 10 * s, oy + 2 * s, 4 * s, 1 * s, C.woodLight);
    } else if (o.weapon === 'fist') {
      drawRect(ctx, ox + (-1 + armSwing) * s, oy + 9 * s, 3 * s, 2 * s, skin);
      drawRect(ctx, ox + (10 - armSwing) * s, oy + 9 * s, 3 * s, 2 * s, skin);
    } else if (o.weapon === 'qin') {
      drawRect(ctx, ox + 1 * s, oy + 9 * s, 10 * s, 2 * s, accent);
      drawRect(ctx, ox + 2 * s, oy + 8 * s, 8 * s, 1 * s, C.ink);
    } else if (o.weapon === 'club') {
      drawRect(ctx, ox + 11 * s, oy + 5 * s, 2 * s, 7 * s, C.mist);
      drawRect(ctx, ox + 10 * s, oy + 4 * s, 4 * s, 1 * s, C.cinnabar);
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

  // ——— 客棧接客舞台 ———
  const InnStage = (function () {
    const W = 320;
    const H = 180;
    let canvas = null;
    let ctx = null;
    let raf = 0;
    let running = false;
    let phase = 'idle'; // idle | enter | serve | pay | leave
    let t0 = 0;
    let guestName = '過路客';
    let payAmt = 0;
    let guestKind = 'meal';
    let queue = [];
    let coinY = 0;
    let coinAlpha = 0;
    let floatLabel = null; // { text, x, y, life }
    let staffArm = 0;
    let guestX = 300;
    let guestStride = 0;
    let idleBlink = 0;

    function mount(host) {
      if (!host) return;
      host.innerHTML = '';
      const wrap = document.createElement('div');
      wrap.className = 'stage-wrap inn-stage-wrap';
      wrap.innerHTML = '<canvas class="px-stage" width="320" height="180" aria-label="客棧接客舞台"></canvas>' +
        '<div class="stage-caption" id="inn-stage-cap">等待客人上門…</div>';
      host.appendChild(wrap);
      canvas = wrap.querySelector('canvas');
      ctx = canvas.getContext('2d');
      ctx.imageSmoothingEnabled = false;
      running = true;
      t0 = performance.now();
      if (phase !== 'idle' && phase !== 'enter' && phase !== 'serve' && phase !== 'pay' && phase !== 'leave') {
        phase = 'idle';
      }
      // remount 時若佇列有客或正閒置，接續／開下一場
      cancelAnimationFrame(raf);
      loop(performance.now());
      if (phase === 'idle' && queue.length) startNext();
    }

    function destroy() {
      running = false;
      cancelAnimationFrame(raf);
      canvas = null;
      ctx = null;
    }

    function isMounted() { return !!canvas && running && canvas.isConnected; }

    function setCaption(text) {
      const el = document.getElementById('inn-stage-cap');
      if (el) el.textContent = text;
    }

    function enqueueGuest(guest, pay) {
      queue.push({ guest: guest || { name: '過路客', kind: 'meal' }, pay: pay || 0 });
      if (phase === 'idle') startNext();
    }

    function playGuest(guest, pay) {
      enqueueGuest(guest, pay);
    }

    function startNext() {
      if (!queue.length) {
        phase = 'idle';
        setCaption('等待客人上門…');
        return;
      }
      const job = queue.shift();
      guestName = job.guest.name || '過路客';
      guestKind = job.guest.kind || 'meal';
      payAmt = job.pay || 0;
      guestX = 310;
      guestStride = 0;
      staffArm = 0;
      coinAlpha = 0;
      floatLabel = null;
      phase = 'enter';
      t0 = performance.now();
      setCaption(guestName + ' 進門…');
    }

    function drawBg() {
      // 室內：木牆＋地板＋櫃檯
      drawRect(ctx, 0, 0, W, 70, C.wood);
      drawRect(ctx, 0, 0, W, 18, C.night);
      // 窗外遠景條
      drawRect(ctx, 24, 22, 70, 36, C.sky);
      drawRect(ctx, 28, 40, 24, 18, C.mtn);
      drawRect(ctx, 48, 34, 30, 24, C.jade);
      drawRect(ctx, 226, 22, 70, 36, C.sky);
      drawRect(ctx, 230, 38, 28, 20, C.mtn);
      // 窗框
      drawRect(ctx, 24, 22, 70, 2, C.ink);
      drawRect(ctx, 24, 56, 70, 2, C.ink);
      drawRect(ctx, 24, 22, 2, 36, C.ink);
      drawRect(ctx, 92, 22, 2, 36, C.ink);
      drawRect(ctx, 58, 22, 2, 36, C.ink);
      drawRect(ctx, 24, 39, 70, 2, C.ink);
      drawRect(ctx, 226, 22, 70, 2, C.ink);
      drawRect(ctx, 226, 56, 70, 2, C.ink);
      drawRect(ctx, 226, 22, 2, 36, C.ink);
      drawRect(ctx, 294, 22, 2, 36, C.ink);
      drawRect(ctx, 260, 22, 2, 36, C.ink);
      drawRect(ctx, 226, 39, 70, 2, C.ink);
      // 燈籠
      drawRect(ctx, 110, 20, 10, 14, C.cinnabarBright);
      drawRect(ctx, 200, 20, 10, 14, C.cinnabarBright);
      drawRect(ctx, 112, 18, 6, 2, C.gold);
      drawRect(ctx, 202, 18, 6, 2, C.gold);
      // 地板
      drawRect(ctx, 0, 70, W, 110, C.loess);
      for (let i = 0; i < 10; i++) {
        drawRect(ctx, 8 + i * 32, 78 + (i % 2) * 10, 14, 4, C.woodLight);
      }
      // 櫃檯
      drawRect(ctx, 70, 100, 180, 28, C.wood);
      drawRect(ctx, 70, 100, 180, 4, C.woodLight);
      drawRect(ctx, 70, 124, 180, 4, C.inkSoft);
      // 茶壺／杯位
      drawRect(ctx, 140, 92, 10, 8, C.teal);
      drawRect(ctx, 142, 88, 6, 4, C.tealBright);
      drawRect(ctx, 160, 96, 6, 4, C.paperLight);
      // 門
      drawRect(ctx, 292, 70, 20, 70, C.night);
      drawRect(ctx, 296, 100, 4, 8, C.gold);
      // 木牌
      drawRect(ctx, 128, 8, 64, 12, C.inkSoft);
      drawRect(ctx, 132, 10, 56, 8, C.blood);
    }

    function loop(now) {
      if (!running || !ctx || !canvas || !canvas.isConnected) return;
      raf = requestAnimationFrame(loop);
      const elapsed = now - t0;
      idleBlink = (idleBlink + 1) % 60;

      // 相位推進
      if (phase === 'enter') {
        guestX = 310 - Math.min(1, elapsed / 900) * 130;
        guestStride = Math.floor(elapsed / 120) % 2;
        if (elapsed >= 900) {
          phase = 'serve';
          t0 = now;
          guestX = 180;
          guestStride = 0;
          setCaption('店員斟茶遞水…');
        }
      } else if (phase === 'serve') {
        staffArm = Math.floor(elapsed / 180) % 2;
        if (elapsed >= 1100) {
          phase = 'pay';
          t0 = now;
          staffArm = 0;
          coinAlpha = 1;
          coinY = 0;
          floatLabel = { text: '+' + payAmt + '兩', x: 168, y: 86, life: 1 };
          setCaption(guestName + ' 付銀 ' + payAmt + ' 兩');
        }
      } else if (phase === 'pay') {
        coinY = Math.min(24, elapsed / 20);
        coinAlpha = clamp(1 - elapsed / 900, 0, 1);
        if (floatLabel) {
          floatLabel.y = 86 - elapsed / 40;
          floatLabel.life = clamp(1 - elapsed / 1000, 0, 1);
        }
        if (elapsed >= 1000) {
          phase = 'leave';
          t0 = now;
          floatLabel = null;
          setCaption(guestName + ' 告辭離場');
        }
      } else if (phase === 'leave') {
        guestX = 180 + Math.min(1, elapsed / 900) * 150;
        guestStride = Math.floor(elapsed / 120) % 2;
        if (elapsed >= 900) {
          startNext();
        }
      }

      // 繪製
      ctx.clearRect(0, 0, W, H);
      drawBg();

      // 店員（櫃後左側）
      const staffPal = HERO_COLORS.staff;
      const staffX = phase === 'serve' ? 118 + staffArm * 2 : 112;
      drawFigure(ctx, staffX, 78, staffPal, {
        weapon: phase === 'serve' ? 'tray' : null,
        arm: staffArm,
        scale: 1
      });

      // 閒時俠客剪影（右後）
      if (phase === 'idle') {
        drawFigure(ctx, 240, 118, HERO_COLORS.qingyi, { weapon: 'sword', scale: 1, stride: idleBlink < 30 ? 0 : 1 });
      }

      // 客人
      if (phase !== 'idle') {
        const gPal = HERO_COLORS.guest;
        // 富紳略改色
        const robe = guestKind === 'stay' ? C.inkSoft : C.mist;
        drawFigure(ctx, guestX, 108, { robe: robe, accent: C.gold, skin: C.skin, hair: C.inkSoft }, {
          stride: guestStride,
          arm: 0,
          scale: 1
        });
      } else {
        // idle 輕微提示：門口影子
        if (idleBlink < 20) {
          drawRect(ctx, 300, 120, 8, 16, C.inkSoft);
        }
      }

      // 銀兩飛向櫃
      if (phase === 'pay' && coinAlpha > 0) {
        const cx = 190;
        const cy = 110 - coinY;
        drawRect(ctx, cx, cy, 6, 6, C.gold);
        drawRect(ctx, cx + 1, cy + 1, 2, 2, C.cream);
        ctx.globalAlpha = coinAlpha;
        drawRect(ctx, 148, 94, 6, 6, C.gold);
        ctx.globalAlpha = 1;
      }

      if (floatLabel && floatLabel.life > 0) {
        ctx.globalAlpha = floatLabel.life;
        drawPixelText(ctx, floatLabel.text, floatLabel.x, floatLabel.y, C.gold);
        ctx.globalAlpha = 1;
      }
    }

    return { mount, destroy, isMounted, playGuest, enqueueGuest };
  })();

  // ——— 戰鬥舞台 ———
  const CombatStage = (function () {
    const W = 320;
    const H = 150;
    let canvas = null;
    let ctx = null;
    let wrapEl = null;
    let raf = 0;
    let running = false;
    let units = []; // { id, name, side, hp, maxHp, shield, heroId, x,y, ox, flash, knock, dodge, dead }
    let fx = []; // { kind, x, y, life, max, text, color }
    let shake = 0;
    let anims = {}; // id -> { kind, t, dur, fromX, toX }

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
      const baseX = side === 'ally' ? 28 : 220;
      const gap = n <= 1 ? 0 : (n === 2 ? 36 : 32);
      const start = baseX - ((n - 1) * gap) / 2;
      return list.map((u, i) => {
        const x = start + i * gap;
        const y = 88 + (i % 2) * 6;
        return { x, y };
      });
    }

    function mount(host) {
      if (!host) return;
      host.innerHTML = '';
      wrapEl = document.createElement('div');
      wrapEl.className = 'stage-wrap combat-stage-wrap';
      wrapEl.innerHTML = '<canvas class="px-stage" width="320" height="150" aria-label="戰鬥舞台"></canvas>';
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
          fx.push({ kind: 'text', text: evt.kind === 'heal' ? ('+' + (evt.heal || 0)) : '盾', x: atk.x + 4, y: atk.y - 8, life: 18, max: 18, color: C.jadeBright });
          atk.flash = 6;
        }
        if (evt.skillName) {
          fx.push({ kind: 'burst', x: (atk ? atk.x : 40) + 6, y: (atk ? atk.y : 80) + 4, life: 10, max: 10, color: C.jade });
        }
        return;
      }

      if (atk && (evt.kind === 'hit' || evt.kind === 'skill' || evt.kind === 'miss')) {
        const dir = atk.side === 'ally' ? 1 : -1;
        anims[atk.id] = { kind: 'lunge', t: 0, dur: 10, dir: dir };
        if (evt.skillName) {
          fx.push({ kind: 'burst', x: atk.x + 6, y: atk.y + 4, life: 12, max: 12, color: evt.kind === 'skill' ? C.cinnabarBright : C.gold });
          fx.push({ kind: 'text', text: evt.skillName, x: atk.x - 4, y: atk.y - 12, life: 20, max: 20, color: C.cream });
        }
      }

      if (evt.kind === 'miss' && tgt) {
        anims[tgt.id] = { kind: 'dodge', t: 0, dur: 12, dir: tgt.side === 'ally' ? -1 : 1 };
        fx.push({ kind: 'text', text: '閃', x: tgt.x + 2, y: tgt.y - 6, life: 14, max: 14, color: C.sky });
        return;
      }

      if ((evt.kind === 'hit' || evt.kind === 'skill') && tgt) {
        const dmg = evt.damage || 0;
        anims[tgt.id] = { kind: 'hit', t: 0, dur: 10, dir: tgt.side === 'ally' ? -1 : 1 };
        tgt.flash = 8;
        fx.push({ kind: 'text', text: '-' + dmg, x: tgt.x + 2, y: tgt.y - 4, life: 22, max: 22, color: C.cinnabarBright });
        fx.push({ kind: 'slash', x: tgt.x + 4, y: tgt.y + 4, life: 8, max: 8, color: C.cream });
        shake = Math.max(shake, evt.kind === 'skill' ? 3 : 2);
      }

      if (evt.kind === 'ko' && tgt) {
        fx.push({ kind: 'text', text: '倒', x: tgt.x + 2, y: tgt.y - 8, life: 24, max: 24, color: C.blood });
        shake = Math.max(shake, 3);
      }
    }

    function drawBg() {
      drawRect(ctx, 0, 0, W, 70, C.sky);
      drawRect(ctx, 0, 48, 50, 30, C.mtn);
      drawRect(ctx, 40, 40, 60, 38, C.jade);
      drawRect(ctx, 200, 44, 70, 34, C.mtn);
      drawRect(ctx, 250, 36, 50, 42, C.jade);
      drawRect(ctx, 0, 70, W, 20, C.loess);
      drawRect(ctx, 0, 90, W, 60, C.wood);
      for (let i = 0; i < 8; i++) {
        drawRect(ctx, 10 + i * 40, 96, 16, 3, C.woodLight);
      }
      // 中線
      drawRect(ctx, 158, 78, 4, 4, C.cinnabar);
      drawRect(ctx, 156, 84, 8, 2, C.ink);
    }

    function drawUnit(u) {
      const pal = palFor(u);
      let dx = u.x;
      let dy = u.y;
      const an = anims[u.id];
      let arm = 0;
      let flash = u.flash > 0;
      if (an) {
        const p = an.t / an.dur;
        if (an.kind === 'lunge') {
          const amp = p < 0.5 ? p * 2 : (1 - p) * 2;
          dx = u.ox + an.dir * 14 * amp;
          arm = 1;
        } else if (an.kind === 'hit') {
          const amp = p < 0.4 ? p / 0.4 : (1 - p) / 0.6;
          dx = u.ox + an.dir * 6 * amp;
          flash = true;
        } else if (an.kind === 'dodge') {
          const amp = Math.sin(p * Math.PI);
          dx = u.ox + an.dir * 10 * amp;
          dy = u.oy - 4 * amp;
        }
      }
      if (u.dead) {
        ctx.globalAlpha = 0.35;
      }
      drawFigure(ctx, dx, dy, pal, {
        weapon: weaponFor(u.heroId),
        arm: arm,
        flash: flash,
        scale: 1
      });
      ctx.globalAlpha = 1;

      // HP 條
      const bw = 28;
      const pct = u.maxHp > 0 ? clamp(u.hp / u.maxHp, 0, 1) : 0;
      drawRect(ctx, dx - 8, dy - 6, bw, 4, C.night);
      drawRect(ctx, dx - 8, dy - 6, Math.round(bw * pct), 4, u.side === 'ally' ? C.jadeBright : C.cinnabarBright);
      drawRect(ctx, dx - 8, dy - 6, bw, 1, C.ink);
      if (u.shield > 0) {
        drawRect(ctx, dx - 8, dy - 8, Math.min(bw, 4 + Math.round(u.shield / u.maxHp * bw)), 2, C.sky);
      }
      // 名
      drawPixelText(ctx, u.name.slice(0, 4), dx - 6, dy + 18, C.cream);
    }

    function loop() {
      if (!running || !ctx || !canvas || !canvas.isConnected) return;
      raf = requestAnimationFrame(loop);

      // 更新動畫
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
        if (f.kind === 'text') f.y -= 0.6;
        return f.life > 0;
      });
      if (shake > 0) shake -= 0.35;
      if (wrapEl) {
        const sx = shake > 0 ? (Math.round(shake) % 2 === 0 ? 2 : -2) : 0;
        const sy = shake > 0 ? (Math.round(shake * 1.3) % 2 === 0 ? 1 : -1) : 0;
        wrapEl.style.transform = 'translate(' + sx + 'px,' + sy + 'px)';
      }

      ctx.clearRect(0, 0, W, H);
      drawBg();
      // 先畫遠的（較高 y）
      const sorted = units.slice().sort((a, b) => a.y - b.y);
      sorted.forEach(drawUnit);

      fx.forEach((f) => {
        const a = f.life / f.max;
        ctx.globalAlpha = clamp(a, 0, 1);
        if (f.kind === 'text') {
          drawPixelText(ctx, f.text, f.x, f.y, f.color || C.cream);
        } else if (f.kind === 'burst') {
          drawRect(ctx, f.x - 4, f.y - 4, 10, 10, f.color || C.gold);
          drawRect(ctx, f.x - 2, f.y - 2, 6, 6, C.cream);
        } else if (f.kind === 'slash') {
          drawRect(ctx, f.x, f.y, 12, 2, f.color || C.cream);
          drawRect(ctx, f.x + 2, f.y - 3, 2, 8, f.color || C.cream);
        }
        ctx.globalAlpha = 1;
      });
    }

    function resetIdle() {
      units = [];
      fx = [];
      anims = {};
      shake = 0;
    }

    return { mount, destroy, isMounted, sync, playAction, resetIdle };
  })();

  global.WuxiaStages = {
    Inn: InnStage,
    Combat: CombatStage,
    COLORS: C
  };
})(typeof window !== 'undefined' ? window : globalThis);
