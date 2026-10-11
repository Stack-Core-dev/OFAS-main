import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ofas_admin/src/core/auth/auth_provider.dart';
import 'package:ofas_admin/src/shared/theme/app_theme.dart';
import 'package:ofas_admin/src/shared/widgets/common_widgets.dart';
import 'package:ofas_admin/src/features/dashboard/presentation/dashboard_content.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});
  
  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  int _selectedIndex = 0;
  
  final List<NavigationItem> _navigationItems = const [
    NavigationItem(
      icon: Icons.dashboard_outlined,
      selectedIcon: Icons.dashboard,
      label: 'Dashboard',
      route: '/dashboard',
    ),
    NavigationItem(
      icon: Icons.agriculture_outlined,
      selectedIcon: Icons.agriculture,
      label: 'Fields',
      route: '/dashboard/fields',
    ),
    NavigationItem(
      icon: Icons.people_outlined,
      selectedIcon: Icons.people,
      label: 'Surveyors',
      route: '/dashboard/surveyors',
    ),
    NavigationItem(
      icon: Icons.phone_android_outlined,
      selectedIcon: Icons.phone_android,
      label: 'Phones',
      route: '/dashboard/phones',
    ),
    NavigationItem(
      icon: Icons.assignment_outlined,
      selectedIcon: Icons.assignment,
      label: 'Assignments',
      route: '/dashboard/assignments',
    ),
    NavigationItem(
      icon: Icons.fact_check_outlined,
      selectedIcon: Icons.fact_check,
      label: 'Visits',
      route: '/dashboard/visits',
    ),
    NavigationItem(
      icon: Icons.security_outlined,
      selectedIcon: Icons.security,
      label: 'Audit Log',
      route: '/dashboard/audit',
    ),
  ];
  
  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);
    final user = authState is AuthStateAuthenticated ? (authState as AuthStateAuthenticated).user : null;
    final isSuperAdmin = user?.role == 'SUPER_ADMIN';
    
    // Filter navigation items based on role
    final availableItems = _navigationItems.where((item) {
      if (item.label == 'Audit Log' && !isSuperAdmin) return false;
      return true;
    }).toList();
    
    return Scaffold(
      body: Row(
        children: [
          // Sidebar
          NavigationRail(
            selectedIndex: _selectedIndex.clamp(0, availableItems.length - 1),
            onDestinationSelected: (index) {
              setState(() => _selectedIndex = index);
              context.go(availableItems[index].route);
            },
            labelType: NavigationRailLabelType.all,
            leading: Padding(
              padding: const EdgeInsets.symmetric(vertical: 24),
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Icon(
                      Icons.verified_user_outlined,
                      size: 32,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'OFAS Admin',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                ],
              ),
            ),
            trailing: Expanded(
              child: Align(
                alignment: Alignment.bottomCenter,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Divider(),
                      ListTile(
                        leading: const CircleAvatar(
                          child: Icon(Icons.person, size: 20),
                        ),
                        title: Text(
                          user?.fullName ?? 'Admin',
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                        subtitle: Text(
                          user?.role ?? 'ADMIN',
                          style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                        ),
                        trailing: PopupMenuButton<String>(
                          onSelected: (value) {
                            if (value == 'logout') {
                              ref.read(authStateProvider.notifier).logout();
                            }
                          },
                          itemBuilder: (context) => [
                            const PopupMenuItem(
                              value: 'profile',
                              child: ListTile(
                                leading: Icon(Icons.person_outline),
                                title: Text('Profile'),
                                contentPadding: EdgeInsets.zero,
                              ),
                            ),
                            const PopupMenuItem(
                              value: 'settings',
                              child: ListTile(
                                leading: Icon(Icons.settings_outlined),
                                title: Text('Settings'),
                                contentPadding: EdgeInsets.zero,
                              ),
                            ),
                            const PopupMenuDivider(),
                            const PopupMenuItem(
                              value: 'logout',
                              child: ListTile(
                                leading: Icon(Icons.logout, color: AppTheme.errorColor),
                                title: Text('Logout', style: TextStyle(color: AppTheme.errorColor)),
                                contentPadding: EdgeInsets.zero,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            destinations: availableItems.map((item) {
              return NavigationRailDestination(
                icon: Icon(item.icon),
                selectedIcon: Icon(item.selectedIcon),
                label: Text(item.label),
              );
            }).toList(),
          ),
          
          const VerticalDivider(thickness: 1, width: 1),
          
          // Main Content
          Expanded(
            child: DashboardContent(
              selectedIndex: _selectedIndex,
              navigationItems: availableItems,
            ),
          ),
        ],
      ),
    );
  }
}