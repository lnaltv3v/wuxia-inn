/**
 * 俠客棧 — 靜態資料：俠客模板、敵人、武學、羈絆、據點、設施、任務、常數
 * v0.5.3
 */
(function (global) {
  'use strict';

  const GAME = {
    name: '俠客棧',
    version: '0.5.3',
    saveKey: 'wuxia-inn-save-v1',
    tickMs: 1200,
    offlineCapHours: 8,
    combatTickMs: 1000,
    dropManualChance: 0.32,
    maxParty: 3,
    questRefreshCost: 25,       // 手動刷新任務板銀兩
    questBoardSize: 3,
    maxGarrisonPerOutpost: 1    // 每據點駐守人數
  };

  /** 客棧等級表 */
  const INN_LEVELS = [
    { level: 1, name: '茅屋客棧', repNeed: 0, silverNeed: 0, incomeMul: 1.0, heroSlots: 2, guestCap: 3 },
    { level: 2, name: '青石小店', repNeed: 50, silverNeed: 200, incomeMul: 1.3, heroSlots: 3, guestCap: 5 },
    { level: 3, name: '江湖客棧', repNeed: 150, silverNeed: 600, incomeMul: 1.7, heroSlots: 4, guestCap: 7 },
    { level: 4, name: '名滿四方', repNeed: 400, silverNeed: 1500, incomeMul: 2.2, heroSlots: 5, guestCap: 10 },
    { level: 5, name: '天下第一棧', repNeed: 1000, silverNeed: 4000, incomeMul: 3.0, heroSlots: 6, guestCap: 14 }
  ];

  const GUESTS = [
    { id: 'wanderer', name: '過路客', weight: 40, payMin: 2, payMax: 5, kind: 'meal' },
    { id: 'merchant', name: '行商', weight: 25, payMin: 5, payMax: 12, kind: 'stay' },
    { id: 'scholar', name: '書生', weight: 15, payMin: 4, payMax: 8, kind: 'meal' },
    { id: 'knight', name: '遊俠', weight: 12, payMin: 8, payMax: 18, kind: 'stay' },
    { id: 'noble', name: '富紳', weight: 8, payMin: 15, payMax: 35, kind: 'stay' }
  ];

  /** 今日江湖傳聞（Hub 氣氛／日誌輕量內容，不改存檔結構） */
  const RUMORS = [
    '青石鎮夜市又見黑衣人閃過屋脊。',
    '有人說邊關哨站外有怪風，像黑風寨餘黨。',
    '鐵掌門舊識寄來藥方，醫館或許用得上。',
    '琴心師太曾於月下撫琴退賊，江湖仍傳。',
    '行商誇本棧茶香，願多住一晚。',
    '告示欄貼了尋人帖，酬銀不菲。',
    '酒窖陳釀開封，今晚客似更多。',
    '有遊俠於門前比劍，未傷和氣便散。',
    '聽說邪醫毒霧散於南邊河谷，切莫獨行。',
    '小二夢見客滿盈門——或許是個好兆頭。'
  ];


  /**
   * 據點／分舵
   * unlock：客棧等級、聲望、銀兩；incomePerTick／repChance 為駐守時被動收益基礎
   */
  const OUTPOSTS = [
    {
      id: 'main',
      name: '本棧',
      emoji: '🏯',
      desc: '江湖樞紐所在，設施皆建於此。駐守可略增本棧收入。',
      unlock: null,
      baseIncome: 0,
      garrisonIncome: 1.2,
      garrisonRepChance: 0.04
    },
    {
      id: 'qingshi',
      name: '青石鎮分舵',
      emoji: '🏘️',
      desc: '商旅雲集的小鎮分舵，適合派駐俠客招徠聲望與銀兩。',
      unlock: { innLevel: 2, reputation: 30, silver: 180 },
      baseIncome: 0.6,
      garrisonIncome: 2.5,
      garrisonRepChance: 0.08
    },
    {
      id: 'bianguan',
      name: '邊關哨站',
      emoji: '🏰',
      desc: '邊陲要衝，駐守可獲較高銀兩，偶得聲望。',
      unlock: { innLevel: 3, reputation: 100, silver: 420 },
      baseIncome: 1.0,
      garrisonIncome: 4.0,
      garrisonRepChance: 0.12
    }
  ];

  /**
   * 設施：建於本棧，可升級
   * maxLevel 含「已建造」等級；level 0 = 未建
   */
  const FACILITIES = [
    {
      id: 'cellar',
      name: '酒窖',
      emoji: '🍷',
      desc: '陳釀招客：每級提高客棧收入倍率。',
      maxLevel: 3,
      costs: [120, 280, 560],
      repNeed: [0, 20, 80],
      effectLabel: (lv) => lv ? `收入 +${(lv * 8)}%` : '未建'
    },
    {
      id: 'training',
      name: '練武場',
      emoji: '🥋',
      desc: '石鎖木樁齊備：每級降低訓練花費、略增練武／調息收益。',
      maxLevel: 3,
      costs: [140, 300, 620],
      repNeed: [10, 40, 100],
      effectLabel: (lv) => lv ? `訓練費 -${lv * 10}% · 收益 +${lv}` : '未建'
    },
    {
      id: 'clinic',
      name: '醫館',
      emoji: '💊',
      desc: '藥香滿室：加快休養生息回血，出巡歸隊額外療傷。',
      maxLevel: 3,
      costs: [150, 320, 650],
      repNeed: [15, 50, 120],
      effectLabel: (lv) => lv ? `回血 +${lv * 2}%/秒 · 戰後療 ${lv * 8}%` : '未建'
    }
  ];

  /**
   * 聲望任務模板
   * durationSec：派駐後計時結算（真實秒數）
   * heroesNeed：需派出人數
   */
  const QUEST_TEMPLATES = [
    {
      id: 'escort',
      name: '護送商隊',
      emoji: '🐴',
      kind: '護送',
      desc: '護送行商過山，途中或遇小匪。',
      durationSec: 45,
      heroesNeed: 1,
      rewardSilver: [35, 60],
      rewardRep: [4, 8],
      manualChance: 0.08,
      weight: 30,
      minInn: 1
    },
    {
      id: 'bandit_hunt',
      name: '剿匪懸賞',
      emoji: '🗡️',
      kind: '剿匪',
      desc: '官府懸賞：清剿近郊流寇。',
      durationSec: 70,
      heroesNeed: 2,
      rewardSilver: [70, 120],
      rewardRep: [8, 14],
      manualChance: 0.14,
      weight: 22,
      minInn: 1
    },
    {
      id: 'find_item',
      name: '尋物委託',
      emoji: '📿',
      kind: '尋物',
      desc: '書生遺失玉佩，請俠客沿官道尋回。',
      durationSec: 40,
      heroesNeed: 1,
      rewardSilver: [25, 45],
      rewardRep: [3, 6],
      manualChance: 0.10,
      weight: 28,
      minInn: 1
    },
    {
      id: 'deliver_letter',
      name: '傳書急遞',
      emoji: '✉️',
      kind: '護送',
      desc: '將密函送至青石鎮，越快越好。',
      durationSec: 35,
      heroesNeed: 1,
      rewardSilver: [30, 50],
      rewardRep: [5, 9],
      manualChance: 0.06,
      weight: 20,
      minInn: 2
    },
    {
      id: 'guard_caravan',
      name: '押運糧草',
      emoji: '📦',
      kind: '護送',
      desc: '邊軍糧草需人押運，報酬豐厚。',
      durationSec: 90,
      heroesNeed: 2,
      rewardSilver: [110, 180],
      rewardRep: [12, 20],
      manualChance: 0.18,
      weight: 12,
      minInn: 3
    },
    {
      id: 'herb_gather',
      name: '採藥問診',
      emoji: '🌿',
      kind: '尋物',
      desc: '醫館缺藥，入山採集珍稀草藥。',
      durationSec: 55,
      heroesNeed: 1,
      rewardSilver: [40, 70],
      rewardRep: [4, 7],
      manualChance: 0.12,
      weight: 18,
      minInn: 2
    }
  ];


  /**
   * 劇情章節：unlock 以聲望／客棧等級／勝仗數判定
   * 閱覽後發一次性獎勵；若有 bossId，閱覽後解鎖對應 Boss 戰
   */
  const STORY_CHAPTERS = [
    {
      id: 'ch1_lantern',
      title: '第一章 · 客棧燈火',
      subtitle: '新棧開張',
      emoji: '🏮',
      unlock: { battlesWon: 1 },
      bossId: null,
      reward: { silver: 30, reputation: 5 },
      lines: [
        { speaker: '掌櫃', text: '夜風捲過青石路，客棧門楣的燈籠終於亮起來了。' },
        { speaker: '青衣劍客', text: '掌櫃不必客氣。山賊最近躁動，我守一夜便是一夜。' },
        { speaker: '掌櫃', text: '江湖路遠，先把這盞燈守住。他日名滿四方，也不忘今夜的微光。' },
        { speaker: '旁白', text: '—— 第一章完。勝仗已開，江湖傳聞開始朝這間小棧聚攏。' }
      ]
    },
    {
      id: 'ch2_heifeng',
      title: '第二章 · 黑風壓境',
      subtitle: '寨主來信',
      emoji: '🌪️',
      unlock: { reputation: 35, battlesWon: 3 },
      bossId: 'boss_heifeng',
      reward: { silver: 55, reputation: 10 },
      lines: [
        { speaker: '行商', text: '掌櫃……黑風寨放話了，要「借」你們半個月的酒稅，否則夜夜劫路。' },
        { speaker: '浪人刀客', text: '借？哈哈，刀也可以「借」給寨主臉上！' },
        { speaker: '鐵掌醫女', text: '別逞兇。寨主身旁護衛不弱，出巡前先把傷養好。' },
        { speaker: '掌櫃', text: '客棧不交黑稅。備馬——我們去黑風寨問個明白。' },
        { speaker: '旁白', text: '—— 第二章完。Boss「黑風寨主」已可於戰鬥分頁挑戰。' }
      ]
    },
    {
      id: 'ch3_xieyi',
      title: '第三章 · 邪醫迷霧',
      subtitle: '藥香異變',
      emoji: '☠️',
      unlock: { innLevel: 2, reputation: 70, battlesWon: 6 },
      bossId: 'boss_xieyi',
      reward: { silver: 90, reputation: 15 },
      lines: [
        { speaker: '琴心師太', text: '山中藥香……不對。此味腐骨，絕非尋常郎中所為。' },
        { speaker: '鐵掌醫女', text: '邪醫煉藥人，以活人試毒。若不除之，青石鎮會成瘟土。' },
        { speaker: '青衣劍客', text: '聲望既起，俠義便不能退。我們進霧。' },
        { speaker: '掌櫃', text: '客棧醫館已備好傷藥。去吧——把迷霧撕開。' },
        { speaker: '旁白', text: '—— 第三章完。Boss「邪醫·腐骨」已可挑戰。擊敗後可獲獨特秘籍獎勵。' }
      ]
    }
  ];

  /**
   * 具名 Boss：難度高於普通山賊；需先閱覽對應章節
   * rewardManual：首次擊敗保底秘籍（已擁有則折銀）
   */
  const BOSS_ENCOUNTERS = [
    {
      id: 'boss_heifeng',
      name: '黑風寨主',
      emoji: '🌪️',
      chapterId: 'ch2_heifeng',
      desc: '盤踞黑風寨的匪首，刀勢如狂風，護衛成雙。',
      minInnLevel: 1,
      rewardSilver: [180, 260],
      rewardRep: [22, 35],
      rewardManual: 'jinzhong',
      bonusSilver: 100,
      enemies: [
        {
          name: '黑風護衛', emoji: '👺', force: 15, nei: 8, hp: 90,
          skill: { name: '護主斬', mul: 1.55, chance: 0.22 }
        },
        {
          name: '黑風護衛', emoji: '👺', force: 15, nei: 8, hp: 90,
          skill: { name: '護主斬', mul: 1.55, chance: 0.22 }
        },
        {
          name: '黑風寨主', emoji: '🌪️', force: 28, nei: 15, hp: 210,
          skill: { name: '黑風狂刀', mul: 2.15, chance: 0.32 },
          mitBonus: 0.08,
          startShield: 0.12
        }
      ]
    },
    {
      id: 'boss_xieyi',
      name: '邪醫·腐骨',
      emoji: '☠️',
      chapterId: 'ch3_xieyi',
      desc: '煉製藥人的邪醫，毒掌削弱敵方，霧中氣血難復。',
      minInnLevel: 2,
      rewardSilver: [260, 380],
      rewardRep: [35, 50],
      rewardManual: 'fanyin',
      bonusSilver: 150,
      enemies: [
        {
          name: '藥人甲', emoji: '🧟', force: 18, nei: 12, hp: 110,
          skill: { name: '毒爪', mul: 1.4, chance: 0.25, weaken: 0.1 }
        },
        {
          name: '藥人乙', emoji: '🧟', force: 18, nei: 12, hp: 110,
          skill: { name: '毒爪', mul: 1.4, chance: 0.25, weaken: 0.1 }
        },
        {
          name: '邪醫·腐骨', emoji: '☠️', force: 24, nei: 30, hp: 260,
          skill: { name: '腐骨毒掌', mul: 1.9, chance: 0.34, weaken: 0.2, heal: 0.08 },
          mitBonus: 0.1,
          startShield: 0.1
        }
      ]
    }
  ];

  /**
   * 成就：解鎖後 toast＋可於江湖分頁查看
   * check 於執行期由 game.js 依 state 判定
   */
  const ACHIEVEMENTS = [
    { id: 'first_win', name: '初試鋒芒', desc: '贏得第一場出巡勝仗', emoji: '⚔️' },
    { id: 'wins_10', name: '百戰初成', desc: '累計勝仗達 10 場', emoji: '🏆' },
    { id: 'recruit_all', name: '高朋滿座', desc: '招募全部可入駐俠客', emoji: '🏯' },
    { id: 'bond_confidant', name: '知己難求', desc: '任一名俠客羈絆達「知己」', emoji: '💞' },
    { id: 'inn_lv2', name: '青石新貌', desc: '客棧升級至 Lv.2 或以上', emoji: '🏗️' },
    { id: 'outpost_any', name: '分舵初開', desc: '解鎖本棧以外的任一據點', emoji: '🗺️' },
    { id: 'facility_any', name: '百工就緒', desc: '建造任一設施（達 Lv.1）', emoji: '🔧' },
    { id: 'boss_heifeng', name: '黑風盡滅', desc: '擊敗 Boss「黑風寨主」', emoji: '🌪️' },
    { id: 'boss_xieyi', name: '霧破毒消', desc: '擊敗 Boss「邪醫·腐骨」', emoji: '☠️' },
    { id: 'manuals_4', name: '武學初成', desc: '藏書閣收藏至少 4 本秘籍', emoji: '📚' },
    { id: 'quest_5', name: '俠義奔走', desc: '完成至少 5 件聲望委託', emoji: '📋' },
    { id: 'story_all', name: '燈火三章', desc: '閱覽全部劇情章節', emoji: '📜' }
  ];

  const BOND_TIERS = [
    { id: 'distant', name: '疏遠', min: 0, pairAtk: 0 },
    { id: 'acquaint', name: '相識', min: 25, pairAtk: 0.06 },
    { id: 'confidant', name: '知己', min: 50, pairAtk: 0.12 },
    { id: 'lifedeath', name: '生死之交', min: 80, pairAtk: 0.20 }
  ];

  const MARTIAL_ARTS = [
    {
      id: 'qingfeng',
      name: '青鋒十三式',
      type: 'active',
      desc: '劍勢連環，傷害提高。',
      effect: { mul: 1.7, chance: 0.24 },
      learnCost: 70,
      dropWeight: 12
    },
    {
      id: 'tiesha',
      name: '鐵砂掌',
      type: 'active',
      desc: '掌勁剛猛，並回復少量氣血。',
      effect: { mul: 1.45, chance: 0.26, heal: 0.12 },
      learnCost: 85,
      dropWeight: 10
    },
    {
      id: 'langren_slash',
      name: '浪人斬',
      type: 'active',
      desc: '狂刀一擊，高倍率、較低觸發。',
      effect: { mul: 2.15, chance: 0.16 },
      learnCost: 100,
      dropWeight: 8
    },
    {
      id: 'fanyin',
      name: '梵音破障',
      type: 'active',
      desc: '琴音亂神，傷害並短暫削弱敵方出力。',
      effect: { mul: 1.65, chance: 0.25, weaken: 0.12 },
      learnCost: 130,
      dropWeight: 5
    },
    {
      id: 'tuna',
      name: '吐納心法',
      type: 'passive',
      desc: '內息綿長：內力提升，每回合微量回血。',
      effect: { neiBonus: 0.14, regen: 0.025 },
      learnCost: 80,
      dropWeight: 11
    },
    {
      id: 'jinzhong',
      name: '金鐘罩',
      type: 'passive',
      desc: '周身護氣：減傷，開戰獲少量護盾。',
      effect: { mitBonus: 0.10, startShield: 0.08 },
      learnCost: 95,
      dropWeight: 7
    },
    {
      id: 'liuyun',
      name: '流雲步',
      type: 'passive',
      desc: '身法輕靈：略增武力，並提高主動技觸發。',
      effect: { forceBonus: 0.08, skillChanceBonus: 0.06 },
      learnCost: 90,
      dropWeight: 9
    }
  ];

  const HERO_TEMPLATES = [
    {
      id: 'qingyi',
      name: '青衣劍客',
      title: '清風一劍',
      emoji: '🗡️',
      unlocked: true,
      unlockCost: 0,
      base: { force: 12, nei: 10, hp: 80, favor: 20 },
      growth: { force: 2.2, nei: 1.8, hp: 12 },
      defaultActive: 'qingfeng',
      defaultPassive: null,
      lore: '江湖新秀，劍意清冷，似有往事難言。'
    },
    {
      id: 'tiezhang',
      name: '鐵掌醫女',
      title: '妙手回春',
      emoji: '✋',
      unlocked: false,
      unlockCost: 160,
      base: { force: 8, nei: 14, hp: 70, favor: 10 },
      growth: { force: 1.5, nei: 2.5, hp: 10 },
      defaultActive: 'tiesha',
      defaultPassive: 'tuna',
      lore: '醫武雙修，掌力綿裡藏針，常為客棧療傷。'
    },
    {
      id: 'langren',
      name: '浪人刀客',
      title: '孤刀浪跡',
      emoji: '⚔️',
      unlocked: false,
      unlockCost: 280,
      base: { force: 16, nei: 7, hp: 95, favor: 5 },
      growth: { force: 2.8, nei: 1.2, hp: 15 },
      defaultActive: 'langren_slash',
      defaultPassive: null,
      lore: '來歷不明的浪客，刀勢狂烈，酒後更兇。'
    },
    {
      id: 'qinshi',
      name: '琴心師太',
      title: '梵音破魔',
      emoji: '🎵',
      unlocked: false,
      unlockCost: 450,
      unlockReq: { reputation: 60, anyFavor: 40, innLevel: 2 },
      base: { force: 10, nei: 18, hp: 85, favor: 0 },
      growth: { force: 1.6, nei: 3.0, hp: 11 },
      defaultActive: 'fanyin',
      defaultPassive: 'jinzhong',
      lore: '雲遊至此的師太，琴音可亂敵心神。聲望與情誼達標可請入駐。'
    }
  ];

  const BOND_EVENTS = {
    qingyi: [
      {
        id: 'qy_1',
        favorNeed: 25,
        title: '月下問劍',
        text: '青衣執杯望月：「客棧雖小，卻比江湖安靜。你若願聽，他日我說從前那一劍。」好感漸生，劍意略溫。'
      },
      {
        id: 'qy_2',
        favorNeed: 55,
        title: '往事如鋒',
        text: '她低聲道出師門舊怨，末了却笑：「有你守這盞燈，我便不急著復仇。」知己之交，青鋒更準。'
      }
    ],
    tiezhang: [
      {
        id: 'tz_1',
        favorNeed: 25,
        title: '藥香一盞',
        text: '鐵掌醫女塞來一碗苦藥：「傷患多，掌櫃也別逞強。」你苦笑飲下，她眼底卻有暖意。'
      },
      {
        id: 'tz_2',
        favorNeed: 50,
        title: '夜診心事',
        text: '雨夜她替你包紮刀傷：「醫人易，醫心難……你這客棧，倒醫好了我一半漂泊。」'
      }
    ],
    langren: [
      {
        id: 'lr_1',
        favorNeed: 25,
        title: '酒後真言',
        text: '浪人拍桌大笑：「刀是冷的，酒是熱的——客棧有酒，便算有家！」狂性稍斂。'
      },
      {
        id: 'lr_2',
        favorNeed: 50,
        title: '孤刀不孤',
        text: '他罕見收起浪態：「從前一人走江湖，現在……出巡有人并肩，也成。」'
      }
    ],
    qinshi: [
      {
        id: 'qs_1',
        favorNeed: 25,
        title: '一曲問心',
        text: '師太撫琴：「施主心火稍旺。且聽此一曲，火自滅、義自生。」梵音繞樑。'
      },
      {
        id: 'qs_2',
        favorNeed: 55,
        title: '琴心相契',
        text: '她收弦微笑：「客棧香火，亦是修行。貧尼願長伴此間鐘聲。」'
      }
    ]
  };

  const ENEMY_WAVES = [
    {
      id: 'bandit_small',
      name: '山賊小隊',
      minInnLevel: 1,
      rewardSilver: [28, 48],
      rewardRep: [3, 6],
      enemies: [
        { name: '山賊喽啰', emoji: '👺', force: 6, nei: 3, hp: 40 },
        { name: '山賊喽啰', emoji: '👺', force: 6, nei: 3, hp: 40 }
      ]
    },
    {
      id: 'bandit_camp',
      name: '流寇營寨',
      minInnLevel: 1,
      rewardSilver: [55, 95],
      rewardRep: [6, 12],
      enemies: [
        { name: '流寇刀手', emoji: '💀', force: 10, nei: 5, hp: 60 },
        { name: '流寇弓手', emoji: '🏹', force: 8, nei: 6, hp: 45 },
        { name: '流寇頭目', emoji: '👹', force: 14, nei: 8, hp: 90 }
      ]
    },
    {
      id: 'black_market',
      name: '黑市惡霸',
      minInnLevel: 2,
      rewardSilver: [100, 160],
      rewardRep: [12, 20],
      enemies: [
        { name: '惡霸護院', emoji: '🛡️', force: 12, nei: 8, hp: 80 },
        { name: '惡霸護院', emoji: '🛡️', force: 12, nei: 8, hp: 80 },
        { name: '黑市惡霸', emoji: '👿', force: 18, nei: 12, hp: 130 }
      ]
    },
    {
      id: 'demon_cult',
      name: '魔教探子',
      minInnLevel: 3,
      rewardSilver: [180, 280],
      rewardRep: [20, 35],
      enemies: [
        { name: '魔教探子', emoji: '🌑', force: 16, nei: 14, hp: 100 },
        { name: '魔教刺客', emoji: '🗡️', force: 20, nei: 10, hp: 90 },
        { name: '血影使', emoji: '🩸', force: 24, nei: 18, hp: 160 }
      ]
    }
  ];

  const TRAIN = {
    force: { label: '練武（武力）', cost: 28, gain: 2, favor: 1 },
    nei: { label: '調息（內力）', cost: 28, gain: 2, favor: 1 },
    favor: { label: '談心／情誼', cost: 18, gain: 6, favor: 6 }
  };

  const LIBRARY = {
    buyMul: 1.75,
    equipCost: 15
  };

  function weightedPick(list) {
    const total = list.reduce((s, x) => s + (x.weight || x.dropWeight || 1), 0);
    let r = Math.random() * total;
    for (const item of list) {
      r -= (item.weight || item.dropWeight || 1);
      if (r <= 0) return item;
    }
    return list[list.length - 1];
  }

  function randInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function heroStatsAtLevel(template, level) {
    const lv = Math.max(1, level | 0);
    const g = template.growth;
    const b = template.base;
    return {
      force: Math.round(b.force + g.force * (lv - 1)),
      nei: Math.round(b.nei + g.nei * (lv - 1)),
      maxHp: Math.round(b.hp + g.hp * (lv - 1)),
      favor: b.favor
    };
  }

  function getMartial(id) {
    return MARTIAL_ARTS.find((m) => m.id === id) || null;
  }

  function getBondTier(favor) {
    let tier = BOND_TIERS[0];
    for (const t of BOND_TIERS) {
      if (favor >= t.min) tier = t;
    }
    return tier;
  }

  function nextBondTier(favor) {
    for (const t of BOND_TIERS) {
      if (favor < t.min) return t;
    }
    return null;
  }

  function pairBondMul(favors) {
    if (!favors || favors.length < 2) return { mul: 1, tier: BOND_TIERS[0] };
    const minF = Math.min.apply(null, favors);
    const tier = getBondTier(minF);
    return { mul: 1 + (tier.pairAtk || 0), tier };
  }

  function getOutpost(id) {
    return OUTPOSTS.find((o) => o.id === id) || null;
  }

  function getFacility(id) {
    return FACILITIES.find((f) => f.id === id) || null;
  }

  function getQuestTemplate(id) {
    return QUEST_TEMPLATES.find((q) => q.id === id) || null;
  }

  /** 日鍵（本地日），用於每日任務刷新 */
  function dayKey(ts) {
    const d = new Date(ts == null ? Date.now() : ts);
    return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate();
  }

  function getStoryChapter(id) {
    return STORY_CHAPTERS.find((c) => c.id === id) || null;
  }

  function getBoss(id) {
    return BOSS_ENCOUNTERS.find((b) => b.id === id) || null;
  }

  function getAchievement(id) {
    return ACHIEVEMENTS.find((a) => a.id === id) || null;
  }

  global.WuxiaData = {
    GAME,
    INN_LEVELS,
    GUESTS,
    RUMORS,
    HERO_TEMPLATES,
    ENEMY_WAVES,
    TRAIN,
    MARTIAL_ARTS,
    BOND_TIERS,
    BOND_EVENTS,
    LIBRARY,
    OUTPOSTS,
    FACILITIES,
    QUEST_TEMPLATES,
    STORY_CHAPTERS,
    BOSS_ENCOUNTERS,
    ACHIEVEMENTS,
    weightedPick,
    randInt,
    heroStatsAtLevel,
    getMartial,
    getBondTier,
    nextBondTier,
    pairBondMul,
    getOutpost,
    getFacility,
    getQuestTemplate,
    getStoryChapter,
    getBoss,
    getAchievement,
    dayKey
  };
})(typeof window !== 'undefined' ? window : globalThis);
