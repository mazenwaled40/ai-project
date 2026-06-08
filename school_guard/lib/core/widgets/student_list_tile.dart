import 'package:flutter/material.dart';
import '../theme/app_spacing.dart';
import '../theme/app_typography.dart';
import '../theme/app_colors.dart';
import '../utils/responsive.dart';

class StudentListTile extends StatelessWidget {
  final String name;
  final String subtitle;
  final String? imageUrl;
  final VoidCallback? onTap;

  const StudentListTile({
    super.key,
    required this.name,
    required this.subtitle,
    this.imageUrl,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: EdgeInsets.symmetric(
          horizontal: context.wp(5),
          vertical: context.scale(AppSpacing.listItemVerticalPadding),
        ),
        child: Row(
          children: [
            CircleAvatar(
              radius: context.scale(AppSpacing.avatarRadiusSmall),
              backgroundColor: AppColors.surfaceVariant,
              backgroundImage: imageUrl != null ? NetworkImage(imageUrl!) : null,
              child: imageUrl == null
                  ? Text(
                      name.isNotEmpty ? name[0].toUpperCase() : '?',
                      style: AppTypography.bodyLarge.copyWith(
                        color: AppColors.textSecondary,
                        fontSize: context.scale(16),
                      ),
                    )
                  : null,
            ),
            SizedBox(width: context.wp(3)),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: AppTypography.bodyLarge.copyWith(
                      fontSize: context.scale(16),
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: AppTypography.bodyMedium.copyWith(
                      fontSize: context.scale(14),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
