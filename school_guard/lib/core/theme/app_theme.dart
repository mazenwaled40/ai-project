import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'app_colors.dart';
import 'app_spacing.dart';
import 'app_typography.dart';

/// Builds the Material [ThemeData] for the entire app from our design tokens.
///
/// Only a light theme is provided — the design is white-dominant / minimalist.
abstract final class AppTheme {
  static ThemeData get light {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: AppColors.background,

      // ─── Color Scheme ────────────────────────────────────────────
      colorScheme: const ColorScheme.light(
        primary: AppColors.primary,
        onPrimary: AppColors.white,
        secondary: AppColors.primary,
        surface: AppColors.surface,
        onSurface: AppColors.textPrimary,
        error: AppColors.alertDot,
      ),

      // ─── Buttons ─────────────────────────────────────────────────
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: AppColors.background,
          elevation: 0,
          shape: const StadiumBorder(),
          textStyle: AppTypography.label.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // ─── AppBar ──────────────────────────────────────────────────
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.background,
        foregroundColor: AppColors.textPrimary,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        titleTextStyle: AppTypography.titleLarge,
        systemOverlayStyle: SystemUiOverlayStyle.dark,
      ),

      // ─── Card ────────────────────────────────────────────────────
      cardTheme: CardThemeData(
        color: AppColors.card,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.cardRadius),
          side: const BorderSide(
            color: AppColors.cardBorder,
            width: AppSpacing.cardBorderWidth,
          ),
        ),
      ),

      // ─── Input / Search ──────────────────────────────────────────
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.searchBarFill,
        hintStyle: AppTypography.searchHint,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.sm,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppSpacing.searchBarRadius),
          borderSide: BorderSide.none,
        ),
      ),

      // ─── Divider ─────────────────────────────────────────────────
      dividerTheme: const DividerThemeData(
        color: AppColors.divider,
        thickness: 0.5,
        space: 0,
      ),

      // ─── Bottom Navigation ───────────────────────────────────────
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: AppColors.navBarBackground,
        selectedItemColor: AppColors.navBarActive,
        unselectedItemColor: AppColors.navBarInactive,
        type: BottomNavigationBarType.fixed,
        showSelectedLabels: false,
        showUnselectedLabels: false,
        elevation: 0,
      ),

      // ─── List Tile ───────────────────────────────────────────────
      listTileTheme: const ListTileThemeData(
        contentPadding: EdgeInsets.symmetric(
          horizontal: AppSpacing.listItemHorizontalPadding,
          vertical: AppSpacing.listItemVerticalPadding,
        ),
        titleTextStyle: AppTypography.bodyLarge,
        subtitleTextStyle: AppTypography.bodyMedium,
      ),

      // ─── Text Theme ──────────────────────────────────────────────
      textTheme: const TextTheme(
        headlineLarge: AppTypography.titleLarge,
        headlineMedium: AppTypography.titleMedium,
        headlineSmall: AppTypography.titleSmall,
        bodyLarge: AppTypography.bodyLarge,
        bodyMedium: AppTypography.bodyMedium,
        bodySmall: AppTypography.bodySmall,
        labelLarge: AppTypography.label,
        labelMedium: AppTypography.labelValue,
      ),
    );
  }
}
