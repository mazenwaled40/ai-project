import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'features/dashboard/presentation/pages/dashboard_page.dart';
import 'features/students/presentation/pages/student_search_page.dart';
import 'features/alerts/presentation/pages/alerts_page.dart';
import 'features/cameras/presentation/pages/cameras_page.dart';
import 'features/incidents/presentation/pages/add_incident_page.dart';

final currentNavIndexProvider = StateProvider<int>((ref) => 0);

class MainNavigationShell extends ConsumerWidget {
  const MainNavigationShell({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentIndex = ref.watch(currentNavIndexProvider);

    final pages = [
      DashboardPage(),
      const StudentSearchPage(),
      const AddIncidentPage(),
      const AlertsPage(),
      const CamerasPage(),
    ];

    return Scaffold(
      body: IndexedStack(index: currentIndex, children: pages),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          border: Border(
            top: BorderSide(color: Theme.of(context).dividerColor, width: 1.0),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: currentIndex,
          onTap: (index) {
            ref.read(currentNavIndexProvider.notifier).state = index;
          },
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_filled),
              label: 'Home',
            ),
            BottomNavigationBarItem(icon: Icon(Icons.search), label: 'Search'),
            BottomNavigationBarItem(
              icon: Icon(Icons.add_circle_outline),
              label: 'Add',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.notifications_none),
              label: 'Alerts',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.camera_alt_outlined),
              label: 'Cameras',
            ),
          ],
        ),
      ),
    );
  }
}
