import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/pet_controller.dart';
import '../platform/overlay_bridge.dart';

/// Draggable pet sprite + speech bubble + companions.
class PetStage extends StatelessWidget {
  const PetStage({super.key, this.onTapPet});

  final VoidCallback? onTapPet;

  @override
  Widget build(BuildContext context) {
    final pet = context.watch<PetController>();
    final size = pet.displaySize;

    return LayoutBuilder(
      builder: (context, constraints) {
        final maxX = (constraints.maxWidth - size).clamp(0.0, double.infinity);
        final maxY = (constraints.maxHeight - size - 40).clamp(0.0, double.infinity);
        final x = pet.petX.clamp(0.0, maxX);
        final y = pet.petY.clamp(0.0, maxY);

        return Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [Color(0xFFC9D9E8), Color(0xFFEDE6D8)],
            ),
          ),
          child: Stack(
            children: [
              if (pet.speechVisible)
                Positioned(
                  left: x.clamp(8, maxX),
                  top: (y - 56).clamp(8, maxY),
                  child: _Bubble(text: pet.speechText),
                ),
              Positioned(
                left: x,
                top: y,
                child: GestureDetector(
                  onTap: () {
                    onTapPet?.call();
                    if (pet.mode == PetMode.work) {
                      pet.workDeliverBox();
                    }
                  },
                  onPanStart: (_) => pet.dragging = true,
                  onPanUpdate: (d) {
                    pet.petX = (pet.petX + d.delta.dx).clamp(0.0, maxX);
                    pet.petY = (pet.petY + d.delta.dy).clamp(0.0, maxY);
                    pet.bump();
                    context.read<OverlayBridge>().updateOverlayPose(
                          asset: pet.poseAsset,
                          x: pet.petX,
                          y: pet.petY,
                          size: size,
                        );
                  },
                  onPanEnd: (_) => pet.dragging = false,
                  child: SizedBox(
                    width: size + (pet.companionAster || pet.companionMorvay ? 72 : 0),
                    height: size,
                    child: Stack(
                      clipBehavior: Clip.none,
                      children: [
                        Image.asset(
                          'assets/sprites/${pet.poseAsset}',
                          width: size,
                          height: size,
                          fit: BoxFit.contain,
                          filterQuality: FilterQuality.none,
                          errorBuilder: (_, __, ___) => Icon(Icons.pets, size: size * 0.6),
                        ),
                        if (pet.wearFlower)
                          Positioned(
                            right: 4,
                            top: 8,
                            child: Icon(Icons.local_florist, size: size * 0.18, color: Colors.pink.shade300),
                          ),
                        if (pet.companionAster)
                          Positioned(
                            right: 0,
                            bottom: 0,
                            child: Image.asset(
                              'assets/sprites/Aster1.png',
                              width: size * 0.45,
                              height: size * 0.45,
                              errorBuilder: (_, __, ___) => const SizedBox.shrink(),
                            ),
                          ),
                        if (pet.companionMorvay)
                          Positioned(
                            left: -size * 0.2,
                            bottom: 0,
                            child: Image.asset(
                              'assets/sprites/Morvay1.png',
                              width: size * 0.45,
                              height: size * 0.45,
                              errorBuilder: (_, __, ___) => const SizedBox.shrink(),
                            ),
                          ),
                        if (pet.mode == PetMode.work)
                          Positioned(
                            right: -8,
                            bottom: 4,
                            child: Image.asset(
                              'assets/sprites/box.png',
                              width: size * 0.28,
                              errorBuilder: (_, __, ___) => const Icon(Icons.inventory_2),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
              Positioned(
                left: 12,
                bottom: 12,
                child: Text(
                  '陪伴 ${pet.companionDays} 天 · 相遇 ${pet.friendship.meetCount}',
                  style: Theme.of(context).textTheme.labelMedium,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _Bubble extends StatelessWidget {
  const _Bubble({required this.text});
  final String text;

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 220),
      child: Material(
        elevation: 2,
        borderRadius: BorderRadius.circular(12),
        color: Colors.white.withOpacity(0.95),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Text(text, style: const TextStyle(fontSize: 13, height: 1.35)),
        ),
      ),
    );
  }
}
