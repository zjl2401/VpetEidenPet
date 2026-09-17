import 'dart:convert';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import '../audio/media_hub.dart';
import '../core/pet_controller.dart';

Future<void> openFeaturePage(BuildContext context, String id) async {
  final Widget page = switch (id) {
    'feed' => const FeedPage(),
    'outfit' => const OutfitPage(),
    'stopwatch' => const StopwatchPage(),
    'timer' => const TimerPage(),
    'pomo' => const PomoPage(),
    'schedule' => const SchedulePage(),
    'birthday' => const BirthdayPage(),
    'clock' => const ClockPage(),
    'collect' => const CollectGamePage(),
    'rhythm' => const RhythmGamePage(),
    'expose' => const ExposeGamePage(),
    'lime' => const LimeGamePage(),
    'typing' => const TypingGamePage(),
    'vocab' => const VocabGamePage(),
    'rpg' => const RpgStubPage(),
    'home' => const HomeFarmPage(),
    'owner' => const OwnerPage(),
    'size' => const SizePage(),
    'volume' => const VolumePage(),
    'difficulty' => const DifficultyPage(),
    'diary' => const DiaryPage(),
    'achievements' => const AchievementsPage(),
    'gallery' => const GalleryPage(),
    'phonograph' => const PhonographPage(),
    'community' => const CommunityPage(),
    'reset' => const ResetPage(),
    _ => Scaffold(appBar: AppBar(title: Text(id)), body: Center(child: Text('未实现: $id'))),
  };
  await Navigator.of(context).push(MaterialPageRoute(builder: (_) => page));
}

// ——— interact ———

class FeedPage extends StatelessWidget {
  const FeedPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    final foods = pet.wallet.items.entries.where((e) => e.value > 0).toList();
    return Scaffold(
      appBar: AppBar(title: const Text('喂食')),
      body: ListView(
        children: [
          for (final e in foods)
            ListTile(
              title: Text(e.key),
              subtitle: Text('×${e.value}'),
              trailing: FilledButton(
                onPressed: () => pet.feed(e.key),
                child: const Text('喂'),
              ),
            ),
          if (foods.isEmpty) const ListTile(title: Text('背包空空')),
          ListTile(
            title: Text('金币 ${pet.wallet.gold}'),
            trailing: TextButton(
              onPressed: () {
                if (pet.wallet.gold >= 2) {
                  pet.wallet.gold -= 2;
                  pet.wallet.items['bread'] = (pet.wallet.items['bread'] ?? 0) + 1;
                  pet.showBubble('买了面包');
                  pet.persist();
                  pet.bump();
                }
              },
              child: const Text('买面包 -2'),
            ),
          ),
        ],
      ),
    );
  }
}

class OutfitPage extends StatelessWidget {
  const OutfitPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    const outfits = ['default', 'scarf', 'hat', 'glasses'];
    return Scaffold(
      appBar: AppBar(title: const Text('装扮')),
      body: ListView(
        children: [
          SwitchListTile(
            title: const Text('戴花'),
            value: pet.wearFlower,
            onChanged: (_) => pet.toggleFlower(),
          ),
          for (final o in outfits)
            ListTile(
              title: Text(o),
              selected: pet.outfitDecorId == o,
              onTap: () => pet.setOutfit(o == 'default' ? null : o),
            ),
        ],
      ),
    );
  }
}

// ——— tools ———

class StopwatchPage extends StatelessWidget {
  const StopwatchPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    final d = pet.stopwatchDisplay;
    final text =
        '${d.inHours.toString().padLeft(2, '0')}:${(d.inMinutes % 60).toString().padLeft(2, '0')}:${(d.inSeconds % 60).toString().padLeft(2, '0')}';
    return Scaffold(
      appBar: AppBar(title: const Text('秒表')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(text, style: Theme.of(context).textTheme.displayMedium),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                FilledButton(
                  onPressed: pet.toggleStopwatch,
                  child: Text(pet.stopwatchRunning ? '暂停' : '开始'),
                ),
                const SizedBox(width: 12),
                OutlinedButton(onPressed: pet.resetStopwatch, child: const Text('复位')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class TimerPage extends StatefulWidget {
  const TimerPage({super.key});
  @override
  State<TimerPage> createState() => _TimerPageState();
}

class _TimerPageState extends State<TimerPage> {
  int minutes = 5;
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('计时器')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text('剩余 ${pet.timerSecondsLeft}s', style: Theme.of(context).textTheme.headlineMedium),
            Slider(
              value: minutes.toDouble(),
              min: 1,
              max: 60,
              divisions: 59,
              label: '$minutes 分',
              onChanged: (v) => setState(() => minutes = v.round()),
            ),
            FilledButton(
              onPressed: () => pet.startTimer(minutes * 60),
              child: const Text('开始'),
            ),
          ],
        ),
      ),
    );
  }
}

class PomoPage extends StatelessWidget {
  const PomoPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('番茄钟')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text(
              pet.pomoRunning
                  ? '${pet.pomoOnBreak ? '休息' : '专注'} ${pet.pomoLeftSec ~/ 60}:${(pet.pomoLeftSec % 60).toString().padLeft(2, '0')}'
                  : '未开始',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 16),
            FilledButton(onPressed: () => pet.startPomo(), child: const Text('25/5 开始')),
            TextButton(onPressed: pet.stopPomo, child: const Text('停止')),
          ],
        ),
      ),
    );
  }
}

class SchedulePage extends StatefulWidget {
  const SchedulePage({super.key});
  @override
  State<SchedulePage> createState() => _SchedulePageState();
}

class _SchedulePageState extends State<SchedulePage> {
  final _ctl = TextEditingController();
  @override
  void dispose() {
    _ctl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('日程')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(child: TextField(controller: _ctl, decoration: const InputDecoration(hintText: '新日程'))),
                IconButton(
                  onPressed: () {
                    if (_ctl.text.trim().isEmpty) return;
                    pet.addSchedule(_ctl.text.trim());
                    _ctl.clear();
                  },
                  icon: const Icon(Icons.add),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView(
              children: [for (final n in pet.scheduleNotes) ListTile(title: Text(n))],
            ),
          ),
        ],
      ),
    );
  }
}

class BirthdayPage extends StatelessWidget {
  const BirthdayPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('生日')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(pet.birthdayDate == null
                ? '未设定'
                : '${pet.birthdayDate!.year}-${pet.birthdayDate!.month}-${pet.birthdayDate!.day}'),
            FilledButton(
              onPressed: () async {
                final now = DateTime.now();
                final d = await showDatePicker(
                  context: context,
                  firstDate: DateTime(1970),
                  lastDate: DateTime(now.year + 1),
                  initialDate: pet.birthdayDate ?? now,
                );
                if (d != null) pet.setBirthday(d);
              },
              child: const Text('选择日期'),
            ),
          ],
        ),
      ),
    );
  }
}

class ClockPage extends StatelessWidget {
  const ClockPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('时间显示')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.asset('assets/sprites/${pet.poseAsset}', height: 120, errorBuilder: (_, __, ___) => const Icon(Icons.pets, size: 80)),
            const SizedBox(height: 12),
            StreamBuilder(
              stream: Stream.periodic(const Duration(seconds: 1)),
              builder: (_, __) {
                final n = DateTime.now();
                return Text(
                  '${n.hour.toString().padLeft(2, '0')}:${n.minute.toString().padLeft(2, '0')}:${n.second.toString().padLeft(2, '0')}',
                  style: Theme.of(context).textTheme.displaySmall,
                );
              },
            ),
            Text('天气 ${pet.weatherText}'),
          ],
        ),
      ),
    );
  }
}

// ——— games ———

class CollectGamePage extends StatefulWidget {
  const CollectGamePage({super.key});
  @override
  State<CollectGamePage> createState() => _CollectGamePageState();
}

class _CollectGamePageState extends State<CollectGamePage> {
  int score = 0;
  final rng = Random();
  late List<Offset> nodes;

  @override
  void initState() {
    super.initState();
    context.read<PetController>().setMode(PetMode.game);
    nodes = List.generate(8, (_) => Offset(rng.nextDouble(), rng.nextDouble()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('采集 · $score')),
      body: LayoutBuilder(
        builder: (context, c) {
          return Stack(
            children: [
              for (var i = 0; i < nodes.length; i++)
                Positioned(
                  left: nodes[i].dx * (c.maxWidth - 48),
                  top: nodes[i].dy * (c.maxHeight - 48),
                  child: GestureDetector(
                    onTap: () {
                      setState(() {
                        score++;
                        nodes[i] = Offset(rng.nextDouble(), rng.nextDouble());
                      });
                    },
                    child: const Icon(Icons.grass, size: 40, color: Colors.green),
                  ),
                ),
              Positioned(
                bottom: 24,
                left: 0,
                right: 0,
                child: Center(
                  child: FilledButton(
                    onPressed: () {
                      context.read<PetController>().finishCollect(score);
                      if (score < 5) {
                        context.read<MediaHub>().playVoiceCategory('hurt');
                      }
                      Navigator.pop(context);
                    },
                    child: const Text('结算'),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class RhythmGamePage extends StatefulWidget {
  const RhythmGamePage({super.key});
  @override
  State<RhythmGamePage> createState() => _RhythmGamePageState();
}

class _RhythmGamePageState extends State<RhythmGamePage> {
  int score = 0;
  int beat = 0;

  @override
  void initState() {
    super.initState();
    context.read<PetController>().setMode(PetMode.game);
    context.read<MediaHub>().startBgm();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('音游 · $score')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('节拍 $beat', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 16),
            Wrap(
              spacing: 12,
              children: [
                for (final lane in ['A', 'B', 'C', 'D'])
                  ElevatedButton(
                    onPressed: () => setState(() {
                      score += 50;
                      beat++;
                    }),
                    child: Text(lane),
                  ),
              ],
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: () async {
                await context.read<MediaHub>().pauseBgmCapture();
                if (!context.mounted) return;
                context.read<PetController>().finishRhythm(score);
                await context.read<MediaHub>().startBgm(fromResume: true);
                if (context.mounted) Navigator.pop(context);
              },
              child: const Text('结算并续播 BGM'),
            ),
          ],
        ),
      ),
    );
  }
}

class ExposeGamePage extends StatefulWidget {
  const ExposeGamePage({super.key});
  @override
  State<ExposeGamePage> createState() => _ExposeGamePageState();
}

class _ExposeGamePageState extends State<ExposeGamePage> {
  int hits = 0;
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('暴露 QTE')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('连击 $hits / 5'),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () => setState(() => hits++),
              child: const Text('时机！'),
            ),
            TextButton(
              onPressed: () {
                context.read<PetController>().finishExpose(hits);
                Navigator.pop(context);
              },
              child: const Text('结束'),
            ),
          ],
        ),
      ),
    );
  }
}

class LimeGamePage extends StatelessWidget {
  const LimeGamePage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.read<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('莱姆')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('选择行动'),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: () {
                pet.limeFight(Random().nextBool());
                Navigator.pop(context);
              },
              child: const Text('战斗'),
            ),
          ],
        ),
      ),
    );
  }
}

class TypingGamePage extends StatefulWidget {
  const TypingGamePage({super.key});
  @override
  State<TypingGamePage> createState() => _TypingGamePageState();
}

class _TypingGamePageState extends State<TypingGamePage> {
  final target = 'eiden loves quiet nights';
  final ctl = TextEditingController();
  int score = 0;

  @override
  void dispose() {
    ctl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('打字')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text(target, style: Theme.of(context).textTheme.titleLarge),
            TextField(
              controller: ctl,
              onChanged: (v) {
                if (v == target) {
                  score = 100;
                  context.read<PetController>().finishTyping(score);
                  Navigator.pop(context);
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}

class VocabGamePage extends StatefulWidget {
  const VocabGamePage({super.key});
  @override
  State<VocabGamePage> createState() => _VocabGamePageState();
}

class _VocabGamePageState extends State<VocabGamePage> {
  List<Map<String, String>> words = [];
  int idx = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final raw = await rootBundle.loadString('assets/data/vocab_en.json');
      final list = (jsonDecode(raw) as List).cast<Map<String, dynamic>>();
      setState(() {
        words = list.map((e) => {'en': '${e['en']}', 'zh': '${e['zh']}'}).toList();
      });
    } catch (_) {
      words = [
        {'en': 'apple', 'zh': '苹果'},
        {'en': 'moon', 'zh': '月亮'},
      ];
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    if (words.isEmpty) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final w = words[idx % words.length];
    final opts = [...words]..shuffle();
    return Scaffold(
      appBar: AppBar(title: const Text('背单词')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text(w['en']!, style: Theme.of(context).textTheme.displaySmall),
            const SizedBox(height: 24),
            for (final o in opts.take(3))
              ListTile(
                title: Text(o['zh']!),
                onTap: () {
                  final ok = o['zh'] == w['zh'];
                  context.read<PetController>().vocabAnswer(ok);
                  setState(() => idx++);
                },
              ),
          ],
        ),
      ),
    );
  }
}

class RpgStubPage extends StatelessWidget {
  const RpgStubPage({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Silent Oath（应用内）')),
      body: const Padding(
        padding: EdgeInsets.all(24),
        child: Text(
          '桌面版 Silent Oath 为独立进程；手机版在应用内嵌套入口。\n'
          '当前为可玩占位：探索 → 战斗结算进钱包。后续可换完整剧情资源。',
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          final pet = context.read<PetController>();
          pet.wallet.gold += 8;
          pet.unlockAchievement('rpg_enter');
          pet.showBubble('冒险收获 +8 金');
          pet.persist();
          pet.bump();
          Navigator.pop(context);
        },
        label: const Text('探索一局'),
      ),
    );
  }
}

// ——— home ———

class HomeFarmPage extends StatelessWidget {
  const HomeFarmPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    const tools = [
      ('hoe', '锄'),
      ('plant', '种'),
      ('water', '浇'),
      ('harvest', '收'),
      ('chop', '砍'),
      ('fish', '钓'),
      ('flower', '花'),
      ('shop', '店'),
    ];
    return Scaffold(
      appBar: AppBar(
        title: Text(pet.homeOutdoor ? '家园·户外' : '家园·室内'),
        actions: [
          TextButton(
            onPressed: () {
              pet.homeOutdoor = !pet.homeOutdoor;
              pet.bump();
            },
            child: Text(pet.homeOutdoor ? '进室内' : '去户外'),
          ),
        ],
      ),
      body: Column(
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.all(8),
            child: Row(
              children: [
                for (final t in tools)
                  Padding(
                    padding: const EdgeInsets.only(right: 6),
                    child: ChoiceChip(
                      label: Text(t.$2),
                      selected: pet.homeTool == t.$1,
                      onSelected: (_) {
                        pet.homeTool = t.$1;
                        pet.bump();
                      },
                    ),
                  ),
              ],
            ),
          ),
          if (pet.homeFarmLog.isNotEmpty) Text(pet.homeFarmLog),
          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.all(8),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 8,
                mainAxisSpacing: 2,
                crossAxisSpacing: 2,
              ),
              itemCount: pet.homeCells.length,
              itemBuilder: (_, i) {
                final c = pet.homeCells[i];
                Color color = Colors.brown.shade200;
                if (c.kind == 'crop') {
                  color = Color.lerp(Colors.lightGreen.shade200, Colors.green.shade700, c.growth / 100)!;
                } else if (c.kind == 'empty') {
                  color = Colors.grey.shade300;
                }
                return GestureDetector(
                  onTap: () => pet.homeUseTool(i),
                  child: Container(
                    color: color,
                    alignment: Alignment.center,
                    child: c.kind == 'crop' ? Text('${c.growth.round()}', style: const TextStyle(fontSize: 8)) : null,
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

// ——— system ———

class OwnerPage extends StatelessWidget {
  const OwnerPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('所属人')),
      body: ListTile(
        title: Text(pet.ownerName),
        subtitle: Text('陪伴 ${pet.companionDays} 天'),
      ),
    );
  }
}

class SizePage extends StatelessWidget {
  const SizePage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('大小')),
      body: ListView(
        children: [
          for (final k in sizePresets.keys)
            RadioListTile<String>(
              title: Text(k),
              value: k,
              groupValue: pet.sizeKey,
              onChanged: (v) {
                if (v != null) pet.setSize(v);
              },
            ),
        ],
      ),
    );
  }
}

class VolumePage extends StatelessWidget {
  const VolumePage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    final media = context.read<MediaHub>();
    return Scaffold(
      appBar: AppBar(title: const Text('音量')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            SwitchListTile(
              title: const Text('语音'),
              value: pet.voiceEnabled,
              onChanged: (v) {
                pet.voiceEnabled = v;
                pet.persist();
                pet.bump();
              },
            ),
            Text('音乐 ${(pet.musicVolume * 100).round()}%'),
            Slider(
              value: pet.musicVolume,
              onChanged: (v) {
                pet.musicVolume = v;
                media.applyVolumes();
                pet.bump();
              },
              onChangeEnd: (_) => pet.persist(),
            ),
            Text('语音 ${(pet.voiceVolume * 100).round()}%'),
            Slider(
              value: pet.voiceVolume,
              onChanged: (v) {
                pet.voiceVolume = v;
                media.applyVolumes();
                pet.bump();
              },
              onChangeEnd: (_) => pet.persist(),
            ),
          ],
        ),
      ),
    );
  }
}

class DifficultyPage extends StatelessWidget {
  const DifficultyPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('难度')),
      body: Column(
        children: [
          for (final d in ['低', '中', '高'])
            RadioListTile<String>(
              title: Text(d),
              value: d,
              groupValue: pet.difficulty,
              onChanged: (v) {
                pet.difficulty = v ?? '中';
                pet.persist();
                pet.bump();
              },
            ),
        ],
      ),
    );
  }
}

class DiaryPage extends StatefulWidget {
  const DiaryPage({super.key});
  @override
  State<DiaryPage> createState() => _DiaryPageState();
}

class _DiaryPageState extends State<DiaryPage> {
  final ctl = TextEditingController();
  @override
  void dispose() {
    ctl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('日记')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(child: TextField(controller: ctl)),
                IconButton(
                  onPressed: () {
                    if (ctl.text.trim().isEmpty) return;
                    pet.addDiary(ctl.text.trim());
                    ctl.clear();
                  },
                  icon: const Icon(Icons.send),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView(children: [for (final p in pet.diaryPages) ListTile(title: Text(p))]),
          ),
        ],
      ),
    );
  }
}

class AchievementsPage extends StatelessWidget {
  const AchievementsPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('成就')),
      body: ListView(
        children: [
          if (pet.achievements.isEmpty) const ListTile(title: Text('暂无')),
          for (final a in pet.achievements) ListTile(leading: const Icon(Icons.emoji_events), title: Text(a)),
        ],
      ),
    );
  }
}

class GalleryPage extends StatelessWidget {
  const GalleryPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('画廊')),
      body: GridView.count(
        crossAxisCount: 2,
        children: [
          for (final t in pet.galleryTitles)
            Card(
              child: Center(child: Text(t)),
            ),
        ],
      ),
    );
  }
}

class PhonographPage extends StatelessWidget {
  const PhonographPage({super.key});
  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(title: const Text('留声机')),
      body: ListView(
        children: [
          for (final c in pet.phonographClips)
            ListTile(
              title: Text(c['title']!),
              trailing: const Icon(Icons.play_arrow),
              onTap: () => context.read<MediaHub>().playVoiceCategory(c['id']!),
            ),
        ],
      ),
    );
  }
}

class CommunityPage extends StatelessWidget {
  const CommunityPage({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('社区说明')),
      body: const Padding(
        padding: EdgeInsets.all(24),
        child: Text(
          '投稿与反馈请通过应用商店评价或项目社区渠道。\n'
          '桌面版 exe 旁 zip 投稿在手机上对应应用内「相册投稿」入口（后续版本开放）。',
        ),
      ),
    );
  }
}

class ResetPage extends StatelessWidget {
  const ResetPage({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('重置')),
      body: Center(
        child: FilledButton(
          onPressed: () async {
            final ok = await showDialog<bool>(
              context: context,
              builder: (ctx) => AlertDialog(
                title: const Text('确认重置？'),
                content: const Text('将清空经济/家园/成就等，保留所属人名字。'),
                actions: [
                  TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('取消')),
                  FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('重置')),
                ],
              ),
            );
            if (ok == true && context.mounted) {
              await context.read<PetController>().resetKeepOwner();
              if (context.mounted) Navigator.pop(context);
            }
          },
          child: const Text('重置存档（保留所属人）'),
        ),
      ),
    );
  }
}
