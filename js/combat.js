/**
 * 俠客棧 — 自動即時走位戰鬥（v0.6.2）
 * 近身接觸感（貼身近戰／knockback）；戰鬥速度 0.5–2×；走位＋閃避招架；技能／遠程可遠放
 */
(function (global) {
  'use strict';

  const { randInt, getMartial } = global.WuxiaData;

  /** 戰場座標（對齊 CombatStage 400×180） */
  const FIELD = {
    W: 400,
    allyMinX: 28,
    allyMaxX: 210,
    enemyMinX: 190,
    enemyMaxX: 372,
    meleeRange: 24,
    contactRange: 16,
    skillRange: 118,
    rangedRange: 168,
    maxSpeed: 11,
    accel: 3.2,
    friction: 0.78,
    sepDist: 26,
    sepForce: 4.2,
    foeSepDist: 11,
    strafeY: 10,
    yMin: 96,
    yMax: 140,
    yBase: 108,
    iFrameDodge: 3,
    iFrameParry: 2
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
    if (n === 1) return FIELD.yBase + (side === 'enemy' ? 2 : 0);
    if (n === 2) return FIELD.yBase + (i === 0 ? -14 : 14);
    // 3+：上中下錯開，避免全擠同一點
    const spread = [-18, 0, 18, -9, 9];
    return FIELD.yBase + (spread[i % spread.length] || ((i % 2) * 12 - 6));
  }

  function cloneUnit(src, side, slotIndex, slotCount) {
    const n = Math.max(1, slotCount || 1);
    const i = slotIndex || 0;
    const gap = n <= 1 ? 0 : (n === 2 ? 48 : 40);
    const baseX = side === 'ally' ? 56 : 320;
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
      x: start + i * gap,
      y: y,
      homeY: y,
      lane: i,
      vx: 0,
      vy: 0,
      intent: 'approach',
      facing: side === 'ally' ? 1 : -1,
      invuln: 0,
      engage: false
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

    function effectiveTickMs() {
      return Math.max(120, Math.round(baseTickMs / speedMul));
    }

    function restartTimer() {
      if (!timer) return;
      clearInterval(timer);
      timer = setInterval(step, effectiveTickMs());
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
      log(win ? '—— 勝！殘敵潰逃 ——' : '—— 敗……俠客負傷退回 ——', win ? 'win' : 'lose');
      emit();
      if (hooks && hooks.onEnd) hooks.onEnd(result, units);
    }

    function emitAction(evt) {
      if (hooks && hooks.onAction) hooks.onAction(evt);
      if (!evt) return;
      // hold 以 tick 計；速度倍率會自然縮短 wall-clock
      if (evt.kind === 'hit') holdTicks = Math.max(holdTicks, evt.contact ? 2 : 1);
      else if (evt.kind === 'skill' || evt.kind === 'parry') holdTicks = Math.max(holdTicks, 3);
      else if (evt.kind === 'ko') holdTicks = Math.max(holdTicks, 4);
      else if (evt.kind === 'move') { /* no hold */ }
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
          a.vx -= nx * push;
          a.vy -= ny * push * 0.85;
          b.vx += nx * push;
          b.vy += ny * push * 0.85;
          // 同隊再強制錯開 lane
          if (same && Math.abs(a.homeY - b.homeY) < 4) {
            a.vy -= 1.2;
            b.vy += 1.2;
          }
        }
      }
    }

    function tryDefend(attacker, target, skillName) {
      if (target.invuln > 0) {
        // 無敵窗內強制當閃過
        const back = target.side === 'ally' ? -1 : 1;
        target.x = clampX(target, target.x + back * 8);
        target.y = clampY(target.homeY + (Math.random() < 0.5 ? -FIELD.strafeY : FIELD.strafeY));
        target.vx += back * 6;
        target.intent = 'dodge';
        log(target.emoji + target.name + ' 仍在身法之中，卸開 ' + attacker.name + '！', 'info');
        emitAction({
          kind: 'miss',
          attackerId: attacker.id,
          targetId: target.id,
          skillName: skillName,
          side: attacker.side,
          damage: 0,
          ax: attacker.x,
          ay: attacker.y,
          tx: target.x,
          ty: target.y,
          iFrame: true
        });
        return true;
      }

      const low = target.hp / target.maxHp < 0.35;
      const base = skillName ? 0.10 : 0.18;
      const chance = base + (low ? 0.08 : 0) + Math.min(0.08, (target.nei || 0) * 0.004);
      if (Math.random() >= chance) return false;

      const doParry = Math.random() < (low ? 0.35 : 0.5);
      const back = target.side === 'ally' ? -1 : 1;
      if (doParry) {
        target.vx += back * 7;
        target.vy += (Math.random() < 0.5 ? -1 : 1) * 5;
        target.x = clampX(target, target.x + back * 12);
        target.y = clampY(target.homeY + (Math.random() < 0.5 ? -FIELD.strafeY : FIELD.strafeY));
        target.intent = 'parry';
        target.invuln = Math.max(target.invuln, FIELD.iFrameParry);
        log(target.emoji + target.name + ' 提勁招架 ' + attacker.name + ' 的招！', 'info');
        emitAction({
          kind: 'parry',
          attackerId: attacker.id,
          targetId: target.id,
          skillName: skillName,
          side: attacker.side,
          damage: 0,
          ax: attacker.x,
          ay: attacker.y,
          tx: target.x,
          ty: target.y
        });
      } else {
        target.vx += back * 11;
        target.vy += (Math.random() < 0.5 ? -1 : 1) * 7;
        target.x = clampX(target, target.x + back * (16 + Math.random() * 10));
        target.y = clampY(target.homeY + (Math.random() < 0.5 ? -FIELD.strafeY * 1.6 : FIELD.strafeY * 1.6));
        target.intent = 'dodge';
        target.invuln = Math.max(target.invuln, FIELD.iFrameDodge);
        log(target.emoji + target.name + ' 側身閃過 ' + attacker.name + ' 的招！', 'info');
        emitAction({
          kind: 'miss',
          attackerId: attacker.id,
          targetId: target.id,
          skillName: skillName,
          side: attacker.side,
          damage: 0,
          ax: attacker.x,
          ay: attacker.y,
          tx: target.x,
          ty: target.y
        });
      }
      return true;
    }

    function resolveAttack(attacker, target, usedSkill, skillMul, skillName) {
      if (tryDefend(attacker, target, skillName)) {
        attacker.atkCd = usedSkill ? 3 : 2;
        return;
      }
      const dmg = calcDamage(attacker, target, skillMul);
      applyDamage(target, dmg);
      if (skillName && skillMul > 1) {
        log(attacker.emoji + attacker.name + '「' + skillName + '」→ ' + target.name + '，造成 ' + dmg + '！', 'skill');
      } else if (!skillName) {
        log(attacker.emoji + attacker.name + ' 攻向 ' + target.name + '，傷害 ' + dmg, attacker.side);
      }
      const contactDist = dist(attacker, target);
      const wasContact = !attacker._lastRanged && contactDist <= FIELD.contactRange + 4;
      emitAction({
        kind: usedSkill && skillMul > 1 ? 'skill' : 'hit',
        attackerId: attacker.id,
        targetId: target.id,
        damage: dmg,
        skillName: skillName,
        side: attacker.side,
        ranged: !!attacker._lastRanged,
        contact: wasContact || !attacker._lastRanged,
        ax: attacker.x,
        ay: attacker.y,
        tx: target.x,
        ty: target.y
      });
      // 近身：雙方短推開再彈回／摩擦（接觸感）
      const knock = attacker.side === 'ally' ? -1 : 1;
      if (!attacker._lastRanged) {
        const pushAtk = wasContact ? 7 : 5;
        const pushTgt = wasContact ? 14 : 10;
        attacker.vx += knock * pushAtk;
        target.vx -= knock * pushTgt;
        attacker.vy += (Math.random() < 0.5 ? -1 : 1) * (wasContact ? 2.2 : 1.2);
        target.vy += (Math.random() < 0.5 ? -1 : 1) * (wasContact ? 3.2 : 1.8);
        attacker.x = clampX(attacker, attacker.x + knock * (wasContact ? 6 : 4));
        target.x = clampX(target, target.x - knock * (wasContact ? 12 : 9));
        attacker.intent = 'hold';
        target.intent = 'hold';
      }
      attacker.atkCd = usedSkill ? 3 : 2;
      if (target.hp <= 0) {
        log(target.emoji + target.name + ' 倒下！', 'ko');
        emitAction({
          kind: 'ko',
          attackerId: attacker.id,
          targetId: target.id,
          side: attacker.side,
          damage: dmg,
          ax: attacker.x,
          ay: attacker.y,
          tx: target.x,
          ty: target.y
        });
      }
    }

    function decideAndMove(u) {
      if (u.hp <= 0) return;
      if (u.invuln > 0) u.invuln -= 1;

      const foeSide = u.side === 'ally' ? 'enemy' : 'ally';
      const target = pickTarget(units, foeSide, u);
      if (!target) {
        u.intent = 'hold';
        u.engage = false;
        u.vx *= FIELD.friction;
        u.vy *= FIELD.friction;
        return;
      }
      const d = dist(u, target);
      const ranged = isRangedUnit(u);
      const preferRange = ranged ? FIELD.rangedRange * 0.55 : FIELD.contactRange;
      const hpRatio = u.hp / u.maxHp;
      const skillReady = u.skill && u.cd <= 0;
      u.engage = !ranged && d <= FIELD.meleeRange + 2;
      u.contact = !ranged && d <= FIELD.contactRange + 2;

      if (hpRatio < 0.28 && d < FIELD.meleeRange + 20 && Math.random() < 0.7) {
        u.intent = 'retreat';
      } else if (ranged && d < FIELD.meleeRange + 8 && Math.random() < 0.55) {
        u.intent = 'retreat';
      } else if (d > (ranged ? FIELD.rangedRange * 0.9 : FIELD.meleeRange)) {
        u.intent = 'approach';
      } else if (d < preferRange - 8 && !ranged && Math.random() < 0.28) {
        u.intent = 'strafe';
      } else {
        u.intent = 'hold';
      }

      if (skillReady && d <= FIELD.skillRange && d > FIELD.meleeRange && Math.random() < 0.45) {
        u.intent = 'hold';
      }

      const toward = target.x >= u.x ? 1 : -1;
      u.facing = toward;
      let ax = 0;
      let ay = 0;
      const speedScale = 0.85 + Math.random() * 0.3;

      if (u.intent === 'approach') {
        ax = toward * FIELD.accel * speedScale;
        // 對齊自家 lane，同時略向目標 Y
        ay += ((u.homeY) - u.y) * 0.22;
        ay += ((target.y || target.homeY) - u.y) * 0.06;
      } else if (u.intent === 'retreat') {
        ax = -toward * FIELD.accel * 1.05 * speedScale;
        ay += (u.homeY - u.y) * 0.3;
      } else if (u.intent === 'strafe') {
        ax = toward * FIELD.accel * 0.18;
        const side = (u.lane % 2 === 0) ? -1 : 1;
        ay += side * FIELD.accel * 0.7 + (u.homeY - u.y) * 0.15;
      } else {
        ax *= 0.2;
        ay += (u.homeY - u.y) * 0.35;
        // 近戰圈內微幅對峙，唔原地黏死
        if (u.engage && Math.random() < 0.35) {
          ay += (Math.random() < 0.5 ? -1 : 1) * 1.2;
        }
      }

      u.vx = (u.vx + ax) * FIELD.friction;
      u.vy = (u.vy + ay) * FIELD.friction;
      const sp = Math.sqrt(u.vx * u.vx + u.vy * u.vy);
      const maxSp = FIELD.maxSpeed * speedScale;
      if (sp > maxSp) {
        u.vx = (u.vx / sp) * maxSp;
        u.vy = (u.vy / sp) * maxSp;
      }
    }

    function integrateMove(u) {
      if (u.hp <= 0) return;
      u.x = clampX(u, u.x + u.vx);
      u.y = clampY(u.y + u.vy);
    }

    function tryAct(attacker) {
      if (attacker.hp <= 0) return false;
      if (attacker.atkCd > 0) return false;
      // 閃避／招架硬直短窗：唔好邊閃邊砍
      if (attacker.intent === 'dodge' || attacker.intent === 'parry') {
        if (attacker.invuln > 0) return false;
      }

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
          log(attacker.emoji + attacker.name + ' 使出「' + skillName + '」，回復 ' + healAmt + ' 氣血！', 'skill');
          emitAction({
            kind: 'heal',
            attackerId: attacker.id,
            targetId: attacker.id,
            heal: healAmt,
            skillName: skillName,
            side: attacker.side,
            ax: attacker.x,
            ay: attacker.y
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
            ax: attacker.x,
            ay: attacker.y
          });
        }
        if (attacker.skill.weaken) {
          target.weaken = Math.max(target.weaken || 0, attacker.skill.weaken);
          log(attacker.emoji + attacker.name + '「' + skillName + '」削弱 ' + target.name + '！', 'skill');
        }
        if (attacker.skill.heal && skillMul <= 1 && !attacker.skill.weaken) {
          didHealOnly = true;
          attacker.atkCd = 2;
        }
      }

      if (attacker.cd > 0) attacker.cd -= 1;
      if (attacker.weaken > 0) attacker.weaken = Math.max(0, attacker.weaken - 0.03);

      if (didHealOnly) return true;

      // 普攻：近戰必須距離內；遠程單位可在 rangedRange；技能傷害可遠放
      const canBasic = ranged ? rangedOk : meleeOk;
      const canSkillHit = usedSkill && skillMul > 1 && skillOk;

      if (!canBasic && !canSkillHit) {
        return false;
      }

      // 近戰隔空保險：再量一次距離，唔夠唔砍（技能／遠程除外）
      if (!ranged && !canSkillHit && dist(attacker, target) > FIELD.meleeRange) {
        return false;
      }

      if (canSkillHit || canBasic) {
        attacker._lastRanged = (ranged || canSkillHit) && d > FIELD.meleeRange;
        // 近戰：出手前撲到貼身，唔好隔空揮
        if (!attacker._lastRanged) {
          const toward = target.x >= attacker.x ? 1 : -1;
          let dNow = dist(attacker, target);
          if (dNow > FIELD.contactRange) {
            const close = Math.min(dNow - FIELD.contactRange + 1, 14);
            attacker.vx += toward * 6;
            attacker.x = clampX(attacker, attacker.x + toward * close);
            // 微對齊 Y，兩人碰撞框重疊
            attacker.y = clampY(attacker.y + ((target.y || target.homeY) - attacker.y) * 0.45);
            dNow = dist(attacker, target);
          }
          // 仍太遠就唔斬（避免隔空）
          if (dNow > FIELD.meleeRange) {
            attacker.intent = 'approach';
            return false;
          }
        }
        resolveAttack(attacker, target, usedSkill && skillMul > 1, skillMul, skillName);
        return true;
      }
      return false;
    }

    function step() {
      if (finished) return;
      if (holdTicks > 0) {
        holdTicks -= 1;
        emit();
        return;
      }
      turn += 1;

      const alive = units.filter(function (u) { return u.hp > 0; });
      if (!alive.length) {
        emit();
        return;
      }

      // 1) 意圖＋加速度
      alive.forEach(decideAndMove);
      // 2) 分離力（防疊）
      separateAll();
      // 3) 積分位移
      alive.forEach(integrateMove);

      alive.forEach(function (u) {
        if (u.atkCd > 0) u.atkCd -= 1;
      });

      const order = alive.slice().sort(function (a, b) {
        return (b.nei + b.force * 0.5) - (a.nei + a.force * 0.5) + (Math.random() - 0.5);
      });
      let acted = 0;
      for (let i = 0; i < order.length && acted < 2; i++) {
        if (tryAct(order[i])) acted += 1;
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
      finished = false;
      result = null;
      turn = 0;
      holdTicks = 0;
      log('戰鼓擂響，俠客出巡！', 'system');
      log('雙方自動走位——貼身交鋒；遠程／技能可遠放。速度 ×' + speedMul, 'system');
      const withBond = units.filter(function (u) {
        return u.side === 'ally' && u.bondMul > 1;
      });
      if (withBond.length) {
        log('羈絆加持！同隊攻擊 ×' + withBond[0].bondMul.toFixed(2), 'skill');
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
      // 吸附到 0.5 檔
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
      isFinished: function () { return finished; }
    };
  }

  function scaleEnemy(template, innLevel, bossScale) {
    const base = 1 + (innLevel - 1) * 0.12;
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
      ranged: !!(template.ranged || (template.name && template.name.indexOf('弓') >= 0) || template.emoji === '🏹')
    };
    if (template.skill) {
      out.skill = Object.assign({}, template.skill);
    }
    if (template.startShield) {
      out.shield = Math.round(hp * template.startShield);
    }
    if (template.id) out.id = template.id;
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
    FIELD: FIELD
  };
})(typeof window !== 'undefined' ? window : globalThis);
