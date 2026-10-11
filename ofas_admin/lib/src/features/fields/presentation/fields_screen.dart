import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ofas_admin/src/core/auth/auth_provider.dart';
import 'package:ofas_admin/src/shared/theme/app_theme.dart';
import 'package:ofas_admin/src/shared/widgets/common_widgets.dart';
import 'package:ofas_admin/src/core/api/api_client.dart';
import 'package:ofas_admin/src/core/models/field.dart';

final fieldsProvider = FutureProvider.autoDispose.family<FieldListResponse, Map<String, dynamic>>((ref, params) async {
  final apiClient = ref.read(apiClientProvider);
  return apiClient.getFields(
    page: params['page'] ?? 1,
    pageSize: params['pageSize'] ?? 20,
    search: params['search'],
    cropType: params['cropType'],
    season: params['season'],
    isActive: params['isActive'],
  );
});

class FieldsScreen extends ConsumerStatefulWidget {
  const FieldsScreen({super.key});
  
  @override
  ConsumerState<FieldsScreen> createState() => _FieldsScreenState();
}

class _FieldsScreenState extends ConsumerState<FieldsScreen> {
  final _searchController = TextEditingController();
  int _currentPage = 1;
  String _searchQuery = '';
  String? _selectedCropType;
  String? _selectedSeason;
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
      'cropType': _selectedCropType,
      'season': _selectedSeason,
      'isActive': _isActive,
    };
    
    final fieldsAsync = ref.watch(fieldsProvider(params));
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fields Management'),
        actions: [
          FilledButton.icon(
            onPressed: () => _showCreateFieldDialog(context),
            icon: const Icon(Icons.add),
            label: const Text('Add Field'),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Column(
        children: [
          // Search & Filters
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
                      hintText: 'Search fields...',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: _searchQuery.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              _searchController.clear();
                              setState(() => _searchQuery = '');
                            },
                          )
                        : null,
                    ),
                    onSubmitted: (value) => setState(() => _searchQuery = value),
                  ),
                ),
                const SizedBox(width: 16),
                SizedBox(
                  width: 180,
                  child: DropdownButtonFormField<String?>(
                    initialValue: _selectedCropType,
                    decoration: const InputDecoration(labelText: 'Crop Type', prefixIcon: Icon(Icons.agriculture)),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('All Crops')),
                      const DropdownMenuItem(value: 'WHEAT', child: Text('Wheat')),
                      const DropdownMenuItem(value: 'RICE', child: Text('Rice')),
                      const DropdownMenuItem(value: 'CORN', child: Text('Corn')),
                      const DropdownMenuItem(value: 'COTTON', child: Text('Cotton')),
                    ],
                    onChanged: (value) => setState(() => _selectedCropType = value),
                  ),
                ),
                const SizedBox(width: 16),
                SizedBox(
                  width: 150,
                  child: DropdownButtonFormField<String?>(
                    initialValue: _selectedSeason,
                    decoration: const InputDecoration(labelText: 'Season', prefixIcon: Icon(Icons.wb_sunny_outlined)),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('All Seasons')),
                      const DropdownMenuItem(value: 'RABI', child: Text('Rabi')),
                      const DropdownMenuItem(value: 'KHARIF', child: Text('Kharif')),
                      const DropdownMenuItem(value: 'ZAYED', child: Text('Zayed')),
                    ],
                    onChanged: (value) => setState(() => _selectedSeason = value),
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
                    onChanged: (value) => setState(() => _isActive = value),
                  ),
                ),
              ],
            ),
          ),
          
          // Fields Table
          Expanded(
            child: fieldsAsync.when(
              data: (response) => _buildFieldsTable(context, response),
              loading: () => const AppLoadingState(message: 'Loading fields...'),
              error: (error, _) => AppErrorState(message: error.toString(), onRetry: () => ref.invalidate(fieldsProvider(params))),
            ),
          ),
          
          // Pagination
          fieldsAsync.when(
            data: (response) => _buildPagination(response.total, response.page, response.pageSize),
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
        ],
      ),
    );
  }
  
  Widget _buildFieldsTable(BuildContext context, FieldListResponse response) {
    if (response.fields.isEmpty) {
      return const AppEmptyState(
        icon: Icons.agriculture_outlined,
        title: 'No Fields Found',
        message: 'Create your first field to get started',
      );
    }
    
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Name')),
          DataColumn(label: Text('Crop/Season')),
          DataColumn(label: Text('Location')),
          DataColumn(label: Text('Radius')),
          DataColumn(label: Text('Photos')),
          DataColumn(label: Text('Status')),
          DataColumn(label: Text('Created')),
          DataColumn(label: Text('Actions')),
        ],
        rows: response.fields.map((field) => DataRow(cells: [
          DataCell(Text(field.name, style: const TextStyle(fontWeight: FontWeight.w500))),
          DataCell(Text('${field.cropType} / ${field.season}')),
          DataCell(Text('${field.centerLatitude.toStringAsFixed(4)}, ${field.centerLongitude.toStringAsFixed(4)}')),
          DataCell(Text('${field.radiusMeters.toInt()}m')),
          DataCell(Text('${field.referencePhotos.length}')),
          DataCell(AppStatusChip(
            label: field.isActive ? 'Active' : 'Inactive',
            type: field.isActive ? StatusType.success : StatusType.neutral,
            small: true,
          )),
          DataCell(Text(_formatDate(field.createdAt))),
          DataCell(Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              IconButton(
                icon: const Icon(Icons.visibility, size: 20),
                onPressed: () => _showFieldDetails(context, field),
                tooltip: 'View Details',
              ),
              IconButton(
                icon: const Icon(Icons.edit, size: 20),
                onPressed: () => _showEditFieldDialog(context, field),
                tooltip: 'Edit',
              ),
              IconButton(
                icon: Icon(Icons.delete_outline, size: 20, color: AppTheme.errorColor),
                onPressed: () => _confirmDeleteField(context, field),
                tooltip: 'Delete',
              ),
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
          IconButton(
            icon: const Icon(Icons.chevron_left),
            onPressed: page > 1 ? () => setState(() => _currentPage = page - 1) : null,
          ),
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
              return const Padding(
                padding: EdgeInsets.symmetric(horizontal: 4),
                child: Text('...', style: TextStyle(color: AppTheme.textMuted)),
              );
            }
            return const SizedBox.shrink();
          }),
          IconButton(
            icon: const Icon(Icons.chevron_right),
            onPressed: page < totalPages ? () => setState(() => _currentPage = page + 1) : null,
          ),
        ],
      ),
    );
  }
  
  void _showCreateFieldDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => _FieldFormDialog(onSubmit: () => ref.invalidate(fieldsProvider)),
    );
  }
  
  void _showEditFieldDialog(BuildContext context, Field field) {
    showDialog(
      context: context,
      builder: (context) => _FieldFormDialog(field: field, onSubmit: () => ref.invalidate(fieldsProvider)),
    );
  }
  
  void _showFieldDetails(BuildContext context, Field field) {
    showDialog(
      context: context,
      builder: (context) => _FieldDetailsDialog(field: field),
    );
  }
  
  void _confirmDeleteField(BuildContext context, Field field) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Field'),
        content: Text('Are you sure you want to delete "${field.name}"? This action cannot be undone.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: AppTheme.errorColor),
            onPressed: () {
              Navigator.pop(context);
              // TODO: Implement delete
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Field "${field.name}" deleted')),
              );
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
  
  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

class _FieldFormDialog extends ConsumerStatefulWidget {
  final Field? field;
  final VoidCallback onSubmit;
  
  const _FieldFormDialog({this.field, required this.onSubmit});
  
  @override
  ConsumerState<_FieldFormDialog> createState() => _FieldFormDialogState();
}

class _FieldFormDialogState extends ConsumerState<_FieldFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  late final TextEditingController _descriptionController;
  late final TextEditingController _latController;
  late final TextEditingController _lngController;
  late final TextEditingController _radiusController;
  String _cropType = 'WHEAT';
  String _season = 'RABI';
  bool _isActive = true;
  bool _isLoading = false;
  
  @override
  void initState() {
    super.initState();
    final f = widget.field;
    _nameController = TextEditingController(text: f?.name ?? '');
    _descriptionController = TextEditingController(text: f?.description ?? '');
    _latController = TextEditingController(text: f?.centerLatitude.toString() ?? '');
    _lngController = TextEditingController(text: f?.centerLongitude.toString() ?? '');
    _radiusController = TextEditingController(text: f?.radiusMeters.toString() ?? '');
    _cropType = f?.cropType ?? 'WHEAT';
    _season = f?.season ?? 'RABI';
    _isActive = f?.isActive ?? true;
  }
  
  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _latController.dispose();
    _lngController.dispose();
    _radiusController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.field == null ? 'Create Field' : 'Edit Field'),
      content: SizedBox(
        width: 500,
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(labelText: 'Field Name *', hintText: 'e.g., Field 1 - North Block'),
                  validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _descriptionController,
                  decoration: const InputDecoration(labelText: 'Description', hintText: 'Field details, landmarks, etc.'),
                  maxLines: 3,
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _latController,
                        decoration: const InputDecoration(labelText: 'Latitude *', hintText: 'e.g., 28.6139'),
                        keyboardType: const TextInputType.numberWithOptions(decimal: true, signed: true),
                        validator: (v) {
                          if (v?.isEmpty ?? true) return 'Required';
                          final val = double.tryParse(v!);
                          if (val == null || val < -90 || val > 90) return 'Invalid latitude';
                          return null;
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: TextFormField(
                        controller: _lngController,
                        decoration: const InputDecoration(labelText: 'Longitude *', hintText: 'e.g., 77.2090'),
                        keyboardType: const TextInputType.numberWithOptions(decimal: true, signed: true),
                        validator: (v) {
                          if (v?.isEmpty ?? true) return 'Required';
                          final val = double.tryParse(v!);
                          if (val == null || val < -180 || val > 180) return 'Invalid longitude';
                          return null;
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _radiusController,
                  decoration: const InputDecoration(labelText: 'Radius (meters) *', hintText: 'e.g., 100'),
                  keyboardType: TextInputType.number,
                  validator: (v) {
                    if (v?.isEmpty ?? true) return 'Required';
                    final val = int.tryParse(v!);
                    if (val == null || val < 10 || val > 5000) return '10-5000m';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        initialValue: _cropType,
                        decoration: const InputDecoration(labelText: 'Crop Type'),
                        items: const [
                          DropdownMenuItem(value: 'WHEAT', child: Text('Wheat')),
                          DropdownMenuItem(value: 'RICE', child: Text('Rice')),
                          DropdownMenuItem(value: 'CORN', child: Text('Corn')),
                          DropdownMenuItem(value: 'COTTON', child: Text('Cotton')),
                          DropdownMenuItem(value: 'OTHER', child: Text('Other')),
                        ],
                        onChanged: (v) => setState(() => _cropType = v!),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        initialValue: _season,
                        decoration: const InputDecoration(labelText: 'Season'),
                        items: const [
                          DropdownMenuItem(value: 'RABI', child: Text('Rabi')),
                          DropdownMenuItem(value: 'KHARIF', child: Text('Kharif')),
                          DropdownMenuItem(value: 'ZAYED', child: Text('Zayed')),
                        ],
                        onChanged: (v) => setState(() => _season = v!),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                SwitchListTile(
                  title: const Text('Active'),
                  value: _isActive,
                  onChanged: (v) => setState(() => _isActive = v),
                  contentPadding: EdgeInsets.zero,
                ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: _isLoading ? null : _submit,
          child: _isLoading
            ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
            : Text(widget.field == null ? 'Create' : 'Update'),
        ),
      ],
    );
  }
  
  void _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    
    // TODO: Call API
    await Future.delayed(const Duration(seconds: 1));
    
    if (mounted) {
      Navigator.pop(context);
      widget.onSubmit();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(widget.field == null ? 'Field created' : 'Field updated')),
      );
    }
  }
}

class _FieldDetailsDialog extends StatelessWidget {
  final Field field;
  
  const _FieldDetailsDialog({required this.field});
  
  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(field.name),
      content: SizedBox(
        width: 500,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDetailRow('Description', field.description),
              _buildDetailRow('Crop Type', field.cropType),
              _buildDetailRow('Season', field.season),
              _buildDetailRow('Center', '${field.centerLatitude.toStringAsFixed(6)}, ${field.centerLongitude.toStringAsFixed(6)}'),
              _buildDetailRow('Radius', '${field.radiusMeters}m'),
              _buildDetailRow('Reference Photos', '${field.referencePhotos.length}'),
              _buildDetailRow('Status', field.isActive ? 'Active' : 'Inactive'),
              _buildDetailRow('Created', '${field.createdAt.day}/${field.createdAt.month}/${field.createdAt.year}'),
              if (field.updatedAt != null)
                _buildDetailRow('Updated', '${field.updatedAt!.day}/${field.updatedAt!.month}/${field.updatedAt!.year}'),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close')),
      ],
    );
  }
  
  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label, style: const TextStyle(fontWeight: FontWeight.w500, color: AppTheme.textSecondary)),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}