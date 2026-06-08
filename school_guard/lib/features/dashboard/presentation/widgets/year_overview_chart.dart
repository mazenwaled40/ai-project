import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/utils/responsive.dart';

class YearOverviewChart extends StatelessWidget {
  const YearOverviewChart({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(context.scale(AppSpacing.cardPadding)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Year Overview',
              style: AppTypography.titleMedium.copyWith(
                fontSize: context.scale(16),
              ),
            ),
            SizedBox(height: context.hp(2)),
            SizedBox(
              height: context.hp(25),
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: 5,
                    getDrawingHorizontalLine: (value) {
                      return FlLine(
                        color: AppColors.chartGridLine,
                        strokeWidth: 1,
                      );
                    },
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: context.scale(30),
                        interval: 1,
                        getTitlesWidget: (v, m) => bottomTitleWidgets(v, m, context),
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        interval: 10,
                        getTitlesWidget: (v, m) => leftTitleWidgets(v, m, context),
                        reservedSize: context.scale(42),
                      ),
                    ),
                  ),
                  borderData: FlBorderData(show: false),
                  minX: 23,
                  maxX: 30,
                  minY: 20,
                  maxY: 50,
                  lineBarsData: [
                    LineChartBarData(
                      spots: const [
                        FlSpot(23, 26),
                        FlSpot(24, 27),
                        FlSpot(25, 31),
                        FlSpot(26, 33),
                        FlSpot(27, 36),
                        FlSpot(28, 40),
                        FlSpot(29, 37),
                        FlSpot(30, 48),
                      ],
                      isCurved: false,
                      color: AppColors.chartLine,
                      barWidth: context.scale(3),
                      isStrokeCapRound: true,
                      dotData: FlDotData(
                        show: true,
                        checkToShowDot: (spot, barData) => spot.x == 30,
                        getDotPainter: (spot, percent, barData, index) =>
                            FlDotCirclePainter(
                          radius: context.scale(4),
                          color: AppColors.chartLine,
                          strokeWidth: context.scale(2),
                          strokeColor: AppColors.primaryLight,
                        ),
                      ),
                      belowBarData: BarAreaData(
                        show: true,
                        color: AppColors.chartLine.withOpacity(0.1),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget bottomTitleWidgets(double value, TitleMeta meta, BuildContext context) {
    final style = TextStyle(
      color: AppColors.textTertiary,
      fontSize: context.scale(10),
    );
    String text = value == 23 ? 'Nov 23' : value.toInt().toString();
    return SideTitleWidget(
      meta: meta,
      child: Text(text, style: style),
    );
  }

  Widget leftTitleWidgets(double value, TitleMeta meta, BuildContext context) {
    final style = TextStyle(
      color: AppColors.textTertiary,
      fontSize: context.scale(10),
    );
    String text = '\$${value.toInt()}K';
    return SideTitleWidget(
      meta: meta,
      child: Text(text, style: style, textAlign: TextAlign.left),
    );
  }
}
