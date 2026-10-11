import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ofas_admin/src/core/auth/auth_provider.dart';
import 'package:ofas_admin/src/core/storage/secure_storage.dart';
import 'package:ofas_admin/src/features/auth/presentation/login_screen.dart';
import 'package:ofas_admin/src/features/dashboard/presentation/dashboard_screen.dart';
import 'package:ofas_admin/src/features/fields/presentation/fields_screen.dart';
import 'package:ofas_admin/src/features/surveyors/presentation/surveyors_screen.dart';
import 'package:ofas_admin/src/features/phones/presentation/phones_screen.dart';
import 'package:ofas_admin/src/features/assignments/presentation/assignments_screen.dart';
import 'package:ofas_admin/src/features/visits/presentation/visits_screen.dart';
import 'package:ofas_admin/src/features/audit/presentation/audit_screen.dart';
import 'package:ofas_admin/src/shared/theme/app_theme.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);
  
  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final isLoggedIn = authState is AuthStateAuthenticated;
      final isLoginPage = state.matchedLocation == '/login';
      
      if (!isLoggedIn && !isLoginPage) {
        return '/login';
      }
      
      if (isLoggedIn && isLoginPage) {
        return '/dashboard';
      }
      
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/dashboard',
        builder: (context, state) => const DashboardScreen(),
        routes: [
          GoRoute(
            path: 'fields',
            builder: (context, state) => const FieldsScreen(),
          ),
          GoRoute(
            path: 'surveyors',
            builder: (context, state) => const SurveyorsScreen(),
          ),
          GoRoute(
            path: 'phones',
            builder: (context, state) => const PhonesScreen(),
          ),
          GoRoute(
            path: 'assignments',
            builder: (context, state) => const AssignmentsScreen(),
          ),
          GoRoute(
            path: 'visits',
            builder: (context, state) => const VisitsScreen(),
          ),
          GoRoute(
            path: 'audit',
            builder: (context, state) => const AuditScreen(),
          ),
        ],
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Page not found: ${state.error}'),
      ),
    ),
  );
});

class OFASAdminApp extends ConsumerWidget {
  const OFASAdminApp({super.key});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    
    return MaterialApp.router(
      title: 'OFAS Admin',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(
            textScaler: TextScaler.linear(MediaQuery.of(context).textScaler.scale(1.0).clamp(0.8, 1.2)),
          ),
          child: child!,
        );
      },
    );
  }
}