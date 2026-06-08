import 'package:flutter/material.dart';

/// School Guard color palette — extracted from the Figma/design mockups.
///
/// Design language: Clean, minimalist, iOS-inspired.
/// Dominant white backgrounds with selective accent colors.
abstract final class AppColors {
  // ─── Brand / Primary ───────────────────────────────────────────────
  /// Black accent — used for primary actions and branding
  static const Color primary = Color(0xFF000000);
  static const Color primaryLight = Color(0xFF333333);
  static const Color primaryDark = Color(0xFF000000);

  // ─── Alert / Danger ────────────────────────────────────────────────
  /// Small red/pink dot used as a live/alert indicator
  static const Color alertDot = Color(0xFFE53935);
  static const Color alertDotLight = Color(0xFFFF6F60);

  // ─── Neutral / Surface ─────────────────────────────────────────────
  static const Color background = Color(0xFFFFFFFF);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF5F5F5);

  /// Card background — white with subtle border
  static const Color card = Color(0xFFFFFFFF);
  static const Color cardBorder = Color(0xFFE8E8E8);

  // ─── Text ──────────────────────────────────────────────────────────
  static const Color textPrimary = Color(0xFF1A1A1A);
  static const Color textSecondary = Color(0xFF8E8E93);
  static const Color textTertiary = Color(0xFFAEAEB2);

  // ─── Search Bar ────────────────────────────────────────────────────
  static const Color searchBarFill = Color(0xFF3A3A3C);
  static const Color searchBarText = Color(0xFFAEAEB2);

  // ─── Bottom Navigation ─────────────────────────────────────────────
  static const Color navBarBackground = Color(0xFFFFFFFF);
  static const Color navBarActive = Color(0xFF1A1A1A);
  static const Color navBarInactive = Color(0xFF8E8E93);
  static const Color navBarBorder = Color(0xFFE5E5EA);

  // ─── Chart ─────────────────────────────────────────────────────────
  static const Color chartLine = Color(0xFF3478F6);
  static const Color chartGridLine = Color(0xFFE5E5EA);

  // ─── Divider ───────────────────────────────────────────────────────
  static const Color divider = Color(0xFFE5E5EA);

  // ─── Positive / Success ────────────────────────────────────────────
  static const Color positive = Color(0xFF34C759);

  // ─── Absolute Colors ────────────────────────────────────────────────
  static const Color white = Color(0xFFFFFFFF);
  static const Color black = Color(0xFF000000);
  static const Color videoBackground = Color(0xFF000000);
}
