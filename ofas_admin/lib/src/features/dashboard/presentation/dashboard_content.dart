import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ofas_admin/src/core/auth/auth_provider.dart';
import 'package:ofas_admin/src/shared/theme/app_theme.dart';
import 'package:ofas_admin/src/shared/widgets/common_widgets.dart';
import 'package:ofas_admin/src/core/api/api_client.dart';
import 'package:ofas_admin/src/core/models/visit.dart';
import 'package:ofas_admin/src/features/fields/presentation/fields_screen.dart';
import 'package:ofas_admin/src/features/surveyors/presentation/surveyors_screen.dart';
import 'package:ofas_admin/src/features/phones/presentation/phones_screen.dart';
import 'package:ofas_admin/src/features/assignments/presentation/assignments_screen.dart';
import 'package:ofas_admin/src/features/visits/presentation/visits_screen.dart';
import 'package:ofas_admin/src/features/audit/presentation/audit_screen.dart';

final dashboardStatsProvider = FutureProvider.autoDispose<DashboardStats>((ref) async {
  final apiClient = ref.read(apiClientProvider);
  return apiClient.getDashboardStats();
});

final recentVisitsProvider = FutureProvider.autoDispose<List<Visit>>((ref) async {
  final apiClient = ref.read(apiClientProvider);
  return apiClient.getRecentVisits(limit: 5);
});

final pendingReviewsProvider = FutureProvider.autoDispose<List<Visit>>((ref) async {
  final apiClient = ref.read(apiClientProvider);
  return apiClient.getPendingReviews(limit: 5);
});

class NavigationItem {
  final IconData icon;
  final IconData selectedIcon;
  final String label;
  final String route;
  
  const NavigationItem({
    required this.icon,
    required this.selectedIcon,
    required this.label,
    required this.route,
  });
}

class DashboardContent extends ConsumerWidget {
  final int selectedIndex;
  final List<NavigationItem> navigationItems;
  
  const DashboardContent({
    super.key,
    required this.selectedIndex,
    required this.navigationItems,
  });
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentRoute = navigationItems[selectedIndex].route;
    
    if (currentRoute == '/dashboard') {
      return _buildDashboardView(context, ref);
    } else if (currentRoute == '/dashboard/fields') {
      return const FieldsScreen();
    } else if (currentRoute == '/dashboard/surveyors') {
      return const SurveyorsScreen();
    } else if (currentRoute == '/dashboard/phones') {
      return const PhonesScreen();
    } else if (currentRoute == '/dashboard/assignments') {
      return const AssignmentsScreen();
    } else if (currentRoute == '/dashboard/visits') {
      return const VisitsScreen();
    } else if (currentRoute == '/dashboard/audit') {
      return const AuditScreen();
    }
    
    return const Center(child: Text('Page not found'));
  }
  
  Widget _buildDashboardView(BuildContext context, WidgetRef ref) {
    final statsAsync = ref.watch(dashboardStatsProvider);
    final recentVisitsAsync = ref.watch(recentVisitsProvider);
    final pendingReviewsAsync = ref.watch(pendingReviewsProvider);
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Dashboard',
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Overview of field visit verification system',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: AppTheme.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              FilledButton.icon(
                onPressed: () => ref.invalidate(dashboardStatsProvider),
                icon: const Icon(Icons.refresh),
                label: const Text('Refresh'),
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // Stats Grid
          statsAsync.when(
            data: (stats) => _buildStatsGrid(context, stats),
            loading: () => _buildStatsSkeleton(),
            error: (error, _) => _buildErrorState(context, error.toString(), () => ref.invalidate(dashboardStatsProvider)),
          ),
          
          const SizedBox(height: 24),
          
          // Charts Row
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                flex: 2,
                child: _buildVisitsByStatusChart(context, statsAsync),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildVisitsByDayChart(context, statsAsync),
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // Recent Visits & Pending Reviews
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: _buildRecentVisitsCard(context, ref, recentVisitsAsync),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildPendingReviewsCard(context, ref, pendingReviewsAsync),
              ),
            ],
          ),
        ],
      ),
    );
  }
  
  Widget _buildStatsGrid(BuildContext context, DashboardStats stats) {
    return GridView.count(
      crossAxisCount: 4,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 1.3,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      children: [
        AppStatCard(
          title: 'Total Fields',
          value: stats.totalFields.toString(),
          icon: Icons.agriculture_outlined,
          iconColor: AppTheme.primaryColor,
          subtitle: '${stats.activeFields} active',
          onTap: () => context.go('/dashboard/fields'),
        ),
        AppStatCard(
          title: 'Surveyors',
          value: stats.totalSurveyors.toString(),
          icon: Icons.people_outlined,
          iconColor: AppTheme.secondaryColor,
          subtitle: '${stats.activeSurveyors} active',
          onTap: () => context.go('/dashboard/surveyors'),
        ),
        AppStatCard(
          title: 'Phones',
          value: stats.totalPhones.toString(),
          icon: Icons.phone_android_outlined,
          iconColor: AppTheme.accentColor,
          subtitle: '${stats.activePhones} active',
          onTap: () => context.go('/dashboard/phones'),
        ),
        AppStatCard(
          title: 'Sync Rate',
          value: '${(stats.syncRate * 100).toStringAsFixed(1)}%',
          icon: Icons.sync_outlined,
          iconColor: stats.syncRate > 0.9 ? AppTheme.successColor : AppTheme.warningColor,
          subtitle: 'Visits synced',
        ),
        AppStatCard(
          title: 'Total Visits',
          value: stats.totalVisits.toString(),
          icon: Icons.fact_check_outlined,
          iconColor: AppTheme.primaryColor,
          subtitle: '${stats.pendingVisits} pending',
          onTap: () => context.go('/dashboard/visits'),
        ),
        AppStatCard(
          title: 'Valid Visits',
          value: stats.validVisits.toString(),
          icon: Icons.check_circle_outlined,
          iconColor: AppTheme.successColor,
        ),
        AppStatCard(
          title: 'Invalid Visits',
          value: stats.invalidVisits.toString(),
          icon: Icons.cancel_outlined,
          iconColor: AppTheme.errorColor,
        ),
        AppStatCard(
          title: 'Flagged Visits',
          value: stats.flaggedVisits.toString(),
          icon: Icons.flag_outlined,
          iconColor: AppTheme.warningColor,
        ),
        AppStatCard(
          title: 'Today\'s Assignments',
          value: stats.todayAssignments.toString(),
          icon: Icons.assignment_outlined,
          iconColor: AppTheme.secondaryColor,
          subtitle: '${stats.completedToday} completed',
          onTap: () => context.go('/dashboard/assignments'),
        ),
        AppStatCard(
          title: 'Completion Rate',
          value: stats.todayAssignments > 0 
            ? '${((stats.completedToday / stats.todayAssignments) * 100).toStringAsFixed(1)}%' 
            : '0%',
          icon: Icons.trending_up_outlined,
          iconColor: AppTheme.successColor,
        ),
      ],
    );
  }
  
  Widget _buildStatsSkeleton() {
    return GridView.count(
      crossAxisCount: 4,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 1.3,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      children: List.generate(8, (index) => _buildStatCardSkeleton()),
    );
  }
  
  Widget _buildStatCardSkeleton() {
    return AppCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: AppTheme.surfaceColor,
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              const Spacer(),
              Container(
                width: 60,
                height: 12,
                decoration: BoxDecoration(
                  color: AppTheme.surfaceColor,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            width: 80,
            height: 28,
            decoration: BoxDecoration(
              color: AppTheme.surfaceColor,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(height: 4),
          Container(
            width: 100,
            height: 16,
            decoration: BoxDecoration(
              color: AppTheme.surfaceColor,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildErrorState(BuildContext context, String error, VoidCallback onRetry) {
    return AppCard(
      padding: const EdgeInsets.all(24),
      child: Center(
        child: Column(
          children: [
            Icon(Icons.error_outline, size: 48, color: AppTheme.errorColor),
            const SizedBox(height: 16),
            Text('Failed to load statistics', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Text(error, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppTheme.textSecondary)),
            const SizedBox(height: 16),
            FilledButton(onPressed: onRetry, child: const Text('Retry')),
          ],
        ),
      ),
    );
  }
  
  Widget _buildVisitsByStatusChart(BuildContext context, AsyncValue<DashboardStats> statsAsync) {
    return AppCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Visits by Status',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 20),
          statsAsync.when(
            data: (stats) => _buildStatusChartContent(context, stats),
            loading: () => const Center(
              child: SizedBox(height: 200, child: Center(child: CircularProgressIndicator())),
            ),
            error: (error, _) => Center(
              child: Text('Error loading chart: $error', style: TextStyle(color: AppTheme.errorColor)),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildStatusChartContent(BuildContext context, DashboardStats stats) {
    final total = stats.visitsByStatus.values.fold(0, (a, b) => a + b);
    if (total == 0) {
      return const SizedBox(
        height: 200,
        child: Center(child: Text('No visit data available')),
      );
    }
    
    final statusData = [
      ('Valid', stats.visitsByStatus['VALID'] ?? 0, AppTheme.successColor),
      ('Invalid', stats.visitsByStatus['INVALID'] ?? 0, AppTheme.errorColor),
      ('Flagged', stats.visitsByStatus['FLAGGED'] ?? 0, AppTheme.warningColor),
      ('Pending', stats.visitsByStatus['PENDING'] ?? 0, AppTheme.primaryColor),
      ('Failed', stats.visitsByStatus['FAILED'] ?? 0, AppTheme.textMuted),
    ];
    
    return Column(
      children: statusData.map((data) {
        final count = data.$2;
        final percentage = total > 0 ? (count / total) : 0.0;
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: data.$3,
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(child: Text(data.$1, style: Theme.of(context).textTheme.bodyMedium)),
                  Text('$count', style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600)),
                ],
              ),
              const SizedBox(height: 4),
              LinearProgressIndicator(
                value: percentage,
                backgroundColor: AppTheme.dividerColor,
                valueColor: AlwaysStoppedAnimation<Color>(data.$3),
                minHeight: 6,
                borderRadius: BorderRadius.circular(3),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
  
  Widget _buildVisitsByDayChart(BuildContext context, AsyncValue<DashboardStats> statsAsync) {
    return AppCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Visits (Last 7 Days)',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 20),
          statsAsync.when(
            data: (stats) => _buildDayChartContent(context, stats),
            loading: () => const Center(
              child: SizedBox(height: 200, child: Center(child: CircularProgressIndicator())),
            ),
            error: (error, _) => Center(
              child: Text('Error loading chart: $error', style: TextStyle(color: AppTheme.errorColor)),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildDayChartContent(BuildContext context, DashboardStats stats) {
    final days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    final visitsByDay = stats.visitsByDay;
    final maxVisits = visitsByDay.values.fold(0, (a, b) => a > b ? a : b);
    
    if (maxVisits == 0) {
      return const SizedBox(
        height: 200,
        child: Center(child: Text('No visit data')),
      );
    }
    
    return SizedBox(
      height: 200,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: days.map((day) {
          final count = visitsByDay[day] ?? 0;
          final height = maxVisits > 0 ? (count / maxVisits) * 160 : 0.0;
          
          return Column(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Text('$count', style: Theme.of(context).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w600)),
              const SizedBox(height: 4),
              Container(
                width: 32,
                height: height.clamp(4.0, 160.0),
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              const SizedBox(height: 8),
              Text(day, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppTheme.textMuted)),
            ],
          );
        }).toList(),
      ),
    );
  }
  
  Widget _buildRecentVisitsCard(BuildContext context, WidgetRef ref, AsyncValue<List<Visit>> visitsAsync) {
    return AppCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Recent Visits',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
              ),
              TextButton(
                onPressed: () => context.go('/dashboard/visits'),
                child: const Text('View All'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          visitsAsync.when(
            data: (visits) => visits.isEmpty
              ? const AppEmptyState(
                  icon: Icons.fact_check_outlined,
                  title: 'No Recent Visits',
                  message: 'Field visits will appear here',
                )
              : Column(
                  children: visits.map((visit) => _buildVisitListItem(context, visit)).toList(),
                ),
            loading: () => const Center(child: SizedBox(height: 100, child: Center(child: CircularProgressIndicator()))),
            error: (error, _) => Center(child: Text('Error: $error', style: TextStyle(color: AppTheme.errorColor))),
          ),
        ],
      ),
    );
  }
  
  Widget _buildPendingReviewsCard(BuildContext context, WidgetRef ref, AsyncValue<List<Visit>> visitsAsync) {
    return AppCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Text(
                    'Pending Review',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppTheme.warningColor.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      visitsAsync.when(data: (v) => v.length.toString(), loading: () => '0', error: (_, __) => '0'),
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppTheme.warningColor),
                    ),
                  ),
                ],
              ),
              TextButton(
                onPressed: () => context.go('/dashboard/visits?status=FLAGGED'),
                child: const Text('View All'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          visitsAsync.when(
            data: (visits) => visits.isEmpty
              ? const AppEmptyState(
                  icon: Icons.pending_outlined,
                  title: 'No Pending Reviews',
                  message: 'All visits reviewed',
                )
              : Column(
                  children: visits.map((visit) => _buildVisitListItem(context, visit, isPending: true)).toList(),
                ),
            loading: () => const Center(child: SizedBox(height: 100, child: Center(child: CircularProgressIndicator()))),
            error: (error, _) => Center(child: Text('Error: $error', style: TextStyle(color: AppTheme.errorColor))),
          ),
        ],
      ),
    );
  }
  
  Widget _buildVisitListItem(BuildContext context, Visit visit, {bool isPending = false}) {
    return InkWell(
      onTap: () => context.go('/dashboard/visits/${visit.id}'),
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Row(
          children: [
            AppAvatar(name: visit.surveyorId, radius: 20),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          'Field ${visit.fieldId}',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      AppStatusChip(
                        label: visit.status.name.toUpperCase(),
                        type: _getStatusType(visit.status),
                        small: true,
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${visit.surveyorId} • ${_formatDate(visit.completedAt)}',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppTheme.textMuted),
                  ),
                ],
              ),
            ),
            if (isPending)
              Icon(Icons.chevron_right, color: AppTheme.textMuted),
          ],
        ),
      ),
    );
  }
  
  StatusType _getStatusType(VisitStatus status) {
    switch (status) {
      case VisitStatus.valid:
        return StatusType.success;
      case VisitStatus.invalid:
        return StatusType.error;
      case VisitStatus.flagged:
        return StatusType.warning;
      case VisitStatus.queued:
      case VisitStatus.syncing:
      case VisitStatus.synced:
        return StatusType.info;
      case VisitStatus.failed:
        return StatusType.error;
      default:
        return StatusType.neutral;
    }
  }
  
  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    
    if (diff.inDays == 0) {
      return 'Today ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
    } else if (diff.inDays == 1) {
      return 'Yesterday';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}d ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}