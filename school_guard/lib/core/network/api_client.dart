import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

class ApiClient {
  final Dio _dio;

  ApiClient(this._dio) {
    _dio.options.baseUrl = _getBaseUrl();
    _dio.options.connectTimeout = const Duration(seconds: 15);
    _dio.options.receiveTimeout = const Duration(seconds: 15);
  }

  String _getBaseUrl() {
    const backendUrl = String.fromEnvironment('BACKEND_URL');
    if (backendUrl.isNotEmpty) {
      return backendUrl;
    }
    if (kIsWeb) {
      return 'http://localhost:8001';
    }
    if (Platform.isAndroid) {
      return 'http://10.0.2.2:8001'; // شغال تمام للأندرويد إيموليتر عند صحابك
    }
    if (Platform.isWindows) {
      return 'http://127.0.0.1:8001'; // 💡 التعديل الجديد: هيشغل السيرفر صراحة على الويندوز ويحل الـ Semaphore Timeout أوتوماتيك
    }
    return 'http://localhost:8001';
  }

  Future<String> startViolenceDetection({
    required File videoFile,
    required String modelName,
  }) async {
    try {
      String fileName = videoFile.path.split('/').last;

      FormData formData = FormData.fromMap({
        "video": await MultipartFile.fromFile(
          videoFile.path,
          filename: fileName,
        ),
        "model_name": modelName,
        "window_stride": 8,
        "smoothing_size": 5,
      });

      final response = await _dio.post('/detect', data: formData);

      if (response.statusCode == 200) {
        return response.data['job_id'];
      }
      throw Exception('Failed to start detection');
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> checkJobStatus(String jobId) async {
    try {
      final response = await _dio.get('/jobs/$jobId');
      if (response.statusCode == 200) {
        return response.data;
      }
      throw Exception('Failed to get job status');
    } catch (e) {
      rethrow;
    }
  }
}
