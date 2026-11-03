/**
 * 俠客棧 — 自動即時走位戰鬥（v0.6.0）
 * 雙方自動靠近；近戰距離普攻；技能／遠程可遠放；AI 會閃避／招架／後退
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
    meleeRange: 46,
    skillRange: 118,
    rangedRange: 168,
    moveStep: 14,
    strafeY: 6,
    yBase: 108
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

  function cloneUnit(src, side, slotIndex, slotCount) {
    const n = Math.max(1, slotCount || 1);
    const i = slotIndex || 0;
    const gap = n <= 1 ? 0 : (n === 2 ? 42 : 36);
    const baseX = side === 'ally' ? 56 : 320;
    const start = baseX - ((n - 1) * gap) / 2;
    const y = FIELD.yBase + (i % 2) * 10 + (side === 'enemy' ? 2 : 0);
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
      atkCd: Math.floor(Math.random() * 2), // 錯開首擊
      shield: src.shield || 0,
      weaken: 0,
      mitBonus: src.mitBonus || 0,
      bondMul: src.bondMul || 1,
      regen: src.regen || 0,
      ranged: !!src.ranged || isRangedUnit(src),
      x: start + i * gap,
      y: y,
      homeY: y,
      intent: 'approach',
      facing: side === 'ally' ? 1 : -1
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
    // 優先血少，其次距離近
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
    return Math.sqrt(dx * dx + dy * dy * 0.35);
  }

  function clampX(u, x) {
    if (u.side === 'ally') {
      return Math.max(FIELD.allyMinX, Math.min(FIELD.allyMaxX, x));
    }
    return Math.max(FIELD.enemyMinX, Math.min(FIELD.enemyMaxX, x));
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
    const tickMs = (hooks && hooks.tickMs) || global.WuxiaData.GAME.combatTickMs;
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
      if (evt.kind === 'hit') holdTicks = Math.max(holdTicks, 1);
      else if (evt.kind === 'skill' || evt.kind === 'parry') holdTicks = Math.max(holdTicks, 2);
      else if (evt.kind === 'ko') holdTicks = Math.max(holdTicks, 3);
      else if (evt.kind === 'move') { /* no hold */ }
    }

    function tryDefend(attacker, target, skillName) {
      // AI 閃避／招架：近戰較易；技能較難；低血更傾向閃
      const low = target.hp / target.maxHp < 0.35;
      const base = skillName ? 0.10 : 0.18;
      const chance = base + (low ? 0.08 : 0) + Math.min(0.08, (target.nei || 0) * 0.004);
      if (Math.random() >= chance) return false;

      const doParry = Math.random() < (low ? 0.35 : 0.5);
      // 閃避／招架時側移或後撤
      const back = target.side === 'ally' ? -1 : 1;
      if (doParry) {
        target.x = clampX(target, target.x + back * 6);
        target.y = target.homeY + (Math.random() < 0.5 ? -FIELD.strafeY : FIELD.strafeY);
        target.intent = 'parry';
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
        target.x = clampX(target, target.x + back * (10 + Math.random() * 8));
        target.y = target.homeY + (Math.random() < 0.5 ? -FIELD.strafeY * 1.4 : FIELD.strafeY * 1.4);
        target.intent = 'dodge';
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
      emitAction({
        kind: usedSkill && skillMul > 1 ? 'skill' : 'hit',
        attackerId: attacker.id,
        targetId: target.id,
        damage: dmg,
        skillName: skillName,
        side: attacker.side,
        ranged: !!attacker._lastRanged,
        ax: attacker.x,
        ay: attacker.y,
        tx: target.x,
        ty: target.y
      });
      // 命中後小幅頂住／後退，避免黏著互砍
      const knock = attacker.side === 'ally' ? -1 : 1;
      if (!attacker._lastRanged) {
        attacker.x = clampX(attacker, attacker.x + knock * 4);
        target.x = clampX(target, target.x - knock * 6);
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
      const foeSide = u.side === 'ally' ? 'enemy' : 'ally';
      const target = pickTarget(units, foeSide, u);
      if (!target) {
        u.intent = 'hold';
        return;
      }
      const d = dist(u, target);
      const ranged = isRangedUnit(u);
      const preferRange = ranged ? FIELD.rangedRange * 0.55 : FIELD.meleeRange * 0.85;
      const hpRatio = u.hp / u.maxHp;
      const skillReady = u.skill && u.cd <= 0;

      // 低血：拉開距離
      if (hpRatio < 0.28 && d < FIELD.meleeRange + 20 && Math.random() < 0.7) {
        u.intent = 'retreat';
      } else if (ranged && d < FIELD.meleeRange + 8 && Math.random() < 0.55) {
        u.intent = 'retreat';
      } else if (d > (ranged ? FIELD.rangedRange * 0.9 : FIELD.meleeRange)) {
        u.intent = 'approach';
      } else if (d < preferRange - 10 && !ranged && Math.random() < 0.25) {
        u.intent = 'strafe';
      } else {
        u.intent = 'hold';
      }

      // 有技能且距離在技能範圍：可先站住準備放
      if (skillReady && d <= FIELD.skillRange && d > FIELD.meleeRange && Math.random() < 0.45) {
        u.intent = 'hold';
      }

      const toward = target.x >= u.x ? 1 : -1;
      u.facing = toward;
      let nx = u.x;
      let ny = u.y;
      const step = FIELD.moveStep * (0.75 + Math.random() * 0.5);

      if (u.intent === 'approach') {
        nx = u.x + toward * step;
        // 略對齊 Y，唔完全重疊
        ny = u.y + ((target.homeY || target.y) - u.y) * 0.15;
      } else if (u.intent === 'retreat') {
        nx = u.x - toward * step;
        ny = u.homeY + (Math.random() < 0.5 ? -2 : 2);
      } else if (u.intent === 'strafe') {
        nx = u.x + toward * (step * 0.2);
        ny = u.homeY + (Math.random() < 0.5 ? -FIELD.strafeY : FIELD.strafeY);
      } else {
        // hold：慢慢回 homeY
        ny = u.y + (u.homeY - u.y) * 0.25;
      }

      // 避免友軍嚴重重疊
      living(units, u.side).forEach(function (ally) {
        if (ally.id === u.id) return;
        if (Math.abs(nx - ally.x) < 18 && Math.abs(ny - ally.y) < 14) {
          nx += (nx >= ally.x ? 1 : -1) * 8;
          ny += (u.homeY >= ally.homeY ? 1 : -1) * 4;
        }
      });

      u.x = clampX(u, nx);
      u.y = Math.max(96, Math.min(140, ny));
    }

    function tryAct(attacker) {
      if (attacker.hp <= 0) return false;
      if (attacker.atkCd > 0) return false;

      // 被動回血（每次成功出手前）
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

      // 技能：可在 skillRange 釋放（唔一定要貼身）
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

      // 普攻：近戰要貼身；遠程單位可在 rangedRange 普攻
      const canBasic = ranged ? rangedOk : meleeOk;
      const canSkillHit = usedSkill && skillMul > 1 && skillOk;

      if (!canBasic && !canSkillHit) {
        // 未到距離：唔出手，繼續走位
        return false;
      }

      // 純技能傷害可遠放；否則近戰普攻
      if (canSkillHit || canBasic) {
        attacker._lastRanged = ranged && d > FIELD.meleeRange;
        // 近戰出手前再逼近一小步，動畫更貼
        if (!attacker._lastRanged && d > 28) {
          const toward = target.x >= attacker.x ? 1 : -1;
          attacker.x = clampX(attacker, attacker.x + toward * 8);
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

      // 1) 全員走位
      alive.forEach(decideAndMove);

      // 2) 冷卻遞減
      alive.forEach(function (u) {
        if (u.atkCd > 0) u.atkCd -= 1;
      });

      // 3) 按身法排序，最多兩人出手（保持慢節奏可讀）
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
      log('雙方自動走位——近則刀兵相接，遠則伺機放招。', 'system');
      const withBond = units.filter(function (u) {
        return u.side === 'ally' && u.bondMul > 1;
      });
      if (withBond.length) {
        log('羈絆加持！同隊攻擊 ×' + withBond[0].bondMul.toFixed(2), 'skill');
      }
      emit();
      timer = setInterval(step, tickMs);
      step();
    }

    function stop() {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
    }

    return {
      start: start,
      stop: stop,
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
