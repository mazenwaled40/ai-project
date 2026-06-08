import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/widgets/student_list_tile.dart';
import '../../../../core/utils/responsive.dart';
import '../widgets/student_search_bar.dart';
import 'student_profile_page.dart';

class StudentSearchPage extends ConsumerWidget {
  const StudentSearchPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final mockStudents = [
      {'name': 'Nada Esam', 'subtitle': 'ID: 123214', 'image': 'https://i.pravatar.cc/150?u=nada'},
      {'name': 'Eslam Mekawi', 'subtitle': 'ID: 923092', 'image': 'https://i.pravatar.cc/150?u=eslam'},
      {'name': 'Mazen Walid', 'subtitle': 'ID: 234556', 'image': 'https://i.pravatar.cc/150?u=mazen'},
      {'name': 'Daniel Jay Park', 'subtitle': 'djpark@gmail.com', 'image': 'https://i.pravatar.cc/150?u=daniel'},
      {'name': 'Mark Rojas', 'subtitle': 'rojasmar@skiff.com', 'image': 'https://i.pravatar.cc/150?u=mark'},
    ];

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: EdgeInsets.symmetric(
                horizontal: context.wp(5),
                vertical: context.hp(2),
              ),
              child: const StudentSearchBar(),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: mockStudents.length * 2, // duplicate for scrolling demo
                itemBuilder: (context, index) {
                  final student = mockStudents[index % mockStudents.length];
                  return StudentListTile(
                    name: student['name']!,
                    subtitle: student['subtitle']!,
                    imageUrl: student['image']!,
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => const StudentProfilePage(),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
