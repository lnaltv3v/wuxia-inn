/**
 * 俠客棧 — 靜態資料：俠客模板、敵人、武學、羈絆、據點、設施、任務、常數
 * v2.9.0
 */
(function (global) {
  'use strict';

  const GAME = {
    name: '俠客棧',
    version: '2.9.0',
    saveKey: 'wuxia-inn-save-v1',
    tickMs: 1200,
    offlineCapHours: 8,
    combatTickMs: 900,
    combatSpeeds: [0.5, 1, 1.5, 2],
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
    // preferPhase：對上當日時辰則小費／付銀更爽；錯時略淡（連日夜）
    { id: 'wanderer', name: '過路客', weight: 40, payMin: 2, payMax: 5, kind: 'meal', preferPhase: 'day', preferLabel: '喜白日歇腳' },
    { id: 'merchant', name: '行商', weight: 25, payMin: 5, payMax: 12, kind: 'stay', preferPhase: 'day', preferLabel: '喜白日談生意' },
    { id: 'scholar', name: '書生', weight: 15, payMin: 4, payMax: 8, kind: 'meal', preferPhase: 'dawn', preferLabel: '喜破曉清靜' },
    { id: 'knight', name: '遊俠', weight: 12, payMin: 8, payMax: 18, kind: 'stay', preferPhase: 'night', preferLabel: '喜夜路投棧' },
    { id: 'noble', name: '富紳', weight: 8, payMin: 15, payMax: 35, kind: 'stay', preferPhase: 'dusk', preferLabel: '喜黃昏酒宴' }
  ];

  /** 客人時辰偏好倍率（match 加成／mismatch 略減） */
  function guestPhaseMul(guest, phase) {
    if (!guest || !guest.preferPhase) return 1;
    const ph = phase || 'day';
    if (guest.preferPhase === ph) return 1.28;
    // 鄰近時辰略寬容
    const near = {
      dawn: ['day'], day: ['dawn', 'dusk'], dusk: ['day', 'night'], night: ['dusk', 'dawn']
    };
    if ((near[ph] || []).indexOf(guest.preferPhase) >= 0) return 1.08;
    return 0.88;
  }

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
    '小二夢見客滿盈門——或許是個好兆頭。',
    '聽說青衣劍客昨夜於廊下練劍至三更。',
    '茶客嘀咕：黑風寨主近日少了蹤影，恐有異動。',
    '有書生在書架前抄方，說要寫話本《俠客棧夜話》。',
    '邊關來信：哨站缺人手，願出銀請俠客暫駐。',
    '月下有人撫琴，曲終只留一枚玉扣於門檻。',
    '富紳嫌菜淡，又立刻為小二加賞——脾氣怪但爽快。',
    '鎮口張貼告示：莫信路邊「免費傳功」之人。',
    '廚下傳出鍋鏟聲，像是又有江湖客點了大魚大肉。'
  ];

  /** 小二對白池（氣氛，不改存檔） */
  const XIAOER_LINES = [
    '客官裏面請，熱茶現煮！',
    '今日雅座尚有空位。',
    '外間風大，進來歇歇腳罷。',
    '小店粗茶淡飯，莫嫌棄。',
    '聽聞江湖不平事，可問櫃上。',
    '枱面抹亮了，客官請坐。',
    '剛開一罈陳釀，要不要試試？',
    '大門那邊有風聲，可是要出巡？',
    '俠客席的刀劍擦過了，趁手得很。',
    '告示又換新紙，江湖事一日三變。',
    '地圖上的紅點——那是去分舵的路。',
    '有客官鬧脾氣？叫小二來勸勸便是。',
    '破曉客少，正好擦燈籠。',
    '白日人聲嘈雜，小的耳朵都熱啦。',
    '黃昏酒香一飄，富紳就愛這個點。',
    '夜深了，遊俠腳步卻更密。',
    '雅座茶寮一開，小費眼神都不一樣。',
    '客官若趕路，小的給您打包乾糧。',
    '雨打屋簷——正好聽書生唸詩。',
    '誰把刀掛歪了？小的扶正先。',
    '櫃上算盤響，掌櫃又賺啦？',
    '門口有野貓，別踩到牠尾巴。',
    '客官愛清茶還是濃茶？小的都備著。',
    '時辰對了，賞銀自己會響——您聽！',
    '刀客坐下先卸刀，規矩如此。',
    '掌櫃說：雅座一開，面子跟銀子一塊來。'
  ];

  /** 時辰專屬招呼（偶發） */
  const XIAOER_PHASE_LINES = {
    dawn: ['天剛亮，茶溫著等您。', '晨客稀少，雅座隨便坐。', '書生最愛這辰——清靜。', '破曉抹完桌，才算開市。'],
    day: ['午市將至，熱菜出鍋！', '行商一到，銀兩就響。', '白日好做生意，客官裏面請。', '熱茶續上，談生意才順。'],
    dusk: ['日落酒溫，富紳常來。', '黃昏燈未點，先聞酒香。', '要酒要菜，小的一聲招呼。', '燈一點，雅座就滿。'],
    night: ['夜路辛苦，熱湯壓驚。', '遊俠腳步——小的聽得出來。', '燈籠亮起，夜客賞銀最豪。', '更深了，還有客？裏面請。']
  };

  /**
   * 接客小事件（執行期抽選；只動銀兩／日誌／對白，唔改 migrate 結構）
   * kind: tip | difficult | meet
   */
  const GUEST_EVENTS = [
    { id: 'tip_kind', kind: 'tip', weight: 28, text: '客人點頭稱善，額外賞了些銀。', tipMin: 2, tipMax: 6 },
    { id: 'tip_tea', kind: 'tip', weight: 18, text: '熱茶對味，客官多付了賞錢。', tipMin: 1, tipMax: 4 },
    { id: 'tip_phase', kind: 'tip', weight: 14, text: '來得正是時候，賞得爽快。', tipMin: 3, tipMax: 8, preferBoost: true },
    { id: 'hard_bargain', kind: 'difficult', weight: 16, text: '刁難客嫌貴，理論半晌才勉為付款。', cutMin: 1, cutMax: 4 },
    { id: 'hard_salt', kind: 'difficult', weight: 10, text: '刁難客嚷鹽多了，小費免談。', cutMin: 0, cutMax: 2 },
    { id: 'hard_rush', kind: 'difficult', weight: 8, text: '趕路客罵上菜慢，少給了錢。', cutMin: 1, cutMax: 3 },
    { id: 'meet_qingyi', kind: 'meet', weight: 9, text: '偶遇遊俠點頭：「貴棧刀光不錯。」', heroHint: 'qingyi' },
    { id: 'meet_doc', kind: 'meet', weight: 7, text: '醫女打扮的過客低聲：「傷藥可曾備足？」', heroHint: 'tiezhang' },
    { id: 'meet_qin', kind: 'meet', weight: 6, text: '有人聽見琴音，笑道：「此間有佛心。」', heroHint: 'qinshi' },
    { id: 'meet_blade', kind: 'meet', weight: 5, text: '刀客臨去丟下一句：「黑風未絕，小心。」', heroHint: 'langren' },
    { id: 'meet_cat', kind: 'meet', weight: 6, text: '小二跟門口野貓對視三秒，客人大笑。', heroHint: null },
    { id: 'meet_ledger', kind: 'meet', weight: 5, text: '行商盯著算盤：「這棧的帳，乾脆。」', heroHint: null },
    { id: 'tip_teahouse', kind: 'tip', weight: 12, text: '雅座茶香對味，客官多賞了幾兩。', tipMin: 2, tipMax: 7, preferBoost: true },
    { id: 'meet_teahouse', kind: 'meet', weight: 5, text: '茶寮客輕歎：「這茶寮一開，才像個江湖棧。」', heroHint: null },
    { id: 'hard_phase', kind: 'difficult', weight: 7, text: '客官嫌時辰不對，語氣僵硬，少付了錢。', cutMin: 1, cutMax: 3 },
    { id: 'tip_odd_mask', kind: 'tip', weight: 4, text: '蒙面奇客留一錠碎銀作「茶錢」，不留名。', tipMin: 5, tipMax: 12 },
    { id: 'meet_odd_story', kind: 'meet', weight: 4, text: '說書奇客拍扇：「今夜有本棧新段子！」', heroHint: null }
  ];

  /**
   * 場景化江湖事件（Hub 泡泡＋短暫行人演出；唔淨對話面板）
   * beats.at：毫秒；line／caption／move／end
   */
  const SCENE_EVENTS = [
    {
      id: 'door_spar',
      caption: '門前兩俠比劃兩招…',
      walkers: [
        { id: 'langren', x: 72, y: 336, tx: 220, ty: 352 },
        { id: 'qingyi', x: 340, y: 352, tx: 236, ty: 340 }
      ],
      beats: [
        { at: 0, caption: '門前刀光一閃——', line: '領教！', walker: 0, life: 1.1 },
        { at: 700, line: '好刀法！', walker: 1, life: 1.1, move: { i: 0, tx: 260, ty: 348 } },
        { at: 1500, line: '點到即止。', walker: 0, life: 1.0, move: { i: 1, tx: 200, ty: 336 } },
        { at: 2400, line: '改日再戰。', walker: 1, life: 1.0, end: true }
      ]
    },
    {
      id: 'tea_rumor',
      caption: '雅座茶客低聲議論…',
      walkers: [
        { id: 'qinshi', x: 600, y: 360, tx: 520, ty: 372 },
        { id: 'tiezhang', x: 440, y: 376, tx: 500, ty: 368 }
      ],
      beats: [
        { at: 0, caption: '茶香裡飄來江湖話', line: '聽說黑風又動。', walker: 1, life: 1.2 },
        { at: 900, line: '莫慌，本棧有俠客。', walker: 0, life: 1.15 },
        { at: 1800, line: '琴音可定心神。', walker: 0, life: 1.0, end: true }
      ]
    },
    {
      id: 'teahouse_toast',
      caption: '雅座茶寮舉杯閒談…',
      walkers: [
        { id: 'qinshi', x: 560, y: 368, tx: 500, ty: 372 },
        { id: 'xiaoer', x: 420, y: 340, tx: 460, ty: 352 }
      ],
      beats: [
        { at: 0, caption: '茶寮一角，杯蓋輕響', line: '這泡正好。', walker: 0, life: 1.15 },
        { at: 850, line: '客官慢用，小的續水。', walker: 1, life: 1.1 },
        { at: 1700, line: '時辰對了，茶也甜。', walker: 0, life: 1.0, end: true }
      ]
    },
    {
      id: 'merchant_boast',
      caption: '行商在櫃前誇貨…',
      walkers: [
        { id: 'langren', x: 400, y: 320, tx: 460, ty: 336 }
      ],
      beats: [
        { at: 0, caption: '櫃前一陣喧嘩', line: '總有一款適合您！', x: 480, y: 200, life: 1.2 },
        { at: 800, line: '江湖隱藏各路高手。', walker: 0, life: 1.15 },
        { at: 1700, line: '客官裏面請。', x: 420, y: 280, life: 1.0, end: true }
      ]
    },
    {
      id: 'wounded_seeker',
      caption: '負傷遊俠踉蹌入門…',
      interactive: true,
      walkers: [
        { id: 'langren', x: 40, y: 344, tx: 300, ty: 356 },
        { id: 'tiezhang', x: 560, y: 372, tx: 400, ty: 360 }
      ],
      beats: [
        { at: 0, caption: '大門一陣急腳步', line: '咳……可有歇腳處？', walker: 0, life: 1.25 },
        { at: 900, line: '先坐下，我來瞧瞧傷口。', walker: 1, life: 1.2, move: { i: 0, tx: 336, ty: 352 } },
        { at: 1800, caption: '遊俠望向掌櫃——', line: '江湖救急，後日必報。', walker: 0, life: 1.3 },
        { at: 2600, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'aid',
          label: '贈藥療傷（-12 兩）',
          effects: { silver: -12, reputation: 4, favorHero: 'tiezhang', favor: 3 },
          resultLine: '醫女點頭：「善心會記在江湖簿上。」聲望＋羈絆微升。'
        },
        {
          id: 'work',
          label: '留他幫工換宿',
          effects: { silver: 6, reputation: 1 },
          resultLine: '遊俠抹汗：「多謝收留。」櫃上多得些散銀。'
        },
        {
          id: 'turn',
          label: '婉拒門外',
          effects: { reputation: -2 },
          resultLine: '遊俠苦笑拱手離去……棧聲略損。'
        }
      ]
    },
    {
      id: 'night_courier',
      caption: '夜路信使叩門…',
      interactive: true,
      walkers: [
        { id: 'qingyi', x: 48, y: 340, tx: 280, ty: 352 },
        { id: 'xiaoer', x: 520, y: 336, tx: 420, ty: 344 }
      ],
      beats: [
        { at: 0, caption: '更鼓剛響，有人輕叩大門', line: '掌櫃可在？有急件。', walker: 0, life: 1.25 },
        { at: 900, line: '夜深路滑，先喝口熱茶。', walker: 1, life: 1.15, move: { i: 0, tx: 336, ty: 348 } },
        { at: 1800, caption: '信使捧出油布小包——', line: '不知可否代為暫存？', walker: 0, life: 1.3 },
        { at: 2600, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'hold',
          label: '代為保管（+聲望）',
          effects: { reputation: 5, favorHero: 'qingyi', favor: 2 },
          resultLine: '信使拱手：「江湖有信。」聲望與青衣好感微升。'
        },
        {
          id: 'peek',
          label: '私下拆看（+銀／−聲望）',
          effects: { silver: 18, reputation: -3 },
          resultLine: '包裡有散銀……可名聲亦損。信使未察覺。'
        },
        {
          id: 'refuse',
          label: '拒收門外',
          effects: { reputation: -1 },
          resultLine: '信使嘆了口氣，消失在夜色裡。'
        }
      ]
    },
    {
      id: 'moon_sword',
      caption: '廊下青衣邀你月下論劍…',
      interactive: true,
      walkers: [
        { id: 'qingyi', x: 80, y: 340, tx: 300, ty: 352 },
        { id: 'xiaoer', x: 560, y: 336, tx: 440, ty: 344 }
      ],
      beats: [
        { at: 0, caption: '月色灑在廊下青石', line: '掌櫃可敢接我一劍？', walker: 0, life: 1.25 },
        { at: 900, line: '小心別碰倒茶壺！', walker: 1, life: 1.1 },
        { at: 1800, caption: '青衣劍尖輕點——', line: '點到即止，亦可只觀。', walker: 0, life: 1.25 },
        { at: 2600, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'spar',
          label: '接劍點到為止（+羈絆）',
          effects: { favorHero: 'qingyi', favor: 5, reputation: 2 },
          resultLine: '劍風掠過燈籠。青衣收劍淺笑：「劍意更近。」羈絆上升。'
        },
        {
          id: 'watch',
          label: '旁觀指點（+銀／微羈絆）',
          effects: { silver: 8, favorHero: 'qingyi', favor: 2 },
          resultLine: '你點破一處收勢，她頷首謝過，茶錢也多給了。'
        },
        {
          id: 'decline',
          label: '今夜改日',
          effects: { favorHero: 'qingyi', favor: -1 },
          resultLine: '青衣收劍：「也好。」廊下只餘月光。'
        }
      ]
    },
    {
      id: 'wine_oath',
      caption: '浪人拍桌邀酒結義…',
      interactive: true,
      walkers: [
        { id: 'langren', x: 600, y: 356, tx: 460, ty: 364 },
        { id: 'tiezhang', x: 160, y: 360, tx: 300, ty: 368 }
      ],
      beats: [
        { at: 0, caption: '雅座忽然喧鬧', line: '掌櫃！來喝！刀酒同盟！', walker: 0, life: 1.25 },
        { at: 900, line: '少灌，傷肝。', walker: 1, life: 1.15, move: { i: 0, tx: 400, ty: 360 } },
        { at: 1800, caption: '浪人舉碗相邀——', line: '你敢陪，我便護這棧。', walker: 0, life: 1.3 },
        { at: 2600, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'drink',
          label: '對飲三碗（+羈絆／−銀）',
          effects: { silver: -10, favorHero: 'langren', favor: 6, reputation: 1 },
          resultLine: '酒氣衝天。浪人拍肩大笑：「成！出巡有我。」羈絆大升。'
        },
        {
          id: 'tea',
          label: '以茶代酒（微羈絆）',
          effects: { favorHero: 'langren', favor: 3, favorHero2: 'tiezhang', favor2: 2 },
          resultLine: '浪人撇嘴仍乾了茶。醫女點頭：「這樣才像話。」'
        },
        {
          id: 'refuse_wine',
          label: '拒酒勸他歇息',
          effects: { favorHero: 'langren', favor: -2, favorHero2: 'tiezhang', favor2: 1 },
          resultLine: '浪人哼一聲離席；醫女卻道：「掌櫃懂分寸。」'
        }
      ]
    },
    {
      id: 'qin_mercy',
      caption: '師太於廊下撫琴止爭…',
      interactive: true,
      walkers: [
        { id: 'qinshi', x: 520, y: 348, tx: 400, ty: 360 },
        { id: 'langren', x: 80, y: 352, tx: 260, ty: 364 }
      ],
      beats: [
        { at: 0, caption: '琴聲忽然蓋過刀聲', line: '施主且止。', walker: 0, life: 1.2 },
        { at: 900, line: '……哼，好琴。', walker: 1, life: 1.15, move: { i: 1, tx: 320, ty: 360 } },
        { at: 1800, caption: '師太望向掌櫃——', line: '可願聽貧尼一勸？', walker: 0, life: 1.25 },
        { at: 2600, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'listen',
          label: '靜聽一曲（+羈絆／望）',
          effects: { favorHero: 'qinshi', favor: 5, reputation: 3 },
          resultLine: '梵音入耳。浪人收刀。師太微頷：「心定，棧安。」'
        },
        {
          id: 'donate',
          label: '添香火銀（−銀／++望）',
          effects: { silver: -15, reputation: 6, favorHero: 'qinshi', favor: 3 },
          resultLine: '香火錢入匣。過路客紛紛稱善，聲望上升。'
        },
        {
          id: 'busy',
          label: '推說忙碌',
          effects: { favorHero: 'qinshi', favor: -1 },
          resultLine: '師太輕嘆收弦：「貧尼自去。」廊下只餘餘音。'
        }
      ]
    },
    {
      id: 'challenge_letter',
      caption: '告示欄多了一紙挑戰書…',
      interactive: true,
      walkers: [
        { id: 'qingyi', x: 200, y: 220, tx: 240, ty: 240 },
        { id: 'langren', x: 700, y: 360, tx: 560, ty: 350 }
      ],
      beats: [
        { at: 0, caption: '告示欄前圍了幾人', line: '有人點名本棧護院。', walker: 0, life: 1.2 },
        { at: 900, line: '正好手癢！', walker: 1, life: 1.1, move: { i: 1, tx: 480, ty: 340 } },
        { at: 1800, caption: '青衣將挑戰書遞來——', line: '掌櫃定夺，我等聽令。', walker: 0, life: 1.25 },
        { at: 2600, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'accept',
          label: '應戰約期（+望／微銀）',
          effects: { reputation: 4, silver: 12, favorHero: 'qingyi', favor: 2, favorHero2: 'langren', favor2: 2 },
          resultLine: '約期已定。江湖傳開：此棧不怯戰。'
        },
        {
          id: 'mediate',
          label: '調解撤帖（+望／−銀）',
          effects: { silver: -8, reputation: 5, favorHero: 'qinshi', favor: 2 },
          resultLine: '你出面講和。挑戰書撕去，聲望反升。'
        },
        {
          id: 'ignore',
          label: '當無事撕掉',
          effects: { reputation: -2, favorHero: 'langren', favor: -2 },
          resultLine: '浪人撇嘴。外頭有人笑本棧怯陣……'
        }
      ]
    },
    {
      id: 'board_secret_letter',
      caption: '告示欄多了一封燈火密信…',
      interactive: true,
      weight: 22,
      walkers: [
        { id: 'xiaoer', x: 240, y: 300, tx: 260, ty: 280 },
        { id: 'qingyi', x: 80, y: 340, tx: 220, ty: 320 }
      ],
      beats: [
        { at: 0, caption: '告示欄前，油布信角微翹', line: '掌櫃！有人夤夜貼信！', walker: 0, life: 1.2 },
        { at: 900, line: '邊關筆跡……求援。', walker: 1, life: 1.15, move: { i: 0, tx: 280, ty: 290 } },
        { at: 1800, caption: '密信展開——三條路', line: '如何回覆，由掌櫃定夺。', walker: 1, life: 1.25 },
        { at: 2600, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'aid_border',
          label: '派援邊關（-40 兩 · +望）',
          effects: { silver: -40, reputation: 12, favorHero: 'qingyi', favor: 4, favorHero2: 'tiezhang', favor2: 2 },
          resultLine: '青衣領命夜馳。邊關回信：哨站穩住，聲望遠播。'
        },
        {
          id: 'qingshi_net',
          label: '托青石線眼查探（-18 兩）',
          effects: { silver: -18, reputation: 6, favorHero: 'langren', favor: 3 },
          resultLine: '分舵線眼帶回夜市傳聞：黑風餘黨混商隊——青石銀路更清。'
        },
        {
          id: 'watch_wait',
          label: '按兵觀望（+少銀）',
          effects: { silver: 15, reputation: -1, favorHero: 'qinshi', favor: 1 },
          resultLine: '師太點頭：「忍亦是鋒。」櫃上多得一筆匿名茶錢。'
        }
      ]
    },
    {
      id: 'qingshi_night_market',
      caption: '青石鎮線：夜市抽成…',
      outpost: 'qingshi',
      walkers: [
        { id: 'langren', x: 400, y: 330, tx: 460, ty: 340 }
      ],
      beats: [
        { at: 0, caption: '青石來信：夜市熱鬧', line: '分舵抽成到了。', walker: 0, life: 1.2 },
        { at: 1000, line: '商旅說本棧公道。', x: 480, y: 220, life: 1.1, end: true }
      ]
    },
    {
      id: 'bianguan_alarm',
      caption: '邊關線：哨崗警報…',
      outpost: 'bianguan',
      walkers: [
        { id: 'tiezhang', x: 520, y: 360, tx: 440, ty: 350 },
        { id: 'qingyi', x: 60, y: 340, tx: 200, ty: 330 }
      ],
      beats: [
        { at: 0, caption: '邊關急腳報：怪風再起', line: '哨站要人！', walker: 1, life: 1.2 },
        { at: 900, line: '傷藥我備了半囊。', walker: 0, life: 1.15 },
        { at: 1800, line: '出巡勝仗，邊關另有犒賞。', walker: 1, life: 1.0, end: true }
      ]
    },
    {
      id: 'odd_mask_guest',
      caption: '奇客：蒙面人落座…',
      interactive: true,
      weight: 26,
      walkers: [
        { id: 'xiaoer', x: 420, y: 330, tx: 300, ty: 340 },
        { id: 'langren', x: 80, y: 350, tx: 200, ty: 348 }
      ],
      beats: [
        { at: 0, caption: '斗笠遮臉，只有一雙銳眼', line: '掌櫃，一壺熱酒，不問名。', x: 240, y: 260, life: 1.3 },
        { at: 1000, line: '這位客官……眼神不像善類。', walker: 0, life: 1.15 },
        { at: 1900, line: '江湖人各有隱情。你怎麼處置？', walker: 1, life: 1.2 },
        { at: 2700, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'serve_quiet',
          label: '照常接待（＋少銀 · 望）',
          effects: { silver: 12, reputation: 2 },
          resultLine: '蒙面人飲盡一盞，留下碎銀與一句「有燈處便有路」，飄然離去。'
        },
        {
          id: 'ask_gently',
          label: '輕聲詢來意（好感浪人）',
          effects: { silver: 6, reputation: 4, favorHero: 'langren', favor: 3 },
          resultLine: '他略一頓：「黑風餘黨在查燈火。小心。」浪人握刀點頭。'
        },
        {
          id: 'refuse_odd',
          label: '婉拒留宿（穩）',
          effects: { reputation: 1 },
          resultLine: '蒙面人拱手：「無妨。」轉身沒入夜色，小二鬆了口氣。'
        }
      ]
    },
    {
      id: 'odd_storyteller',
      caption: '奇客：說書人開場…',
      interactive: true,
      weight: 24,
      walkers: [
        { id: 'qinshi', x: 520, y: 340, tx: 400, ty: 350 },
        { id: 'xiaoer', x: 280, y: 360, tx: 340, ty: 352 }
      ],
      beats: [
        { at: 0, caption: '折扇一響，滿座側耳', line: '今日不說帝王，說這盞俠客燈！', x: 420, y: 240, life: 1.35 },
        { at: 1100, line: '……把本棧編進去了？', walker: 1, life: 1.15 },
        { at: 2000, line: '梵音亦可助興。掌櫃可願加賞？', walker: 0, life: 1.2 },
        { at: 2800, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'sponsor_tale',
          label: '打賞開講（-15 兩 · ＋望）',
          effects: { silver: -15, reputation: 8, favorHero: 'qinshi', favor: 2 },
          resultLine: '說書人聲若洪鐘，過路客紛紛駐足。本棧聲名又遠了半分。'
        },
        {
          id: 'free_seat',
          label: '免茶錢請說（＋望少 · 好感）',
          effects: { reputation: 4, favorHero: 'qinshi', favor: 3, silver: 4 },
          resultLine: '師太拂塵微笑。說書人改口：「燈火長明——便是今日主角。」'
        },
        {
          id: 'cut_short',
          label: '請改日再來（平）',
          effects: { silver: 2 },
          resultLine: '說書人呵呵收扇：「江湖路長，改日見。」小二偷笑：改日見。'
        }
      ]
    },
    {
      id: 'ember_ash_scout',
      caption: '餘燼探路：灰路風起…',
      interactive: true,
      needChapter: 'ch6_ember_road',
      once: true,
      weight: 55,
      walkers: [
        { id: 'qingyi', x: 200, y: 330, tx: 300, ty: 340 },
        { id: 'xiaoer', x: 500, y: 320, tx: 420, ty: 330 }
      ],
      beats: [
        { at: 0, caption: '告示角又翹起一角灰紙', line: '掌櫃！灰路上有人求援……又像試探。', walker: 1, life: 1.2 },
        { at: 950, line: '我可先走一遭，不必全隊。', walker: 0, life: 1.2 },
        { at: 1900, caption: '探路三選', line: '如何定夺？', walker: 0, life: 1.15 },
        { at: 2600, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'ember_go',
          label: '允青衣輕裝探路（-25 兩 · +望）',
          effects: { silver: -25, reputation: 10, favorHero: 'qingyi', favor: 5 },
          resultLine: '青衣去又回：舊營火確認，東岔可通。聲望遠播。'
        },
        {
          id: 'ember_herb',
          label: '先備傷藥再探（-18 兩 · 鐵掌好感）',
          effects: { silver: -18, reputation: 6, favorHero: 'tiezhang', favor: 4, favorHero2: 'qingyi', favor2: 2 },
          resultLine: '鐵掌塞滿半囊傷藥。探路雖慢，卻更穩。'
        },
        {
          id: 'ember_wait',
          label: '再觀望一夜',
          effects: { silver: 10, reputation: -1, favorHero: 'qinshi', favor: 2 },
          resultLine: '師太低聲誦了一段。櫃上多得一筆匿名茶錢。'
        }
      ]
    },
    {
      id: 'ember_wind_whisper',
      caption: '餘燼：風裡有人笑…',
      interactive: true,
      needChapter: 'ch6_ember_road',
      once: true,
      weight: 40,
      walkers: [
        { id: 'qinshi', x: 320, y: 330, tx: 400, ty: 340 },
        { id: 'langren', x: 560, y: 340, tx: 470, ty: 342 }
      ],
      beats: [
        { at: 0, caption: '夜風穿堂，梵音微顫', line: '風聲裡有笑。不是善類。', walker: 0, life: 1.25 },
        { at: 1000, line: '那就削了它。', walker: 1, life: 1.1 },
        { at: 1850, caption: '掌櫃定夺', line: '守棧，還是迎上去？', walker: 0, life: 1.2 },
        { at: 2550, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'ember_guard_inn',
          label: '守棧添燈（+望／小好感）',
          effects: { reputation: 5, favorHero: 'qinshi', favor: 4, favorHero2: 'qingyi', favor2: 2 },
          resultLine: '燈火更亮。笑意遠了些——暫時。'
        },
        {
          id: 'ember_strike_out',
          label: '浪人迎風一探（-14 兩 · 戰意）',
          effects: {
            silver: -14, reputation: 4,
            favorHero: 'langren', favor: 5,
            combatBuff: { id: 'buff_ember_wind', label: '迎風', forceMul: 1.08, battles: 2, heroes: ['langren'] }
          },
          resultLine: '浪人帶回半截黑布。戰意未散。'
        },
        {
          id: 'ember_ignore_wind',
          label: '當風聲罷了',
          effects: { reputation: -2 },
          resultLine: '眾人無言。風，卻好像又近了寸許。'
        }
      ]
    },
    {
      id: 'fest_lantern_tea',
      title: '燈節茶會',
      caption: '客棧掛起紙燈，茶香裡有節慶氣…',
      interactive: true,
      once: true,
      fest: true,
      preferPhase: 'night',
      needHubDays: 2,
      weight: 60,
      walkers: [
        { id: 'xiaoer', x: 280, y: 330, tx: 360, ty: 340 },
        { id: 'qinshi', x: 560, y: 340, tx: 470, ty: 345 }
      ],
      beats: [
        { at: 0, caption: '紙燈搖曳，雅座滿座', line: '掌櫃！今夜像過節——要唔要辦個小茶會？', walker: 0, life: 1.2 },
        { at: 950, line: '燈明則心安。施主可定夺賞與義。', walker: 1, life: 1.25 },
        { at: 1900, caption: '燈節三選', line: '銀、望，還是人情？', walker: 0, life: 1.15 },
        { at: 2600, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'fest_silver',
          label: '開茶會收茶資（＋銀）',
          effects: { silver: 36, reputation: 2 },
          resultLine: '茶客紛至。櫃上多了一筆燈節茶錢。'
        },
        {
          id: 'fest_rep',
          label: '義贈熱茶（＋望）',
          effects: { silver: -8, reputation: 14 },
          resultLine: '過路人傳開：此棧燈節有義。聲望遠播。'
        },
        {
          id: 'fest_favor',
          label: '邀俠客共盞（好感）',
          effects: {
            favorHero: 'qingyi', favor: 4,
            favorHero2: 'qinshi', favor2: 4,
            reputation: 3
          },
          resultLine: '青衣與師太各飲一盞。人情暖過紙燈。'
        }
      ]
    },
    {
      id: 'rain_eave_spar',
      title: '雨簷劍影',
      caption: '簷下雨絲斜，兩刃未出先有風…',
      interactive: true,
      once: true,
      preferPhase: 'night',
      weight: 36,
      walkers: [
        { id: 'qingyi', x: 120, y: 336, tx: 260, ty: 348 },
        { id: 'langren', x: 620, y: 350, tx: 480, ty: 352 }
      ],
      beats: [
        { at: 0, caption: '雨打簷瓦，廊下兩人對峙', line: '點到為止？', walker: 0, scale: 1.2 },
        { at: 900, line: '刀不快，路還長。', walker: 1, scale: 1.15 },
        { at: 1800, caption: '掌櫃定夺', line: '勸和、觀戰，還是請去廂房歇雨？', walker: 0, scale: 1.1 },
        { at: 2500, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'rain_mediate',
          label: '勸和奉茶（＋望／小好感）',
          effects: { silver: -6, reputation: 8, favorHero: 'qingyi', favor: 3, favorHero2: 'langren', favor2: 3 },
          resultLine: '兩人收刃，共飲簷下熱茶。雨聲也溫了些。'
        },
        {
          id: 'rain_watch',
          label: '准比試三招（＋銀／戰意）',
          effects: {
            silver: 18, reputation: 3,
            favorHero: 'langren', favor: 2,
            combatBuff: { id: 'buff_rain_eave', label: '雨簷', forceMul: 1.06, battles: 2, heroes: ['qingyi', 'langren'] }
          },
          resultLine: '刀劍過三招，圍觀客賞了些碎銀。戰意未散。'
        },
        {
          id: 'rain_shelter',
          label: '請入廂房避雨（平）',
          effects: { silver: 4, reputation: 2, favorHero: 'qinshi', favor: 2 },
          resultLine: '浪人收刀，青衣點頭。廂房多點了一盞燈。'
        }
      ]
    },
    {
      id: 'ink_guest_verse',
      title: '墨客題壁',
      caption: '過路墨客要在告示旁留一句…',
      interactive: true,
      once: true,
      preferPhase: 'dusk',
      needHubDays: 1,
      weight: 34,
      walkers: [
        { id: 'xiaoer', x: 300, y: 320, tx: 380, ty: 330 },
        { id: 'qinshi', x: 540, y: 340, tx: 460, ty: 345 }
      ],
      beats: [
        { at: 0, caption: '墨客執筆，小二捏一把汗', line: '掌櫃！他要題壁——寫壞怎麼辦？', walker: 0, scale: 1.2 },
        { at: 950, line: '字如人。善惡在心，不在牆。', walker: 1, scale: 1.25 },
        { at: 1850, caption: '兩選', line: '准他寫，還是請去雅座另紙？', walker: 0, scale: 1.1 },
        { at: 2500, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'ink_allow_wall',
          label: '准題壁（＋望／人情）',
          effects: { reputation: 9, favorHero: 'qinshi', favor: 4, favorHero2: 'qingyi', favor2: 2 },
          resultLine: '墨客留下「客心如水」。過路人駐足念了半日。'
        },
        {
          id: 'ink_paper_fee',
          label: '改題宣紙收潤筆（＋銀）',
          effects: { silver: 22, reputation: 3 },
          resultLine: '墨客笑納潤筆，紙捲帶走。櫃上多了幾兩。'
        }
      ]
    }
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
      garrisonRepChance: 0.04,
      traitLabel: '本棧樞紐',
      traitDesc: '設施加成皆歸於此。'
    },
    {
      id: 'qingshi',
      name: '青石鎮分舵',
      emoji: '🏘️',
      desc: '商旅雲集：駐守偏聲望與夜市抽成；偶發「青石夜市」場景。',
      unlock: { innLevel: 2, reputation: 30, silver: 180 },
      baseIncome: 0.6,
      garrisonIncome: 2.5,
      garrisonRepChance: 0.11,
      marketTipChance: 0.18,
      marketTipSilver: [3, 9],
      traitLabel: '夜市抽成',
      traitDesc: '駐守時偶得夜市抽成；聲望機率較高。'
    },
    {
      id: 'bianguan',
      name: '邊關哨站',
      emoji: '🏰',
      desc: '邊陲要衝：駐守銀兩高；出巡勝仗邊關犒賞；偶發「哨崗警報」。',
      unlock: { innLevel: 3, reputation: 100, silver: 420 },
      baseIncome: 1.0,
      garrisonIncome: 4.0,
      garrisonRepChance: 0.10,
      patrolBonusMul: 0.10,
      patrolBonusCap: 36,
      traitLabel: '邊關犒賞',
      traitDesc: '出巡勝仗銀兩約 +10%（有上限）；駐守進帳偏高。'
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
    },
    {
      id: 'teahouse',
      name: '雅座茶寮',
      emoji: '🍵',
      desc: '專伺雅座：明顯拉高小費／時辰偏好賞銀（同酒窖增收手感唔同——偏賞唔偏底薪）。',
      maxLevel: 3,
      costs: [100, 240, 480],
      repNeed: [5, 35, 90],
      effectLabel: (lv) => lv ? `小費／賞銀 +${lv * 14}% · 偏好客再 +${lv * 4}%` : '未建'
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
    },
    {
      id: 'ember_ash_road',
      name: '餘燼探路委託',
      emoji: '🌫️',
      kind: '探路',
      desc: '閱第六章後可接：沿灰路探探舊營火，回報掌櫃。',
      durationSec: 60,
      heroesNeed: 1,
      rewardSilver: [55, 90],
      rewardRep: [8, 14],
      manualChance: 0.12,
      weight: 16,
      minInn: 3,
      needChapter: 'ch6_ember_road'
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
    },
    {
      id: 'ch4_xueying',
      title: '第四章 · 血影樓訊',
      subtitle: '樓主預告',
      emoji: '🩸',
      unlock: { innLevel: 3, reputation: 110, battlesWon: 9, bossDefeated: 'boss_xieyi' },
      bossId: 'boss_xueying',
      reward: { silver: 120, reputation: 18 },
      lines: [
        { speaker: '行商', text: '掌櫃……血影樓的紅帖到了。說是「借刀」，實則要本棧交人。' },
        { speaker: '浪人刀客', text: '紅帖？哼，樓裡那些影刀，最喜歡夜裡從窗縫鑽進來。' },
        { speaker: '青衣劍客', text: '邪醫既除，更大的影卻來了。樓主善用雙刃，專挑弱處。' },
        { speaker: '琴心師太', text: '血氣過重，梵音可鎮其鋒。然此戰不宜輕忽。' },
        { speaker: '掌櫃', text: '客棧不交人。備傷藥、亮燈——去血影樓問個明白。' },
        { speaker: '旁白', text: '—— 第四章骨架完。Boss「血影樓主」已可挑戰（路線預告・可再戰）。' }
      ]
    },
    {
      id: 'ch5_lantern_long',
      title: '第五章 · 燈火長明',
      subtitle: '邊關密信',
      emoji: '🕯️',
      unlock: { innLevel: 3, reputation: 140, battlesWon: 12, chapterRead: 'ch4_xueying' },
      bossId: null,
      reward: { silver: 150, reputation: 22 },
      lines: [
        { speaker: '旁白', text: '血影樓的紅帖餘燼未冷，邊關又送來一封油布密信。' },
        { speaker: '青衣劍客', text: '信上說哨站外怪風再起——像黑風餘黨，又不像。' },
        { speaker: '鐵掌醫女', text: '傷藥要備足。邊關苦寒，刀口見風即裂。' },
        { speaker: '浪人刀客', text: '樓裡的影、寨裡的風，連在一塊可就熱鬧了。' },
        { speaker: '琴心師太', text: '燈火若長明，邪影難近門。掌櫃，告示欄那邊……還有人求援。' },
        { speaker: '掌櫃', text: '本棧燈不滅。密信收下——江湖支線，告示欄上見。' },
        { speaker: '旁白', text: '—— 第五章完。邊關與青石分舵獨特加成更清晰；告示欄可觸「燈火密信」支線。' }
      ]
    },
    {
      id: 'ch6_ember_road',
      title: '第六章 · 餘燼之路（開頭）',
      subtitle: '結局預告 · 可玩探路',
      emoji: '🌫️',
      unlock: { innLevel: 3, reputation: 170, battlesWon: 14, chapterRead: 'ch5_lantern_long' },
      bossId: null,
      reward: { silver: 80, reputation: 12 },
      lines: [
        { speaker: '旁白', text: '邊關密信的蠟印裂開時，裡面只有半句：「燈熄之處，影自為王。」' },
        { speaker: '青衣劍客', text: '黑風、邪醫、血影……像被人一串串牽著，朝同一處餘燼走。' },
        { speaker: '浪人刀客', text: '那地方有名嗎？還是只剩地名燒剩的灰？' },
        { speaker: '鐵掌醫女', text: '灰裡若有傷者，藥要早備。掌櫃，廂房裡的行囊也該清一清。' },
        { speaker: '琴心師太', text: '梵音聽得見風聲裡有人笑。不是善類——可先派人探路，不必全軍齊出。' },
        { speaker: '掌櫃', text: '本棧燈還亮。結局未至——今夜先定兩樁：探路、立誓。' },
        { speaker: '旁白', text: '—— 第六章開頭加厚。閱後可於本章「餘燼探路／灰上立誓」動手；Hub 亦會偶遇餘燼短景。' }
      ],
      playables: [
        {
          id: 'ch6_scout',
          title: '餘燼探路',
          blurb: '派一人沿灰路探探風向（短對話＋小回報）',
          choices: [
            {
              id: 'qingyi_scout',
              label: '青衣夜探（-20 兩 · +望）',
              effects: { silver: -20, reputation: 8, favorHero: 'qingyi', favor: 4 },
              resultLine: '青衣帶回半截路標：灰路東岔有舊營火。聲望微升。'
            },
            {
              id: 'langren_scout',
              label: '浪人摸營（-12 兩 · 刀客好感）',
              effects: { silver: -12, reputation: 4, favorHero: 'langren', favor: 5 },
              resultLine: '浪人笑說：「只有空帳篷同冷灰。」刀柄多了道新劃痕。'
            },
            {
              id: 'delay_scout',
              label: '暫緩探路（穩）',
              effects: { reputation: 1, favorHero: 'qinshi', favor: 2 },
              resultLine: '師太合十：「忍亦是鋒。燈先守好。」'
            }
          ]
        },
        {
          id: 'ch6_ash_vow',
          title: '灰上立誓',
          blurb: '眾俠於燈下立一誓，換短暫戰意',
          choices: [
            {
              id: 'vow_guard',
              label: '誓守燈火（雙方好感／戰意）',
              effects: {
                favorHero: 'qingyi', favor: 3,
                favorHero2: 'qinshi', favor2: 3,
                reputation: 3,
                combatBuff: { id: 'buff_ember_guard', label: '燈下誓', forceMul: 1.07, battles: 2, heroes: ['qingyi', 'qinshi', 'tiezhang', 'langren'] }
              },
              resultLine: '盞碰盞。眾人齊聲：「燈不滅，影難近。」短暫戰意高昂。'
            },
            {
              id: 'vow_hunt',
              label: '誓追餘燼（-15 兩 · 戰意）',
              effects: {
                silver: -15, reputation: 5,
                favorHero: 'langren', favor: 3,
                favorHero2: 'tiezhang', favor2: 3,
                combatBuff: { id: 'buff_ember_hunt', label: '追燼', forceMul: 1.1, battles: 2, heroes: ['langren', 'tiezhang'] }
              },
              resultLine: '浪人與鐵掌對視一眼。灰路的風，似乎近了些。'
            },
            {
              id: 'vow_quiet',
              label: '只默默添油（小好感）',
              effects: { favorHero: 'tiezhang', favor: 2, favorHero2: 'qinshi', favor2: 2 },
              resultLine: '你添滿燈油。無人多言，卻都明白路已開。'
            }
          ]
        }
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
    },
    {
      id: 'boss_xueying',
      name: '血影樓主',
      emoji: '🩸',
      chapterId: 'ch4_xueying',
      desc: '血影樓主，雙刃嗜血，影衛成對；專剋護盾薄弱者。（第四章路線預告）',
      minInnLevel: 3,
      rewardSilver: [320, 460],
      rewardRep: [42, 60],
      rewardManual: 'xueying',
      bonusSilver: 180,
      enemies: [
        {
          name: '血影衛甲', emoji: '🗡️', force: 20, nei: 14, hp: 120,
          skill: { name: '影刺', mul: 1.5, chance: 0.26 }
        },
        {
          name: '血影衛乙', emoji: '🗡️', force: 20, nei: 14, hp: 120,
          skill: { name: '影刺', mul: 1.5, chance: 0.26 }
        },
        {
          id: 'boss_xueying',
          name: '血影樓主', emoji: '🩸', force: 30, nei: 22, hp: 300,
          skill: { name: '血影連斬', mul: 2.05, chance: 0.36, weaken: 0.12 },
          mitBonus: 0.09,
          startShield: 0.08
        }
      ]
    }
  ];

  /**
   * 成就：解鎖後 toast＋可於江湖分頁查看
   * check 於執行期由 game.js 依 state 判定
   */
  const ACHIEVEMENTS = [
    { id: 'first_win', name: '初試鋒芒', desc: '贏得第一場出巡勝仗', emoji: '⚔️', reward: { silver: 20, reputation: 2 } },
    { id: 'wins_10', name: '百戰初成', desc: '累計勝仗達 10 場', emoji: '🏆', reward: { silver: 60, reputation: 8 } },
    { id: 'recruit_all', name: '高朋滿座', desc: '招募全部可入駐俠客', emoji: '🏯', reward: { silver: 50, reputation: 6 } },
    { id: 'bond_confidant', name: '知己難求', desc: '任一名俠客羈絆達「知己」', emoji: '💞', reward: { silver: 40, reputation: 5 } },
    { id: 'inn_lv2', name: '青石新貌', desc: '客棧升級至 Lv.2 或以上', emoji: '🏗️', reward: { silver: 35, reputation: 4 } },
    { id: 'outpost_any', name: '分舵初開', desc: '解鎖本棧以外的任一據點', emoji: '🗺️', reward: { silver: 45, reputation: 5 } },
    { id: 'facility_any', name: '百工就緒', desc: '建造任一設施（達 Lv.1）', emoji: '🔧', reward: { silver: 25, reputation: 3 } },
    { id: 'boss_heifeng', name: '黑風盡滅', desc: '擊敗 Boss「黑風寨主」', emoji: '🌪️', reward: { silver: 80, reputation: 10 } },
    { id: 'boss_xieyi', name: '霧破毒消', desc: '擊敗 Boss「邪醫·腐骨」', emoji: '☠️', reward: { silver: 100, reputation: 12 } },
    { id: 'boss_xueying', name: '血影盡散', desc: '擊敗 Boss「血影樓主」', emoji: '🩸', reward: { silver: 120, reputation: 14 } },
    { id: 'manuals_4', name: '武學初成', desc: '藏書閣收藏至少 4 本秘籍', emoji: '📚', reward: { silver: 55, reputation: 6 } },
    { id: 'quest_5', name: '俠義奔走', desc: '完成至少 5 件聲望委託', emoji: '📋', reward: { silver: 50, reputation: 7 } },
    { id: 'story_ch5', name: '燈火長明', desc: '閱覽第五章「燈火長明」', emoji: '🕯️', reward: { silver: 70, reputation: 10 } },
    { id: 'story_all', name: '燈火篇章', desc: '閱覽全部劇情章節', emoji: '📜', reward: { silver: 100, reputation: 15 } },
    { id: 'counter_8', name: '借力打力', desc: '招架反打命中累計 8 次', emoji: '🛡️', reward: { silver: 55, reputation: 8 } },
    { id: 'teahouse_1', name: '雅座初香', desc: '建造雅座茶寮（達 Lv.1）', emoji: '🍵', reward: { silver: 40, reputation: 6 } },
    { id: 'qingshi_open', name: '青石夜市', desc: '解鎖青石鎮分舵', emoji: '🏘️', reward: { silver: 50, reputation: 7 } },
    { id: 'bianguan_open', name: '邊關戍衛', desc: '解鎖邊關哨站', emoji: '🏰', reward: { silver: 70, reputation: 9 } },
    { id: 'board_letter', name: '密信有回', desc: '於告示完成「燈火密信」任一選擇', emoji: '✉️', reward: { silver: 45, reputation: 8 } },
    { id: 'market_tip_3', name: '夜市抽成', desc: '青石夜市抽成累計入帳 3 次', emoji: '🪙', reward: { silver: 60, reputation: 6 } },
    { id: 'duo_bonds_all', name: '六合連枝', desc: '解鎖全部六組雙人羈絆合擊', emoji: '☯️', reward: { silver: 120, reputation: 15 } }
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
      desc: '劍勢連環，出手時傷害提高。',
      effect: { mul: 1.7, chance: 0.24 },
      learnCost: 70,
      dropWeight: 12
    },
    {
      id: 'tiesha',
      name: '鐵砂掌',
      type: 'active',
      desc: '掌勁剛猛，打中時可回少量氣血。',
      effect: { mul: 1.45, chance: 0.26, heal: 0.12 },
      learnCost: 85,
      dropWeight: 10
    },
    {
      id: 'langren_slash',
      name: '浪人斬',
      type: 'active',
      desc: '孤刀猛劈，威力大、出手稍稀。',
      effect: { mul: 2.15, chance: 0.16 },
      learnCost: 100,
      dropWeight: 8
    },
    {
      id: 'fanyin',
      name: '梵音破障',
      type: 'active',
      desc: '琴音亂神，傷敵之餘略削其力。',
      effect: { mul: 1.65, chance: 0.25, weaken: 0.12 },
      learnCost: 130,
      dropWeight: 5
    },
    {
      id: 'tuna',
      name: '吐納心法',
      type: 'passive',
      desc: '內息綿長，內力見長，緩慢回血。',
      effect: { neiBonus: 0.14, regen: 0.025 },
      learnCost: 80,
      dropWeight: 11
    },
    {
      id: 'jinzhong',
      name: '金鐘罩',
      type: 'passive',
      desc: '周身護氣，減傷，開戰略帶護盾。',
      effect: { mitBonus: 0.10, startShield: 0.08 },
      learnCost: 95,
      dropWeight: 7
    },
    {
      id: 'liuyun',
      name: '流雲步',
      type: 'passive',
      desc: '身法輕靈，略增武力，主動技更常出手。',
      effect: { forceBonus: 0.08, skillChanceBonus: 0.06 },
      learnCost: 90,
      dropWeight: 9
    },
    {
      id: 'xueying',
      name: '血影雙刃',
      type: 'active',
      desc: '雙刃錯落，出手頻密，並短暫削弱敵方。',
      effect: { mul: 1.85, chance: 0.28, weaken: 0.1 },
      learnCost: 150,
      dropWeight: 3
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
      lore: '醫武雙修，掌力綿裡藏針，常為客棧療傷。',
      unlockHint: '銀兩足夠即可請入；入駐後有藥香抵達短景。'
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
      lore: '來歷不明的浪客，刀勢狂烈，酒後更兇。',
      unlockHint: '銀兩足夠即可請入；入駐後有對刀抵達短景。'
    },
    {
      id: 'qinshi',
      name: '琴心師太',
      title: '梵音破魔',
      emoji: '🎵',
      unlocked: false,
      unlockCost: 450,
      unlockReq: { reputation: 60, anyFavor: 40, innLevel: 2 },
      unlockHint: '需客棧 Lv.2、聲望 60、任一名已入駐俠客好感達 40（談心／出巡可累積）。達標後入駐有梵音抵達演出。',
      base: { force: 10, nei: 18, hp: 85, favor: 0 },
      growth: { force: 1.6, nei: 3.0, hp: 11 },
      defaultActive: 'fanyin',
      defaultPassive: 'jinzhong',
      lore: '雲遊至此的師太，琴音可亂敵心神。聲望、客棧等級與情誼達標可請入駐。'
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
      },
      {
        id: 'qy_3',
        favorNeed: 80,
        title: '燈下同守',
        text: '夜深她為你添一盞燈：「江湖再亂，此棧有燈、有你，我便有歸處。」劍意與心同時安定。'
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
      },
      {
        id: 'lr_3',
        favorNeed: 78,
        title: '酒盡真義',
        text: '他將空碗一扣：「刀可以借，命可以拼——只這棧，不許人欺。」狂名之下，竟是護短。'
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


  /** v1.5 雙人羈絆／情愛事件（Hub 場景＋選擇；可帶短暫戰鬥加成） */
  const DUO_BOND_EVENTS = [
    {
      id: 'duo_sword_herb',
      title: '劍與藥',
      heroes: ['qingyi', 'tiezhang'],
      favorNeed: { qingyi: 40, tiezhang: 35 },
      caption: '雅座一角，青衣與鐵掌並坐…',
      interactive: true,
      weight: 50,
      walkers: [
        { id: 'qingyi', x: 300, y: 340, tx: 360, ty: 350 },
        { id: 'tiezhang', x: 520, y: 350, tx: 430, ty: 352 }
      ],
      beats: [
        { at: 0, caption: '藥香混著劍穗清氣', line: '你的腕力又緊了。', walker: 1, life: 1.2 },
        { at: 900, line: '……習慣。有你在，傷好得快些。', walker: 0, life: 1.25 },
        { at: 1900, caption: '二人望向掌櫃', line: '掌櫃可願聽我們一樁心事？', walker: 1, life: 1.2 },
        { at: 2700, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'hear_both',
          label: '靜聽心事（雙方好感＋）',
          effects: {
            favorHero: 'qingyi', favor: 5,
            favorHero2: 'tiezhang', favor2: 5,
            combatBuff: { id: 'buff_sword_herb', label: '劍藥同心', forceMul: 1.08, battles: 2, heroes: ['qingyi', 'tiezhang'] }
          },
          resultLine: '青衣輕笑，鐵掌為二人搭脈。來日出巡，劍鋒與藥力似更合拍。'
        },
        {
          id: 'toast_pair',
          label: '敬二人一盞（-22 兩 · 戰意）',
          effects: {
            silver: -22, reputation: 2,
            favorHero: 'qingyi', favor: 4,
            favorHero2: 'tiezhang', favor2: 4,
            combatBuff: { id: 'buff_sword_herb_toast', label: '燈下共盞', forceMul: 1.12, battles: 3, heroes: ['qingyi', 'tiezhang'] }
          },
          resultLine: '盞碰盞。鐵掌低聲：「傷好了，便一起守這盞燈。」短暫戰意高昂。'
        },
        {
          id: 'step_aside',
          label: '不便打擾（小好感）',
          effects: { favorHero: 'qingyi', favor: 1, favorHero2: 'tiezhang', favor2: 1 },
          resultLine: '你默默添茶離開。二人交換一眼，似有默契未說完。'
        }
      ]
    },
    {
      id: 'duo_blade_moon',
      title: '刀劍邀月',
      heroes: ['qingyi', 'langren'],
      favorNeed: { qingyi: 45, langren: 40 },
      caption: '月下庭階，青衣與浪人對立而立…',
      interactive: true,
      weight: 48,
      walkers: [
        { id: 'qingyi', x: 280, y: 320, tx: 340, ty: 330 },
        { id: 'langren', x: 560, y: 330, tx: 460, ty: 332 }
      ],
      beats: [
        { at: 0, caption: '刀光與劍影錯落', line: '再來一招？', walker: 1, life: 1.15 },
        { at: 850, line: '今夜月好。掌櫃若在，便算有見證。', walker: 0, life: 1.25 },
        { at: 1800, caption: '二人收勢', line: '你說——刀與劍，可否同路？', walker: 1, life: 1.2 },
        { at: 2600, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'witness',
          label: '願作見證（雙方好感＋）',
          effects: {
            favorHero: 'qingyi', favor: 5,
            favorHero2: 'langren', favor2: 5,
            combatBuff: { id: 'buff_blade_moon', label: '刀劍同輝', forceMul: 1.09, battles: 2, heroes: ['qingyi', 'langren'] }
          },
          resultLine: '浪人收刀大笑，青衣點頭。月下並肩之感，帶入下一場出巡。'
        },
        {
          id: 'spar_wager',
          label: '加注切磋彩頭（-18 兩）',
          effects: {
            silver: -18, reputation: 3,
            favorHero: 'qingyi', favor: 3,
            favorHero2: 'langren', favor2: 6,
            combatBuff: { id: 'buff_blade_wager', label: '月下彩頭', forceMul: 1.11, battles: 3, heroes: ['qingyi', 'langren'] }
          },
          resultLine: '彩頭入櫃。二人又過三招，汗意與笑意同起——戰意未散。'
        },
        {
          id: 'call_rest',
          label: '勸二人歇手（穩）',
          effects: { favorHero: 'qingyi', favor: 2, favorHero2: 'langren', favor2: 2, reputation: 1 },
          resultLine: '青衣收劍：「掌櫃說得是。」浪人嘟囔著去討酒，卻沒有真惱。'
        }
      ]
    },
    {
      id: 'duo_herb_fan',
      title: '藥梵同心',
      heroes: ['tiezhang', 'qinshi'],
      favorNeed: { tiezhang: 40, qinshi: 40 },
      caption: '藥香與梵音在廂房外廊下交疊…',
      interactive: true,
      weight: 46,
      walkers: [
        { id: 'tiezhang', x: 300, y: 340, tx: 360, ty: 348 },
        { id: 'qinshi', x: 540, y: 336, tx: 450, ty: 340 }
      ],
      beats: [
        { at: 0, caption: '鐵掌搭脈，師太輕撥念珠', line: '這脈象……要靜。', walker: 0, life: 1.2 },
        { at: 900, line: '梵音可安神。你掌力穩，正好護他心脈。', walker: 1, life: 1.25 },
        { at: 1900, caption: '二人望向掌櫃', line: '掌櫃可願聽我們同心一計？', walker: 1, life: 1.2 },
        { at: 2700, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'hear_herb_fan',
          label: '靜聽藥梵（雙方好感＋）',
          effects: {
            favorHero: 'tiezhang', favor: 5,
            favorHero2: 'qinshi', favor2: 5,
            combatBuff: { id: 'buff_herb_fan', label: '藥梵', forceMul: 1.08, battles: 2, heroes: ['tiezhang', 'qinshi'] }
          },
          resultLine: '藥香繞梵。來日出巡，掌力與琴音似更合拍——合擊「藥梵同心」可解鎖。'
        },
        {
          id: 'toast_herb_fan',
          label: '備茶相敬（-20 兩 · 戰意）',
          effects: {
            silver: -20, reputation: 2,
            favorHero: 'tiezhang', favor: 4,
            favorHero2: 'qinshi', favor2: 4,
            combatBuff: { id: 'buff_herb_fan_tea', label: '廊下茶', forceMul: 1.11, battles: 3, heroes: ['tiezhang', 'qinshi'] }
          },
          resultLine: '清茶入喉。鐵掌與師太同時點頭——短暫戰意高昂。'
        },
        {
          id: 'step_herb_fan',
          label: '不便打擾（小好感）',
          effects: { favorHero: 'tiezhang', favor: 1, favorHero2: 'qinshi', favor2: 1 },
          resultLine: '你輕步走開。廊下梵音仍緩，藥香未散。'
        }
      ]
    },
    {
      id: 'duo_blade_herb',
      title: '刀藥破障',
      heroes: ['langren', 'tiezhang'],
      favorNeed: { langren: 42, tiezhang: 38 },
      caption: '後院石階，浪人擦刀，鐵掌調膏…',
      interactive: true,
      weight: 44,
      walkers: [
        { id: 'langren', x: 280, y: 330, tx: 350, ty: 340 },
        { id: 'tiezhang', x: 560, y: 345, tx: 460, ty: 348 }
      ],
      beats: [
        { at: 0, caption: '刀光一閃，藥香跟上', line: '再砍深一寸，你那傷藥跟不跟得上？', walker: 0, life: 1.15 },
        { at: 900, line: '跟得上。你別亂逞能便是。', walker: 1, life: 1.2 },
        { at: 1850, caption: '二人收勢', line: '掌櫃——刀與藥，可否破障同行？', walker: 0, life: 1.2 },
        { at: 2650, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'witness_blade_herb',
          label: '願作見證（雙方好感＋）',
          effects: {
            favorHero: 'langren', favor: 5,
            favorHero2: 'tiezhang', favor2: 5,
            combatBuff: { id: 'buff_blade_herb', label: '刀藥', forceMul: 1.09, battles: 2, heroes: ['langren', 'tiezhang'] }
          },
          resultLine: '浪人收刀大笑，鐵掌翻個白眼卻沒反對。合擊「刀藥破障」可解鎖。'
        },
        {
          id: 'wager_blade_herb',
          label: '加注傷藥彩頭（-16 兩）',
          effects: {
            silver: -16, reputation: 3,
            favorHero: 'langren', favor: 4,
            favorHero2: 'tiezhang', favor2: 5,
            combatBuff: { id: 'buff_blade_herb_wager', label: '彩頭膏', forceMul: 1.12, battles: 3, heroes: ['langren', 'tiezhang'] }
          },
          resultLine: '彩頭入櫃。刀鋒與藥力較勁三招——戰意未散。'
        },
        {
          id: 'call_blade_herb',
          label: '勸二人歇手（穩）',
          effects: { favorHero: 'langren', favor: 2, favorHero2: 'tiezhang', favor2: 2, reputation: 1 },
          resultLine: '鐵掌收膏：「聽掌櫃的。」浪人嘟囔，刀卻入了鞘。'
        }
      ]
    },
    {
      id: 'duo_qin_sword',
      title: '琴心劍膽',
      heroes: ['qingyi', 'qinshi'],
      favorNeed: { qingyi: 42, qinshi: 40 },
      caption: '雅座燈下，青衣聽琴，師太拂塵輕顫…',
      interactive: true,
      weight: 47,
      walkers: [
        { id: 'qingyi', x: 300, y: 340, tx: 360, ty: 348 },
        { id: 'qinshi', x: 540, y: 336, tx: 450, ty: 340 }
      ],
      beats: [
        { at: 0, caption: '琴音似水，劍穗輕搖', line: '你這劍，心裡有音。', walker: 1, life: 1.25 },
        { at: 900, line: '……有你琴聲，劍才不躁。', walker: 0, life: 1.2 },
        { at: 1850, caption: '二人望向掌櫃', line: '掌櫃——琴心與劍膽，可否同行？', walker: 1, life: 1.2 },
        { at: 2650, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'hear_qin_sword',
          label: '靜聽琴劍（雙方好感＋）',
          effects: {
            favorHero: 'qingyi', favor: 5,
            favorHero2: 'qinshi', favor2: 5,
            combatBuff: { id: 'buff_qin_sword', label: '琴心劍膽', forceMul: 1.09, battles: 2, heroes: ['qingyi', 'qinshi'] }
          },
          resultLine: '琴停劍收。來日出巡，可解鎖合擊「琴心劍膽」。'
        },
        {
          id: 'toast_qin_sword',
          label: '備清茶相敬（-20 兩 · 戰意）',
          effects: {
            silver: -20, reputation: 2,
            favorHero: 'qingyi', favor: 4,
            favorHero2: 'qinshi', favor2: 4,
            combatBuff: { id: 'buff_qin_sword_tea', label: '燈下琴劍', forceMul: 1.12, battles: 3, heroes: ['qingyi', 'qinshi'] }
          },
          resultLine: '清茶入喉。青衣與師太同時點頭——短暫戰意高昂。'
        },
        {
          id: 'step_qin_sword',
          label: '不便打擾（小好感）',
          effects: { favorHero: 'qingyi', favor: 1, favorHero2: 'qinshi', favor2: 1 },
          resultLine: '你輕步走開。雅座琴音仍緩，劍穗未停。'
        }
      ]

    },
    {
      id: 'duo_blade_fan',
      title: '刀梵夜語',
      heroes: ['langren', 'qinshi'],
      favorNeed: { langren: 42, qinshi: 40 },
      caption: '夜廊燈影，浪人倚柱擦刀，師太撥動念珠…',
      interactive: true,
      weight: 45,
      walkers: [
        { id: 'langren', x: 280, y: 330, tx: 350, ty: 340 },
        { id: 'qinshi', x: 560, y: 336, tx: 460, ty: 340 }
      ],
      beats: [
        { at: 0, caption: '刀響輕、梵音緩', line: '你這刀，夜裡比白天更吵。', walker: 1, life: 1.2 },
        { at: 900, line: '……吵醒了野鬼也好。師太你怕不怕？', walker: 0, life: 1.2 },
        { at: 1850, caption: '二人望向掌櫃', line: '掌櫃——刀與梵，可否共守一夜？', walker: 1, life: 1.2 },
        { at: 2650, prompt: true, end: true }
      ],
      choices: [
        {
          id: 'hear_blade_fan',
          label: '靜聽刀梵（雙方好感＋）',
          effects: {
            favorHero: 'langren', favor: 5,
            favorHero2: 'qinshi', favor2: 5,
            combatBuff: { id: 'buff_blade_fan', label: '刀梵夜語', forceMul: 1.09, battles: 2, heroes: ['langren', 'qinshi'] }
          },
          resultLine: '刀入鞘，梵音歇。來日出巡，可解鎖合擊「刀梵夜語」。'
        },
        {
          id: 'toast_blade_fan',
          label: '備清茶相敬（-18 兩 · 戰意）',
          effects: {
            silver: -18, reputation: 2,
            favorHero: 'langren', favor: 4,
            favorHero2: 'qinshi', favor2: 4,
            combatBuff: { id: 'buff_blade_fan_tea', label: '夜廊清茶', forceMul: 1.12, battles: 3, heroes: ['langren', 'qinshi'] }
          },
          resultLine: '清茶入喉。浪人與師太同時點頭——短暫戰意高昂。'
        },
        {
          id: 'step_blade_fan',
          label: '不便打擾（小好感）',
          effects: { favorHero: 'langren', favor: 1, favorHero2: 'qinshi', favor2: 1 },
          resultLine: '你輕步走開。夜廊刀響漸歇，念珠仍緩。'
        }
      ]

    }
  ];


  /**
   * v2.0 雙人合擊：需已完成對應雙人羈絆事件（duoBondDone），且雙方同隊存活。
   * 一場戰鬥最多施放一次；自動戰鬥條件滿足時觸發。
   */
  const DUO_COMBOS = [
    {
      id: 'combo_sword_herb',
      duoId: 'duo_sword_herb',
      name: '劍藥同心',
      heroes: ['qingyi', 'tiezhang'],
      damageMul: 1.9,
      breakMit: 0.2,
      telegraph: '劍鋒挾藥勁',
      resultLine: '青衣一劍，鐵掌跟掌——破防！'
    },
    {
      id: 'combo_blade_moon',
      duoId: 'duo_blade_moon',
      name: '刀劍邀月',
      heroes: ['qingyi', 'langren'],
      damageMul: 2.0,
      breakMit: 0.18,
      telegraph: '刀光劍影錯落',
      resultLine: '浪人橫刀，青衣順勢——合擊破敵！'
    },
    {
      id: 'combo_herb_fan',
      duoId: 'duo_herb_fan',
      name: '藥梵同心',
      heroes: ['tiezhang', 'qinshi'],
      damageMul: 1.85,
      breakMit: 0.22,
      telegraph: '藥勁挾梵音',
      resultLine: '鐵掌震脈，師太梵音跟上——破防！'
    },
    {
      id: 'combo_blade_herb',
      duoId: 'duo_blade_herb',
      name: '刀藥破障',
      heroes: ['langren', 'tiezhang'],
      damageMul: 1.95,
      breakMit: 0.19,
      telegraph: '刀風捲藥霧',
      resultLine: '浪人劈障，鐵掌跟掌——合擊破敵！'
    },
    {
      id: 'combo_qin_sword',
      duoId: 'duo_qin_sword',
      name: '琴心劍膽',
      heroes: ['qingyi', 'qinshi'],
      damageMul: 1.92,
      breakMit: 0.21,
      telegraph: '琴音引劍、劍膽護心',
      resultLine: '師太梵音一撥，青衣劍光跟上——合擊破敵！'
    },
    {
      id: 'combo_blade_fan',
      duoId: 'duo_blade_fan',
      name: '刀梵夜語',
      heroes: ['langren', 'qinshi'],
      damageMul: 1.9,
      breakMit: 0.2,
      telegraph: '刀光夜語、梵音護心',
      resultLine: '浪人橫刀，師太梵音跟上——合擊破敵！'
    }
  ];

  const SIT_ORDER_LINES = {
    wait: ['等茶…', '今日有咩菜？', '慢慢嚟都得'],
    order: ['來壺熱茶', '兩碟小菜', '斟滿啲', '掌櫃，落單啦'],
    happy: ['好味！', '再來一盅', '賞你', '坐得舒服'],
    impatient: ['等咗好耐…', '茶呢？', '走唔走得成', '小二——']
  };

  function getDuoCombo(id) {
    return DUO_COMBOS.find(function (c) { return c.id === id || c.duoId === id; }) || null;
  }

  /** partyIds: 出戰 id 列表；doneIds: state.duoBondDone */
  function resolvePartyCombo(partyIds, doneIds) {
    const party = partyIds || [];
    const done = doneIds || [];
    for (let i = 0; i < DUO_COMBOS.length; i++) {
      const c = DUO_COMBOS[i];
      if (done.indexOf(c.duoId) < 0) continue;
      if (c.heroes.every(function (h) { return party.indexOf(h) >= 0; })) return c;
    }
    return null;
  }

  /** 招募抵達短景（Hub 泡泡／行人） */
  const RECRUIT_ARRIVALS = {
    tiezhang: {
      id: 'arrive_tiezhang',
      caption: '鐵掌醫女入駐…',
      walkers: [
        { id: 'tiezhang', x: 80, y: 360, tx: 280, ty: 350 },
        { id: 'xiaoer', x: 400, y: 320, tx: 340, ty: 340 }
      ],
      beats: [
        { at: 0, caption: '藥箱落櫃', line: '傷藥帶齊了。有傷，找我。', walker: 0, life: 1.35 },
        { at: 1100, line: '醫女姐姐好！小二給您拂席！', walker: 1, life: 1.2, end: true }
      ]
    },
    langren: {
      id: 'arrive_langren',
      caption: '浪人刀客入駐…',
      walkers: [
        { id: 'langren', x: 900, y: 340, tx: 520, ty: 350 },
        { id: 'xiaoer', x: 300, y: 330, tx: 400, ty: 340 }
      ],
      beats: [
        { at: 0, caption: '刀鞘磕門檻', line: '有酒麼？沒酒也成——有架打就行。', walker: 0, life: 1.35 },
        { at: 1200, line: '刀客爺，雅座這邊！先登記……', walker: 1, life: 1.2, end: true }
      ]
    },
    qinshi: {
      id: 'arrive_qinshi',
      caption: '琴心師太入駐…',
      walkers: [
        { id: 'qinshi', x: 100, y: 300, tx: 360, ty: 340 },
        { id: 'xiaoer', x: 500, y: 340, tx: 420, ty: 350 }
      ],
      beats: [
        { at: 0, caption: '梵音初起', line: '施主有緣。容貧尼借一角清靜。', walker: 0, life: 1.4 },
        { at: 1200, line: '師太裏面請！小二去焚一炷香。', walker: 1, life: 1.25, end: true }
      ]
    }
  };


  const ENEMY_WAVES = [
    {
      id: 'bandit_small',
      name: '山賊小隊',
      minInnLevel: 1,
      risk: 1,
      tags: ['近戰', '練手'],
      blurb: '喽啰成群，節奏仍可讀；早期略硬，唔好無腦衝。',
      rewardSilver: [22, 40],
      rewardRep: [3, 5],
      enemies: [
        { name: '山賊喽啰', emoji: '👺', force: 8, nei: 4, hp: 48, ai: 'skirmish', sprite: 'enemy_melee' },
        { name: '山賊喽啰', emoji: '👺', force: 8, nei: 4, hp: 48, ai: 'skirmish', sprite: 'enemy_melee' }
      ]
    },
    {
      id: 'bandit_camp',
      name: '流寇營寨',
      minInnLevel: 1,
      risk: 2,
      tags: ['混合', '拉距'],
      blurb: '刀手推進、弓手拉距；頭目會伺機衝鋒。早期第二關略壓。',
      rewardSilver: [48, 82],
      rewardRep: [6, 11],
      enemies: [
        { name: '流寇刀手', emoji: '💀', force: 12, nei: 6, hp: 70, ai: 'skirmish', sprite: 'enemy_melee' },
        { name: '流寇弓手', emoji: '🏹', force: 9, nei: 7, hp: 52, ranged: true, ai: 'kite', sprite: 'enemy_kite' },
        { name: '流寇頭目', emoji: '👹', force: 16, nei: 9, hp: 105, ai: 'charge', sprite: 'enemy_charge' }
      ]
    },
    {
      id: 'horse_raid',
      name: '馬匪衝陣',
      minInnLevel: 2,
      risk: 3,
      tags: ['衝鋒', '高壓'],
      blurb: '槍騎直撲中軍；側翼弓手風箏。輸贏往往在前十秒。',
      rewardSilver: [110, 170],
      rewardRep: [13, 20],
      enemies: [
        { name: '馬匪槍騎', emoji: '🐎', force: 15, nei: 7, hp: 85, ai: 'charge', sprite: 'enemy_charge' },
        { name: '馬匪槍騎', emoji: '🐎', force: 15, nei: 7, hp: 85, ai: 'charge', sprite: 'enemy_charge' },
        { name: '馬匪弓手', emoji: '🏹', force: 11, nei: 9, hp: 55, ranged: true, ai: 'kite', sprite: 'enemy_kite' }
      ]
    },
    {
      id: 'black_market',
      name: '黑市惡霸',
      minInnLevel: 2,
      risk: 3,
      tags: ['厚血', '護盾感'],
      blurb: '護院肉盾纏鬥，惡霸下手重；宜集火頭目。',
      rewardSilver: [95, 150],
      rewardRep: [12, 18],
      enemies: [
        { name: '惡霸護院', emoji: '🛡️', force: 12, nei: 8, hp: 80, ai: 'skirmish', mitBonus: 0.08, sprite: 'enemy_melee' },
        { name: '惡霸護院', emoji: '🛡️', force: 12, nei: 8, hp: 80, ai: 'skirmish', mitBonus: 0.08, sprite: 'enemy_melee' },
        { name: '黑市惡霸', emoji: '👿', force: 18, nei: 12, hp: 130, ai: 'charge', sprite: 'enemy_charge' }
      ]
    },
    {
      id: 'demon_cult',
      name: '魔教探子',
      minInnLevel: 3,
      risk: 4,
      tags: ['刺客', '高壓'],
      blurb: '刺客喜突進，血影使內力深厚；慢熱易崩。後期犒賞已收斂。',
      rewardSilver: [160, 230],
      rewardRep: [18, 28],
      enemies: [
        { name: '魔教探子', emoji: '🌑', force: 16, nei: 14, hp: 100, ai: 'kite', ranged: true, sprite: 'enemy_kite' },
        { name: '魔教刺客', emoji: '🗡️', force: 20, nei: 10, hp: 90, ai: 'charge', sprite: 'enemy_charge' },
        { name: '血影使', emoji: '🩸', force: 24, nei: 18, hp: 160, ai: 'charge', sprite: 'enemy_charge' }
      ]
    }
  ];

  /** 出巡路線資訊：風險星／報酬字串（供 UI） */
  function waveThreatScore(wave) {
    if (!wave || !wave.enemies) return 0;
    return wave.enemies.reduce(function (s, e) {
      const aiW = e.ai === 'charge' ? 1.25 : (e.ai === 'kite' ? 1.1 : 1);
      return s + (e.force * 2.2 + (e.nei || 0) + (e.hp || 0) / 12) * aiW;
    }, 0);
  }

  function waveRiskStars(wave) {
    const r = wave && wave.risk != null ? wave.risk : Math.max(1, Math.min(5, Math.round(waveThreatScore(wave) / 55)));
    return Math.max(1, Math.min(5, r | 0));
  }

  function formatWavePreview(wave) {
    const stars = waveRiskStars(wave);
    const starStr = '★'.repeat(stars) + '☆'.repeat(5 - stars);
    const sil = wave.rewardSilver || [0, 0];
    const rep = wave.rewardRep || [0, 0];
    const tags = (wave.tags || []).slice(0, 3).join('·') || '常規';
    return {
      stars: stars,
      starStr: starStr,
      rewardLine: '銀 ' + sil[0] + '–' + sil[1] + ' · 望 ' + rep[0] + '–' + rep[1],
      tagsLine: tags,
      blurb: wave.blurb || '',
      enemyLine: (wave.enemies || []).map(function (e) {
        const tip = e.ai === 'charge' ? '衝' : (e.ai === 'kite' ? '距' : '常');
        return e.name + '[' + tip + ']';
      }).join('、')
    };
  }

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
    guestPhaseMul,
    XIAOER_PHASE_LINES,
    RUMORS,
    XIAOER_LINES,
    GUEST_EVENTS,
    SCENE_EVENTS,
    HERO_TEMPLATES,
    ENEMY_WAVES,
    waveThreatScore,
    waveRiskStars,
    formatWavePreview,
    TRAIN,
    MARTIAL_ARTS,
    BOND_TIERS,
    BOND_EVENTS,
    DUO_BOND_EVENTS,
    DUO_COMBOS,
    SIT_ORDER_LINES,
    RECRUIT_ARRIVALS,
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
    getDuoCombo,
    resolvePartyCombo,
    getOutpost,
    getFacility,
    getQuestTemplate,
    getStoryChapter,
    getBoss,
    getAchievement,
    dayKey
  };
})(typeof window !== 'undefined' ? window : globalThis);
