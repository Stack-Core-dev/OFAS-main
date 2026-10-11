import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ofas_admin/src/core/auth/auth_provider.dart';
import 'package:ofas_admin/src/shared/theme/app_theme.dart';
import 'package:ofas_admin/src/shared/widgets/common_widgets.dart';
import 'package:ofas_admin/src/core/api/api_client.dart';
import 'package:ofas_admin/src/core/models/surveyor.dart';

final surveyorsProvider = FutureProvider.autoDispose.family<SurveyorListResponse, Map<String, dynamic>>((ref, params) async {
  final apiClient = ref.read(apiClientProvider);
  return apiClient.getSurveyors(
    page: params['page'] ?? 1,
    pageSize: params['pageSize'] ?? 20,
    search: params['search'],
    department: params['department'],
    isActive: params['isActive'],
  );
});

class SurveyorsScreen extends ConsumerStatefulWidget {
  const SurveyorsScreen({super.key});
  
  @override
  ConsumerState<SurveyorsScreen> createState() => _SurveyorsScreenState();
}

class _SurveyorsScreenState extends ConsumerState<SurveyorsScreen> {
  final _searchController = TextEditingController();
  int _currentPage = 1;
  String _searchQuery = '';
  String? _selectedDepartment;
  bool? _isActive;
  
  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    final params = {
      'page': _currentPage,
      'pageSize': 20,
      'search': _searchQuery.isEmpty ? null : _searchQuery,
      'department': _selectedDepartment,
      'isActive': _isActive,
    };
    
    final surveyorsAsync = ref.watch(surveyorsProvider(params));
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Surveyors Management'),
        actions: [
          FilledButton.icon(
            onPressed: () => _showCreateSurveyorDialog(context),
            icon: const Icon(Icons.person_add),
            label: const Text('Add Surveyor'),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Column(
        children: [
          AppCard(
            margin: const EdgeInsets.all(24),
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  flex: 3,
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Search surveyors...',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: _searchQuery.isNotEmpty
                        ? IconButton(icon: const Icon(Icons.clear), onPressed: () { _searchController.clear(); setState(() => _searchQuery = ''); })
                        : null,
                    ),
                    onSubmitted: (v) => setState(() => _searchQuery = v),
                  ),
                ),
                const SizedBox(width: 16),
                SizedBox(
                  width: 200,
                  child: DropdownButtonFormField<String?>(
                    initialValue: _selectedDepartment,
                    decoration: const InputDecoration(labelText: 'Department', prefixIcon: Icon(Icons.business)),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('All Departments')),
                      const DropdownMenuItem(value: 'FIELD_OPS', child: Text('Field Operations')),
                      const DropdownMenuItem(value: 'QUALITY', child: Text('Quality Control')),
                      const DropdownMenuItem(value: 'SUPERVISION', child: Text('Supervision')),
                    ],
                    onChanged: (v) => setState(() => _selectedDepartment = v),
                  ),
                ),
                const SizedBox(width: 16),
                SizedBox(
                  width: 130,
                  child: DropdownButtonFormField<bool?>(
                    initialValue: _isActive,
                    decoration: const InputDecoration(labelText: 'Status', prefixIcon: Icon(Icons.filter_list)),
                    items: const [
                      DropdownMenuItem(value: null, child: Text('All')),
                      DropdownMenuItem(value: true, child: Text('Active')),
                      DropdownMenuItem(value: false, child: Text('Inactive')),
                    ],
                    onChanged: (v) => setState(() => _isActive = v),
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: surveyorsAsync.when(
              data: (response) => _buildSurveyorsTable(context, response),
              loading: () => const AppLoadingState(message: 'Loading surveyors...'),
              error: (error, _) => AppErrorState(message: error.toString(), onRetry: () => ref.invalidate(surveyorsProvider(params))),
            ),
          ),
          surveyorsAsync.when(
            data: (response) => _buildPagination(response.total, response.page, response.pageSize),
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
        ],
      ),
    );
  }
  
  Widget _buildSurveyorsTable(BuildContext context, SurveyorListResponse response) {
    if (response.surveyors.isEmpty) {
      return const AppEmptyState(
        icon: Icons.people_outline,
        title: 'No Surveyors Found',
        message: 'Add surveyors to start field operations',
      );
    }
    
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Surveyor')),
          DataColumn(label: Text('Employee ID')),
          DataColumn(label: Text('Department')),
          DataColumn(label: Text('Contact')),
          DataColumn(label: Text('Face Template')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Last Sync')),
          DataColumn(label: Text('Actions')),
        ],
        rows: response.surveyors.map((s) => DataRow(cells: [
          DataCell(Row(
            children: [
              AppAvatar(name: s.fullName, radius: 18),
              const SizedBox(width: 12),
              Text(s.fullName, style: const TextStyle(fontWeight: FontWeight.w500)),
            ],
          )),
          DataCell(Text(s.employeeId)),
          DataCell(Text(s.department)),
          DataCell(Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(s.email, style: const TextStyle(fontSize: 12)),
              Text(s.phoneNumber, style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
            ],
          )),
          DataCell(AppStatusChip(
            label: s.activeFaceTemplate != null ? 'Enrolled' : 'Missing',
            type: s.activeFaceTemplate != null ? StatusType.success : StatusType.warning,
            small: true,
          )),
          DataCell(AppStatusChip(
            label: s.isActive ? 'Active' : 'Inactive',
            type: s.isActive ? StatusType.success : StatusType.neutral,
            small: true,
          )),
          DataCell(Text(s.lastSyncAt != null ? _formatDateTime(s.lastSyncAt!) : 'Never')),
          DataCell(Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              IconButton(icon: const Icon(Icons.visibility, size: 20), onPressed: () => _showSurveyorDetails(context, s), tooltip: 'View'),
              IconButton(icon: const Icon(Icons.edit, size: 20), onPressed: () => _showEditSurveyorDialog(context, s), tooltip: 'Edit'),
              IconButton(icon: Icon(Icons.face, size: 20, color: AppTheme.primaryColor), onPressed: () => _enrollFace(context, s), tooltip: 'Enroll Face'),
              IconButton(icon: Icon(Icons.delete_outline, size: 20, color: AppTheme.errorColor), onPressed: () => _confirmDelete(context, s), tooltip: 'Delete'),
            ],
          )),
        ])).toList(),
      ),
    );
  }
  
  Widget _buildPagination(int total, int page, int pageSize) {
    final totalPages = (total / pageSize).ceil();
    if (totalPages <= 1) return const SizedBox.shrink();
    
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          IconButton(icon: const Icon(Icons.chevron_left), onPressed: page > 1 ? () => setState(() => _currentPage = page - 1) : null),
          ...List.generate(totalPages, (index) {
            final pageNum = index + 1;
            if (pageNum == page || pageNum == 1 || pageNum == totalPages || (pageNum >= page - 1 && pageNum <= page + 1)) {
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: pageNum == page ? AppTheme.primaryColor : AppTheme.surfaceColor,
                    foregroundColor: pageNum == page ? Colors.white : AppTheme.textPrimary,
                    minimumSize: const Size(40, 40),
                  ),
                  onPressed: () => setState(() => _currentPage = pageNum),
                  child: Text(pageNum.toString()),
                ),
              );
            } else if (pageNum == page - 2 || pageNum == page + 2) {
              return const Padding(padding: EdgeInsets.symmetric(horizontal: 4), child: Text('...', style: TextStyle(color: AppTheme.textMuted)));
            }
            return const SizedBox.shrink();
          }),
          IconButton(icon: const Icon(Icons.chevron_right), onPressed: page < totalPages ? () => setState(() => _currentPage = page + 1) : null),
        ],
      ),
    );
  }
  
  void _showCreateSurveyorDialog(BuildContext context) {
    showDialog(context: context, builder: (context) => _SurveyorFormDialog(onSubmit: () => ref.invalidate(surveyorsProvider)));
  }
  
  void _showEditSurveyorDialog(BuildContext context, Surveyor surveyor) {
    showDialog(context: context, builder: (context) => _SurveyorFormDialog(surveyor: surveyor, onSubmit: () => ref.invalidate(surveyorsProvider)));
  }
  
  void _showSurveyorDetails(BuildContext context, Surveyor surveyor) {
    showDialog(context: context, builder: (context) => _SurveyorDetailsDialog(surveyor: surveyor));
  }
  
  void _enrollFace(BuildContext context, Surveyor surveyor) {
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Face enrollment - camera access needed')));
  }
  
  void _confirmDelete(BuildContext context, Surveyor surveyor) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Surveyor'),
        content: Text('Delete "${surveyor.fullName}"? This cannot be undone.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(style: FilledButton.styleFrom(backgroundColor: AppTheme.errorColor), onPressed: () { Navigator.pop(context); ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${surveyor.fullName} deleted'))); }, child: const Text('Delete')),
        ],
      ),
    );
  }
  
  String _formatDateTime(DateTime date) => '${date.day}/${date.month}/${date.year} ${date.hour.toString().padLeft(2,'0')}:${date.minute.toString().padLeft(2,'0')}';
}

class _SurveyorFormDialog extends ConsumerStatefulWidget {
  final Surveyor? surveyor;
  final VoidCallback onSubmit;
  const _SurveyorFormDialog({this.surveyor, required this.onSubmit});
  
  @override
  ConsumerState<_SurveyorFormDialog> createState() => _SurveyorFormDialogState();
}

class _SurveyorFormDialogState extends ConsumerState<_SurveyorFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _employeeIdController;
  late final TextEditingController _nameController;
  late final TextEditingController _emailController;
  late final TextEditingController _phoneController;
  String _department = 'FIELD_OPS';
  bool _isActive = true;
  bool _isLoading = false;
  
  @override
  void initState() {
    super.initState();
    final s = widget.surveyor;
    _employeeIdController = TextEditingController(text: s?.employeeId ?? '');
    _nameController = TextEditingController(text: s?.fullName ?? '');
    _emailController = TextEditingController(text: s?.email ?? '');
    _phoneController = TextEditingController(text: s?.phoneNumber ?? '');
    _department = s?.department ?? 'FIELD_OPS';
    _isActive = s?.isActive ?? true;
  }
  
  @override
  void dispose() {
    _employeeIdController.dispose(); _nameController.dispose(); _emailController.dispose(); _phoneController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.surveyor == null ? 'Add Surveyor' : 'Edit Surveyor'),
      content: SizedBox(width: 500, child: Form(key: _formKey, child: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
        TextFormField(controller: _employeeIdController, decoration: const InputDecoration(labelText: 'Employee ID *'), validator: (v) => v?.isEmpty ?? true ? 'Required' : null),
        const SizedBox(height: 16),
        TextFormField(controller: _nameController, decoration: const InputDecoration(labelText: 'Full Name *'), validator: (v) => v?.isEmpty ?? true ? 'Required' : null),
        const SizedBox(height: 16),
        TextFormField(controller: _emailController, decoration: const InputDecoration(labelText: 'Email *'), keyboardType: TextInputType.emailAddress, validator: (v) => v?.isEmpty ?? true ? 'Required' : (v!.contains('@') ? null : 'Invalid email')),
        const SizedBox(height: 16),
        TextFormField(controller: _phoneController, decoration: const InputDecoration(labelText: 'Phone *'), keyboardType: TextInputType.phone, validator: (v) => v?.isEmpty ?? true ? 'Required' : null),
        const SizedBox(height: 16),
        DropdownButtonFormField<String>(initialValue: _department, decoration: const InputDecoration(labelText: 'Department'), items: const [
          DropdownMenuItem(value: 'FIELD_OPS', child: Text('Field Operations')),
          DropdownMenuItem(value: 'QUALITY', child: Text('Quality Control')),
          DropdownMenuItem(value: 'SUPERVISION', child: Text('Supervision')),
        ], onChanged: (v) => setState(() => _department = v!)),
        const SizedBox(height: 16),
        SwitchListTile(title: const Text('Active'), value: _isActive, onChanged: (v) => setState(() => _isActive = v), contentPadding: EdgeInsets.zero),
      ])))),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(onPressed: _isLoading ? null : _submit, child: _isLoading ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : Text(widget.surveyor == null ? 'Create' : 'Update')),
      ],
    );
  }
  
  void _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 1));
    if (mounted) { Navigator.pop(context); widget.onSubmit(); ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(widget.surveyor == null ? 'Surveyor created' : 'Surveyor updated'))); }
  }
}

class _SurveyorDetailsDialog extends StatelessWidget {
  final Surveyor surveyor;
  const _SurveyorDetailsDialog({required this.surveyor});
  
  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(children: [AppAvatar(name: surveyor.fullName, radius: 24), const SizedBox(width: 12), Expanded(child: Text(surveyor.fullName))]),
      content: SizedBox(width: 500, child: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
        _detail('Employee ID', surveyor.employeeId),
        _detail('Email', surveyor.email),
        _detail('Phone', surveyor.phoneNumber),
        _detail('Department', surveyor.department),
        _detail('Face Templates', '${surveyor.faceTemplates.length} (${surveyor.activeFaceTemplate != null ? 'Active' : 'None'})'),
        _detail('Status', surveyor.isActive ? 'Active' : 'Inactive'),
        _detail('Created', '${surveyor.createdAt.day}/${surveyor.createdAt.month}/${surveyor.createdAt.year}'),
        _detail('Last Sync', surveyor.lastSyncAt != null ? '${surveyor.lastSyncAt!.day}/${surveyor.lastSyncAt!.month}/${surveyor.lastSyncAt!.year} ${surveyor.lastSyncAt!.hour.toString().padLeft(2,'0')}:${surveyor.lastSyncAt!.minute.toString().padLeft(2,'0')}' : 'Never'),
      ]))),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
    );
  }
  
  Widget _detail(String label, String value) => Padding(padding: const EdgeInsets.symmetric(vertical: 6), child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [SizedBox(width: 120, child: Text(label, style: const TextStyle(fontWeight: FontWeight.w500, color: AppTheme.textSecondary))), Expanded(child: Text(value))]));
}