import 'package:flutter/widgets.dart';

extension ResponsiveContext on BuildContext {
  /// Get the screen width
  double get width => MediaQuery.of(this).size.width;

  /// Get the screen height
  double get height => MediaQuery.of(this).size.height;

  /// Get percentage of screen width (e.g., wp(50) = 50% of width)
  double wp(double percent) => width * (percent / 100);

  /// Get percentage of screen height (e.g., hp(10) = 10% of height)
  double hp(double percent) => height * (percent / 100);

  /// Scale a value based on the design width (default: 375px for standard mobile)
  double scale(double size) {
    const double designWidth = 375.0;
    return (width / designWidth) * size;
  }

  /// Breakpoint checks
  bool get isMobile => width < 600;
  bool get isTablet => width >= 600 && width < 1200;
  bool get isDesktop => width >= 1200;
}

class Responsive extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const Responsive({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= 1200 && desktop != null) {
          return desktop!;
        } else if (constraints.maxWidth >= 600 && tablet != null) {
          return tablet!;
        } else {
          return mobile;
        }
      },
    );
  }
}
