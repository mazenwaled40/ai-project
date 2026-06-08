import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/utils/responsive.dart';

class CameraDetailPage extends StatelessWidget {
  final String cameraName;

  const CameraDetailPage({
    super.key,
    required this.cameraName,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.videoBackground,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: const BackButton(color: AppColors.white),
        title: Text(
          cameraName,
          style: const TextStyle(color: AppColors.white),
        ),
      ),
      extendBodyBehindAppBar: true,
      body: Column(
        children: [
          Expanded(
            flex: 3,
            child: Container(
              width: double.infinity,
              color: AppColors.videoBackground,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  Icon(
                    Icons.videocam_off_outlined,
                    color: AppColors.white.withOpacity(0.24),
                    size: context.scale(64),
                  ),
                  Positioned(
                    top: context.hp(12),
                    left: context.wp(5),
                    child: Container(
                      padding: EdgeInsets.symmetric(
                        horizontal: context.wp(3),
                        vertical: context.hp(0.5),
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.alertDot,
                        borderRadius: BorderRadius.circular(context.scale(4)),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: context.scale(8),
                            height: context.scale(8),
                            decoration: const BoxDecoration(
                              color: AppColors.white,
                              shape: BoxShape.circle,
                            ),
                          ),
                          SizedBox(width: context.wp(2)),
                          Text(
                            'LIVE',
                            style: AppTypography.label.copyWith(
                              color: AppColors.white,
                              fontSize: context.scale(12),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: Container(
              width: double.infinity,
              decoration: const BoxDecoration(
                color: AppColors.background,
                borderRadius: BorderRadius.vertical(
                  top: Radius.circular(24),
                ),
              ),
              padding: EdgeInsets.all(context.wp(6)),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            cameraName,
                            style: AppTypography.titleLarge.copyWith(
                              fontSize: context.scale(24),
                              color: AppColors.textPrimary,
                            ),
                          ),
                          Text(
                            'Main Hallway - North Wing',
                            style: AppTypography.bodyMedium.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                      IconButton(
                        onPressed: () {},
                        icon: const Icon(Icons.settings_outlined, color: AppColors.textPrimary),
                      ),
                    ],
                  ),
                  SizedBox(height: context.hp(4)),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _ControlButton(
                        icon: Icons.mic_none,
                        label: 'Talk',
                        onTap: () {},
                      ),
                      _ControlButton(
                        icon: Icons.videocam_outlined,
                        label: 'Record',
                        onTap: () {},
                      ),
                      _ControlButton(
                        icon: Icons.camera_alt_outlined,
                        label: 'Snapshot',
                        onTap: () {},
                      ),
                      _ControlButton(
                        icon: Icons.notifications_none,
                        label: 'Alerts',
                        onTap: () {},
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ControlButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _ControlButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(context.scale(30)),
          child: Container(
            padding: EdgeInsets.all(context.scale(16)),
            decoration: BoxDecoration(
              color: AppColors.surfaceVariant,
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: AppColors.primary),
          ),
        ),
        SizedBox(height: context.hp(1)),
        Text(
          label,
          style: AppTypography.bodySmall.copyWith(
            fontSize: context.scale(12),
          ),
        ),
      ],
    );
  }
}