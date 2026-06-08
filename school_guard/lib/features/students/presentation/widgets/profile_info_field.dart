import 'package:flutter/material.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/utils/responsive.dart';

class ProfileInfoField extends StatelessWidget {
  final String label;
  final String value;

  const ProfileInfoField({
    super.key,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: context.hp(3)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: AppTypography.label.copyWith(
              fontSize: context.scale(12),
            ),
          ),
          SizedBox(height: context.hp(0.5)),
          Text(
            value,
            style: AppTypography.labelValue.copyWith(
              fontSize: context.scale(16),
            ),
          ),
        ],
      ),
    );
  }
}
