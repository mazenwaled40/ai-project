import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/utils/responsive.dart';
import '../pages/camera_detail_page.dart';

class CameraListTile extends StatelessWidget {
  final String cameraName;
  final String date;
  final bool isLive;

  const CameraListTile({
    super.key,
    required this.cameraName,
    required this.date,
    this.isLive = true,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => CameraDetailPage(cameraName: cameraName),
          ),
        );
      },
      child: Padding(
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
                  color: isLive ? AppColors.alertDotLight : Colors.transparent,
                  shape: BoxShape.circle,
                ),
              ),
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    cameraName,
                    style: AppTypography.bodyLarge.copyWith(
                      fontSize: context.scale(16),
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    date,
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
