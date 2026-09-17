import 'dart:convert';
import 'dart:math';

import 'package:shared_preferences/shared_preferences.dart';

/// Same-device “other pet” presence stub + optional LAN payload shape.
class MeetPresence {
  MeetPresence({this.petId, this.displayName = '伊得'});

  String? petId;
  String displayName;
  final _rng = Random();

  Future<void> ensureId() async {
    final p = await SharedPreferences.getInstance();
    petId ??= p.getString('meet_pet_id');
    if (petId == null) {
      petId = 'eiden_${_rng.nextInt(1 << 32)}';
      await p.setString('meet_pet_id', petId!);
    }
  }

  Map<String, dynamic> advertisePayload() => {
        'pet_id': petId,
        'name': displayName,
        'species': 'eiden',
        'ts': DateTime.now().toIso8601String(),
      };

  String advertiseJson() => jsonEncode(advertisePayload());

  /// Simulate encountering another presence on this device / LAN.
  Future<Map<String, dynamic>> simulatePeer() async {
    await ensureId();
    return {
      'pet_id': 'peer_${_rng.nextInt(99999)}',
      'name': '路过的桌宠',
      'species': 'other',
      'ts': DateTime.now().toIso8601String(),
    };
  }
}
