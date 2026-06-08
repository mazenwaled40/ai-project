import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/utils/responsive.dart';
import '../widgets/alert_list_tile.dart';

class AlertsPage extends ConsumerWidget {
  const AlertsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: EdgeInsets.symmetric(
                horizontal: context.wp(5),
                vertical: context.hp(2),
              ),
              child: Text(
                'Alerts',
                style: AppTypography.titleLarge.copyWith(
                  fontSize: context.scale(28),
                ),
              ),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: 10,
                itemBuilder: (context, index) {
                  return const AlertListTile(
                    date: '12-1-2025',
                    type: 'Violence',
                    cameraName: 'Camera 5',
                    isUnread: true,
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
