import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../core/utils/responsive.dart';

class ProfileBanner extends StatelessWidget {
  final String imageUrl;

  const ProfileBanner({
    super.key,
    required this.imageUrl,
  });

  @override
  Widget build(BuildContext context) {
    final bannerHeight = context.hp(20);
    final avatarRadius = context.scale(AppSpacing.avatarRadiusLarge);

    return SizedBox(
      height: bannerHeight + avatarRadius,
      child: Stack(
        alignment: Alignment.topCenter,
        children: [
          // Background Shape
          ClipPath(
            clipper: _WaveClipper(),
            child: Container(
              height: bannerHeight,
              color: AppColors.primary,
            ),
          ),
          // Avatar
          Positioned(
            bottom: 0,
            child: Container(
              padding: EdgeInsets.all(context.scale(4)), // white border width
              decoration: const BoxDecoration(
                color: AppColors.background,
                shape: BoxShape.circle,
              ),
              child: CircleAvatar(
                radius: avatarRadius,
                backgroundImage: NetworkImage(imageUrl),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _WaveClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    var path = Path();
    path.lineTo(0, size.height - 40);
    
    var firstControlPoint = Offset(size.width / 4, size.height);
    var firstEndPoint = Offset(size.width / 2.25, size.height - 20.0);
    path.quadraticBezierTo(firstControlPoint.dx, firstControlPoint.dy,
        firstEndPoint.dx, firstEndPoint.dy);

    var secondControlPoint = Offset(size.width - (size.width / 3.25), size.height - 45);
    var secondEndPoint = Offset(size.width, size.height - 30);
    path.quadraticBezierTo(secondControlPoint.dx, secondControlPoint.dy,
        secondEndPoint.dx, secondEndPoint.dy);

    path.lineTo(size.width, 0);
    path.close();
    return path;
  }

  @override
  bool shouldReclip(CustomClipper<Path> oldClipper) => false;
}
