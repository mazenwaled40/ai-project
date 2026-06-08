import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../utils/responsive.dart';

class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final IconData? icon;
  final Color? backgroundColor;
  final Color? foregroundColor;

  const AppButton({
    super.key,
    required this.text,
    this.onPressed,
    this.isLoading = false,
    this.icon,
    this.backgroundColor,
    this.foregroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: context.hp(7),
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: backgroundColor ?? AppColors.primary,
          foregroundColor: foregroundColor ?? AppColors.background,
        ),
        child: isLoading
            ? SizedBox(
                height: context.scale(20),
                width: context.scale(20),
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: foregroundColor ?? AppColors.background,
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (icon != null) ...[
                    Icon(icon, size: context.scale(20)),
                    SizedBox(width: context.wp(2)),
                  ],
                  Text(
                    text,
                    style: TextStyle(
                      fontSize: context.scale(16),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
