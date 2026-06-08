import 'package:equatable/equatable.dart';

class Alert extends Equatable {
  final String id;
  final String cameraId;
  final DateTime timestamp;
  final String type;

  const Alert({
    required this.id,
    required this.cameraId,
    required this.timestamp,
    required this.type,
  });

  @override
  List<Object?> get props => [id, cameraId, timestamp, type];
}
