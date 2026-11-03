/**
 * 俠客棧 — 自動即時走位戰鬥（v2.0.0：雙人合擊）
 * 戰場 960×540；狀態機：idle→approach→windup→strike→recover（hurt／parry／dodge）
 * 幀語意 v0.9；舞台鏡頭／VFX 加厚見 stages；僅 strike 判定幀傷害；近戰須接觸；速度 0.5–2×
 * v2.0：已解鎖雙人羈絆同隊時可一場一次合擊（額外傷害＋短暫破防）
 */
(function (global) {
  'use strict';

  const { randInt, getMartial } = global.WuxiaData;

  /** 戰場座標（對齊 CombatStage 960×540） */
  const FIELD = {
    W: 960,
    allyMinX: 68,
    allyMaxX: 504,
    enemyMinX: 456,
    enemyMaxX: 892,
    meleeRange: 58,
    contactRange: 38,
    skillRange: 284,
    rangedRange: 404,
    maxSpeed: 40,
    accel: 12,
    friction: 0.78,
    sepDist: 62,
    sepForce: 5.5,
    foeSepDist: 26,
    strafeY: 30,
    yMin: 288,
    yMax: 420,
    yBase: 325,
    iFrameDodge: 3,
    iFrameParry: 2
  };

  /**
   * 戰鬥手感參數（tick 為單位；baseTickMs≈900，速度鈕縮短 wall-clock）
   * windup 可見讀招；strike 第 activeFrame 幀判定；recover／hurt 硬直
   */
  const FEEL = {
    windupTicks: 1,
    strikeTicks: 1,
    recoverTicks: 1,
    hurtTicks: 2,
    parryTicks: 2,
    dodgeTicks: 2,
    activeFrame: 0,
    hitStopOnHit: 1,
    hitStopOnSkill: 2,
    hitStopOnClash: 2,
    hitStopOnKo: 3,
    windupMoveScale: 0.22,
    strikeMoveScale: 0.08,
    recoverMoveScale: 0.3,
    hurtMoveScale: 0.05,
    defendMoveScale: 0.15,
    contactSlack: 8,
    clashWindow: true
  };

  const STATES = {
    IDLE: 'idle',
    APPROACH: 'approach',
    WINDUP: 'windup',
    STRIKE: 'strike',
    RECOVER: 'recover',
    HURT: 'hurt',
    PARRY: 'parry',
    DODGE: 'dodge'
  };

  function isRangedUnit(u) {
    if (!u) return false;
    if (u.ranged) return true;
    const id = String(u.id || '');
    const name = String(u.name || '');
    if (id === 'qinshi' || id.indexOf('qinshi') >= 0) return true;
    if (name.indexOf('弓') >= 0 || name.indexOf('琴') >= 0) return true;
    if (u.emoji === '🏹' || u.emoji === '🎵') return true;
    return false;
  }

  function laneY(side, slotIndex, slotCount) {
    const n = Math.max(1, slotCount || 1);
    const i = slotIndex || 0;
    if (n === 1) return FIELD.yBase + (side === 'enemy' ? 5 : 0);
    if (n === 2) return FIELD.yBase + (i === 0 ? -42 : 42);
    const spread = [-55, 0, 55, -28, 28];
    return FIELD.yBase + (spread[i % spread.length] || ((i % 2) * 30 - 15));
  }

  function setState(u, state, dur) {
    u.combatState = state;
    u.stateT = 0;
    u.stateDur = Math.max(1, dur || 1);
    // 兼容舊舞台：intent 映射
    if (state === STATES.APPROACH) u.intent = 'approach';
    else if (state === STATES.WINDUP) u.intent = 'windup';
    else if (state === STATES.STRIKE) u.intent = 'strike';
    else if (state === STATES.RECOVER) u.intent = 'recover';
    else if (state === STATES.HURT) u.intent = 'hurt';
    else if (state === STATES.PARRY) u.intent = 'parry';
    else if (state === STATES.DODGE) u.intent = 'dodge';
    else u.intent = 'hold';
  }

  function inBusyState(u) {
    const s = u.combatState;
    return s === STATES.WINDUP || s === STATES.STRIKE || s === STATES.RECOVER
      || s === STATES.HURT || s === STATES.PARRY || s === STATES.DODGE;
  }

  function canControlMove(u) {
    const s = u.combatState;
    return s === STATES.IDLE || s === STATES.APPROACH;
  }

  function cloneUnit(src, side, slotIndex, slotCount) {
    const n = Math.max(1, slotCount || 1);
    const i = slotIndex || 0;
    const gap = n <= 1 ? 0 : (n === 2 ? 116 : 96);
    const baseX = side === 'ally' ? 134 : 768;
    const start = baseX - ((n - 1) * gap) / 2;
    const y = laneY(side, i, n);
    const u = {
      id: src.id || src.name + '_' + Math.random().toString(36).slice(2, 6),
      name: src.name,
      emoji: src.emoji || '⚔️',
      side: side,
      force: src.force,
      nei: src.nei || 0,
      hp: src.hp != null ? src.hp : src.maxHp,
      maxHp: src.maxHp || src.hp,
      skill: src.skill ? Object.assign({}, src.skill) : null,
      passive: src.passive ? Object.assign({}, src.passive) : null,
      cd: 0,
      atkCd: Math.floor(Math.random() * 2),
      shield: src.shield || 0,
      weaken: 0,
      mitBonus: src.mitBonus || 0,
      bondMul: src.bondMul || 1,
      regen: src.regen || 0,
      ranged: !!src.ranged || isRangedUnit(src),
      ai: src.ai || null,
      x: start + i * gap,
      y: y,
      homeY: y,
      lane: i,
      vx: 0,
      vy: 0,
      intent: 'approach',
      combatState: STATES.APPROACH,
      stateT: 0,
      stateDur: 1,
      facing: side === 'ally' ? 1 : -1,
      invuln: 0,
      engage: false,
      contact: false,
      pending: null,
      hitDone: false,
      telegraph: false,
      chargeT: 0,
      chargeCd: Math.floor(Math.random() * 20),
      counterWindow: 0,
      counterReady: false,
      _counterStrike: false,
      comboHits: 0,
      heroId: src.heroId || src.id || null,
      sprite: src.sprite || null
    };
    return u;
  }

  function buildAllyCombatant(hero, bondMul) {
    const active = hero.activeMartial || null;
    const passive = hero.passiveMartial || null;
    let force = hero.force;
    let nei = hero.nei;
    let mitBonus = 0;
    let regen = 0;
    let shield = 0;
    let skillChanceBonus = 0;

    if (passive && passive.effect) {
      const e = passive.effect;
      if (e.forceBonus) force = Math.round(force * (1 + e.forceBonus));
      if (e.neiBonus) nei = Math.round(nei * (1 + e.neiBonus));
      if (e.mitBonus) mitBonus += e.mitBonus;
      if (e.regen) regen += e.regen;
      if (e.startShield) shield = Math.round(hero.maxHp * e.startShield);
      if (e.skillChanceBonus) skillChanceBonus += e.skillChanceBonus;
    }

    let skill = null;
    if (active && active.effect) {
      skill = {
        name: active.name,
        mul: active.effect.mul || 1.5,
        chance: (active.effect.chance || 0.2) + skillChanceBonus,
        heal: active.effect.heal || 0,
        shield: active.effect.shield || 0,
        weaken: active.effect.weaken || 0
      };
    } else if (hero.skill) {
      skill = Object.assign({}, hero.skill);
    }

    return {
      id: hero.id,
      name: hero.name,
      emoji: hero.emoji,
      force: force,
      nei: nei,
      hp: hero.hp,
      maxHp: hero.maxHp,
      skill: skill,
      passive: passive,
      shield: shield,
      mitBonus: mitBonus,
      regen: regen,
      bondMul: bondMul || 1,
      ranged: hero.id === 'qinshi'
    };
  }

  function living(units, side) {
    return units.filter(function (u) { return u.side === side && u.hp > 0; });
  }

  function pickTarget(units, side, from) {
    const foes = living(units, side);
    if (!foes.length) return null;
    foes.sort(function (a, b) {
      const ha = a.hp / a.maxHp;
      const hb = b.hp / b.maxHp;
      if (Math.abs(ha - hb) > 0.12) return ha - hb;
      if (!from) return 0;
      return Math.abs(a.x - from.x) - Math.abs(b.x - from.x);
    });
    return foes[0];
  }

  function dist(a, b) {
    if (!a || !b) return 9999;
    const dx = a.x - b.x;
    const dy = (a.y || 0) - (b.y || 0);
    return Math.sqrt(dx * dx + dy * dy * 0.45);
  }

  function clampX(u, x) {
    if (u.side === 'ally') {
      return Math.max(FIELD.allyMinX, Math.min(FIELD.allyMaxX, x));
    }
    return Math.max(FIELD.enemyMinX, Math.min(FIELD.enemyMaxX, x));
  }

  function clampY(y) {
    return Math.max(FIELD.yMin, Math.min(FIELD.yMax, y));
  }

  function applyDamage(target, dmg) {
    let remain = dmg;
    if (target.shield > 0) {
      const absorb = Math.min(target.shield, remain);
      target.shield -= absorb;
      remain -= absorb;
    }
    if (remain > 0) {
      target.hp = Math.max(0, target.hp - remain);
    }
    return dmg;
  }

  function calcDamage(attacker, defender, skillMul) {
    const raw = attacker.force * 0.7 + attacker.nei * 0.35;
    const variance = 0.85 + Math.random() * 0.3;
    const mul = skillMul || 1;
    const bond = attacker.bondMul || 1;
    const weakenPen = 1 - Math.min(0.4, attacker.weaken || 0);
    const mit = 1 - Math.min(0.45, (defender.nei * 0.008) + (defender.mitBonus || 0));
    return Math.max(1, Math.round(raw * variance * mul * bond * weakenPen * mit));
  }

  function createBattle(allies, enemies, hooks) {
    const baseTickMs = (hooks && hooks.tickMs) || global.WuxiaData.GAME.combatTickMs;
    let speedMul = (hooks && hooks.speedMul) || 1;
    if (speedMul < 0.5) speedMul = 0.5;
    if (speedMul > 2) speedMul = 2;
    const units = [];
    allies.forEach(function (a, i) {
      units.push(cloneUnit(a, 'ally', i, allies.length));
    });
    enemies.forEach(function (e, i) {
      units.push(cloneUnit(e, 'enemy', i, enemies.length));
    });

    let timer = null;
    let turn = 0;
    let finished = false;
    let result = null;
    let holdTicks = 0;
    let paused = false;
    const comboDef = (hooks && hooks.combo) ? hooks.combo : null;
    let comboUsed = false;
    let comboArmed = false; // 讀招中（雙方已進 windup）
    let comboReadyHint = false;

    function effectiveTickMs() {
      return Math.max(120, Math.round(baseTickMs / speedMul));
    }

    function restartTimer() {
      if (timer) clearInterval(timer);
      timer = null;
      if (paused || finished) return;
      timer = setInterval(step, effectiveTickMs());
    }

    function setPaused(p) {
      paused = !!p;
      if (paused) {
        if (timer) { clearInterval(timer); timer = null; }
      } else if (!finished) {
        restartTimer();
      }
    }

    function log(msg, kind) {
      if (hooks && hooks.onLog) hooks.onLog(msg, kind || 'info');
    }

    function emit() {
      if (hooks && hooks.onUpdate) {
        hooks.onUpdate({
          units: units.map(function (u) { return Object.assign({}, u); }),
          turn: turn,
          finished: finished,
          result: result
        });
      }
    }

    function end(win) {
      finished = true;
      result = win ? 'win' : 'lose';
      stop();
      log(win ? '—— 勝。殘敵散去 ——' : '—— 敗。俠客負傷退回客棧 ——', win ? 'win' : 'lose');
      emit();
      if (hooks && hooks.onEnd) hooks.onEnd(result, units);
    }

    function emitAction(evt) {
      if (hooks && hooks.onAction) hooks.onAction(evt);
      if (!evt) return;
      if (evt.kind === 'hit') holdTicks = Math.max(holdTicks, evt.clash ? FEEL.hitStopOnClash : FEEL.hitStopOnHit);
      else if (evt.kind === 'skill' || evt.kind === 'combo') holdTicks = Math.max(holdTicks, FEEL.hitStopOnSkill);
      else if (evt.kind === 'combo_windup') holdTicks = Math.max(holdTicks, 1);
      else if (evt.kind === 'parry' || evt.kind === 'clash') holdTicks = Math.max(holdTicks, FEEL.hitStopOnClash);
      else if (evt.kind === 'ko') holdTicks = Math.max(holdTicks, FEEL.hitStopOnKo);
    }

    function findById(id) {
      for (let i = 0; i < units.length; i++) {
        if (units[i].id === id) return units[i];
      }
      return null;
    }

    function separateAll() {
      const alive = units.filter(function (u) { return u.hp > 0; });
      for (let i = 0; i < alive.length; i++) {
        for (let j = i + 1; j < alive.length; j++) {
          const a = alive[i];
          const b = alive[j];
          const same = a.side === b.side;
          const minD = same ? FIELD.sepDist : FIELD.foeSepDist;
          const dx = b.x - a.x;
          const dy = (b.y - a.y) * 1.15;
          const d = Math.sqrt(dx * dx + dy * dy) || 0.01;
          if (d >= minD) continue;
          const push = (minD - d) / minD * FIELD.sepForce * (same ? 1.15 : 0.55);
          const nx = dx / d;
          const ny = dy / d;
          // 攻擊判定中少推，保碰撞框重疊
          const lockA = a.combatState === STATES.STRIKE || a.combatState === STATES.WINDUP;
          const lockB = b.combatState === STATES.STRIKE || b.combatState === STATES.WINDUP;
          const mulA = lockA ? 0.35 : 1;
          const mulB = lockB ? 0.35 : 1;
          a.vx -= nx * push * mulA;
          a.vy -= ny * push * 0.85 * mulA;
          b.vx += nx * push * mulB;
          b.vy += ny * push * 0.85 * mulB;
          if (same && Math.abs(a.homeY - b.homeY) < 10) {
            a.vy -= 2.4;
            b.vy += 2.4;
          }
        }
      }
    }

    function enterDefend(target, kind, attacker, skillName) {
      const back = target.side === 'ally' ? -1 : 1;
      if (kind === 'parry') {
        target.vx += back * 14;
        target.vy += (Math.random() < 0.5 ? -1 : 1) * 10;
        target.x = clampX(target, target.x + back * 24);
        target.y = clampY(target.homeY + (Math.random() < 0.5 ? -FIELD.strafeY : FIELD.strafeY));
        setState(target, STATES.PARRY, FEEL.parryTicks);
        target.invuln = Math.max(target.invuln, FIELD.iFrameParry);
        target.pending = null;
        target.telegraph = false;
        // 招架成功：短暫反打窗口（唔改狀態機結構，只開綠燈）
        target.counterWindow = 3;
        target.counterReady = true;
        target.atkCd = 0;
        target.comboHits = 0;
        log(target.emoji + target.name + ' 提勁招架 ' + attacker.name + ' 的招！反打可期！', 'info');
        emitAction({
          kind: 'parry',
          attackerId: attacker.id,
          targetId: target.id,
          skillName: skillName,
          side: attacker.side,
          damage: 0,
          counter: true,
          ax: attacker.x, ay: attacker.y, tx: target.x, ty: target.y
        });
      } else {
        target.vx += back * 22;
        target.vy += (Math.random() < 0.5 ? -1 : 1) * 14;
        target.x = clampX(target, target.x + back * (32 + Math.random() * 20));
        target.y = clampY(target.homeY + (Math.random() < 0.5 ? -FIELD.strafeY * 1.6 : FIELD.strafeY * 1.6));
        setState(target, STATES.DODGE, FEEL.dodgeTicks);
        target.invuln = Math.max(target.invuln, FIELD.iFrameDodge);
        target.pending = null;
        target.telegraph = false;
        log(target.emoji + target.name + (kind === 'iframe' ? ' 仍在身法之中，卸開 ' : ' 側身閃過 ') + attacker.name + '！', 'info');
        emitAction({
          kind: 'miss',
          attackerId: attacker.id,
          targetId: target.id,
          skillName: skillName,
          side: attacker.side,
          damage: 0,
          iFrame: kind === 'iframe',
          ax: attacker.x, ay: attacker.y, tx: target.x, ty: target.y
        });
      }
    }

    function tryDefend(attacker, target, skillName) {
      if (target.invuln > 0) {
        enterDefend(target, 'iframe', attacker, skillName);
        return true;
      }
      // 讀招中較易招架／閃
      const reading = target.combatState === STATES.WINDUP || target.combatState === STATES.STRIKE;
      const low = target.hp / target.maxHp < 0.35;
      const base = skillName ? 0.10 : 0.18;
      const chance = base + (low ? 0.08 : 0) + (reading ? 0.06 : 0) + Math.min(0.08, (target.nei || 0) * 0.004);
      if (Math.random() >= chance) return false;
      const doParry = Math.random() < (low ? 0.35 : 0.5);
      enterDefend(target, doParry ? 'parry' : 'dodge', attacker, skillName);
      return true;
    }

    function applyHitKnock(attacker, target, wasContact) {
      const knock = attacker.side === 'ally' ? -1 : 1;
      if (attacker._lastRanged) return;
      const pushAtk = wasContact ? 14 : 10;
      const pushTgt = wasContact ? 28 : 20;
      attacker.vx += knock * pushAtk;
      target.vx -= knock * pushTgt;
      attacker.vy += (Math.random() < 0.5 ? -1 : 1) * (wasContact ? 4.4 : 2.4);
      target.vy += (Math.random() < 0.5 ? -1 : 1) * (wasContact ? 6.4 : 3.6);
      attacker.x = clampX(attacker, attacker.x + knock * (wasContact ? 12 : 8));
      target.x = clampX(target, target.x - knock * (wasContact ? 24 : 18));
    }

    function enterHurt(target, heavy) {
      setState(target, STATES.HURT, heavy ? FEEL.hurtTicks + 1 : FEEL.hurtTicks);
      target.pending = null;
      target.telegraph = false;
      target.hitDone = false;
      target.comboHits = 0;
      target.counterReady = false;
      target.counterWindow = 0;
      target._counterStrike = false;
    }

    function resolveStrikeHit(attacker, target, pending, clash) {
      const skillMul = pending.skillMul || 1;
      const skillName = pending.skillName || null;
      const usedSkill = !!(pending.usedSkill && skillMul > 1);
      const isCombo = !!(pending && pending.isCombo);

      if (!isCombo && tryDefend(attacker, target, skillName)) {
        return { defended: true, clash: !!clash };
      }

      let hitMul = skillMul;
      let isCounter = !!attacker._counterStrike;
      if (isCounter) {
        hitMul = skillMul * 1.4;
        attacker._counterStrike = false;
      }
      if (isCombo && pending.comboMul) hitMul = pending.comboMul;
      let dmg = calcDamage(attacker, target, hitMul);
      if (isCombo && pending.breakMit) {
        target.weaken = Math.max(target.weaken || 0, pending.breakMit);
        target.mitBonus = Math.max(0, (target.mitBonus || 0) - pending.breakMit * 0.5);
      }
      applyDamage(target, dmg);
      attacker.comboHits = (attacker.comboHits || 0) + 1;
      if (isCombo) {
        comboArmed = false;
        log('合擊「' + (skillName || '同心') + '」打中 ' + target.name + '（' + dmg + '）' + (pending.breakMit ? ' · 破防' : ''), 'skill');
      } else if (isCounter) {
        log(attacker.emoji + attacker.name + ' 招架反打 ' + target.name + '（' + dmg + '）', 'skill');
      } else if (skillName && skillMul > 1) {
        log(attacker.emoji + attacker.name + '「' + skillName + '」打中 ' + target.name + '（' + dmg + '）', 'skill');
      } else {
        log(attacker.emoji + attacker.name + ' 攻向 ' + target.name + '，傷害 ' + dmg, attacker.side);
      }
      if (!isCounter && attacker.comboHits >= 2 && attacker.comboHits % 2 === 0) {
        log(attacker.emoji + attacker.name + ' 連擊 ×' + attacker.comboHits, 'info');
      }

      const contactDist = dist(attacker, target);
      const wasContact = !pending.ranged && contactDist <= FIELD.contactRange + FEEL.contactSlack;
      emitAction({
        kind: isCombo ? 'combo' : (isCounter ? 'counter' : (usedSkill ? 'skill' : 'hit')),
        attackerId: attacker.id,
        targetId: target.id,
        partnerId: pending.partnerId || null,
        damage: dmg,
        skillName: isCombo ? (skillName || '合擊') : (isCounter ? '反打' : skillName),
        side: attacker.side,
        ranged: !!pending.ranged,
        contact: wasContact || !pending.ranged,
        clash: !!clash,
        counter: isCounter,
        isCombo: isCombo,
        breakMit: pending.breakMit || 0,
        combo: attacker.comboHits || 1,
        phase: 'strike',
        ax: attacker.x, ay: attacker.y, tx: target.x, ty: target.y
      });

      applyHitKnock(attacker, target, wasContact);
      if (target.hp > 0) {
        enterHurt(target, usedSkill || isCombo);
      } else {
        log(target.emoji + target.name + ' 倒下！', 'ko');
        emitAction({
          kind: 'ko',
          attackerId: attacker.id,
          targetId: target.id,
          side: attacker.side,
          damage: dmg,
          ax: attacker.x, ay: attacker.y, tx: target.x, ty: target.y
        });
      }
      return { defended: false, clash: !!clash, damage: dmg };
    }

    function beginWindup(attacker, target, opts) {
      const o = opts || {};
      const ranged = !!o.ranged;
      if (attacker.counterReady || attacker.counterWindow > 0) {
        attacker._counterStrike = true;
        attacker.counterReady = false;
        attacker.counterWindow = 0;
      }
      // 近戰：進入讀招前盡量貼身
      if (!ranged) {
        const toward = target.x >= attacker.x ? 1 : -1;
        let dNow = dist(attacker, target);
        if (dNow > FIELD.contactRange) {
          const close = Math.min(dNow - FIELD.contactRange + 2, 36);
          attacker.vx += toward * 14;
          attacker.x = clampX(attacker, attacker.x + toward * close);
          attacker.y = clampY(attacker.y + ((target.y || target.homeY) - attacker.y) * 0.5);
          dNow = dist(attacker, target);
        }
        if (dNow > FIELD.contactRange + FEEL.contactSlack) {
          setState(attacker, STATES.APPROACH, 1);
          attacker.vx += toward * 8;
          return false;
        }
      }

      attacker.pending = {
        targetId: target.id,
        skillMul: o.skillMul || 1,
        skillName: o.skillName || null,
        usedSkill: !!o.usedSkill,
        ranged: ranged
      };
      attacker.hitDone = false;
      attacker.telegraph = true;
      attacker.facing = target.x >= attacker.x ? 1 : -1;
      setState(attacker, STATES.WINDUP, FEEL.windupTicks);
      emitAction({
        kind: 'windup',
        attackerId: attacker.id,
        targetId: target.id,
        skillName: o.skillName || null,
        side: attacker.side,
        ranged: ranged,
        telegraph: true,
        phase: 'windup',
        ax: attacker.x, ay: attacker.y, tx: target.x, ty: target.y
      });
      return true;
    }

    function decideLocomotion(u) {
      if (u.hp <= 0) return;
      if (!canControlMove(u)) {
        // 忙碌狀態只做極弱歸位／摩擦
        let scale = FEEL.recoverMoveScale;
        if (u.combatState === STATES.WINDUP) scale = FEEL.windupMoveScale;
        else if (u.combatState === STATES.STRIKE) scale = FEEL.strikeMoveScale;
        else if (u.combatState === STATES.HURT) scale = FEEL.hurtMoveScale;
        else if (u.combatState === STATES.PARRY || u.combatState === STATES.DODGE) scale = FEEL.defendMoveScale;
        u.vx *= FIELD.friction * (0.85 + scale * 0.1);
        u.vy = (u.vy + (u.homeY - u.y) * 0.12 * scale) * FIELD.friction;
        // 讀招／出招時微微對準目標
        if (u.pending && (u.combatState === STATES.WINDUP || u.combatState === STATES.STRIKE)) {
          const tgt = findById(u.pending.targetId);
          if (tgt && tgt.hp > 0) {
            u.facing = tgt.x >= u.x ? 1 : -1;
            u.vy += ((tgt.y || tgt.homeY) - u.y) * 0.08;
          }
        }
        return;
      }

      const foeSide = u.side === 'ally' ? 'enemy' : 'ally';
      const target = pickTarget(units, foeSide, u);
      if (!target) {
        setState(u, STATES.IDLE, 1);
        u.engage = false;
        u.contact = false;
        u.vx *= FIELD.friction;
        u.vy *= FIELD.friction;
        return;
      }

      const d = dist(u, target);
      const ranged = isRangedUnit(u);
      const ai = u.ai || (ranged ? 'kite' : 'skirmish');
      const preferRange = (ai === 'kite' || ranged)
        ? FIELD.rangedRange * (ai === 'kite' ? 0.58 : 0.55)
        : (ai === 'charge' ? FIELD.contactRange + 4 : FIELD.contactRange);
      const hpRatio = u.hp / u.maxHp;
      u.engage = !ranged && d <= FIELD.meleeRange;
      u.contact = !ranged && d <= FIELD.contactRange + 1;
      u.facing = target.x >= u.x ? 1 : -1;

      if (u.chargeCd > 0) u.chargeCd -= 1;
      if (u.chargeT > 0) u.chargeT -= 1;

      let want = STATES.IDLE;
      if (ai === 'charge') {
        // 衝鋒：少退、多貼；遠距觸發短衝刺
        if (hpRatio < 0.16 && d < FIELD.meleeRange + 24 && Math.random() < 0.28) {
          want = 'retreat';
        } else if (d > FIELD.contactRange + 2) {
          want = STATES.APPROACH;
          if (d > 96 && u.chargeCd <= 0 && u.chargeT <= 0 && Math.random() < 0.55) {
            u.chargeT = 14;
            u.chargeCd = 70 + Math.floor(Math.random() * 40);
            log(u.emoji + u.name + ' 催動腳步，直衝而來！', 'warn');
          }
        } else if (Math.random() < 0.18) {
          want = 'strafe';
        } else {
          want = STATES.IDLE;
        }
      } else if (ai === 'kite') {
        // 拉距：近則退、遠則靠、中距遊走
        if (d < preferRange - 28) {
          want = 'retreat';
        } else if (d > preferRange + 36) {
          want = STATES.APPROACH;
        } else if (Math.random() < 0.48) {
          want = 'strafe';
        } else {
          want = STATES.IDLE;
        }
        if (hpRatio < 0.3 && d < FIELD.meleeRange + 48 && Math.random() < 0.4) {
          want = 'retreat';
        }
      } else {
        // skirmish：原有邏輯
        if (hpRatio < 0.28 && d < FIELD.meleeRange + 40 && Math.random() < 0.55) {
          want = 'retreat';
        } else if (ranged && d < FIELD.meleeRange + 16 && Math.random() < 0.45) {
          want = 'retreat';
        } else if (d > (ranged ? FIELD.rangedRange * 0.9 : FIELD.meleeRange)) {
          want = STATES.APPROACH;
        } else if (d < preferRange - 16 && !ranged && Math.random() < 0.22) {
          want = 'strafe';
        } else {
          want = STATES.IDLE;
        }
      }

      if (want === STATES.APPROACH) setState(u, STATES.APPROACH, 1);
      else if (want === STATES.IDLE || want === 'retreat' || want === 'strafe') {
        if (u.combatState !== STATES.IDLE && want === STATES.IDLE) setState(u, STATES.IDLE, 1);
        u.intent = want === 'retreat' ? 'retreat' : (want === 'strafe' ? 'strafe' : (u.chargeT > 0 ? 'charge' : 'hold'));
        if (want === STATES.IDLE) u.combatState = STATES.IDLE;
      }
      if (u.chargeT > 0) u.intent = 'charge';

      const toward = target.x >= u.x ? 1 : -1;
      let ax = 0;
      let ay = 0;
      let speedScale = 0.85 + Math.random() * 0.3;
      if (ai === 'charge') speedScale *= 1.12;
      if (ai === 'kite') speedScale *= 1.05;
      if (u.chargeT > 0) speedScale *= 1.55;

      if (want === STATES.APPROACH || u.combatState === STATES.APPROACH || u.chargeT > 0) {
        const accelMul = (ai === 'charge' ? 1.55 : 1.25) * (u.chargeT > 0 ? 1.8 : 1);
        ax = toward * FIELD.accel * accelMul * speedScale;
        ay += (u.homeY - u.y) * (ai === 'charge' ? 0.18 : 0.28);
        ay += ((target.y || target.homeY) - u.y) * (ai === 'charge' ? 0.22 : 0.1);
      } else if (want === 'retreat') {
        ax = -toward * FIELD.accel * (ai === 'kite' ? 1.35 : 1.1) * speedScale;
        ay += (u.homeY - u.y) * 0.3;
      } else if (want === 'strafe') {
        ax = toward * FIELD.accel * (ai === 'kite' ? 0.08 : 0.18);
        const side = (u.lane % 2 === 0) ? -1 : 1;
        ay += side * FIELD.accel * (ai === 'kite' ? 0.95 : 0.7) + (u.homeY - u.y) * 0.15;
      } else {
        ay += (u.homeY - u.y) * 0.35;
        if (u.engage && Math.random() < 0.35) {
          ay += (Math.random() < 0.5 ? -1 : 1) * 2.4;
        }
      }

      u.vx = (u.vx + ax) * FIELD.friction;
      u.vy = (u.vy + ay) * FIELD.friction;
      const sp = Math.sqrt(u.vx * u.vx + u.vy * u.vy);
      const maxSp = FIELD.maxSpeed * speedScale * (u.chargeT > 0 ? 1.35 : 1);
      if (sp > maxSp) {
        u.vx = (u.vx / sp) * maxSp;
        u.vy = (u.vy / sp) * maxSp;
      }
      if (u.chargeT <= 0) u.telegraph = !!u.pending;
    }

    function integrateMove(u) {
      if (u.hp <= 0) return;
      u.x = clampX(u, u.x + u.vx);
      u.y = clampY(u.y + u.vy);
    }

    function tryStartAttack(attacker) {
      if (attacker.hp <= 0) return false;
      if (!canControlMove(attacker)) return false;
      if (attacker.atkCd > 0) return false;

      if (attacker.regen > 0 && attacker.hp < attacker.maxHp && turn % 3 === 0) {
        const healAmt = Math.max(1, Math.round(attacker.maxHp * attacker.regen));
        attacker.hp = Math.min(attacker.maxHp, attacker.hp + healAmt);
      }

      const foeSide = attacker.side === 'ally' ? 'enemy' : 'ally';
      const target = pickTarget(units, foeSide, attacker);
      if (!target) return false;

      const d = dist(attacker, target);
      const ranged = isRangedUnit(attacker);
      const meleeOk = d <= FIELD.meleeRange;
      const skillOk = d <= FIELD.skillRange;
      const rangedOk = d <= FIELD.rangedRange;

      let skillMul = 1;
      let skillName = null;
      let usedSkill = false;
      let didHealOnly = false;

      const wantSkill = attacker.skill && attacker.cd <= 0 &&
        Math.random() < (attacker.skill.chance || 0.2);
      if (wantSkill && skillOk) {
        skillMul = attacker.skill.mul || 1.5;
        skillName = attacker.skill.name;
        attacker.cd = 3;
        usedSkill = true;

        if (attacker.skill.heal) {
          const healAmt = Math.round(attacker.maxHp * attacker.skill.heal);
          attacker.hp = Math.min(attacker.maxHp, attacker.hp + healAmt);
          log(attacker.emoji + attacker.name + '「' + skillName + '」，回氣血 ' + healAmt, 'skill');
          emitAction({
            kind: 'heal',
            attackerId: attacker.id,
            targetId: attacker.id,
            heal: healAmt,
            skillName: skillName,
            side: attacker.side,
            ax: attacker.x, ay: attacker.y
          });
        }
        if (attacker.skill.shield) {
          const sh = Math.round(attacker.maxHp * attacker.skill.shield);
          attacker.shield = (attacker.shield || 0) + sh;
          log(attacker.emoji + attacker.name + '「' + skillName + '」護體，護盾 +' + sh, 'skill');
          emitAction({
            kind: 'shield',
            attackerId: attacker.id,
            targetId: attacker.id,
            shield: sh,
            skillName: skillName,
            side: attacker.side,
            ax: attacker.x, ay: attacker.y
          });
        }
        if (attacker.skill.weaken) {
          target.weaken = Math.max(target.weaken || 0, attacker.skill.weaken);
          log(attacker.emoji + attacker.name + '「' + skillName + '」令 ' + target.name + ' 氣勢一滯', 'skill');
        }
        if (attacker.skill.heal && skillMul <= 1 && !attacker.skill.weaken) {
          didHealOnly = true;
          attacker.atkCd = 2;
        }
      }

      if (attacker.cd > 0) attacker.cd -= 1;
      if (attacker.weaken > 0) attacker.weaken = Math.max(0, attacker.weaken - 0.03);

      if (didHealOnly) return true;

      const canBasic = ranged ? rangedOk : meleeOk;
      const canSkillHit = usedSkill && skillMul > 1 && skillOk;
      if (!canBasic && !canSkillHit) return false;

      if (!ranged && !canSkillHit && d > FIELD.meleeRange) return false;

      const asRanged = (ranged || canSkillHit) && d > FIELD.meleeRange;
      attacker._lastRanged = asRanged;
      return beginWindup(attacker, target, {
        skillMul: canSkillHit ? skillMul : 1,
        skillName: canSkillHit ? skillName : null,
        usedSkill: canSkillHit,
        ranged: asRanged
      });
    }

    function advanceCombatStates() {
      const strikers = [];

      units.forEach(function (u) {
        if (u.hp <= 0) return;
        if (u.invuln > 0) u.invuln -= 1;

        const s = u.combatState;
        if (!inBusyState(u) && s !== STATES.APPROACH && s !== STATES.IDLE) {
          // 兜底
          setState(u, STATES.IDLE, 1);
        }

        if (s === STATES.WINDUP) {
          u.telegraph = true;
          u.stateT += 1;
          if (u.stateT >= u.stateDur) {
            // → strike
            u.telegraph = false;
            u.hitDone = false;
            setState(u, STATES.STRIKE, FEEL.strikeTicks);
            emitAction({
              kind: 'strike',
              attackerId: u.id,
              targetId: u.pending ? u.pending.targetId : null,
              skillName: u.pending ? u.pending.skillName : null,
              side: u.side,
              ranged: !!(u.pending && u.pending.ranged),
              phase: 'strike',
              ax: u.x, ay: u.y
            });
          }
        } else if (s === STATES.STRIKE) {
          strikers.push(u);
          // 判定幀處理喺下面統一做
        } else if (s === STATES.RECOVER || s === STATES.HURT || s === STATES.PARRY || s === STATES.DODGE) {
          u.stateT += 1;
          if (u.stateT >= u.stateDur) {
            u.pending = null;
            u.telegraph = false;
            u.hitDone = false;
            setState(u, STATES.IDLE, 1);
          }
        }
      });

      // Clash：雙方同時 strike 且互指
      const clashPairs = {};
      if (FEEL.clashWindow) {
        for (let i = 0; i < strikers.length; i++) {
          for (let j = i + 1; j < strikers.length; j++) {
            const a = strikers[i];
            const b = strikers[j];
            if (a.side === b.side) continue;
            if (!a.pending || !b.pending) continue;
            if (a.pending.targetId === b.id && b.pending.targetId === a.id) {
              clashPairs[a.id] = b.id;
              clashPairs[b.id] = a.id;
            }
          }
        }
      }

      const clashedEmitted = {};
      strikers.forEach(function (u) {
        if (u.hitDone) {
          u.stateT += 1;
          if (u.stateT >= u.stateDur) {
            setState(u, STATES.RECOVER, FEEL.recoverTicks);
            u.pending = null;
            emitAction({
              kind: 'recover',
              attackerId: u.id,
              side: u.side,
              phase: 'recover',
              ax: u.x, ay: u.y
            });
          }
          return;
        }

        // 僅 activeFrame 可造成傷害
        if (u.stateT !== FEEL.activeFrame) {
          u.stateT += 1;
          return;
        }

        const pending = u.pending;
        if (!pending) {
          u.hitDone = true;
          u.stateT += 1;
          return;
        }

        const target = findById(pending.targetId);
        if (!target || target.hp <= 0) {
          u.hitDone = true;
          u.stateT += 1;
          setState(u, STATES.RECOVER, FEEL.recoverTicks);
          u.pending = null;
          return;
        }

        // 近戰必須接觸；遠程／技能例外
        if (!pending.ranged) {
          const dNow = dist(u, target);
          if (dNow > FIELD.contactRange + FEEL.contactSlack) {
            // 揮空：無傷害，進 recover
            log(u.emoji + u.name + ' 一招落空！', 'info');
            emitAction({
              kind: 'miss',
              attackerId: u.id,
              targetId: target.id,
              side: u.side,
              damage: 0,
              whiff: true,
              phase: 'strike',
              ax: u.x, ay: u.y, tx: target.x, ty: target.y
            });
            u.hitDone = true;
            u.atkCd = 2;
            u.stateT += 1;
            setState(u, STATES.RECOVER, FEEL.recoverTicks);
            u.pending = null;
            return;
          }
        }

        const isClash = !!clashPairs[u.id];
        if (isClash && !clashedEmitted[u.id] && !clashedEmitted[clashPairs[u.id]]) {
          const other = findById(clashPairs[u.id]);
          const mx = (u.x + (other ? other.x : u.x)) / 2;
          const my = (u.y + (other ? other.y : u.y)) / 2;
          emitAction({
            kind: 'clash',
            attackerId: u.id,
            targetId: other ? other.id : pending.targetId,
            side: u.side,
            phase: 'strike',
            ax: mx, ay: my, tx: mx, ty: my
          });
          clashedEmitted[u.id] = true;
          if (other) clashedEmitted[other.id] = true;
        }

        u._lastRanged = !!pending.ranged;
        resolveStrikeHit(u, target, pending, isClash);
        u.hitDone = true;
        u.atkCd = pending.usedSkill ? 3 : 2;
        u.stateT += 1;

        // strike 結束後若仲喺 strike 狀態（冇被改成 hurt／parry），轉 recover
        if (u.combatState === STATES.STRIKE && u.stateT >= u.stateDur) {
          setState(u, STATES.RECOVER, FEEL.recoverTicks);
          u.pending = null;
          emitAction({
            kind: 'recover',
            attackerId: u.id,
            side: u.side,
            phase: 'recover',
            ax: u.x, ay: u.y
          });
        }
      });
    }


    function getComboState() {
      const avail = !!comboDef;
      const partnersOk = avail && comboDef.heroes.every(function (hid) {
        const u = findById(hid);
        return u && u.hp > 0;
      });
      return {
        available: avail,
        ready: avail && !comboUsed && partnersOk,
        used: comboUsed,
        armed: comboArmed,
        name: comboDef ? comboDef.name : null,
        heroes: comboDef ? comboDef.heroes.slice() : []
      };
    }

    function tryTriggerCombo() {
      if (!comboDef || comboUsed || comboArmed) return false;
      if (turn < 4) return false;
      const a = findById(comboDef.heroes[0]);
      const b = findById(comboDef.heroes[1]);
      if (!a || !b || a.hp <= 0 || b.hp <= 0) return false;
      if (!canControlMove(a) || !canControlMove(b)) return false;
      if (a.atkCd > 0 && b.atkCd > 0) return false;
      const target = pickTarget(units, 'enemy', a) || pickTarget(units, 'enemy', b);
      if (!target) return false;
      // 至少一人接近，或回合稍後自動釋放
      const near = dist(a, target) <= FIELD.skillRange || dist(b, target) <= FIELD.skillRange;
      if (!near && turn < 8) return false;
      if (Math.random() > (near ? 0.72 : 0.4) && turn < 14) return false;

      comboUsed = true;
      comboArmed = true;
      comboReadyHint = false;
      const mul = comboDef.damageMul || 1.9;
      const brk = comboDef.breakMit || 0.18;
      const cname = comboDef.name || '合擊';

      function armPartner(u, partnerId, primary) {
        u.pending = {
          targetId: target.id,
          skillMul: mul,
          comboMul: primary ? mul : Math.max(1.2, mul * 0.55),
          skillName: cname,
          usedSkill: true,
          ranged: false,
          isCombo: true,
          breakMit: primary ? brk : brk * 0.5,
          partnerId: partnerId
        };
        u.hitDone = false;
        u.telegraph = true;
        u.facing = target.x >= u.x ? 1 : -1;
        u.atkCd = 3;
        // 微進場感
        const toward = target.x >= u.x ? 1 : -1;
        u.vx += toward * 10;
        u.x = clampX(u, u.x + toward * 18);
        setState(u, STATES.WINDUP, Math.max(FEEL.windupTicks, 2));
        emitAction({
          kind: 'combo_windup',
          attackerId: u.id,
          partnerId: partnerId,
          targetId: target.id,
          skillName: cname,
          side: 'ally',
          telegraph: true,
          isCombo: true,
          primary: !!primary,
          phase: 'windup',
          ax: u.x, ay: u.y, tx: target.x, ty: target.y
        });
      }

      armPartner(a, b.id, true);
      armPartner(b, a.id, false);
      log('合擊「' + cname + '」——' + (comboDef.telegraph || '二人齊進！'), 'skill');
      holdTicks = Math.max(holdTicks, 1);
      return true;
    }

    function step() {
      if (finished) return;
      if (holdTicks > 0) {
        holdTicks -= 1;
        // hit-stop：凍結動作推進，但仍刷新畫面
        emit();
        return;
      }
      turn += 1;

      const alive = units.filter(function (u) { return u.hp > 0; });
      if (!alive.length) {
        emit();
        return;
      }

      // 1) 推進攻擊／硬直狀態（含判定幀）
      advanceCombatStates();

      // 2) 自由單位走位意圖
      alive.forEach(decideLocomotion);

      // 3) 分離
      separateAll();

      // 4) 位移
      alive.forEach(integrateMove);

      // 5) CD
      alive.forEach(function (u) {
        if (u.counterWindow > 0) {
          u.counterWindow -= 1;
          if (u.atkCd > 0) u.atkCd = 0;
          if (u.counterWindow <= 0 && !u._counterStrike) u.counterReady = false;
        }
        if (u.atkCd > 0 && canControlMove(u)) {
          u.atkCd -= 1;
          if (u.ai === 'charge' && u.engage && u.atkCd > 0 && Math.random() < 0.35) u.atkCd -= 1;
        }
      });

      // 6) 合擊優先（一場一次），再普通讀招
      if (tryTriggerCombo()) {
        // 合擊佔用本 tick 出手額度
      } else {
        const order = alive.filter(canControlMove).slice().sort(function (a, b) {
          return (b.nei + b.force * 0.5) - (a.nei + a.force * 0.5) + (Math.random() - 0.5);
        });
        let started = 0;
        for (let i = 0; i < order.length && started < 2; i++) {
          if (tryStartAttack(order[i])) started += 1;
        }
      }

      if (!living(units, 'enemy').length) {
        end(true);
        return;
      }
      if (!living(units, 'ally').length) {
        end(false);
        return;
      }
      emit();
    }

    function start() {
      if (timer) return;
      paused = false;
      finished = false;
      result = null;
      turn = 0;
      holdTicks = 0;
      log('戰鼓輕響，俠客出巡。', 'system');
      log('近戰須貼身：靠近、蓄勢、出手。速度 ×' + speedMul, 'system');
      const withBond = units.filter(function (u) {
        return u.side === 'ally' && u.bondMul > 1;
      });
      if (withBond.length) {
        log('羈絆加持，同隊出手更利（×' + withBond[0].bondMul.toFixed(2) + '）', 'skill');
      }
      if (comboDef) {
        log('合擊「' + comboDef.name + '」已備——條件滿足時自動施放（一場一次）', 'skill');
        comboReadyHint = true;
      }
      emit();
      timer = setInterval(step, effectiveTickMs());
      step();
    }

    function stop() {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
    }

    function setSpeed(mul) {
      let m = Number(mul);
      if (!(m > 0)) m = 1;
      if (m < 0.5) m = 0.5;
      if (m > 2) m = 2;
      m = Math.round(m * 2) / 2;
      speedMul = m;
      restartTimer();
      return speedMul;
    }

    function getSpeed() { return speedMul; }

    return {
      start: start,
      stop: stop,
      setSpeed: setSpeed,
      getSpeed: getSpeed,
      getUnits: function () { return units; },
      isFinished: function () { return finished; },
      setPaused: setPaused,
      isPaused: function () { return paused; },
      getComboState: getComboState
    };
  }

  function scaleEnemy(template, innLevel, bossScale) {
    // v1.4：前期略硬；後期成長 0.10 並軟頂，避免數值爆炸
    const lv = Math.max(1, innLevel || 1);
    const raw = 1 + (lv - 1) * 0.10;
    const soft = 1 + Math.min(0.55, (lv - 1) * 0.10); // 約 Lv.6.5 後趨平
    const base = Math.min(raw, soft);
    const scale = base * (bossScale || 1);
    const hp = Math.round(template.hp * scale);
    const out = {
      name: template.name,
      emoji: template.emoji,
      force: Math.round(template.force * scale),
      nei: Math.round(template.nei * scale),
      hp: hp,
      maxHp: hp,
      mitBonus: template.mitBonus || 0,
      shield: 0,
      ranged: !!(template.ranged || (template.name && template.name.indexOf('弓') >= 0) || template.emoji === '🏹'),
      ai: template.ai || null
    };
    if (template.skill) {
      out.skill = Object.assign({}, template.skill);
    }
    if (template.startShield) {
      out.shield = Math.round(hp * template.startShield);
    }
    if (template.id) out.id = template.id;
    if (template.sprite) out.sprite = template.sprite;
    return out;
  }

  global.WuxiaCombat = {
    createBattle: createBattle,
    scaleEnemy: scaleEnemy,
    cloneUnit: cloneUnit,
    calcDamage: calcDamage,
    buildAllyCombatant: buildAllyCombatant,
    randInt: randInt,
    getMartial: getMartial,
    FIELD: FIELD,
    FEEL: FEEL,
    STATES: STATES
  };
})(typeof window !== 'undefined' ? window : globalThis);
