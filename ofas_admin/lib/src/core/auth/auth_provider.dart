import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ofas_admin/src/core/models/user.dart';
import 'package:ofas_admin/src/core/api/api_client.dart';
import 'package:ofas_admin/src/core/api/dio_client.dart';
import 'package:ofas_admin/src/core/storage/secure_storage.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(DioClient.instance);
});

final authStateProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(apiClientProvider));
});

sealed class AuthState {
  const AuthState();
}

class AuthStateInitial extends AuthState {
  const AuthStateInitial();
}

class AuthStateLoading extends AuthState {
  const AuthStateLoading();
}

class AuthStateAuthenticated extends AuthState {
  const AuthStateAuthenticated(this.user);
  final User user;
}

class AuthStateUnauthenticated extends AuthState {
  const AuthStateUnauthenticated();
}

class AuthStateError extends AuthState {
  const AuthStateError(this.message);
  final String message;
}

class AuthStateMfaRequired extends AuthState {
  const AuthStateMfaRequired(this.tempToken);
  final String tempToken;
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiClient _apiClient;
  String? _pendingMfaTempToken;
  
  AuthNotifier(this._apiClient) : super(const AuthStateInitial()) {
    _checkAuthStatus();
  }
  
  Future<void> _checkAuthStatus() async {
    final token = SecureStorage.getAccessToken();
    if (token != null && token.isNotEmpty) {
      try {
        final user = await _apiClient.getCurrentUser();
        state = AuthStateAuthenticated(user);
      } catch (_) {
        await SecureStorage.clearAll();
        state = const AuthStateUnauthenticated();
      }
    } else {
      state = const AuthStateUnauthenticated();
    }
  }
  
  Future<void> login(String username, String password, {String? totpCode}) async {
    state = const AuthStateLoading();
    _pendingMfaTempToken = null;
    try {
      final request = LoginRequest(username: username, password: password, totpCode: totpCode);
      final tokens = await _apiClient.login(request);
      
      await SecureStorage.saveTokens(tokens.accessToken, tokens.refreshToken);
      
      final user = await _apiClient.getCurrentUser();
      state = AuthStateAuthenticated(user);
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        final data = e.response?.data;
        if (data is Map && data['mfa_required'] == true) {
          _pendingMfaTempToken = data['temp_token'] ?? '';
          state = AuthStateMfaRequired(_pendingMfaTempToken!);
          return;
        }
      }
      state = AuthStateError(e.message ?? 'Login failed');
    } catch (e) {
      state = AuthStateError(e.toString());
    }
  }
  
  Future<void> verifyMfa(String code) async {
    state = const AuthStateLoading();
    try {
      final tempToken = _pendingMfaTempToken ?? '';
      await _apiClient.verifyMfa(code, tempToken);
      final user = await _apiClient.getCurrentUser();
      _pendingMfaTempToken = null;
      state = AuthStateAuthenticated(user);
    } catch (e) {
      state = AuthStateError(e.toString());
    }
  }
  
  Future<void> logout() async {
    try {
      await _apiClient.logout();
    } catch (_) {}
    await SecureStorage.clearAll();
    state = const AuthStateUnauthenticated();
  }
  
  Future<void> refreshUser() async {
    try {
      final user = await _apiClient.getCurrentUser();
      if (state is AuthStateAuthenticated) {
        state = AuthStateAuthenticated(user);
      }
    } catch (_) {}
  }
  
  bool get isAuthenticated => state is AuthStateAuthenticated;
  bool get isSuperAdmin => state is AuthStateAuthenticated && (state as AuthStateAuthenticated).user.role == 'SUPER_ADMIN';
  bool get isAdmin => state is AuthStateAuthenticated && (state as AuthStateAuthenticated).user.role == 'ADMIN';
  User? get currentUser => state is AuthStateAuthenticated ? (state as AuthStateAuthenticated).user : null;
}