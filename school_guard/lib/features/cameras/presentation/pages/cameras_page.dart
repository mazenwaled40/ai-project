import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/utils/responsive.dart';
import '../widgets/camera_list_tile.dart';

class CamerasPage extends ConsumerWidget {
  const CamerasPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: SafeArea(
        child: ListView.builder(
          padding: EdgeInsets.only(top: context.hp(2)),
          itemCount: 4,
          itemBuilder: (context, index) {
            return CameraListTile(
              cameraName: 'cam ${index + 1}',
              date: '12-1-2025',
              isLive: true,
            );
          },
        ),
      ),
    );
  }
}
