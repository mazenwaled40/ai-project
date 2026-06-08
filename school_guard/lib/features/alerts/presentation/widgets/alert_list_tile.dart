import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/utils/responsive.dart';

class AlertListTile extends StatelessWidget {
  final String date;
  final String type;
  final String cameraName;
  final bool isUnread;

  const AlertListTile({
    super.key,
    required this.date,
    required this.type,
    required this.cameraName,
    this.isUnread = true,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: context.wp(5),
        vertical: context.scale(AppSpacing.listItemVerticalPadding),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: EdgeInsets.only(
              top: context.scale(6),
              right: context.wp(3),
            ),
            child: Container(
              width: context.scale(AppSpacing.alertDotSize),
              height: context.scale(AppSpacing.alertDotSize),
              decoration: BoxDecoration(
                color: isUnread ? AppColors.alertDot : Colors.transparent,
                shape: BoxShape.circle,
              ),
            ),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$date - $type',
                  style: AppTypography.bodyLarge.copyWith(
                    fontSize: context.scale(16),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  cameraName,
                  style: AppTypography.bodyMedium.copyWith(
                    fontSize: context.scale(14),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
