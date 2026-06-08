import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/utils/responsive.dart';

class StudentSearchBar extends StatelessWidget {
  const StudentSearchBar({super.key});

  @override
  Widget build(BuildContext context) {
    return TextField(
      style: TextStyle(
        color: AppColors.white,
        fontSize: context.scale(16),
      ),
      decoration: InputDecoration(
        hintText: 'Student ID',
        hintStyle: TextStyle(
          color: AppColors.searchBarText,
          fontSize: context.scale(16),
        ),
        prefixIcon: Icon(
          Icons.search,
          color: AppColors.searchBarText,
          size: context.scale(20),
        ),
        filled: true,
        fillColor: AppColors.searchBarFill,
        contentPadding: EdgeInsets.symmetric(
          vertical: context.hp(1.5),
          horizontal: context.wp(4),
        ),
      ),
    );
  }
}
