import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ofas_admin/src/shared/theme/app_theme.dart';
import 'package:ofas_admin/src/shared/widgets/common_widgets.dart';

class AssignmentsScreen extends ConsumerWidget {
  const AssignmentsScreen({super.key});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Assignments'),
        actions: [
          FilledButton.icon(onPressed: () {}, icon: const Icon(Icons.assignment_add), label: const Text('Create Assignment')),
          const SizedBox(width: 16),
        ],
      ),
      body: const AppEmptyState(
        icon: Icons.assignment_outlined,
        title: 'Assignment Management',
        message: 'Assign fields to surveyors and track daily schedules',
      ),
    );
  }
}