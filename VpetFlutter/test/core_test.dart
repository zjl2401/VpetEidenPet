import 'package:flutter_test/flutter_test.dart';
import 'package:vpet_eiden/core/menu_catalog.dart';
import 'package:vpet_eiden/core/pet_controller.dart';

void main() {
  test('root menus are four', () {
    expect(rootMenus.length, 4);
    expect(rootMenus.map((e) => e.id).toList(), ['interact', 'tools', 'games', 'system']);
  });

  test('wallet json roundtrip', () {
    final w = WalletState(gold: 12, items: {'bread': 1});
    final w2 = WalletState.fromJson(w.toJson());
    expect(w2.gold, 12);
    expect(w2.items['bread'], 1);
  });

  test('meet friendship increments', () {
    final pet = PetController();
    pet.homeCells = List.generate(48, (_) => HomeCell(kind: 'soil'));
    pet.showSpeech = false;
    pet.recordMeet();
    expect(pet.friendship.meetCount, 1);
    pet.recordMeet();
    expect(pet.friendship.meetCount, 2);
  });
}
