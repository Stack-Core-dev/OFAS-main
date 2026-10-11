import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ofas_admin/src/shared/theme/app_theme.dart';
import 'package:ofas_admin/src/shared/widgets/common_widgets.dart';

class AuditScreen extends ConsumerWidget {
  const AuditScreen({super.key});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Audit Log'),
        actions: [
          FilledButton.icon(onPressed: () {}, icon: const Icon(Icons.verified), label: const Text('Verify Chain')),
          const SizedBox(width: 8),
          FilledButton.icon(onPressed: () {}, icon: const Icon(Icons.download), label: const Text('Export')),
          const SizedBox(width: 16),
        ],
      ),
      body: const AppEmptyState(
        icon: Icons.security_outlined,
        title: 'Audit Trail',
        message: 'Immutable audit log of all admin actions with cryptographic chain verification',
      ),
    );
  }
}