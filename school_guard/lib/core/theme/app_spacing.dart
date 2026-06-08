/// Spacing & sizing tokens used across the app.
///
/// Based on an 8-point grid system for consistent rhythm.
abstract final class AppSpacing {
  // ─── Base Grid ─────────────────────────────────────────────────────
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;

  // ─── Page Padding ──────────────────────────────────────────────────
  /// Horizontal padding for all pages
  static const double pagePaddingH = 16.0;
  /// Top padding below status/app bar
  static const double pagePaddingTop = 16.0;

  // ─── Card ──────────────────────────────────────────────────────────
  static const double cardPadding = 16.0;
  static const double cardRadius = 12.0;
  static const double cardBorderWidth = 1.0;

  // ─── List Items ────────────────────────────────────────────────────
  static const double listItemVerticalPadding = 12.0;
  static const double listItemHorizontalPadding = 16.0;

  // ─── Avatar ────────────────────────────────────────────────────────
  /// Student list avatars (circular)
  static const double avatarRadiusSmall = 20.0;
  /// Student profile avatar (large circular)
  static const double avatarRadiusLarge = 48.0;

  // ─── Alert Dot ─────────────────────────────────────────────────────
  static const double alertDotSize = 8.0;

  // ─── Search Bar ────────────────────────────────────────────────────
  static const double searchBarHeight = 44.0;
  static const double searchBarRadius = 10.0;

  // ─── Bottom Nav ────────────────────────────────────────────────────
  static const double bottomNavHeight = 56.0;
  static const double bottomNavIconSize = 24.0;

  // ─── Profile Header Banner ─────────────────────────────────────────
  static const double profileBannerHeight = 160.0;
}
