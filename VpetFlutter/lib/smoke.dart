import 'package:flutter/material.dart';

/// Placeholder so `flutter test` / analyze have a smoke widget without SharedPreferences.
class SmokeApp extends StatelessWidget {
  const SmokeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: Scaffold(body: Center(child: Text('伊得'))),
    );
  }
}
