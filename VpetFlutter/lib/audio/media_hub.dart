import 'dart:async';
import 'dart:convert';

import 'package:audio_session/audio_session.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:just_audio/just_audio.dart';

import '../core/pet_controller.dart';

/// Voice + BGM hub with interrupt → resume-from-position (desktop parity).
class MediaHub extends ChangeNotifier {
  MediaHub(this.pet);

  final PetController pet;
  final AudioPlayer _bgm = AudioPlayer();
  final AudioPlayer _voice = AudioPlayer();

  bool _ready = false;
  List<String> _bgmAssets = [];
  int _bgmIndex = 0;
  DateTime? _voiceCooldownUntil;
  bool _voiceBusy = false;

  bool get ready => _ready;
  bool get bgmPlaying => _bgm.playing;
  Duration get bgmPosition => _bgm.position;

  Future<void> init() async {
    try {
      final session = await AudioSession.instance;
      await session.configure(const AudioSessionConfiguration.music());
      _bgmAssets = await _listAssetPrefix('assets/music/');
      if (_bgmAssets.isEmpty) {
        _bgmAssets = [
          for (var i = 1; i <= 7; i++)
            'assets/music/BGM/pluviasilvae - BGM00$i.mp3',
        ];
      }
      _bgm.playerStateStream.listen((s) {
        pet.musicPlaying = s.playing;
        notifyListeners();
      });
      _ready = true;
    } catch (e) {
      debugPrint('MediaHub init: $e');
      _ready = true;
    }
    notifyListeners();
  }

  Future<List<String>> _listAssetPrefix(String prefix) async {
    try {
      final raw = await rootBundle.loadString('AssetManifest.json');
      final map = jsonDecode(raw) as Map<String, dynamic>;
      return map.keys.where((p) => p.startsWith(prefix) && !p.endsWith('.gitkeep')).toList()
        ..sort();
    } catch (_) {
      try {
        final manifest = await AssetManifest.loadFromAssetBundle(rootBundle);
        return manifest
            .listAssets()
            .where((p) => p.startsWith(prefix) && !p.endsWith('.gitkeep'))
            .toList()
          ..sort();
      } catch (_) {
        return [];
      }
    }
  }

  Future<void> applyVolumes() async {
    await _bgm.setVolume(pet.musicVolume.clamp(0, 1));
    await _voice.setVolume(pet.voiceVolume.clamp(0, 1));
  }

  /// Start / resume BGM stroll. If [fromResume] uses captured position.
  Future<void> startBgm({bool fromResume = false}) async {
    if (_bgmAssets.isEmpty) return;
    await applyVolumes();
    try {
      final asset = _bgmAssets[_bgmIndex % _bgmAssets.length];
      pet.musicTrackId = asset;
      final pos = fromResume ? pet.consumeMusicResume() : Duration.zero;
      await _bgm.setAsset(asset);
      if (pos > Duration.zero) {
        await _bgm.seek(pos);
      }
      await _bgm.play();
      pet.setMode(PetMode.music);
    } catch (e) {
      debugPrint('BGM start: $e');
    }
    notifyListeners();
  }

  Future<void> pauseBgmCapture() async {
    try {
      pet.captureMusicPos(_bgm.position);
      await _bgm.pause();
    } catch (_) {}
    notifyListeners();
  }

  Future<void> stopBgm() async {
    pet.captureMusicPos(_bgm.position);
    await _bgm.stop();
    notifyListeners();
  }

  Future<void> nextBgm() async {
    await pauseBgmCapture();
    _bgmIndex = (_bgmIndex + 1) % (_bgmAssets.isEmpty ? 1 : _bgmAssets.length);
    pet.musicResumePos = null;
    await startBgm();
  }

  /// Play a voice clip; pauses BGM and resumes from the same position after.
  Future<void> playVoiceAsset(String assetPath, {bool force = false}) async {
    if (!pet.voiceEnabled && !force) return;
    final now = DateTime.now();
    if (!force && _voiceCooldownUntil != null && now.isBefore(_voiceCooldownUntil!)) {
      return;
    }
    if (_voiceBusy && !force) return;
    _voiceBusy = true;
    final wasBgm = _bgm.playing;
    if (wasBgm) {
      await pauseBgmCapture();
    }
    try {
      await applyVolumes();
      await _voice.setAsset(assetPath);
      await _voice.play();
      await _voice.playerStateStream.firstWhere(
        (s) => s.processingState == ProcessingState.completed || !s.playing,
      );
    } catch (e) {
      debugPrint('voice: $e');
    } finally {
      _voiceBusy = false;
      _voiceCooldownUntil = DateTime.now().add(const Duration(seconds: 4));
      if (wasBgm || pet.mode == PetMode.music) {
        await startBgm(fromResume: true);
      }
      notifyListeners();
    }
  }

  Future<void> playVoiceCategory(String category, {bool force = false}) async {
    final list = await _listAssetPrefix('assets/voice/');
    final hits = list.where((p) => p.contains('/$category/') || p.contains('\\$category\\')).toList();
    final pick = hits.isNotEmpty
        ? hits[DateTime.now().millisecond % hits.length]
        : (list.isNotEmpty ? list.first : null);
    if (pick == null) {
      pet.showBubble('（语音：$category）');
      return;
    }
    await playVoiceAsset(pick, force: force);
  }

  @override
  void dispose() {
    _bgm.dispose();
    _voice.dispose();
    super.dispose();
  }
}
