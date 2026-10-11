import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ofas_admin/src/shared/theme/app_theme.dart';
import 'package:ofas_admin/src/shared/widgets/common_widgets.dart';

class VisitsScreen extends ConsumerWidget {
  const VisitsScreen({super.key});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Field Visits'),
        actions: [
          FilledButton.icon(onPressed: () {}, icon: const Icon(Icons.download), label: const Text('Export')),
          const SizedBox(width: 16),
        ],
      ),
      body: const AppEmptyState(
        icon: Icons.fact_check_outlined,
        title: 'Visit Review',
        message: 'Review and validate field visits submitted by surveyors',
      ),
    );
  }
}