import 'package:flutter/material.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/utils/responsive.dart';

class StatCard extends StatelessWidget {
  final String title;
  final String topTrailingText;
  final String statValue;
  final String footerText;

  const StatCard({
    super.key,
    required this.title,
    required this.topTrailingText,
    required this.statValue,
    required this.footerText,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(context.scale(AppSpacing.cardPadding)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Flexible(
                  child: Text(
                    title,
                    style: AppTypography.titleSmall.copyWith(
                      fontSize: context.scale(12),
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Text(
                  topTrailingText,
                  style: AppTypography.bodySmall.copyWith(
                    fontSize: context.scale(10),
                  ),
                ),
              ],
            ),
            Text(
              statValue,
              style: AppTypography.statLarge.copyWith(
                fontSize: context.scale(22),
              ),
            ),
            Text(
              footerText,
              style: AppTypography.bodySmall.copyWith(
                fontSize: context.scale(10),
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}
