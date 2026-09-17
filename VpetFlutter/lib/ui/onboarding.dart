import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/pet_controller.dart';

class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final _ctl = TextEditingController();

  @override
  void dispose() {
    _ctl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFFE8F0F7), Color(0xFFF7F3EA), Color(0xFFD9E5EF)],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(28),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Spacer(),
                Image.asset(
                  'assets/sprites/hi1.png',
                  height: 160,
                  errorBuilder: (_, __, ___) => const Icon(Icons.pets, size: 96),
                ),
                const SizedBox(height: 24),
                Text(
                  '伊得',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        letterSpacing: 4,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  '在继续之前，请告诉我你的名字。',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: 28),
                TextField(
                  controller: _ctl,
                  decoration: const InputDecoration(
                    labelText: '所属人名字',
                    border: OutlineInputBorder(),
                  ),
                  textInputAction: TextInputAction.done,
                  onSubmitted: (_) => _submit(context),
                ),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () => _submit(context),
                  child: const Text('认主'),
                ),
                const Spacer(flex: 2),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _submit(BuildContext context) async {
    final name = _ctl.text.trim();
    if (name.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入名字')),
      );
      return;
    }
    await context.read<PetController>().setOwner(name);
  }
}
