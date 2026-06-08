import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/alert.dart';

// Note: In a real implementation, this would interact with a UseCase that calls the Repository.
// We are using a StateNotifier or AsyncNotifier for the UI state.

class AlertsNotifier extends StateNotifier<AsyncValue<List<Alert>>> {
  AlertsNotifier() : super(const AsyncValue.loading()) {
    fetchAlerts();
  }

  Future<void> fetchAlerts() async {
    state = const AsyncValue.loading();
    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 1));
      final mockAlerts = [
        Alert(
          id: '1',
          cameraId: 'cam_1',
          timestamp: DateTime.now(),
          type: 'Fight',
        ),
      ];
      state = AsyncValue.data(mockAlerts);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

final alertsProvider = StateNotifierProvider<AlertsNotifier, AsyncValue<List<Alert>>>((ref) {
  return AlertsNotifier();
});
