import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Pet size presets (≈ desktop mid range, scaled for mobile DPI).
const sizePresets = <String, double>{
  '极小': 96,
  '小': 128,
  '中': 160,
  '大': 192,
  '很大': 224,
  '超大': 256,
  '极大': 288,
};

enum PetMode { free, stroll, follow, sleep, work, music, game }

enum PetPose { stand, walk, sleep, happy, work, action }

class WalletState {
  int gold;
  final Map<String, int> items;
  WalletState({this.gold = 10, Map<String, int>? items})
      : items = items ?? {'bread': 2, 'flower_cut': 0, 'seed_wheat': 3, 'wood': 0};

  Map<String, dynamic> toJson() => {'gold': gold, 'items': items};
  factory WalletState.fromJson(Map<String, dynamic>? j) {
    if (j == null) return WalletState();
    final items = <String, int>{};
    final raw = j['items'];
    if (raw is Map) {
      raw.forEach((k, v) => items['$k'] = (v as num?)?.toInt() ?? 0);
    }
    return WalletState(gold: (j['gold'] as num?)?.toInt() ?? 0, items: items);
  }
}

class HomeCell {
  String kind; // empty / soil / crop / tree / water
  String? cropId;
  double growth; // 0-100
  int waterToday;
  HomeCell({this.kind = 'empty', this.cropId, this.growth = 0, this.waterToday = 0});

  Map<String, dynamic> toJson() => {
        'kind': kind,
        'cropId': cropId,
        'growth': growth,
        'waterToday': waterToday,
      };
  factory HomeCell.fromJson(Map<String, dynamic> j) => HomeCell(
        kind: '${j['kind'] ?? 'empty'}',
        cropId: j['cropId'] as String?,
        growth: (j['growth'] as num?)?.toDouble() ?? 0,
        waterToday: (j['waterToday'] as num?)?.toInt() ?? 0,
      );
}

class MeetFriendship {
  int meetCount;
  double points;
  MeetFriendship({this.meetCount = 0, this.points = 0});
  Map<String, dynamic> toJson() => {'meet_count': meetCount, 'points': points};
  factory MeetFriendship.fromJson(Map<String, dynamic>? j) => MeetFriendship(
        meetCount: (j?['meet_count'] as num?)?.toInt() ?? 0,
        points: (j?['points'] as num?)?.toDouble() ?? 0,
      );
}

/// Central domain controller — mirrors desktop pet.py behaviour in Dart.
class PetController extends ChangeNotifier {
  PetController();

  final _rng = Random();
  SharedPreferences? _prefs;

  // profile
  String ownerName = '';
  bool ownerSet = false;
  DateTime? firstOpenAt;
  DateTime? lastOpenAt;

  // display
  String sizeKey = '中';
  double get displaySize => sizePresets[sizeKey] ?? 160;
  bool showSpeech = true;
  bool voiceEnabled = true;
  bool sfxEnabled = true;
  double musicVolume = 0.55;
  double voiceVolume = 0.85;
  String difficulty = '中'; // 低/中/高

  // runtime
  PetMode mode = PetMode.free;
  PetPose pose = PetPose.stand;
  String poseAsset = 'stand.png';
  int walkFrame = 0;
  double petX = 80;
  double petY = 200;
  bool dragging = false;
  bool overlayRunning = false;
  bool companionAster = false;
  bool companionMorvay = false;
  bool wearFlower = false;
  String? outfitDecorId;

  // speech
  String speechText = '';
  bool speechVisible = false;
  Timer? _speechHide;

  // economy / vitals
  int stamina = 80;
  int mood = 80;
  WalletState wallet = WalletState();
  final List<String> diaryPages = [];
  final Set<String> achievements = {};
  final List<String> galleryTitles = ['夏日合影', '伏案一角', '星空'];
  final List<Map<String, String>> phonographClips = [
    {'id': 'hi', 'title': '打招呼'},
    {'id': 'sleep', 'title': '睡眠'},
    {'id': 'work', 'title': '工作'},
  ];

  // tools
  bool stopwatchRunning = false;
  Duration stopwatchElapsed = Duration.zero;
  DateTime? _swStarted;
  int timerSecondsLeft = 0;
  Timer? _timerTick;
  int pomoWorkMin = 25;
  int pomoBreakMin = 5;
  bool pomoRunning = false;
  bool pomoOnBreak = false;
  int pomoLeftSec = 0;
  Timer? _pomoTick;
  String weatherText = '晴 · 22°C';
  DateTime? birthdayDate;
  final List<String> scheduleNotes = [];

  // home
  int homeCols = 8;
  int homeRows = 6;
  bool homeOutdoor = true;
  String homeTool = 'hoe'; // hoe plant water harvest chop fish flower shop
  late List<HomeCell> homeCells;
  String homeFarmLog = '';

  // games
  int collectScore = 0;
  int rhythmScore = 0;
  int typingScore = 0;
  int vocabStreak = 0;
  int exposeHits = 0;
  int limeWins = 0;

  // meet
  MeetFriendship friendship = MeetFriendship();
  String meetOsLine = '';

  // music resume
  Duration? musicResumePos;
  String? musicTrackId;
  bool musicPlaying = false;

  // work
  int workBoxesDone = 0;
  int workBoxesTarget = 5;
  bool workFlagOn = true;

  Future<void> init() async {
    homeCells = List.generate(homeCols * homeRows, (_) => HomeCell(kind: 'soil'));
    _prefs = await SharedPreferences.getInstance();
    await _load();
    lastOpenAt = DateTime.now();
    _dailyLoginGift();
    notifyListeners();
  }

  Future<void> _load() async {
    final p = _prefs;
    if (p == null) return;
    ownerName = p.getString('owner_name') ?? '';
    ownerSet = ownerName.isNotEmpty;
    sizeKey = p.getString('size_key') ?? '中';
    showSpeech = p.getBool('show_speech') ?? true;
    voiceEnabled = p.getBool('voice_enabled') ?? true;
    musicVolume = p.getDouble('music_volume') ?? 0.55;
    voiceVolume = p.getDouble('voice_volume') ?? 0.85;
    difficulty = p.getString('difficulty') ?? '中';
    companionAster = p.getBool('companion_aster') ?? false;
    companionMorvay = p.getBool('companion_morvay') ?? false;
    wearFlower = p.getBool('wear_flower') ?? false;
    outfitDecorId = p.getString('outfit_decor');
    stamina = p.getInt('stamina') ?? 80;
    mood = p.getInt('mood') ?? 80;
    final w = p.getString('wallet_json');
    if (w != null) {
      try {
        wallet = WalletState.fromJson(jsonDecode(w) as Map<String, dynamic>);
      } catch (_) {}
    }
    diaryPages
      ..clear()
      ..addAll(p.getStringList('diary_pages') ?? []);
    achievements
      ..clear()
      ..addAll(p.getStringList('achievements') ?? []);
    scheduleNotes
      ..clear()
      ..addAll(p.getStringList('schedule_notes') ?? []);
    final b = p.getString('birthday');
    if (b != null) birthdayDate = DateTime.tryParse(b);
    final fo = p.getString('first_open');
    if (fo != null) firstOpenAt = DateTime.tryParse(fo);
    final home = p.getString('home_json');
    if (home != null) {
      try {
        final j = jsonDecode(home) as Map<String, dynamic>;
        homeCols = (j['cols'] as num?)?.toInt() ?? 8;
        homeRows = (j['rows'] as num?)?.toInt() ?? 6;
        homeOutdoor = j['outdoor'] != false;
        final cells = (j['cells'] as List?) ?? [];
        homeCells = cells
            .map((e) => HomeCell.fromJson(Map<String, dynamic>.from(e as Map)))
            .toList();
        if (homeCells.length != homeCols * homeRows) {
          homeCells = List.generate(homeCols * homeRows, (_) => HomeCell(kind: 'soil'));
        }
      } catch (_) {}
    }
    final fri = p.getString('friendship_json');
    if (fri != null) {
      try {
        friendship = MeetFriendship.fromJson(jsonDecode(fri) as Map<String, dynamic>);
      } catch (_) {}
    }
  }

  Future<void> _save() async {
    final p = _prefs;
    if (p == null) return;
    await p.setString('owner_name', ownerName);
    await p.setString('size_key', sizeKey);
    await p.setBool('show_speech', showSpeech);
    await p.setBool('voice_enabled', voiceEnabled);
    await p.setDouble('music_volume', musicVolume);
    await p.setDouble('voice_volume', voiceVolume);
    await p.setString('difficulty', difficulty);
    await p.setBool('companion_aster', companionAster);
    await p.setBool('companion_morvay', companionMorvay);
    await p.setBool('wear_flower', wearFlower);
    if (outfitDecorId != null) await p.setString('outfit_decor', outfitDecorId!);
    await p.setInt('stamina', stamina);
    await p.setInt('mood', mood);
    await p.setString('wallet_json', jsonEncode(wallet.toJson()));
    await p.setStringList('diary_pages', diaryPages);
    await p.setStringList('achievements', achievements.toList());
    await p.setStringList('schedule_notes', scheduleNotes);
    if (birthdayDate != null) await p.setString('birthday', birthdayDate!.toIso8601String());
    if (firstOpenAt != null) await p.setString('first_open', firstOpenAt!.toIso8601String());
    await p.setString(
      'home_json',
      jsonEncode({
        'cols': homeCols,
        'rows': homeRows,
        'outdoor': homeOutdoor,
        'cells': homeCells.map((c) => c.toJson()).toList(),
      }),
    );
    await p.setString('friendship_json', jsonEncode(friendship.toJson()));
  }

  void _dailyLoginGift() {
    final p = _prefs;
    if (p == null) return;
    final today = DateTime.now().toIso8601String().substring(0, 10);
    final last = p.getString('login_gift_day');
    if (last != today) {
      wallet.gold += 1;
      p.setString('login_gift_day', today);
      unlockAchievement('daily_login');
      showBubble('今日登录礼 +1 金币');
    }
  }

  Future<void> setOwner(String name) async {
    ownerName = name.trim();
    if (ownerName.isEmpty) return;
    ownerSet = true;
    firstOpenAt ??= DateTime.now();
    await _save();
    showBubble('你好，$ownerName。我是伊得。');
    notifyListeners();
  }

  void setSize(String key) {
    if (!sizePresets.containsKey(key)) return;
    sizeKey = key;
    _save();
    notifyListeners();
  }

  void setMode(PetMode m) {
    mode = m;
    switch (m) {
      case PetMode.sleep:
        pose = PetPose.sleep;
        poseAsset = 'sleep1.png';
        showBubble('……晚安。');
      case PetMode.work:
        pose = PetPose.work;
        poseAsset = 'work_0.png';
        workBoxesDone = 0;
        showBubble('开始运送吧。');
      case PetMode.music:
        pose = PetPose.walk;
        poseAsset = 'walkleft1.png';
        musicPlaying = true;
        musicTrackId ??= 'bgm001';
        showBubble('听听音乐。');
      case PetMode.follow:
        pose = PetPose.walk;
        poseAsset = 'walkleft1.png';
      case PetMode.stroll:
        pose = PetPose.walk;
        poseAsset = 'walkleft1.png';
      case PetMode.free:
        pose = PetPose.stand;
        poseAsset = 'stand.png';
      case PetMode.game:
        break;
    }
    _save();
    notifyListeners();
  }

  void tickWalk() {
    if (dragging) return;
    if (mode == PetMode.sleep || mode == PetMode.work) return;
    if (mode == PetMode.free || mode == PetMode.stroll || mode == PetMode.follow || mode == PetMode.music) {
      pose = PetPose.walk;
      walkFrame = 1 - walkFrame;
      poseAsset = walkFrame == 0 ? 'walkleft1.png' : 'walkleft2.png';
      petX = (petX + 8 + _rng.nextInt(12)).clamp(0, 2000);
      if (_rng.nextDouble() < 0.08 && mode == PetMode.free) {
        tryRandomIdle();
      }
      notifyListeners();
    }
  }

  void tryRandomIdle() {
    final roll = _rng.nextInt(4);
    if (roll == 0) {
      poseAsset = 'happy.png';
      showBubble('忽然有点开心。');
    } else if (roll == 1) {
      poseAsset = 'hi1.png';
      showBubble('嗨。');
    } else {
      poseAsset = 'stand.png';
    }
    notifyListeners();
    Future.delayed(const Duration(milliseconds: 1600), () {
      if (mode == PetMode.free) {
        poseAsset = 'stand.png';
        notifyListeners();
      }
    });
  }

  void showBubble(String text, {int hideMs = 2800}) {
    if (!showSpeech) return;
    speechText = text;
    speechVisible = true;
    _speechHide?.cancel();
    _speechHide = Timer(Duration(milliseconds: hideMs), () {
      speechVisible = false;
      notifyListeners();
    });
    notifyListeners();
  }

  void playAction(String id) {
    final map = <String, String>{
      'eat': '吃东西……',
      'hi': '你好。',
      'call': '……喂？',
      'adult': '……这个还是算了。',
      'squat': '蹲一下。',
      'kick': '侧踢！',
      'yes': '是。',
      'no': '否。',
      'judge': '让我想想……',
      'walk': '走走。',
      'stand': '站好。',
      'sleep': '去睡一会儿。',
      'work': '去工作。',
    };
    if (id == 'hi') poseAsset = 'hi1.png';
    if (id == 'squat') poseAsset = 'squat.png';
    if (id == 'sleep') {
      setMode(PetMode.sleep);
      return;
    }
    if (id == 'work') {
      setMode(PetMode.work);
      return;
    }
    showBubble(map[id] ?? id);
    notifyListeners();
  }

  void playExpr(String id) {
    final map = <String, (String, String)>{
      'happy': ('happy.png', '开心～'),
      'angry': ('stand.png', '……有点生气。'),
      'question': ('stand.png', '？'),
      'sad': ('stand.png', '有点难过。'),
      'shy': ('shy1.png', '……'),
      'wink': ('wink.png', '眨眼。'),
      'like': ('stand.png', '点赞。'),
      'bixin': ('stand.png', '比心。'),
      'idea': ('stand.png', '有主意了！'),
      'speechless': ('stand.png', '……'),
      'awkward': ('stand.png', '好尴尬。'),
    };
    final v = map[id];
    if (v != null) {
      poseAsset = v.$1;
      showBubble(v.$2);
    }
    notifyListeners();
  }

  void playPresetDialog(String q, List<String> answers) {
    showBubble('「$q」', hideMs: 1600);
    Future.delayed(const Duration(milliseconds: 1700), () {
      final a = answers.isEmpty ? '……' : answers[_rng.nextInt(answers.length)];
      showBubble(a, hideMs: 3600);
    });
  }

  void feed(String foodId) {
    final have = wallet.items[foodId] ?? 0;
    if (have <= 0) {
      showBubble('没有这个食物。');
      return;
    }
    wallet.items[foodId] = have - 1;
    stamina = (stamina + 12).clamp(0, 100);
    mood = (mood + 8).clamp(0, 100);
    poseAsset = 'happy.png';
    showBubble('谢谢投喂。');
    unlockAchievement('first_feed');
    _save();
    notifyListeners();
  }

  void toggleCompanion(String id) {
    if (id == 'aster') companionAster = !companionAster;
    if (id == 'morvay') companionMorvay = !companionMorvay;
    showBubble(id == 'aster'
        ? (companionAster ? '艾斯特来了。' : '艾斯特回去了。')
        : (companionMorvay ? '墨菲来了。' : '墨菲回去了。'));
    _save();
    notifyListeners();
  }

  void setOutfit(String? id) {
    outfitDecorId = id;
    showBubble(id == null ? '卸下装扮。' : '换上了 $id');
    _save();
    notifyListeners();
  }

  void toggleFlower() {
    final n = wallet.items['flower_cut'] ?? 0;
    if (!wearFlower) {
      if (n <= 0) {
        showBubble('没有采下的花。');
        return;
      }
      wallet.items['flower_cut'] = n - 1;
      wearFlower = true;
      showBubble('戴上了小花。');
    } else {
      wallet.items['flower_cut'] = n + 1;
      wearFlower = false;
      showBubble('花已摘下。');
    }
    _save();
    notifyListeners();
  }

  void workDeliverBox() {
    if (mode != PetMode.work) return;
    workBoxesDone++;
    stamina = (stamina - 3).clamp(0, 100);
    showBubble('箱子 $workBoxesDone / $workBoxesTarget');
    if (workBoxesDone >= workBoxesTarget) {
      wallet.gold += 5;
      unlockAchievement('work_batch');
      showBubble('本趟运送完成，+5 金币');
      setMode(PetMode.free);
    }
    _save();
    notifyListeners();
  }

  // —— tools ——
  void toggleStopwatch() {
    if (stopwatchRunning) {
      stopwatchRunning = false;
      if (_swStarted != null) {
        stopwatchElapsed += DateTime.now().difference(_swStarted!);
      }
      _swStarted = null;
    } else {
      stopwatchRunning = true;
      _swStarted = DateTime.now();
    }
    notifyListeners();
  }

  void resetStopwatch() {
    stopwatchRunning = false;
    stopwatchElapsed = Duration.zero;
    _swStarted = null;
    notifyListeners();
  }

  Duration get stopwatchDisplay {
    if (stopwatchRunning && _swStarted != null) {
      return stopwatchElapsed + DateTime.now().difference(_swStarted!);
    }
    return stopwatchElapsed;
  }

  void startTimer(int seconds) {
    _timerTick?.cancel();
    timerSecondsLeft = seconds;
    _timerTick = Timer.periodic(const Duration(seconds: 1), (t) {
      timerSecondsLeft--;
      if (timerSecondsLeft <= 0) {
        t.cancel();
        timerSecondsLeft = 0;
        showBubble('计时结束。');
      }
      notifyListeners();
    });
    notifyListeners();
  }

  void startPomo({int? workMin, int? breakMin}) {
    pomoWorkMin = workMin ?? pomoWorkMin;
    pomoBreakMin = breakMin ?? pomoBreakMin;
    pomoRunning = true;
    pomoOnBreak = false;
    pomoLeftSec = pomoWorkMin * 60;
    setMode(PetMode.work);
    _pomoTick?.cancel();
    _pomoTick = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!pomoRunning) return;
      pomoLeftSec--;
      if (pomoLeftSec <= 0) {
        if (!pomoOnBreak) {
          pomoOnBreak = true;
          pomoLeftSec = pomoBreakMin * 60;
          setMode(PetMode.sleep);
          showBubble('番茄：休息');
        } else {
          pomoOnBreak = false;
          pomoLeftSec = pomoWorkMin * 60;
          setMode(PetMode.work);
          showBubble('番茄：继续工作');
        }
      }
      notifyListeners();
    });
    notifyListeners();
  }

  void stopPomo() {
    pomoRunning = false;
    _pomoTick?.cancel();
    setMode(PetMode.free);
    notifyListeners();
  }

  void refreshWeather() {
    const opts = ['晴 · 22°C', '多云 · 20°C', '小雨 · 18°C', '阴 · 19°C'];
    weatherText = opts[_rng.nextInt(opts.length)];
    showBubble('天气：$weatherText');
    notifyListeners();
  }

  void setBirthday(DateTime d) {
    birthdayDate = d;
    _save();
    showBubble('已设定生日 ${d.month}/${d.day}');
    notifyListeners();
  }

  void addSchedule(String note) {
    scheduleNotes.add(note);
    _save();
    notifyListeners();
  }

  // —— home farm ——
  void homeUseTool(int index) {
    if (index < 0 || index >= homeCells.length) return;
    final c = homeCells[index];
    switch (homeTool) {
      case 'hoe':
        c.kind = 'soil';
        c.cropId = null;
        c.growth = 0;
        homeFarmLog = '锄地';
      case 'plant':
        if (c.kind == 'soil' && (wallet.items['seed_wheat'] ?? 0) > 0) {
          wallet.items['seed_wheat'] = (wallet.items['seed_wheat'] ?? 0) - 1;
          c.kind = 'crop';
          c.cropId = 'wheat';
          c.growth = 5;
          homeFarmLog = '播种小麦';
        }
      case 'water':
        if (c.kind == 'crop' && c.waterToday < 2) {
          c.waterToday++;
          c.growth = (c.growth + 10).clamp(0, 100);
          homeFarmLog = '浇水';
        }
      case 'harvest':
        if (c.kind == 'crop' && c.growth >= 100) {
          wallet.items['wheat'] = (wallet.items['wheat'] ?? 0) + 1;
          wallet.gold += 2;
          c.kind = 'soil';
          c.cropId = null;
          c.growth = 0;
          homeFarmLog = '收获 +1 小麦 +2 金';
          unlockAchievement('first_harvest');
        }
      case 'chop':
        c.kind = 'empty';
        wallet.items['wood'] = (wallet.items['wood'] ?? 0) + 1;
        homeFarmLog = '砍树 +1 木材';
      case 'fish':
        wallet.gold += 1;
        homeFarmLog = '钓鱼 +1 金';
      case 'flower':
        wallet.items['flower_cut'] = (wallet.items['flower_cut'] ?? 0) + 1;
        homeFarmLog = '采花';
      case 'shop':
        if (wallet.gold >= 3) {
          wallet.gold -= 3;
          wallet.items['seed_wheat'] = (wallet.items['seed_wheat'] ?? 0) + 2;
          homeFarmLog = '商店：种子×2';
        } else {
          homeFarmLog = '金币不足';
        }
    }
    _save();
    notifyListeners();
  }

  void homeGrowTick() {
    for (final c in homeCells) {
      if (c.kind == 'crop') {
        final mul = c.waterToday > 0 ? 2.0 : 1.0;
        c.growth = (c.growth + 5 * mul).clamp(0, 100);
      }
    }
    notifyListeners();
  }

  // —— games ——
  void finishCollect(int score) {
    collectScore = score;
    final gold = (score / 5).floor().clamp(1, 30);
    wallet.gold += gold;
    showBubble('采集结束 +$gold 金');
    if (score < 10) showBubble('好痛……（hurt）');
    unlockAchievement('collect_play');
    setMode(PetMode.free);
    _save();
    notifyListeners();
  }

  void finishRhythm(int score) {
    rhythmScore = score;
    final gold = (score / 100).floor().clamp(1, 40);
    wallet.gold += gold;
    showBubble('音游结算 +$gold 金');
    setMode(PetMode.free);
    _save();
    notifyListeners();
  }

  void finishTyping(int score) {
    typingScore = score;
    wallet.gold += (score / 10).floor().clamp(1, 20);
    setMode(PetMode.free);
    _save();
    notifyListeners();
  }

  void vocabAnswer(bool correct) {
    if (correct) {
      vocabStreak++;
      wallet.gold += 1;
      showBubble('答对了！连击 $vocabStreak');
    } else {
      vocabStreak = 0;
      showBubble('再想想……');
    }
    _save();
    notifyListeners();
  }

  void finishExpose(int hits) {
    exposeHits = hits;
    if (hits >= 3) {
      wallet.gold += 5;
      showBubble('暴露成功');
    } else {
      showBubble('暴露失败……');
    }
    setMode(PetMode.free);
    _save();
    notifyListeners();
  }

  void limeFight(bool win) {
    if (win) {
      limeWins++;
      wallet.gold += 3;
      showBubble('莱姆战胜利');
      unlockAchievement('lime_win');
    } else {
      showBubble('莱姆战失败');
    }
    _save();
    notifyListeners();
  }

  void addDiary(String text) {
    diaryPages.insert(0, text);
    _save();
    notifyListeners();
  }

  void unlockAchievement(String id) {
    if (achievements.add(id)) {
      showBubble('成就：$id');
      _save();
    }
  }

  // —— meet ——
  void recordMeet() {
    friendship.meetCount++;
    friendship.points += 1.5;
    if (friendship.meetCount == 1) {
      meetOsLine = '';
      showBubble('（第一次遇见……先记下来。）', hideMs: 2000);
    } else if (friendship.meetCount <= 10) {
      const lines = [
        '好像在哪见过……',
        '又碰到了。',
        '有点眼熟呢。',
        '今天也是你。',
        '嗯，记得你。',
      ];
      meetOsLine = '（${lines[_rng.nextInt(lines.length)]}）';
      showBubble(meetOsLine, hideMs: 2200);
    } else {
      meetOsLine = '';
      showBubble('（可以好好打个招呼了。）');
    }
    _save();
    notifyListeners();
  }

  // —— music resume ——
  void captureMusicPos(Duration pos) {
    musicResumePos = pos;
  }

  Duration consumeMusicResume() {
    final p = musicResumePos ?? Duration.zero;
    musicResumePos = null;
    return p;
  }

  Future<void> resetKeepOwner() async {
    final keep = ownerName;
    final fo = firstOpenAt;
    final p = _prefs;
    await p?.clear();
    ownerName = keep;
    ownerSet = keep.isNotEmpty;
    firstOpenAt = fo;
    wallet = WalletState();
    stamina = 80;
    mood = 80;
    diaryPages.clear();
    achievements.clear();
    homeCells = List.generate(homeCols * homeRows, (_) => HomeCell(kind: 'soil'));
    friendship = MeetFriendship();
    await _save();
    showBubble('已重置（所属人保留）');
    notifyListeners();
  }

  int get companionDays {
    final fo = firstOpenAt;
    if (fo == null) return 0;
    return DateTime.now().difference(fo).inDays;
  }

  void bump() => notifyListeners();

  Future<void> persist() => _save();
}
