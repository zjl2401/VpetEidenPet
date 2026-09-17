import 'package:flutter_test/flutter_test.dart';
import 'package:vpet_eiden/smoke.dart';

void main() {
  testWidgets('smoke app shows brand', (tester) async {
    await tester.pumpWidget(const SmokeApp());
    expect(find.text('伊得'), findsOneWidget);
  });
}
