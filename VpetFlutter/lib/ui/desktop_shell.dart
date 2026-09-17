import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../audio/media_hub.dart';
import '../core/menu_catalog.dart';
import '../core/pet_controller.dart';
import '../meet/meet_presence.dart';
import '../platform/overlay_bridge.dart';
import 'feature_pages.dart';
import 'pet_stage.dart';

/// Main app shell: in-app pet stage + four root menus + feature routes.
class DesktopShell extends StatefulWidget {
  const DesktopShell({super.key});

  @override
  State<DesktopShell> createState() => _DesktopShellState();
}

class _DesktopShellState extends State<DesktopShell> {
  Timer? _walkTimer;
  Timer? _homeGrow;
  final List<MenuNode> _stack = [];

  @override
  void initState() {
    super.initState();
    _walkTimer = Timer.periodic(const Duration(milliseconds: 480), (_) {
      context.read<PetController>().tickWalk();
    });
    _homeGrow = Timer.periodic(const Duration(seconds: 12), (_) {
      context.read<PetController>().homeGrowTick();
    });
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrapOverlay());
  }

  Future<void> _bootstrapOverlay() async {
    final pet = context.read<PetController>();
    final overlay = context.read<OverlayBridge>();
    if (Platform.isAndroid) {
      final ok = await overlay.canDrawOverlays();
      if (!ok && mounted) {
        final go = await showDialog<bool>(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('悬浮窗权限'),
            content: const Text('关闭 App 后仍要看到伊得，需要授予「显示在其他应用上层」。'),
            actions: [
              TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('稍后')),
              FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('去开启')),
            ],
          ),
        );
        if (go == true) await overlay.requestPermission();
      }
      await overlay.startOverlay();
      pet.overlayRunning = true;
    } else if (Platform.isIOS) {
      await overlay.startPipKeepAlive();
    }
  }

  @override
  void dispose() {
    _walkTimer?.cancel();
    _homeGrow?.cancel();
    super.dispose();
  }

  MenuNode? get _current => _stack.isEmpty ? null : _stack.last;

  List<MenuNode> get _visibleChildren {
    if (_stack.isEmpty) return rootMenus;
    return _current!.children;
  }

  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    return Scaffold(
      appBar: AppBar(
        title: Text('伊得 · ${pet.ownerName}'),
        actions: [
          IconButton(
            tooltip: '语音打招呼',
            onPressed: () => context.read<MediaHub>().playVoiceCategory('yuqi', force: true),
            icon: const Icon(Icons.record_voice_over_outlined),
          ),
          IconButton(
            tooltip: Platform.isAndroid ? '重启悬浮' : 'PiP 保活',
            onPressed: () async {
              final o = context.read<OverlayBridge>();
              if (Platform.isAndroid) {
                await o.startOverlay();
                pet.showBubble('悬浮已启动');
              } else {
                await o.startPipKeepAlive();
                pet.showBubble('已请求 PiP 保活');
              }
            },
            icon: const Icon(Icons.picture_in_picture_alt_outlined),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            flex: 3,
            child: PetStage(
              onTapPet: () {
                setState(() {
                  _stack.clear();
                });
              },
            ),
          ),
          _statusBar(pet),
          Expanded(
            flex: 2,
            child: _menuPanel(context),
          ),
        ],
      ),
    );
  }

  Widget _statusBar(PetController pet) {
    return Material(
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(
          children: [
            Text('金 ${pet.wallet.gold}'),
            const SizedBox(width: 12),
            Text('体 ${pet.stamina}'),
            const SizedBox(width: 12),
            Text('心 ${pet.mood}'),
            const Spacer(),
            Text('${pet.mode.name} · ${pet.sizeKey}'),
          ],
        ),
      ),
    );
  }

  Widget _menuPanel(BuildContext context) {
    final title = _stack.isEmpty ? '四大菜单' : _stack.map((e) => e.title).join(' › ');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
          child: Row(
            children: [
              if (_stack.isNotEmpty)
                IconButton(
                  onPressed: () => setState(() => _stack.removeLast()),
                  icon: const Icon(Icons.arrow_back),
                ),
              Expanded(child: Text(title, style: Theme.of(context).textTheme.titleMedium)),
            ],
          ),
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.all(8),
            children: [
              for (final n in _visibleChildren)
                Card(
                  child: ListTile(
                    title: Text(n.title),
                    trailing: n.isLeaf ? null : const Icon(Icons.chevron_right),
                    onTap: () => _onNode(context, n),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }

  Future<void> _onNode(BuildContext context, MenuNode n) async {
    if (!n.isLeaf) {
      setState(() => _stack.add(n));
      return;
    }
    final action = n.action;
    if (action == null) return;
    await dispatchMenuAction(context, action);
  }
}

Future<void> dispatchMenuAction(BuildContext context, String action) async {
  final pet = context.read<PetController>();
  final media = context.read<MediaHub>();
  final overlay = context.read<OverlayBridge>();

  if (action.startsWith('action:')) {
    final id = action.substring(7);
    pet.playAction(id);
    if (id == 'hi' || id == 'call') {
      await media.playVoiceCategory(id == 'hi' ? 'yuqi' : 'normal', force: true);
    }
    return;
  }
  if (action.startsWith('expr:')) {
    pet.playExpr(action.substring(5));
    return;
  }
  if (action.startsWith('dialog:')) {
    final key = action.substring(7);
    final map = <String, (String, List<String>)>{
      'today': ('今天怎么样？', ['还不错。', '有你在就很好。']),
      'story': ('想听故事吗？', ['……那就听一会儿。', '下次吧。']),
      'tired': ('累不累？', ['有一点。', '还撑得住。']),
    };
    final v = map[key];
    if (v != null) pet.playPresetDialog(v.$1, v.$2);
    return;
  }
  if (action.startsWith('companion:')) {
    pet.toggleCompanion(action.substring(10));
    return;
  }
  if (action.startsWith('mode:')) {
    final m = action.substring(5);
    switch (m) {
      case 'free':
        pet.setMode(PetMode.free);
        await media.stopBgm();
      case 'stroll':
        pet.setMode(PetMode.stroll);
      case 'follow':
        pet.setMode(PetMode.follow);
      case 'sleep':
        pet.setMode(PetMode.sleep);
        await media.playVoiceCategory('sleep');
      case 'work':
        pet.setMode(PetMode.work);
        await media.playVoiceCategory('work');
      case 'music':
        await media.startBgm();
    }
    return;
  }
  if (action == 'toggle:speech') {
    pet.showSpeech = !pet.showSpeech;
    pet.showBubble(pet.showSpeech ? '气泡已开' : '气泡已关');
    pet.persist();
    return;
  }
  if (action == 'tool:weather') {
    pet.refreshWeather();
    return;
  }
  if (action == 'meet:now') {
    final presence = MeetPresence(displayName: pet.ownerName.isEmpty ? '伊得' : pet.ownerName);
    await presence.ensureId();
    final peer = await presence.simulatePeer();
    pet.recordMeet();
    pet.showBubble('遇见了 ${peer['name']}');
    return;
  }
  if (action == 'sys:exit_overlay') {
    await overlay.stopOverlay();
    await overlay.stopPipKeepAlive();
    pet.overlayRunning = false;
    pet.showBubble('已退出悬浮/PiP');
    return;
  }
  if (action.startsWith('nav:')) {
    await openFeaturePage(context, action.substring(4));
  }
}
