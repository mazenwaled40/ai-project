import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  bool _isLoading = true;
  Map<String, dynamic> _studentData = {}; // بيانات الطالب
  List<dynamic> _incidents = []; // قائمة المخالفات
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _fetchDashboardData();
  }

  Future<void> _fetchDashboardData() async {
    try {
      final dioInstance = Dio(
        BaseOptions(
          // غير العنوان ده حسب جهازك (10.0.2.2 للـ Emulator)
          baseUrl: 'http://10.0.2.2:8001',
          connectTimeout: const Duration(seconds: 10),
        ),
      );

      final response = await dioInstance.get('/students/1');

      if (response.statusCode == 200) {
        setState(() {
          _studentData = response.data['student_info'];
          _incidents = response.data['incidents_history'];
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load data: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        title: const Text('Student Dashboard'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage.isNotEmpty
          ? Center(
              child: Text(_errorMessage, style: TextStyle(color: Colors.red)),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // كارت بيانات الطالب
                  Card(
                    elevation: 4,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: ListTile(
                      contentPadding: EdgeInsets.all(20),
                      leading: Icon(Icons.person, size: 50, color: Colors.blue),
                      title: Text(
                        "${_studentData['name'] ?? 'N/A'}",
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      subtitle: Text("الصف: ${_studentData['grade'] ?? 'N/A'}"),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    "سجل المخالفات:",
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),
                  // قائمة المخالفات
                  ListView.builder(
                    shrinkWrap: true,
                    physics: NeverScrollableScrollPhysics(),
                    itemCount: _incidents.length,
                    itemBuilder: (context, index) {
                      return Card(
                        margin: EdgeInsets.only(bottom: 10),
                        child: ListTile(
                          leading: Icon(Icons.warning, color: Colors.orange),
                          title: Text(_incidents[index]['title']),
                          subtitle: Text(_incidents[index]['date']),
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
    );
  }
}
