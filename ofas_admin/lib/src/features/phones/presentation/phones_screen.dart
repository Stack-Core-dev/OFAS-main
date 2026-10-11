import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ofas_admin/src/shared/theme/app_theme.dart';
import 'package:ofas_admin/src/shared/widgets/common_widgets.dart';

class PhonesScreen extends ConsumerWidget {
  const PhonesScreen({super.key});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Phone Management'),
        actions: [
          FilledButton.icon(onPressed: () {}, icon: const Icon(Icons.add), label: const Text('Register Phone')),
          const SizedBox(width: 16),
        ],
      ),
      body: const AppEmptyState(
        icon: Icons.phone_android_outlined,
        title: 'Phone Management',
        message: 'Register and manage company phones for field operations',
      ),
    );
  }
}