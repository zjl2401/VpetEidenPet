import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'audio/media_hub.dart';
import 'core/pet_controller.dart';
import 'platform/overlay_bridge.dart';
import 'ui/desktop_shell.dart';
import 'ui/onboarding.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final pet = PetController();
  await pet.init();
  final media = MediaHub(pet);
  await media.init();
  final overlay = OverlayBridge();
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: pet),
        ChangeNotifierProvider.value(value: media),
        Provider.value(value: overlay),
      ],
      child: const VpetEidenApp(),
    ),
  );
}

class VpetEidenApp extends StatelessWidget {
  const VpetEidenApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '伊得',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF5B7C99),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: defaultTargetPlatform == TargetPlatform.iOS ? '.SF Pro Text' : null,
      ),
      home: const _RootGate(),
    );
  }
}

class _RootGate extends StatelessWidget {
  const _RootGate();

  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    if (!pet.ownerSet) {
      return const OnboardingPage();
    }
    return const DesktopShell();
  }
}
