/**
 * 俠客棧 — 自動即時戰鬥（v0.5.7：單人逐步出手＋命中停頓；onAction 含招架／閃避）
 */
(function (global) {
  'use strict';

  const { randInt, getMartial } = global.WuxiaData;

  function cloneUnit(src, side) {
    const u = {
      id: src.id || src.name + '_' + Math.random().toString(36).slice(2, 6),
      name: src.name,
      emoji: src.emoji || '⚔️',
      side,
      force: src.force,
      nei: src.nei || 0,
      hp: src.hp != null ? src.hp : src.maxHp,
      maxHp: src.maxHp || src.hp,
      skill: src.skill ? Object.assign({}, src.skill) : null,
      passive: src.passive ? Object.assign({}, src.passive) : null,
      cd: 0,
      shield: src.shield || 0,
      weaken: 0,
      mitBonus: src.mitBonus || 0,
      bondMul: src.bondMul || 1,
      regen: src.regen || 0
    };
    return u;
  }

  /** 依武學與被動，把俠客編成戰鬥單位 */
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
      force,
      nei,
      hp: hero.hp,
      maxHp: hero.maxHp,
      skill,
      passive: passive,
      shield,
      mitBonus,
      regen,
      bondMul: bondMul || 1
    };
  }

  function living(units, side) {
    return units.filter((u) => u.side === side && u.hp > 0);
  }

  function pickTarget(units, side) {
    const foes = living(units, side);
    if (!foes.length) return null;
    foes.sort((a, b) => a.hp / a.maxHp - b.hp / b.maxHp);
    return foes[0];
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
    const units = [
      ...allies.map((a) => cloneUnit(a, 'ally')),
      ...enemies.map((e) => cloneUnit(e, 'enemy'))
    ];
    let timer = null;
    let turn = 0;
    let finished = false;
    let result = null;
    let actCursor = 0;
    let holdTicks = 0; // 命中後跳過若干 tick，配合畫面 hit-stop

    function log(msg, kind) {
      if (hooks && hooks.onLog) hooks.onLog(msg, kind || 'info');
    }

    function emit() {
      if (hooks && hooks.onUpdate) {
        hooks.onUpdate({
          units: units.map((u) => Object.assign({}, u)),
          turn,
          finished,
          result
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
      // 命中／招架／擊倒：戰鬥邏輯短停，等刀光同閃白睇得清
      if (evt.kind === 'hit') holdTicks = Math.max(holdTicks, 1);
      else if (evt.kind === 'skill' || evt.kind === 'parry') holdTicks = Math.max(holdTicks, 2);
      else if (evt.kind === 'ko') holdTicks = Math.max(holdTicks, 3);
    }

    function act(attacker) {
      if (attacker.hp <= 0) return;

      // 被動回血
      if (attacker.regen > 0 && attacker.hp < attacker.maxHp) {
        const healAmt = Math.max(1, Math.round(attacker.maxHp * attacker.regen));
        attacker.hp = Math.min(attacker.maxHp, attacker.hp + healAmt);
      }

      const foeSide = attacker.side === 'ally' ? 'enemy' : 'ally';
      const target = pickTarget(units, foeSide);
      if (!target) return;

      let skillMul = 1;
      let skillName = null;
      let didHealOnly = false;
      let usedSkill = false;

      if (attacker.skill && attacker.cd <= 0 && Math.random() < (attacker.skill.chance || 0.2)) {
        skillMul = attacker.skill.mul || 1.5;
        skillName = attacker.skill.name;
        attacker.cd = 3;
        usedSkill = true;

        if (attacker.skill.heal) {
          const healAmt = Math.round(attacker.maxHp * attacker.skill.heal);
          attacker.hp = Math.min(attacker.maxHp, attacker.hp + healAmt);
          log(`${attacker.emoji}${attacker.name} 使出「${skillName}」，回復 ${healAmt} 氣血！`, 'skill');
          emitAction({
            kind: 'heal', attackerId: attacker.id, targetId: attacker.id,
            heal: healAmt, skillName: skillName, side: attacker.side
          });
        }
        if (attacker.skill.shield) {
          const sh = Math.round(attacker.maxHp * attacker.skill.shield);
          attacker.shield = (attacker.shield || 0) + sh;
          log(`${attacker.emoji}${attacker.name}「${skillName}」護體，護盾 +${sh}`, 'skill');
          emitAction({
            kind: 'shield', attackerId: attacker.id, targetId: attacker.id,
            shield: sh, skillName: skillName, side: attacker.side
          });
        }
        if (attacker.skill.weaken) {
          target.weaken = Math.max(target.weaken || 0, attacker.skill.weaken);
          log(`${attacker.emoji}${attacker.name}「${skillName}」削弱 ${target.name}！`, 'skill');
        }

        // 純治療技且 mul<=1 可不攻擊；有傷害倍率則繼續打
        if (attacker.skill.heal && skillMul <= 1 && !attacker.skill.weaken) {
          didHealOnly = true;
        }
      }

      if (attacker.cd > 0) attacker.cd -= 1;
      // 削弱每回合衰減
      if (attacker.weaken > 0) attacker.weaken = Math.max(0, attacker.weaken - 0.03);

      if (!didHealOnly) {
        // 偶爾閃避／招架（技能較難躲；約 10%／技能 4%）
        const dodgeChance = usedSkill ? 0.04 : 0.10;
        if (Math.random() < dodgeChance) {
          const doParry = Math.random() < 0.45;
          if (doParry) {
            log(`${target.emoji}${target.name} 提勁招架 ${attacker.name} 的招！`, 'info');
            emitAction({
              kind: 'parry', attackerId: attacker.id, targetId: target.id,
              skillName: skillName, side: attacker.side, damage: 0
            });
          } else {
            log(`${target.emoji}${target.name} 側身閃過 ${attacker.name} 的招！`, 'info');
            emitAction({
              kind: 'miss', attackerId: attacker.id, targetId: target.id,
              skillName: skillName, side: attacker.side, damage: 0
            });
          }
        } else {
          const dmg = calcDamage(attacker, target, skillMul);
          applyDamage(target, dmg);
          if (skillName && skillMul > 1) {
            log(`${attacker.emoji}${attacker.name}「${skillName}」→ ${target.name}，造成 ${dmg}！`, 'skill');
          } else if (!skillName) {
            log(`${attacker.emoji}${attacker.name} 攻向 ${target.name}，傷害 ${dmg}`, attacker.side);
          }
          emitAction({
            kind: usedSkill && skillMul > 1 ? 'skill' : 'hit',
            attackerId: attacker.id,
            targetId: target.id,
            damage: dmg,
            skillName: skillName,
            side: attacker.side
          });
          if (target.hp <= 0) {
            log(`${target.emoji}${target.name} 倒下！`, 'ko');
            emitAction({
              kind: 'ko', attackerId: attacker.id, targetId: target.id,
              side: attacker.side, damage: dmg
            });
          }
        }
      }
    }

    function step() {
      if (finished) return;
      if (holdTicks > 0) {
        holdTicks -= 1;
        emit();
        return;
      }
      turn += 1;
      const order = units
        .filter((u) => u.hp > 0)
        .sort((a, b) => b.nei + b.force * 0.5 - (a.nei + a.force * 0.5) + (Math.random() - 0.5));
      if (!order.length) {
        emit();
        return;
      }
      // 每次 tick 只一人出手，刀光／受擊幀先睇得清
      const u = order[actCursor % order.length];
      actCursor = (actCursor + 1) % order.length;
      act(u);
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
      actCursor = 0;
      holdTicks = 0;
      log('戰鼓擂響，俠客出巡！', 'system');
      const withBond = units.filter((u) => u.side === 'ally' && u.bondMul > 1);
      if (withBond.length) {
        log(`羈絆加持！同隊攻擊 ×${withBond[0].bondMul.toFixed(2)}`, 'skill');
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

    return { start, stop, getUnits: () => units, isFinished: () => finished };
  }

  function scaleEnemy(template, innLevel, bossScale) {
    // Boss 額外倍率，使難度高於普通山賊
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
      shield: 0
    };
    if (template.skill) {
      out.skill = Object.assign({}, template.skill);
    }
    if (template.startShield) {
      out.shield = Math.round(hp * template.startShield);
    }
    return out;
  }

  global.WuxiaCombat = {
    createBattle,
    scaleEnemy,
    cloneUnit,
    calcDamage,
    buildAllyCombatant,
    randInt,
    getMartial
  };
})(typeof window !== 'undefined' ? window : globalThis);
