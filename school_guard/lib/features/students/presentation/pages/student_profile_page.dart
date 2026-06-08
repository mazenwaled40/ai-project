import 'package:flutter/material.dart';
import '../../../../core/utils/responsive.dart';
import '../widgets/profile_banner.dart';
import '../widgets/profile_info_field.dart';

class StudentProfilePage extends StatelessWidget {
  const StudentProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: const BackButton(),
        elevation: 0,
        backgroundColor: Colors.transparent,
      ),
      extendBodyBehindAppBar: true,
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const ProfileBanner(
              imageUrl: 'https://i.pravatar.cc/300?u=monuka',
            ),
            SizedBox(height: context.hp(4)),
            Padding(
              padding: EdgeInsets.symmetric(horizontal: context.wp(6)),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  ProfileInfoField(
                    label: 'Name',
                    value: 'Monuka',
                  ),
                  ProfileInfoField(
                    label: 'ID',
                    value: '17823214',
                  ),
                  ProfileInfoField(
                    label: 'Department',
                    value: 'Science',
                  ),
                  ProfileInfoField(
                    label: 'E-Mail',
                    value: 'monika@gmail.com',
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
