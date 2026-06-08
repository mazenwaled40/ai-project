import 'package:flutter/material.dart';
import '../../../../main_navigation_shell.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            // ننده على الكلاس اللي في الملف اللي نقلناه
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(
                builder: (context) => const MainNavigationShell(),
              ),
            );
          },
          child: const Text('Login'),
        ),
      ),
    );
  }
}
