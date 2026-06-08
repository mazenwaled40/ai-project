import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_typography.dart';
import '../../../../core/utils/responsive.dart';
import '../../../../core/widgets/app_button.dart';

class AddIncidentPage extends ConsumerStatefulWidget {
  const AddIncidentPage({super.key});

  @override
  ConsumerState<AddIncidentPage> createState() => _AddIncidentPageState();
}

class _AddIncidentPageState extends ConsumerState<AddIncidentPage> {
  bool _isUploading = false;
  final String _selectedFileName = 'incident_clip_042.mp4';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Add Incident'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Upload Video for AI Analysis',
                style: AppTypography.titleLarge.copyWith(
                  fontSize: 18,
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 15),

              Container(
                padding: const EdgeInsets.symmetric(vertical: 20),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant.withOpacity(0.4),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: AppColors.primary.withOpacity(0.3),
                    width: 1.5,
                  ),
                ),
                child: Column(
                  children: [
                    Icon(
                      Icons.video_file_rounded,
                      size: 36,
                      color: AppColors.primary,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _selectedFileName,
                      style: AppTypography.titleSmall.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              AppButton(
                text: 'Analyze Video',
                isLoading: _isUploading,
                onPressed: () async {
                  setState(() => _isUploading = true);

                  final dioInstance = Dio(
                    BaseOptions(baseUrl: 'http://127.0.0.1:8001'),
                  );
                  List<int> fakeBytes = utf8.encode("fake video data");

                  // 💡 بعتنا كل التركيبات الممكنة عشان نرضي الـ FastAPI ونعدي الـ 422
                  List<Map<String, dynamic>> payloads = [
                    // احتمال 1: مستني فيديو وموديل ومعاملات تانية
                    {
                      "video": MultipartFile.fromBytes(
                        fakeBytes,
                        filename: _selectedFileName,
                      ),
                      "model_name": "violence_detector.keras",
                      "window_stride": 8,
                      "smoothing_size": 5,
                    },
                    // احتمال 2: مسميها file بدل video ومستني المعاملات
                    {
                      "file": MultipartFile.fromBytes(
                        fakeBytes,
                        filename: _selectedFileName,
                      ),
                      "model_name": "violence_detector.keras",
                      "window_stride": 8,
                      "smoothing_size": 5,
                    },
                    // احتمال 3: فيديو بس من غير معاملات إضافية
                    {
                      "video": MultipartFile.fromBytes(
                        fakeBytes,
                        filename: _selectedFileName,
                      ),
                    },
                  ];

                  bool hasSuccess = false;

                  for (var payload in payloads) {
                    try {
                      FormData formData = FormData.fromMap(payload);
                      final response = await dioInstance.post(
                        '/detect',
                        data: formData,
                      );

                      print(
                        "🎉🎉🎉 مبروك يا مازن!! اخترقنا الـ 422 وجاب 200 OK! الرد: ${response.data}",
                      );
                      hasSuccess = true;

                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            backgroundColor: Colors.green,
                            content: Text(
                              '🎉 Success! Video analyzed successfully.',
                            ),
                          ),
                        );
                      }
                      break;
                    } catch (e) {
                      // لو واحدة جابت 422 بيكمل للي بعدها عشان يشوف الصح
                    }
                  }

                  if (!hasSuccess && mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        backgroundColor: Colors.red,
                        content: Text('لسه في مشكلة في صيغة البيانات المبعوتة'),
                      ),
                    );
                  }

                  setState(() => _isUploading = false);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
