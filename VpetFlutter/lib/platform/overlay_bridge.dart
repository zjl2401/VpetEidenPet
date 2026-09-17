import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

/// Android SYSTEM_ALERT_WINDOW + iOS PiP / foreground-pet bridge.
class OverlayBridge {
  static const _ch = MethodChannel('com.vpet.eiden.mobile/overlay');

  Future<bool> requestPermission() async {
    if (kIsWeb) return false;
    if (Platform.isAndroid) {
      try {
        final ok = await _ch.invokeMethod<bool>('requestOverlayPermission');
        return ok == true;
      } catch (e) {
        debugPrint('overlay perm: $e');
        return false;
      }
    }
    // iOS: no SYSTEM_ALERT_WINDOW; app uses foreground stage + PiP keep-alive.
    return true;
  }

  Future<bool> canDrawOverlays() async {
    if (!Platform.isAndroid) return true;
    try {
      return await _ch.invokeMethod<bool>('canDrawOverlays') == true;
    } catch (_) {
      return false;
    }
  }

  Future<void> startOverlay() async {
    if (!Platform.isAndroid) return;
    try {
      await _ch.invokeMethod('startOverlay');
    } catch (e) {
      debugPrint('startOverlay: $e');
    }
  }

  Future<void> stopOverlay() async {
    if (!Platform.isAndroid) return;
    try {
      await _ch.invokeMethod('stopOverlay');
    } catch (_) {}
  }

  Future<void> updateOverlayPose({
    required String asset,
    required double x,
    required double y,
    required double size,
  }) async {
    if (!Platform.isAndroid) return;
    try {
      await _ch.invokeMethod('updatePose', {
        'asset': asset,
        'x': x,
        'y': y,
        'size': size,
      });
    } catch (_) {}
  }

  /// iOS Picture-in-Picture keep-alive stub (native side may no-op until AVKit wired).
  Future<void> startPipKeepAlive() async {
    if (!Platform.isIOS) return;
    try {
      await _ch.invokeMethod('startPip');
    } catch (e) {
      debugPrint('pip: $e');
    }
  }

  Future<void> stopPipKeepAlive() async {
    if (!Platform.isIOS) return;
    try {
      await _ch.invokeMethod('stopPip');
    } catch (_) {}
  }
}
