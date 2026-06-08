import 'package:flutter/material.dart';
import 'app_colors.dart';

/// Typography system — extracted from the design mockups.
///
/// The design uses a clean system sans-serif font (SF Pro on iOS, Roboto on
/// Android). Hierarchy is achieved through weight and size, not colour variety.
abstract final class AppTypography {
  static const String _fontFamily = 'SF Pro Display';

  // ─── Large Titles ──────────────────────────────────────────────────
  /// "Alerts", "School Guard" — top-level page titles
  static const TextStyle titleLarge = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 28,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.5,
  );

  // ─── Section Headers ───────────────────────────────────────────────
  /// "Year Overview", "The most troublesome"
  static const TextStyle titleMedium = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
  );

  // ─── Card Headers ──────────────────────────────────────────────────
  /// "Total Alerts", "Latest Alert" — inside stat cards
  static const TextStyle titleSmall = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    color: AppColors.textSecondary,
  );

  // ─── List Item Title ───────────────────────────────────────────────
  /// "Nada Esam", "cam 1", "12-1-2025 - Violence"
  static const TextStyle bodyLarge = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
  );

  // ─── List Item Subtitle ────────────────────────────────────────────
  /// "ID: 123214", "Camera 5", "12-1-2025"
  static const TextStyle bodyMedium = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: AppColors.textSecondary,
  );

  // ─── Small Body / Metadata ─────────────────────────────────────────
  /// "+20% month over month"
  static const TextStyle bodySmall = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: AppColors.textTertiary,
  );

  // ─── Big Stat Number ───────────────────────────────────────────────
  /// "8 Alerts", "3 days ago"
  static const TextStyle statLarge = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
  );

  // ─── Label (Profile) ──────────────────────────────────────────────
  /// "Name", "ID", "Department", "E-Mail"
  static const TextStyle label = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
  );

  // ─── Label Value (Profile) ─────────────────────────────────────────
  /// "Monuka", "17823214", "Science"
  static const TextStyle labelValue = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: AppColors.textSecondary,
  );

  // ─── Search Bar Hint ───────────────────────────────────────────────
  static const TextStyle searchHint = TextStyle(
    fontFamily: _fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: AppColors.searchBarText,
  );
}
