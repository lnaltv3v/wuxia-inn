/**
 * 俠客棧 — 主循環、狀態、存檔、UI（v0.3：據點／設施／任務板）
 */
(function () {
  'use strict';

  const {
    GAME, INN_LEVELS, GUESTS, HERO_TEMPLATES, ENEMY_WAVES, TRAIN,
    MARTIAL_ARTS, BOND_EVENTS, LIBRARY,
    OUTPOSTS, FACILITIES, QUEST_TEMPLATES,
    weightedPick, randInt, heroStatsAtLevel,
    getMartial, getBondTier, nextBondTier, pairBondMul,
    getOutpost, getFacility, getQuestTemplate, dayKey
  } = WuxiaData;
  const { createBattle, scaleEnemy, buildAllyCombatant } = WuxiaCombat;

  let state = null;
  let tickTimer = null;
  let battle = null;
  let saveFlashUntil = 0;
  let activeTab = 'inn';
  let bondToast = null;
  let selectedOutpost = 'main';

  function makeHeroState(t, level) {
    const lv = level || 1;
    const stats = heroStatsAtLevel(t, lv);
    return {
      id: t.id,
      level: lv,
      favor: stats.favor,
      exp: 0,
      hp: stats.maxHp,
      recruited: true,
      activeSkill: t.defaultActive || null,
      passiveSkill: t.defaultPassive || null
    };
  }

  function defaultOutposts() {
    const o = {};
    OUTPOSTS.forEach((op) => {
      o[op.id] = {
        unlocked: !op.unlock,
        garrison: null // heroId or null
      };
    });
    return o;
  }

  function defaultFacilities() {
    const f = {};
    FACILITIES.forEach((fac) => { f[fac.id] = 0; });
    return f;
  }

  function defaultState() {
    const heroes = {};
    const unlockedManuals = [];
    HERO_TEMPLATES.forEach((t) => {
      if (!t.unlocked) return;
      heroes[t.id] = makeHeroState(t, 1);
      if (t.defaultActive && unlockedManuals.indexOf(t.defaultActive) < 0) {
        unlockedManuals.push(t.defaultActive);
      }
      if (t.defaultPassive && unlockedManuals.indexOf(t.defaultPassive) < 0) {
        unlockedManuals.push(t.defaultPassive);
      }
    });
    return {
      version: GAME.version,
      silver: 100,
      reputation: 0,
      innLevel: 1,
      heroes,
      party: [],
      log: [],
      lastTick: Date.now(),
      totalEarned: 0,
      battlesWon: 0,
      guestsServed: 0,
      unlockedManuals,
      seenEvents: [],
      libraryHero: null,
      outposts: defaultOutposts(),
      facilities: defaultFacilities(),
      questBoard: [],
      activeQuests: [],
      questDayKey: '',
      questsDone: 0
    };
  }

  /** 舊存檔缺欄位時填預設，保持相容 */
  function migrate(raw) {
    const base = defaultState();
    const s = Object.assign({}, base, raw);
    s.version = GAME.version;
    if (!Array.isArray(s.unlockedManuals)) s.unlockedManuals = base.unlockedManuals.slice();
    if (!Array.isArray(s.seenEvents)) s.seenEvents = [];
    if (!s.heroes || typeof s.heroes !== 'object') s.heroes = base.heroes;
    if (!Array.isArray(s.party)) s.party = [];
    if (!Array.isArray(s.log)) s.log = [];

    // v0.3 據點／設施／任務
    if (!s.outposts || typeof s.outposts !== 'object') s.outposts = defaultOutposts();
    OUTPOSTS.forEach((op) => {
      if (!s.outposts[op.id]) {
        s.outposts[op.id] = { unlocked: !op.unlock, garrison: null };
      } else {
        if (typeof s.outposts[op.id].unlocked !== 'boolean') {
          s.outposts[op.id].unlocked = !op.unlock;
        }
        if (s.outposts[op.id].garrison === undefined) s.outposts[op.id].garrison = null;
      }
    });
    if (!opUnlocked(s, 'main')) s.outposts.main.unlocked = true;

    if (!s.facilities || typeof s.facilities !== 'object') s.facilities = defaultFacilities();
    FACILITIES.forEach((fac) => {
      if (typeof s.facilities[fac.id] !== 'number') s.facilities[fac.id] = 0;
      s.facilities[fac.id] = Math.max(0, Math.min(fac.maxLevel, s.facilities[fac.id] | 0));
    });

    if (!Array.isArray(s.questBoard)) s.questBoard = [];
    if (!Array.isArray(s.activeQuests)) s.activeQuests = [];
    if (typeof s.questDayKey !== 'string') s.questDayKey = '';
    if (typeof s.questsDone !== 'number') s.questsDone = 0;

    HERO_TEMPLATES.forEach((t) => {
      if (t.unlocked && (!s.heroes[t.id] || !s.heroes[t.id].recruited)) {
        s.heroes[t.id] = makeHeroState(t, 1);
      }
      const h = s.heroes[t.id];
      if (!h) return;
      if (h.activeSkill === undefined) {
        h.activeSkill = h.recruited ? (t.defaultActive || null) : null;
      }
      if (h.passiveSkill === undefined) {
        h.passiveSkill = h.recruited ? (t.defaultPassive || null) : null;
      }
      if (typeof h.favor !== 'number') h.favor = t.base.favor;
      if (typeof h.level !== 'number') h.level = 1;
      if (typeof h.exp !== 'number') h.exp = 0;
      if (h.recruited) {
        if (h.activeSkill && s.unlockedManuals.indexOf(h.activeSkill) < 0) {
          s.unlockedManuals.push(h.activeSkill);
        }
        if (h.passiveSkill && s.unlockedManuals.indexOf(h.passiveSkill) < 0) {
          s.unlockedManuals.push(h.passiveSkill);
        }
      }
    });

    // 清掉無效出戰／駐守 id
    s.party = s.party.filter((id) => s.heroes[id] && s.heroes[id].recruited);
    OUTPOSTS.forEach((op) => {
      const g = s.outposts[op.id].garrison;
      if (g && !(s.heroes[g] && s.heroes[g].recruited)) {
        s.outposts[op.id].garrison = null;
      }
    });
    s.activeQuests = s.activeQuests.filter((q) => {
      if (!q || !Array.isArray(q.heroes)) return false;
      q.heroes = q.heroes.filter((id) => s.heroes[id] && s.heroes[id].recruited);
      return q.heroes.length > 0 && q.endsAt;
    });

    return s;
  }

  function opUnlocked(s, id) {
    return s.outposts && s.outposts[id] && s.outposts[id].unlocked;
  }

  function innInfo(level) {
    return INN_LEVELS.find((x) => x.level === level) || INN_LEVELS[0];
  }

  function facilityLevel(id) {
    return (state.facilities && state.facilities[id]) || 0;
  }

  /** 酒窖：收入額外倍率 */
  function cellarIncomeMul() {
    return 1 + facilityLevel('cellar') * 0.08;
  }

  /** 練武場：費用折扣、收益加成 */
  function trainingMods() {
    const lv = facilityLevel('training');
    return { costMul: 1 - lv * 0.10, gainBonus: lv };
  }

  /** 醫館：每 tick 回血比例、戰後療傷比例 */
  function clinicMods() {
    const lv = facilityLevel('clinic');
    return { regenBonus: lv * 0.02, postHeal: lv * 0.08 };
  }

  function heroRuntime(id) {
    const h = state.heroes[id];
    const t = HERO_TEMPLATES.find((x) => x.id === id);
    if (!h || !t) return null;
    const stats = heroStatsAtLevel(t, h.level);
    const activeMartial = getMartial(h.activeSkill) || getMartial(t.defaultActive);
    const active = h.recruited ? (getMartial(h.activeSkill) || activeMartial) : null;
    const passive = h.recruited ? getMartial(h.passiveSkill) : null;
    const favor = h.favor;
    const bond = getBondTier(favor);
    const next = nextBondTier(favor);
    const station = findHeroStation(id);
    const onQuest = findHeroQuest(id);
    return {
      id,
      name: t.name,
      title: t.title,
      emoji: t.emoji,
      lore: t.lore,
      unlockCost: t.unlockCost,
      unlockReq: t.unlockReq || null,
      level: h.level,
      favor,
      bond,
      nextBond: next,
      force: stats.force,
      nei: stats.nei,
      maxHp: stats.maxHp,
      hp: Math.min(h.hp != null ? h.hp : stats.maxHp, stats.maxHp),
      recruited: !!h.recruited,
      activeSkillId: h.activeSkill,
      passiveSkillId: h.passiveSkill,
      activeMartial: active,
      passiveMartial: passive,
      station,
      onQuest,
      busy: !!(station || onQuest),
      skill: active ? {
        name: active.name,
        mul: active.effect.mul || 1.5,
        chance: active.effect.chance || 0.2,
        heal: active.effect.heal || 0
      } : null
    };
  }

  function findHeroStation(heroId) {
    for (const op of OUTPOSTS) {
      if (state.outposts[op.id] && state.outposts[op.id].garrison === heroId) {
        return op.id;
      }
    }
    return null;
  }

  function findHeroQuest(heroId) {
    const q = state.activeQuests.find((aq) => aq.heroes && aq.heroes.indexOf(heroId) >= 0);
    return q ? q.uid : null;
  }

  function pushLog(msg, kind) {
    const time = new Date().toLocaleTimeString('zh-HK', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    state.log.unshift({ t: time, msg, kind: kind || 'info' });
    if (state.log.length > 100) state.log.length = 100;
    if (activeTab === 'log') renderLog();
  }

  function showBondToast(title, text) {
    bondToast = { title, text };
    renderHeroes();
    setTimeout(() => {
      bondToast = null;
      if (activeTab === 'heroes') renderHeroes();
    }, 6000);
  }

  function checkBondEvents(heroId, prevFavor, newFavor) {
    const events = BOND_EVENTS[heroId] || [];
    const unlocked = [];
    events.forEach((ev) => {
      if (prevFavor < ev.favorNeed && newFavor >= ev.favorNeed) {
        if (state.seenEvents.indexOf(ev.id) < 0) {
          state.seenEvents.push(ev.id);
          unlocked.push(ev);
        }
      }
    });
    return unlocked;
  }

  function maxFavorAmongRecruited() {
    let m = 0;
    Object.keys(state.heroes).forEach((id) => {
      const h = state.heroes[id];
      if (h && h.recruited) m = Math.max(m, h.favor || 0);
    });
    return m;
  }

  function canRecruit(t) {
    if (!t.unlockReq) return { ok: true };
    const req = t.unlockReq;
    const reasons = [];
    if (req.reputation != null && state.reputation < req.reputation) {
      reasons.push(`聲望 ${req.reputation}`);
    }
    if (req.innLevel != null && state.innLevel < req.innLevel) {
      reasons.push(`客棧 Lv.${req.innLevel}`);
    }
    if (req.anyFavor != null && maxFavorAmongRecruited() < req.anyFavor) {
      reasons.push(`任俠客好感 ${req.anyFavor}`);
    }
    return { ok: reasons.length === 0, reasons };
  }

  // ——— 存檔 ———
  function save(silent) {
    try {
      state.lastTick = Date.now();
      localStorage.setItem(GAME.saveKey, JSON.stringify(state));
      saveFlashUntil = Date.now() + 1500;
      if (!silent) updateTopbar();
    } catch (e) {
      console.warn('存檔失敗', e);
    }
  }

  function load() {
    try {
      const raw = localStorage.getItem(GAME.saveKey);
      if (!raw) return null;
      const data = JSON.parse(raw);
      if (!data || typeof data.silver !== 'number') return null;
      return data;
    } catch (e) {
      return null;
    }
  }

  function resetGame() {
    if (battle) {
      battle.stop();
      battle = null;
    }
    state = defaultState();
    ensureQuestBoard(true);
    save(true);
    pushLog('新的江湖路開始了。客棧雖小，俠義長存。', 'system');
    renderAll();
  }

  // ——— 據點被動收入 ———
  function processOutpostIncome() {
    let gained = 0;
    let repGain = 0;
    OUTPOSTS.forEach((op) => {
      const st = state.outposts[op.id];
      if (!st || !st.unlocked) return;
      let income = op.baseIncome || 0;
      if (st.garrison) {
        const rt = heroRuntime(st.garrison);
        if (rt && rt.recruited) {
          // 等級略增駐守收益
          income += (op.garrisonIncome || 0) * (1 + (rt.level - 1) * 0.05);
          if (Math.random() < (op.garrisonRepChance || 0)) repGain += 1;
        }
      }
      if (income > 0) {
        const pay = Math.max(0, Math.round(income * cellarIncomeMul()));
        gained += pay;
      }
    });
    if (gained > 0) {
      state.silver += gained;
      state.totalEarned += gained;
    }
    if (repGain > 0) state.reputation += repGain;
    return { gained, repGain };
  }

  // ——— 放置收入 ———
  function processTicks(count) {
    if (count <= 0) return 0;
    const inn = innInfo(state.innLevel);
    const incomeMul = inn.incomeMul * cellarIncomeMul();
    let gained = 0;
    let outpostTotal = 0;
    for (let i = 0; i < count; i++) {
      const chance = Math.min(0.85, 0.35 + inn.guestCap * 0.05);
      if (Math.random() <= chance) {
        const guest = weightedPick(GUESTS);
        const pay = Math.round(randInt(guest.payMin, guest.payMax) * incomeMul);
        gained += pay;
        state.guestsServed += 1;
        if (i === count - 1 || count <= 3) {
          const verb = guest.kind === 'stay' ? '住店一夜' : '點了一桌酒菜';
          pushLog(`${guest.name}${verb}，收入 ${pay} 兩。`, 'earn');
        }
      }
      const op = processOutpostIncome();
      outpostTotal += op.gained;
    }
    if (count > 3 && gained > 0) {
      pushLog(`掛機片刻，接待多位客人，共得 ${gained} 兩。`, 'earn');
    }
    if (outpostTotal > 0 && count > 1) {
      pushLog(`分舵／哨站累積銀兩 ${outpostTotal}。`, 'earn');
    } else if (outpostTotal > 0 && count === 1 && Math.random() < 0.12) {
      pushLog(`據點駐守進帳 ${outpostTotal} 兩。`, 'earn');
    }
    state.silver += gained;
    state.totalEarned += gained;
    if (gained > 0 && Math.random() < 0.15) {
      state.reputation += 1;
    }
    return gained + outpostTotal;
  }

  function applyOffline() {
    const now = Date.now();
    const elapsed = Math.max(0, now - (state.lastTick || now));
    const maxMs = GAME.offlineCapHours * 3600 * 1000;
    const capped = Math.min(elapsed, maxMs);
    const ticks = Math.floor(capped / GAME.tickMs);
    if (ticks > 0) {
      const g = processTicks(ticks);
      if (g > 0) {
        pushLog(`離線約 ${Math.round(capped / 60000)} 分鐘，累積銀兩 ${g}。`, 'system');
      }
    }
    state.lastTick = now;
    settleQuests();
  }

  function gameTick() {
    if (battle) {
      settleQuests();
      return;
    }
    processTicks(1);
    const clinic = clinicMods();
    const regenRate = 0.02 + clinic.regenBonus;
    Object.keys(state.heroes).forEach((id) => {
      const rt = heroRuntime(id);
      if (!rt || !rt.recruited) return;
      if (rt.onQuest) return; // 任務中不回血
      if (state.heroes[id].hp < rt.maxHp) {
        state.heroes[id].hp = Math.min(rt.maxHp, state.heroes[id].hp + Math.ceil(rt.maxHp * regenRate));
      }
    });
    settleQuests();
    state.lastTick = Date.now();
    if (activeTab === 'inn') renderInn();
    if (activeTab === 'outposts') renderOutposts();
    updateTopbar();
    if (Math.floor(Date.now() / GAME.tickMs) % 10 === 0) save(true);
  }

  // ——— 經營 ———
  function tryUpgradeInn() {
    const next = INN_LEVELS.find((x) => x.level === state.innLevel + 1);
    if (!next) {
      pushLog('客棧已達當前版本最高等級。', 'warn');
      return;
    }
    if (state.reputation < next.repNeed || state.silver < next.silverNeed) {
      pushLog(`升級需聲望 ${next.repNeed}、銀兩 ${next.silverNeed}。`, 'warn');
      return;
    }
    state.silver -= next.silverNeed;
    state.innLevel = next.level;
    pushLog(`客棧升為「${next.name}」！俠客欄位 ${next.heroSlots}。`, 'system');
    save();
    renderAll();
  }

  function recruitHero(id) {
    const t = HERO_TEMPLATES.find((x) => x.id === id);
    if (!t) return;
    if (state.heroes[id] && state.heroes[id].recruited) {
      pushLog(`${t.name} 已在客棧。`, 'warn');
      return;
    }
    const gate = canRecruit(t);
    if (!gate.ok) {
      pushLog(`尚未達招募條件：${gate.reasons.join('、')}。`, 'warn');
      return;
    }
    const inn = innInfo(state.innLevel);
    const recruitedCount = Object.values(state.heroes).filter((h) => h.recruited).length;
    if (recruitedCount >= inn.heroSlots) {
      pushLog(`俠客欄位已滿（${inn.heroSlots}）。請先升級客棧。`, 'warn');
      return;
    }
    if (state.silver < t.unlockCost) {
      pushLog(`招募 ${t.name} 需要 ${t.unlockCost} 兩。`, 'warn');
      return;
    }
    state.silver -= t.unlockCost;
    state.heroes[id] = makeHeroState(t, 1);
    if (t.defaultActive && state.unlockedManuals.indexOf(t.defaultActive) < 0) {
      state.unlockedManuals.push(t.defaultActive);
    }
    if (t.defaultPassive && state.unlockedManuals.indexOf(t.defaultPassive) < 0) {
      state.unlockedManuals.push(t.defaultPassive);
    }
    pushLog(`以 ${t.unlockCost} 兩請「${t.name}」入駐！`, 'system');
    save();
    renderAll();
  }

  function trainHero(id, kind) {
    const conf = TRAIN[kind];
    const rt = heroRuntime(id);
    if (!conf || !rt || !rt.recruited) return;
    if (rt.busy) {
      pushLog(`${rt.name} 正在${rt.station ? '駐守據點' : '執行委託'}，無法訓練。`, 'warn');
      return;
    }
    const mods = trainingMods();
    const cost = Math.max(1, Math.round(conf.cost * mods.costMul));
    if (state.silver < cost) {
      pushLog(`銀兩不足（需 ${cost}）。`, 'warn');
      return;
    }
    state.silver -= cost;
    const h = state.heroes[id];
    if (kind === 'favor') {
      const prev = h.favor;
      h.favor = Math.min(100, h.favor + conf.gain);
      pushLog(`與 ${rt.name} 談心論交，好感 +${conf.gain}（${getBondTier(h.favor).name}）。`, 'favor');
      const evs = checkBondEvents(id, prev, h.favor);
      evs.forEach((ev) => {
        pushLog(`【羈絆·${ev.title}】${ev.text}`, 'bond');
        showBondToast(ev.title, ev.text);
      });
    } else {
      const gain = conf.gain + mods.gainBonus;
      h.exp = (h.exp || 0) + gain;
      while (h.exp >= 10) {
        h.exp -= 10;
        h.level += 1;
        const ns = heroStatsAtLevel(HERO_TEMPLATES.find((x) => x.id === id), h.level);
        h.hp = ns.maxHp;
        pushLog(`${rt.name} 修為精進，升至 Lv.${h.level}！`, 'level');
      }
      const prev = h.favor;
      h.favor = Math.min(100, h.favor + conf.favor);
      if (kind === 'force') {
        pushLog(`${rt.name} 苦練刀劍，消耗 ${cost} 兩${mods.gainBonus ? `（練武場 +${mods.gainBonus} 修為）` : ''}。`, 'train');
      } else {
        pushLog(`${rt.name} 調息吐納，消耗 ${cost} 兩${mods.gainBonus ? `（練武場 +${mods.gainBonus} 修為）` : ''}。`, 'train');
      }
      const evs = checkBondEvents(id, prev, h.favor);
      evs.forEach((ev) => {
        pushLog(`【羈絆·${ev.title}】${ev.text}`, 'bond');
        showBondToast(ev.title, ev.text);
      });
    }
    save();
    renderHeroes();
    updateTopbar();
  }

  function toggleParty(id) {
    const rt = heroRuntime(id);
    if (!rt || !rt.recruited) return;
    if (rt.busy && state.party.indexOf(id) < 0) {
      pushLog(`${rt.name} 正在${rt.station ? '駐守' : '執行委託'}，無法出戰。`, 'warn');
      return;
    }
    const idx = state.party.indexOf(id);
    if (idx >= 0) {
      state.party.splice(idx, 1);
    } else {
      if (state.party.length >= GAME.maxParty) {
        pushLog('出戰最多 3 人。', 'warn');
        return;
      }
      state.party.push(id);
    }
    save(true);
    renderHeroes();
    renderCombat();
  }

  // ——— 據點 ———
  function canUnlockOutpost(op) {
    if (!op.unlock) return { ok: true };
    const u = op.unlock;
    const reasons = [];
    if (state.innLevel < u.innLevel) reasons.push(`客棧 Lv.${u.innLevel}`);
    if (state.reputation < u.reputation) reasons.push(`聲望 ${u.reputation}`);
    if (state.silver < u.silver) reasons.push(`銀兩 ${u.silver}`);
    return { ok: reasons.length === 0, reasons, cost: u.silver };
  }

  function unlockOutpost(id) {
    const op = getOutpost(id);
    if (!op || !op.unlock) return;
    if (state.outposts[id].unlocked) {
      pushLog(`${op.name} 已開設。`, 'warn');
      return;
    }
    const gate = canUnlockOutpost(op);
    if (!gate.ok) {
      pushLog(`開設條件未足：${gate.reasons.join('、')}。`, 'warn');
      return;
    }
    state.silver -= op.unlock.silver;
    state.outposts[id].unlocked = true;
    pushLog(`開設「${op.name}」！可派俠客駐守增收。`, 'system');
    save();
    renderOutposts();
    updateTopbar();
  }

  function setGarrison(outpostId, heroId) {
    const op = getOutpost(outpostId);
    if (!op || !state.outposts[outpostId] || !state.outposts[outpostId].unlocked) return;

    // 撤下
    if (!heroId || heroId === '') {
      const prev = state.outposts[outpostId].garrison;
      state.outposts[outpostId].garrison = null;
      if (prev) pushLog(`${heroRuntime(prev).name} 結束駐守「${op.name}」。`, 'system');
      save(true);
      renderOutposts();
      renderHeroes();
      return;
    }

    const rt = heroRuntime(heroId);
    if (!rt || !rt.recruited) return;
    if (rt.onQuest) {
      pushLog(`${rt.name} 正在執行委託。`, 'warn');
      return;
    }
    // 從其他據點撤下
    OUTPOSTS.forEach((o) => {
      if (state.outposts[o.id].garrison === heroId) {
        state.outposts[o.id].garrison = null;
      }
    });
    // 從出戰隊伍撤下
    const pidx = state.party.indexOf(heroId);
    if (pidx >= 0) state.party.splice(pidx, 1);

    state.outposts[outpostId].garrison = heroId;
    pushLog(`${rt.name} 駐守「${op.name}」，該點收益提升。`, 'system');
    save(true);
    renderOutposts();
    renderHeroes();
    renderCombat();
  }

  // ——— 設施 ———
  function tryBuildFacility(id) {
    const fac = getFacility(id);
    if (!fac) return;
    const lv = facilityLevel(id);
    if (lv >= fac.maxLevel) {
      pushLog(`${fac.name} 已達最高等級。`, 'warn');
      return;
    }
    const cost = fac.costs[lv];
    const repNeed = fac.repNeed[lv];
    if (state.reputation < repNeed) {
      pushLog(`建造／升級 ${fac.name} 需聲望 ${repNeed}。`, 'warn');
      return;
    }
    if (state.silver < cost) {
      pushLog(`銀兩不足（需 ${cost}）。`, 'warn');
      return;
    }
    state.silver -= cost;
    state.facilities[id] = lv + 1;
    const verb = lv === 0 ? '建成' : `升至 Lv.${lv + 1}`;
    pushLog(`${fac.emoji}${fac.name}${verb}！${fac.effectLabel(lv + 1)}`, 'system');
    save();
    renderInn();
    renderOutposts();
    updateTopbar();
  }

  // ——— 任務板 ———
  function makeQuestInstance(tpl) {
    return {
      uid: 'q_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 6),
      templateId: tpl.id,
      name: tpl.name,
      emoji: tpl.emoji,
      kind: tpl.kind,
      desc: tpl.desc,
      durationSec: tpl.durationSec,
      heroesNeed: tpl.heroesNeed,
      rewardSilver: tpl.rewardSilver.slice(),
      rewardRep: tpl.rewardRep.slice(),
      manualChance: tpl.manualChance
    };
  }

  function rollQuestBoard() {
    const pool = QUEST_TEMPLATES.filter((q) => state.innLevel >= q.minInn);
    const board = [];
    const used = {};
    let guard = 0;
    while (board.length < GAME.questBoardSize && guard < 40) {
      guard += 1;
      const pick = weightedPick(pool);
      if (!pick) break;
      // 允許同模板重複較少：優先不重複
      if (used[pick.id] && board.length < pool.length) continue;
      used[pick.id] = true;
      board.push(makeQuestInstance(pick));
    }
    // 若因去重不足，補滿
    while (board.length < GAME.questBoardSize) {
      const pick = weightedPick(pool);
      if (!pick) break;
      board.push(makeQuestInstance(pick));
    }
    return board;
  }

  function ensureQuestBoard(force) {
    const today = dayKey();
    if (force || state.questDayKey !== today || !state.questBoard.length) {
      state.questDayKey = today;
      state.questBoard = rollQuestBoard();
      if (!force) pushLog('任務板已按日刷新。', 'system');
    }
  }

  function refreshQuestBoard(paid) {
    if (state.activeQuests.length) {
      // 允許刷新板，不影響進行中
    }
    if (paid) {
      if (state.silver < GAME.questRefreshCost) {
        pushLog(`刷新需 ${GAME.questRefreshCost} 兩。`, 'warn');
        return;
      }
      state.silver -= GAME.questRefreshCost;
      pushLog(`花費 ${GAME.questRefreshCost} 兩刷新任務板。`, 'system');
    }
    state.questBoard = rollQuestBoard();
    state.questDayKey = dayKey();
    save();
    renderOutposts();
    updateTopbar();
  }

  function availableHeroesForQuest() {
    return HERO_TEMPLATES
      .map((t) => heroRuntime(t.id))
      .filter((r) => r && r.recruited && !r.busy && state.party.indexOf(r.id) < 0);
  }

  function startQuest(uid, heroIds) {
    const idx = state.questBoard.findIndex((q) => q.uid === uid);
    if (idx < 0) {
      pushLog('委託已不在任務板。', 'warn');
      return;
    }
    const q = state.questBoard[idx];
    if (!Array.isArray(heroIds) || heroIds.length !== q.heroesNeed) {
      pushLog(`此委託需派出 ${q.heroesNeed} 名空閒俠客。`, 'warn');
      return;
    }
    for (const hid of heroIds) {
      const rt = heroRuntime(hid);
      if (!rt || !rt.recruited || rt.busy || state.party.indexOf(hid) >= 0) {
        pushLog('所選俠客不可用（駐守／出戰／任務中）。', 'warn');
        return;
      }
    }
    // 從駐守／出戰再保險清一次
    heroIds.forEach((hid) => {
      OUTPOSTS.forEach((o) => {
        if (state.outposts[o.id].garrison === hid) state.outposts[o.id].garrison = null;
      });
      const p = state.party.indexOf(hid);
      if (p >= 0) state.party.splice(p, 1);
    });

    const endsAt = Date.now() + q.durationSec * 1000;
    state.activeQuests.push({
      uid: q.uid,
      templateId: q.templateId,
      name: q.name,
      emoji: q.emoji,
      kind: q.kind,
      heroes: heroIds.slice(),
      endsAt,
      durationSec: q.durationSec,
      rewardSilver: q.rewardSilver,
      rewardRep: q.rewardRep,
      manualChance: q.manualChance
    });
    state.questBoard.splice(idx, 1);
    const names = heroIds.map((id) => heroRuntime(id).name).join('、');
    pushLog(`派出 ${names} 執行「${q.name}」（約 ${q.durationSec} 秒後結算）。`, 'system');
    save();
    renderOutposts();
    renderHeroes();
    renderCombat();
  }

  function settleQuests() {
    const now = Date.now();
    const done = [];
    state.activeQuests = state.activeQuests.filter((q) => {
      if (q.endsAt > now) return true;
      done.push(q);
      return false;
    });
    if (!done.length) return;
    done.forEach((q) => {
      const silver = randInt(q.rewardSilver[0], q.rewardSilver[1]);
      const rep = randInt(q.rewardRep[0], q.rewardRep[1]);
      state.silver += silver;
      state.reputation += rep;
      state.questsDone += 1;
      let dropMsg = '';
      if (Math.random() < (q.manualChance || 0)) {
        const drop = rollManualDropForced();
        if (drop) {
          if (drop.already) {
            dropMsg = ` 秘籍共鳴折銀 +${drop.bonus}。`;
          } else {
            dropMsg = ` 偶獲秘籍「${drop.name}」！`;
            pushLog(`委託收穫秘籍：「${drop.name}」。`, 'skill');
          }
        }
      }
      q.heroes.forEach((id) => {
        if (!state.heroes[id]) return;
        const prev = state.heroes[id].favor;
        state.heroes[id].favor = Math.min(100, state.heroes[id].favor + 1);
        state.heroes[id].exp = (state.heroes[id].exp || 0) + 2;
        // 任務中輕傷，醫館抵消
        const rt = heroRuntime(id);
        if (rt) {
          const dmg = Math.round(rt.maxHp * 0.08);
          state.heroes[id].hp = Math.max(1, (state.heroes[id].hp || rt.maxHp) - dmg);
          const clinic = clinicMods();
          if (clinic.postHeal > 0) {
            state.heroes[id].hp = Math.min(rt.maxHp, state.heroes[id].hp + Math.round(rt.maxHp * clinic.postHeal));
          }
        }
        const evs = checkBondEvents(id, prev, state.heroes[id].favor);
        evs.forEach((ev) => pushLog(`【羈絆·${ev.title}】${ev.text}`, 'bond'));
      });
      const names = q.heroes.map((id) => {
        const r = heroRuntime(id);
        return r ? r.name : id;
      }).join('、');
      pushLog(`委託「${q.name}」完成！${names}歸來，銀兩 +${silver}、聲望 +${rep}。${dropMsg}`, 'win');
    });
    save(true);
    if (activeTab === 'outposts') renderOutposts();
    if (activeTab === 'heroes') renderHeroes();
    updateTopbar();
  }

  // ——— 武學／藏書閣 ———
  function ownsManual(mid) {
    return state.unlockedManuals.indexOf(mid) >= 0;
  }

  function manualPrice(m) {
    if (ownsManual(m.id)) return LIBRARY.equipCost;
    return Math.round(m.learnCost * LIBRARY.buyMul);
  }

  function learnOrEquip(heroId, manualId) {
    const m = getMartial(manualId);
    const h = state.heroes[heroId];
    const t = HERO_TEMPLATES.find((x) => x.id === heroId);
    if (!m || !h || !h.recruited || !t) return;

    const price = manualPrice(m);
    if (state.silver < price) {
      pushLog(`銀兩不足（需 ${price} 兩）。`, 'warn');
      return;
    }

    const isNew = !ownsManual(m.id);
    state.silver -= price;
    if (isNew) state.unlockedManuals.push(m.id);

    if (m.type === 'active') {
      h.activeSkill = m.id;
      pushLog(`${t.name} ${isNew ? '研習' : '改習'}主動武學「${m.name}」（${price} 兩）。`, 'skill');
    } else {
      h.passiveSkill = m.id;
      pushLog(`${t.name} ${isNew ? '研習' : '改習'}被動武學「${m.name}」（${price} 兩）。`, 'skill');
    }
    save();
    renderInn();
    renderHeroes();
    updateTopbar();
  }

  function clearPassive(heroId) {
    const h = state.heroes[heroId];
    if (!h || !h.recruited) return;
    h.passiveSkill = null;
    pushLog(`${heroRuntime(heroId).name} 卸下被動武學。`, 'skill');
    save();
    renderInn();
    renderHeroes();
  }

  /** applyCombatChance=true：出巡掉落；false：任務板已過 manualChance 後必抽 */
  function rollManualDropInner(applyCombatChance) {
    if (applyCombatChance && Math.random() > GAME.dropManualChance) return null;
    const locked = MARTIAL_ARTS.filter((m) => !ownsManual(m.id));
    const pool = locked.length ? locked : MARTIAL_ARTS;
    const pick = weightedPick(pool.map((m) => Object.assign({}, m, { weight: m.dropWeight })));
    if (!pick) return null;
    if (!ownsManual(pick.id)) {
      state.unlockedManuals.push(pick.id);
      return pick;
    }
    const bonus = Math.round(pick.learnCost * 0.25);
    state.silver += bonus;
    return { name: pick.name, already: true, bonus };
  }

  function rollManualDrop() {
    return rollManualDropInner(true);
  }

  function rollManualDropForced() {
    return rollManualDropInner(false);
  }

  // ——— 戰鬥 ———
  function startPatrol(waveId) {
    if (battle) {
      pushLog('已在戰鬥中。', 'warn');
      return;
    }
    if (!state.party.length) {
      pushLog('請先在「俠客」分頁編入出戰隊伍。', 'warn');
      activeTab = 'heroes';
      renderAll();
      return;
    }
    const wave = ENEMY_WAVES.find((w) => w.id === waveId) || ENEMY_WAVES[0];
    if (state.innLevel < wave.minInnLevel) {
      pushLog(`此敵需客棧 Lv.${wave.minInnLevel}。`, 'warn');
      return;
    }

    const favors = state.party.map((id) => (state.heroes[id] ? state.heroes[id].favor : 0));
    const bondInfo = pairBondMul(favors);

    const allies = state.party.map((id) => {
      const rt = heroRuntime(id);
      if (!rt) return null;
      return buildAllyCombatant(rt, bondInfo.mul);
    }).filter(Boolean);

    if (allies.some((a) => a.hp <= 0)) {
      pushLog('有俠客氣血耗盡，請先回客棧休養生息。', 'warn');
      return;
    }

    const enemies = wave.enemies.map((e) => scaleEnemy(e, state.innLevel));
    const combatLogEl = document.getElementById('combat-log');
    if (combatLogEl) combatLogEl.innerHTML = '';

    activeTab = 'combat';
    setTab('combat');

    battle = createBattle(allies, enemies, {
      tickMs: GAME.combatTickMs,
      onLog(msg, kind) {
        appendCombatLog(msg, kind);
      },
      onUpdate(snap) {
        renderBattleUnits(snap.units);
      },
      onEnd(result, units) {
        const clinic = clinicMods();
        units.filter((u) => u.side === 'ally').forEach((u) => {
          if (state.heroes[u.id]) {
            let hp = Math.max(0, u.hp);
            if (result === 'win' && clinic.postHeal > 0) {
              const rt = heroRuntime(u.id);
              if (rt) hp = Math.min(rt.maxHp, hp + Math.round(rt.maxHp * clinic.postHeal));
            }
            state.heroes[u.id].hp = hp;
          }
        });
        if (result === 'win') {
          const silver = randInt(wave.rewardSilver[0], wave.rewardSilver[1]);
          const rep = randInt(wave.rewardRep[0], wave.rewardRep[1]);
          state.silver += silver;
          state.reputation += rep;
          state.battlesWon += 1;
          state.party.forEach((id) => {
            if (state.heroes[id]) {
              const prev = state.heroes[id].favor;
              state.heroes[id].favor = Math.min(100, state.heroes[id].favor + 2);
              state.heroes[id].exp = (state.heroes[id].exp || 0) + 3;
              const evs = checkBondEvents(id, prev, state.heroes[id].favor);
              evs.forEach((ev) => {
                pushLog(`【羈絆·${ev.title}】${ev.text}`, 'bond');
              });
            }
          });
          let dropMsg = '';
          const drop = rollManualDrop();
          if (drop) {
            if (drop.already) {
              dropMsg = ` 秘籍共鳴，額外銀兩 +${drop.bonus}。`;
              appendCombatLog(`已藏「${drop.name}」抄本，折銀 ${drop.bonus}`, 'skill');
            } else {
              dropMsg = ` 獲得秘籍「${drop.name}」！`;
              pushLog(`戰利秘籍：「${drop.name}」已入藏書閣。`, 'skill');
              appendCombatLog(`掉落秘籍：${drop.name}`, 'skill');
            }
          }
          pushLog(`剿匪勝利！獲銀兩 ${silver}、聲望 ${rep}。${dropMsg}`, 'win');
          appendCombatLog(`戰利品：銀兩 +${silver}，聲望 +${rep}`, 'win');
          if (bondInfo.mul > 1) {
            appendCombatLog(`羈絆「${bondInfo.tier.name}」加成生效（×${bondInfo.mul.toFixed(2)}）`, 'skill');
          }
        } else {
          pushLog('出巡失利，俠客帶傷而回……', 'lose');
        }
        battle = null;
        save();
        renderAll();
      }
    });
    battle.start();
    renderCombat();
  }

  function stopBattle() {
    if (!battle) return;
    battle.stop();
    battle = null;
    pushLog('你鳴金收兵，隊伍撤回客棧。', 'system');
    renderCombat();
  }

  // ——— UI ———
  function $(id) { return document.getElementById(id); }

  function updateTopbar() {
    const inn = innInfo(state.innLevel);
    $('stat-silver').textContent = Math.floor(state.silver);
    $('stat-rep').textContent = state.reputation;
    $('stat-inn').textContent = `Lv.${state.innLevel} ${inn.name}`;
    const saveEl = $('stat-save');
    if (Date.now() < saveFlashUntil) {
      saveEl.textContent = '已存檔';
      saveEl.classList.add('ok');
    } else {
      saveEl.textContent = '自動存檔';
      saveEl.classList.remove('ok');
    }
  }

  function setTab(name) {
    activeTab = name;
    document.querySelectorAll('.tab-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.tab === name);
    });
    document.querySelectorAll('.panel').forEach((p) => {
      p.classList.toggle('hidden', p.id !== 'panel-' + name);
    });
  }

  function favorBarHtml(favor, bond) {
    const next = nextBondTier(favor);
    const max = next ? next.min : 100;
    const prevMin = bond.min;
    const span = Math.max(1, max - prevMin);
    const pct = next ? Math.min(100, Math.round(((favor - prevMin) / span) * 100)) : 100;
    return `<div class="bars bond-bars">
      <div class="bar-label">好感 ${favor}/100 · 羈絆「${bond.name}」${next ? ` → ${next.name}（${next.min}）` : '（已滿）'}</div>
      <div class="bar bond"><i style="width:${Math.round((favor / 100) * 100)}%"></i></div>
      <div class="bar-label tiny">本階進度 ${pct}%</div>
    </div>`;
  }

  function formatRemain(ms) {
    const s = Math.max(0, Math.ceil(ms / 1000));
    if (s >= 60) return Math.floor(s / 60) + '分' + (s % 60) + '秒';
    return s + '秒';
  }

  function renderInn() {
    const inn = innInfo(state.innLevel);
    const next = INN_LEVELS.find((x) => x.level === state.innLevel + 1);
    const el = $('panel-inn');
    const recruited = Object.values(state.heroes).filter((h) => h.recruited).length;
    const recruitedHeroes = HERO_TEMPLATES
      .map((t) => heroRuntime(t.id))
      .filter((r) => r && r.recruited);

    const selId = state.libraryHero && state.heroes[state.libraryHero] && state.heroes[state.libraryHero].recruited
      ? state.libraryHero
      : (recruitedHeroes[0] ? recruitedHeroes[0].id : null);
    state.libraryHero = selId;
    const selRt = selId ? heroRuntime(selId) : null;

    let libHtml = '<p class="muted">尚無入駐俠客。</p>';
    if (selRt) {
      const opts = recruitedHeroes.map((r) =>
        `<option value="${r.id}" ${r.id === selId ? 'selected' : ''}>${r.emoji}${r.name}</option>`
      ).join('');
      const manuals = MARTIAL_ARTS.map((m) => {
        const owned = ownsManual(m.id);
        const price = manualPrice(m);
        const equipped = (m.type === 'active' && selRt.activeSkillId === m.id) ||
          (m.type === 'passive' && selRt.passiveSkillId === m.id);
        const tag = m.type === 'active' ? '主動' : '被動';
        return `<div class="manual-row ${owned ? 'owned' : ''} ${equipped ? 'equipped' : ''}">
          <div class="manual-info">
            <b>${m.name}</b> <span class="pill">${tag}</span>
            ${owned ? '<span class="pill jade">已藏</span>' : '<span class="pill">未獲</span>'}
            ${equipped ? '<span class="pill cinnabar">裝備中</span>' : ''}
            <div class="muted">${m.desc}</div>
          </div>
          <button class="btn tiny ${equipped ? 'danger' : 'primary'}" data-learn="${m.id}" data-hero="${selId}"
            ${equipped ? 'disabled' : ''}>${equipped ? '已裝備' : (owned ? `改習 ${price}兩` : `購抄 ${price}兩`)}</button>
        </div>`;
      }).join('');

      libHtml = `
        <div class="lib-head">
          <label>傳功對象
            <select id="lib-hero">${opts}</select>
          </label>
          <span class="muted">目前：主動「${selRt.activeMartial ? selRt.activeMartial.name : '無'}」／被動「${selRt.passiveMartial ? selRt.passiveMartial.name : '無'}」</span>
          ${selRt.passiveSkillId ? `<button class="btn tiny" id="btn-clear-passive">卸下被動</button>` : ''}
        </div>
        <div class="manual-list">${manuals}</div>
        <p class="tip">💡 出巡勝利約三成機率掉落秘籍抄本；已擁有則改習僅收手續費。未擁有可高價購買。</p>
      `;
    }

    const facHtml = FACILITIES.map((fac) => {
      const lv = facilityLevel(fac.id);
      const maxed = lv >= fac.maxLevel;
      const cost = maxed ? 0 : fac.costs[lv];
      const repNeed = maxed ? 0 : fac.repNeed[lv];
      const can = !maxed && state.silver >= cost && state.reputation >= repNeed;
      return `<div class="facility-row">
        <div class="facility-info">
          <b>${fac.emoji} ${fac.name}</b> <span class="pill">${lv}/${fac.maxLevel}</span>
          <div class="muted">${fac.desc}</div>
          <div class="muted">效果：${fac.effectLabel(lv)}</div>
        </div>
        ${maxed
          ? '<span class="pill jade">滿級</span>'
          : `<button class="btn tiny ${can ? 'primary' : ''}" data-build="${fac.id}" ${can ? '' : ''}>
              ${lv === 0 ? '建造' : '升級'} ${cost}兩${repNeed ? ` · 聲望${repNeed}` : ''}
            </button>`}
      </div>`;
    }).join('');

    el.innerHTML = `
      <div class="card ink-card">
        <h2>🏯 ${inn.name}</h2>
        <p class="muted">客棧乃江湖樞紐：賺錢、招募、休養生息、藏書練功。設施加成已計入收入與訓練。</p>
        <div class="stat-grid">
          <div><span class="label">收入倍率</span><b>×${(inn.incomeMul * cellarIncomeMul()).toFixed(2)}</b></div>
          <div><span class="label">客容量</span><b>${inn.guestCap}</b></div>
          <div><span class="label">俠客欄位</span><b>${recruited}/${inn.heroSlots}</b></div>
          <div><span class="label">累計收入</span><b>${state.totalEarned}</b></div>
        </div>
        ${next ? `
          <div class="upgrade-box">
            <p>下一級「${next.name}」需：聲望 <b>${next.repNeed}</b>、銀兩 <b>${next.silverNeed}</b></p>
            <button class="btn primary" id="btn-upgrade">升級客棧</button>
          </div>` : `<p class="muted">已達目前最高等級。</p>`}
      </div>
      <div class="card">
        <h3>🏗️ 本棧設施</h3>
        <p class="muted">酒窖增收、練武場降費增益、醫館加快回血與戰後療傷。</p>
        <div class="facility-list">${facHtml}</div>
      </div>
      <div class="card">
        <h3>📚 藏書閣／練功</h3>
        <p class="muted">已收藏秘籍 ${state.unlockedManuals.length}/${MARTIAL_ARTS.length}</p>
        ${libHtml}
      </div>
      <div class="card">
        <h3>今日流水</h3>
        <p>已接待客人 <b>${state.guestsServed}</b> 位 · 勝仗 <b>${state.battlesWon}</b> 場 · 委託 <b>${state.questsDone}</b> 件</p>
        <p class="tip">💡 放置中每秒可能有客人上門；離線最長計算 ${GAME.offlineCapHours} 小時。據點與任務請到「據點」分頁。</p>
      </div>
    `;
    const btn = $('btn-upgrade');
    if (btn) btn.onclick = tryUpgradeInn;
    const sel = $('lib-hero');
    if (sel) {
      sel.onchange = () => {
        state.libraryHero = sel.value;
        renderInn();
      };
    }
    const clr = $('btn-clear-passive');
    if (clr) clr.onclick = () => clearPassive(selId);
    el.querySelectorAll('[data-learn]').forEach((b) => {
      b.onclick = () => learnOrEquip(b.dataset.hero, b.dataset.learn);
    });
    el.querySelectorAll('[data-build]').forEach((b) => {
      b.onclick = () => tryBuildFacility(b.dataset.build);
    });
  }

  function renderOutposts() {
    ensureQuestBoard(false);
    settleQuests();
    const el = $('panel-outposts');
    if (!el) return;

    if (!selectedOutpost || !getOutpost(selectedOutpost)) selectedOutpost = 'main';

    const mapHtml = OUTPOSTS.map((op) => {
      const st = state.outposts[op.id];
      const unlocked = st && st.unlocked;
      const active = selectedOutpost === op.id;
      return `<button type="button" class="outpost-chip ${active ? 'active' : ''} ${unlocked ? '' : 'locked'}" data-select-op="${op.id}">
        ${op.emoji} ${op.name}${unlocked ? '' : ' 🔒'}
      </button>`;
    }).join('');

    const op = getOutpost(selectedOutpost);
    const st = state.outposts[selectedOutpost];
    let detailHtml = '';
    if (!st.unlocked) {
      const gate = canUnlockOutpost(op);
      detailHtml = `
        <h3>${op.emoji} ${op.name}</h3>
        <p class="lore">${op.desc}</p>
        <p>開設需：客棧 Lv.${op.unlock.innLevel}、聲望 ${op.unlock.reputation}、銀兩 ${op.unlock.silver}
          ${gate.ok ? ' ✅' : '（未達：' + gate.reasons.join('、') + '）'}</p>
        <button class="btn primary" id="btn-unlock-op" ${gate.ok ? '' : 'disabled'}>開設分舵（${op.unlock.silver} 兩）</button>
      `;
    } else {
      const gId = st.garrison;
      const gRt = gId ? heroRuntime(gId) : null;
      const freeHeroes = HERO_TEMPLATES
        .map((t) => heroRuntime(t.id))
        .filter((r) => r && r.recruited && (!r.busy || r.station === selectedOutpost) && state.party.indexOf(r.id) < 0 && !r.onQuest);
      const opts = `<option value="">— 無駐守 —</option>` + freeHeroes.map((r) =>
        `<option value="${r.id}" ${gId === r.id ? 'selected' : ''}>${r.emoji}${r.name} Lv.${r.level}</option>`
      ).join('');
      const incomeHint = gRt
        ? `駐守中：約 +${(op.garrisonIncome * (1 + (gRt.level - 1) * 0.05)).toFixed(1)} 兩/秒（酒窖加成另計）`
        : `無駐守：基礎 +${op.baseIncome}/秒`;
      detailHtml = `
        <h3>${op.emoji} ${op.name}</h3>
        <p class="lore">${op.desc}</p>
        <p class="muted">${incomeHint} · 駐守聲望機率 ${(op.garrisonRepChance * 100).toFixed(0)}%</p>
        <div class="garrison-row">
          <label>派駐俠客
            <select id="garrison-select">${opts}</select>
          </label>
          <button class="btn tiny primary" id="btn-set-garrison">確認駐守</button>
        </div>
        <p class="tip">💡 駐守中的俠客不能出戰或接委託；等級越高，據點進帳越高。</p>
      `;
    }

    // 設施摘要（本棧也顯示於據點頁）
    const facSummary = FACILITIES.map((f) => {
      const lv = facilityLevel(f.id);
      return `<span class="tag">${f.emoji}${f.name} Lv.${lv}</span>`;
    }).join(' ');

    // 進行中任務
    const now = Date.now();
    const activeHtml = state.activeQuests.length
      ? state.activeQuests.map((q) => {
          const names = q.heroes.map((id) => {
            const r = heroRuntime(id);
            return r ? r.emoji + r.name : id;
          }).join('、');
          const left = formatRemain(q.endsAt - now);
          const pct = Math.min(100, Math.round((1 - (q.endsAt - now) / (q.durationSec * 1000)) * 100));
          return `<div class="quest-row active">
            <div><b>${q.emoji} ${q.name}</b> <span class="pill cinnabar">${q.kind}</span>
              <div class="muted">執行：${names} · 剩餘 ${left}</div>
              <div class="bar"><i style="width:${pct}%"></i></div>
            </div>
          </div>`;
        }).join('')
      : '<p class="muted">尚無進行中的委託。</p>';

    // 任務板
    const boardHtml = state.questBoard.length
      ? state.questBoard.map((q) => {
          const free = availableHeroesForQuest();
          const can = free.length >= q.heroesNeed;
          const heroOpts = free.map((r) =>
            `<option value="${r.id}">${r.emoji}${r.name} Lv.${r.level}</option>`
          ).join('');
          let picks = '';
          for (let i = 0; i < q.heroesNeed; i++) {
            picks += `<select class="quest-hero-pick" data-q="${q.uid}" data-slot="${i}">
              <option value="">選俠客 ${i + 1}</option>${heroOpts}
            </select>`;
          }
          return `<div class="quest-row">
            <div class="quest-info">
              <b>${q.emoji} ${q.name}</b> <span class="pill">${q.kind}</span>
              <div class="muted">${q.desc}</div>
              <div class="muted">需 ${q.heroesNeed} 人 · 約 ${q.durationSec} 秒 · 獎勵 ${q.rewardSilver[0]}–${q.rewardSilver[1]} 兩／聲望 ${q.rewardRep[0]}–${q.rewardRep[1]}${q.manualChance > 0.1 ? ' · 偶獲秘籍' : ''}</div>
              <div class="quest-picks">${picks}</div>
            </div>
            <button class="btn tiny primary" data-start-quest="${q.uid}" ${can ? '' : 'disabled'}>派出</button>
          </div>`;
        }).join('')
      : '<p class="muted">任務板已空，可刷新或等待明日自動刷新。</p>';

    el.innerHTML = `
      <div class="card ink-card">
        <h2>🗺️ 據點地圖</h2>
        <p class="muted">開設分舵、派駐俠客，穩定增收與聲望。</p>
        <div class="outpost-map">${mapHtml}</div>
        <div class="outpost-detail card-inner">${detailHtml}</div>
        <div class="facility-summary">本棧設施：${facSummary}</div>
      </div>
      <div class="card">
        <h3>📋 聲望任務板</h3>
        <p class="muted">每日自動刷新；亦可花 ${GAME.questRefreshCost} 兩立即刷新。委託為<strong>計時結算</strong>：派出後倒數結束自動發獎。</p>
        <div class="btn-row">
          <button class="btn tiny" id="btn-refresh-quests">刷新任務板（${GAME.questRefreshCost} 兩）</button>
        </div>
        <h4 class="subhead">進行中</h4>
        <div class="quest-list">${activeHtml}</div>
        <h4 class="subhead">可接委託</h4>
        <div class="quest-list">${boardHtml}</div>
      </div>
    `;

    el.querySelectorAll('[data-select-op]').forEach((b) => {
      b.onclick = () => {
        selectedOutpost = b.dataset.selectOp;
        renderOutposts();
      };
    });
    const unlockBtn = $('btn-unlock-op');
    if (unlockBtn) unlockBtn.onclick = () => unlockOutpost(selectedOutpost);
    const setG = $('btn-set-garrison');
    if (setG) {
      setG.onclick = () => {
        const sel = $('garrison-select');
        setGarrison(selectedOutpost, sel ? sel.value : '');
      };
    }
    const ref = $('btn-refresh-quests');
    if (ref) ref.onclick = () => refreshQuestBoard(true);

    el.querySelectorAll('[data-start-quest]').forEach((b) => {
      b.onclick = () => {
        const uid = b.dataset.startQuest;
        const picks = Array.from(el.querySelectorAll(`.quest-hero-pick[data-q="${uid}"]`))
          .map((s) => s.value)
          .filter(Boolean);
        // unique
        const uniq = [];
        picks.forEach((id) => { if (uniq.indexOf(id) < 0) uniq.push(id); });
        startQuest(uid, uniq);
      };
    });
  }

  function renderHeroes() {
    const el = $('panel-heroes');
    const inn = innInfo(state.innLevel);
    const mods = trainingMods();
    let toastHtml = '';
    if (bondToast) {
      toastHtml = `<div class="card bond-toast"><h3>💬 ${bondToast.title}</h3><p>${bondToast.text}</p></div>`;
    }

    let html = `${toastHtml}<div class="card"><h2>⚔️ 俠客名冊</h2>
      <p class="muted">欄位 ${Object.values(state.heroes).filter((h) => h.recruited).length}/${inn.heroSlots} · 出戰最多 ${GAME.maxParty} 人
        ${mods.gainBonus ? ` · 練武場：訓練費 ×${mods.costMul.toFixed(2)}、修為 +${mods.gainBonus}` : ''}</p>
      <div class="party-bar">出戰：${state.party.length ? state.party.map((id) => {
        const r = heroRuntime(id);
        return r ? `<span class="tag">${r.emoji}${r.name}</span>` : '';
      }).join('') : '<span class="muted">尚未編隊</span>'}</div>
    </div><div class="hero-grid">`;

    HERO_TEMPLATES.forEach((t) => {
      const h = state.heroes[t.id];
      const recruited = h && h.recruited;

      if (!recruited) {
        const gate = canRecruit(t);
        const reqLine = t.unlockReq
          ? `<p class="muted">條件：${[
              t.unlockReq.reputation != null ? `聲望≥${t.unlockReq.reputation}` : null,
              t.unlockReq.innLevel != null ? `客棧Lv≥${t.unlockReq.innLevel}` : null,
              t.unlockReq.anyFavor != null ? `任俠客好感≥${t.unlockReq.anyFavor}` : null
            ].filter(Boolean).join('、')} ${gate.ok ? '✅' : '（未達）'}</p>`
          : '';
        html += `<div class="card hero-card locked">
          <div class="hero-head">${t.emoji} <b>${t.name}</b> <span class="title">${t.title}</span></div>
          <p class="lore">${t.lore}</p>
          ${reqLine}
          <p>招募費用：<b>${t.unlockCost}</b> 兩</p>
          <button class="btn" data-recruit="${t.id}" ${gate.ok ? '' : 'disabled'}>${gate.ok ? '招募' : '條件未足'}</button>
        </div>`;
        return;
      }

      const rt = heroRuntime(t.id);
      const inParty = state.party.includes(t.id);
      const hpPct = Math.round((rt.hp / rt.maxHp) * 100);
      const events = BOND_EVENTS[t.id] || [];
      const evStatus = events.map((ev) => {
        const seen = state.seenEvents.indexOf(ev.id) >= 0;
        const ready = rt.favor >= ev.favorNeed;
        return `<span class="pill ${seen ? 'jade' : ready ? 'cinnabar' : ''}">${ev.title}${seen ? '✓' : ready ? '可觸' : `@${ev.favorNeed}`}</span>`;
      }).join(' ');
      const forceCost = Math.max(1, Math.round(TRAIN.force.cost * mods.costMul));
      const neiCost = Math.max(1, Math.round(TRAIN.nei.cost * mods.costMul));
      const favorCost = Math.max(1, Math.round(TRAIN.favor.cost * mods.costMul));
      let status = '';
      if (rt.station) {
        const op = getOutpost(rt.station);
        status = `<span class="pill jade">駐守 ${op ? op.name : rt.station}</span>`;
      } else if (rt.onQuest) {
        status = `<span class="pill cinnabar">委託中</span>`;
      }

      html += `<div class="card hero-card ${inParty ? 'in-party' : ''} ${rt.busy ? 'busy' : ''}">
        <div class="hero-head">${rt.emoji} <b>${rt.name}</b> <span class="title">${rt.title}</span>
          <span class="lv">Lv.${rt.level}</span></div>
        <p class="lore">${rt.lore}</p>
        ${status}
        <div class="bars">
          <div class="bar-label">氣血 ${rt.hp}/${rt.maxHp}</div>
          <div class="bar"><i style="width:${hpPct}%"></i></div>
        </div>
        ${favorBarHtml(rt.favor, rt.bond)}
        <div class="stat-grid compact">
          <div><span class="label">武力</span><b>${rt.force}</b></div>
          <div><span class="label">內力</span><b>${rt.nei}</b></div>
          <div><span class="label">主動</span><b class="skill-name">${rt.activeMartial ? rt.activeMartial.name : '—'}</b></div>
          <div><span class="label">被動</span><b class="skill-name">${rt.passiveMartial ? rt.passiveMartial.name : '—'}</b></div>
        </div>
        <div class="event-row muted">情誼：${evStatus || '—'}</div>
        <div class="btn-row">
          <button class="btn tiny" data-train="${t.id}" data-kind="force" ${rt.busy ? 'disabled' : ''}>練武 ${forceCost}兩</button>
          <button class="btn tiny" data-train="${t.id}" data-kind="nei" ${rt.busy ? 'disabled' : ''}>調息 ${neiCost}兩</button>
          <button class="btn tiny primary" data-train="${t.id}" data-kind="favor" ${rt.busy ? 'disabled' : ''}>談心 ${favorCost}兩</button>
          <button class="btn tiny ${inParty ? 'danger' : 'primary'}" data-party="${t.id}" ${rt.busy && !inParty ? 'disabled' : ''}>${inParty ? '撤下' : '出戰'}</button>
        </div>
      </div>`;
    });
    html += '</div>';
    el.innerHTML = html;
    el.querySelectorAll('[data-recruit]').forEach((b) => {
      b.onclick = () => recruitHero(b.dataset.recruit);
    });
    el.querySelectorAll('[data-train]').forEach((b) => {
      b.onclick = () => trainHero(b.dataset.train, b.dataset.kind);
    });
    el.querySelectorAll('[data-party]').forEach((b) => {
      b.onclick = () => toggleParty(b.dataset.party);
    });
  }

  function renderCombat() {
    const el = $('panel-combat');
    const waves = ENEMY_WAVES.filter((w) => w.minInnLevel <= state.innLevel + 1);
    const favors = state.party.map((id) => (state.heroes[id] ? state.heroes[id].favor : 0));
    const bondInfo = pairBondMul(favors);
    const partyHtml = state.party.length
      ? state.party.map((id) => {
          const r = heroRuntime(id);
          if (!r) return '';
          return `<span class="tag">${r.emoji}${r.name} HP${r.hp}/${r.maxHp}</span>`;
        }).join('')
      : '<span class="muted">未編隊——請到「俠客」勾選出戰</span>';

    const prevLog = $('combat-log') ? $('combat-log').innerHTML : '';
    const prevField = $('battle-field') ? $('battle-field').innerHTML : '';

    el.innerHTML = `
      <div class="card">
        <h2>🗡️ 出巡剿匪</h2>
        <p class="muted">全自動即時戰鬥。羈絆同隊加成：${state.party.length >= 2 ? `「${bondInfo.tier.name}」攻擊 ×${bondInfo.mul.toFixed(2)}` : '需至少 2 人'}</p>
        <div class="party-bar">隊伍：${partyHtml}</div>
        <div class="wave-list" id="wave-list"></div>
        <div class="btn-row">
          ${battle ? '<button class="btn danger" id="btn-flee">鳴金收兵</button>' : ''}
        </div>
      </div>
      <div class="card battle-card">
        <h3>戰場</h3>
        <div id="battle-field" class="battle-field">${battle ? prevField : '<p class="muted">尚未交鋒</p>'}</div>
        <div id="combat-log" class="combat-log">${prevLog}</div>
      </div>
    `;
    const list = $('wave-list');
    waves.forEach((w) => {
      const locked = state.innLevel < w.minInnLevel;
      const btn = document.createElement('button');
      btn.className = 'btn wave-btn' + (locked ? ' locked' : '');
      btn.disabled = !!battle || locked;
      btn.innerHTML = `<b>${w.name}</b><span>獎勵 ${w.rewardSilver[0]}–${w.rewardSilver[1]} 兩 · 聲望 ${w.rewardRep[0]}–${w.rewardRep[1]}${locked ? ` · 需客棧 Lv.${w.minInnLevel}` : ''}</span>`;
      btn.onclick = () => startPatrol(w.id);
      list.appendChild(btn);
    });
    const flee = $('btn-flee');
    if (flee) flee.onclick = stopBattle;
  }

  function renderBattleUnits(units) {
    const field = $('battle-field');
    if (!field) return;
    const allies = units.filter((u) => u.side === 'ally');
    const enemies = units.filter((u) => u.side === 'enemy');
    const row = (list, cls) => list.map((u) => {
      const pct = Math.max(0, Math.round((u.hp / u.maxHp) * 100));
      const dead = u.hp <= 0 ? ' dead' : '';
      const sh = u.shield > 0 ? ` · 盾${Math.round(u.shield)}` : '';
      return `<div class="unit ${cls}${dead}">
        <div class="u-name">${u.emoji} ${u.name}</div>
        <div class="bar"><i style="width:${pct}%"></i></div>
        <div class="u-hp">${Math.max(0, Math.round(u.hp))}/${u.maxHp}${sh}</div>
      </div>`;
    }).join('');
    field.innerHTML = `
      <div class="side allies">${row(allies, 'ally')}</div>
      <div class="vs">⚔</div>
      <div class="side enemies">${row(enemies, 'enemy')}</div>
    `;
  }

  function appendCombatLog(msg, kind) {
    const box = $('combat-log');
    if (!box) return;
    const line = document.createElement('div');
    line.className = 'clog ' + (kind || '');
    line.textContent = msg;
    box.prepend(line);
    while (box.children.length > 60) box.removeChild(box.lastChild);
  }

  function renderLog() {
    const el = $('panel-log');
    if (!el) return;
    el.innerHTML = `<div class="card"><h2>📜 江湖日誌</h2>
      <div class="log-list">${state.log.map((e) =>
        `<div class="log-line ${e.kind}"><span class="t">${e.t}</span>${e.msg}</div>`
      ).join('') || '<p class="muted">尚無記錄</p>'}</div>
      <div class="btn-row">
        <button class="btn" id="btn-save">手動存檔</button>
        <button class="btn danger" id="btn-reset">重置進度</button>
      </div>
    </div>`;
    $('btn-save').onclick = () => { save(); pushLog('手動存檔完成。', 'system'); };
    $('btn-reset').onclick = () => {
      if (confirm('確定要重置所有進度？')) resetGame();
    };
  }

  function renderAll() {
    updateTopbar();
    renderInn();
    renderOutposts();
    renderHeroes();
    renderCombat();
    renderLog();
    setTab(activeTab);
  }

  function init() {
    const loaded = load();
    if (loaded) {
      state = migrate(loaded);
      pushLog('讀取存檔成功（已遷移至 v' + GAME.version + '）。', 'system');
      ensureQuestBoard(false);
      applyOffline();
    } else {
      state = defaultState();
      ensureQuestBoard(true);
      pushLog('新開張！青衣劍客已願為客棧護院。可開分舵、建設施、接任務板委託。', 'system');
    }

    document.querySelectorAll('.tab-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        setTab(btn.dataset.tab);
        if (btn.dataset.tab === 'inn') renderInn();
        if (btn.dataset.tab === 'outposts') renderOutposts();
        if (btn.dataset.tab === 'heroes') renderHeroes();
        if (btn.dataset.tab === 'combat') renderCombat();
        if (btn.dataset.tab === 'log') renderLog();
      });
    });

    $('btn-manual-save').addEventListener('click', () => {
      save();
      pushLog('手動存檔完成。', 'system');
    });

    renderAll();
    tickTimer = setInterval(gameTick, GAME.tickMs);
    setInterval(() => { updateTopbar(); save(true); }, 15000);

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) save(true);
      else {
        applyOffline();
        renderAll();
      }
    });
    window.addEventListener('beforeunload', () => save(true));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
