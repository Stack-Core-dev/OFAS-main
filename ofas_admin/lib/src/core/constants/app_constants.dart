class AppConstants {
  static const String appName = 'OFAS Admin';
  static const String appVersion = '1.0.0';
  
  // API
  static const String baseUrl = 'https://api.ofas.example.com/v1';
  static const Duration apiTimeout = Duration(seconds: 30);
  
  // Storage keys
  static const String tokenKey = 'auth_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'current_user';
  static const String biometricEnabledKey = 'biometric_enabled';
  
  // Roles
  static const String roleSuperAdmin = 'SUPER_ADMIN';
  static const String roleAdmin = 'ADMIN';
  static const String roleSurveyor = 'SURVEYOR';
  
  // Visit statuses
  static const String visitStatusQueued = 'QUEUED';
  static const String visitStatusSyncing = 'SYNCING';
  static const String visitStatusSynced = 'SYNCED';
  static const String visitStatusFailed = 'FAILED';
  static const String visitStatusValid = 'VALID';
  static const String visitStatusInvalid = 'INVALID';
  static const String visitStatusFlagged = 'FLAGGED';
  
  // Phone statuses
  static const String phoneStatusActive = 'ACTIVE';
  static const String phoneStatusBlocked = 'BLOCKED';
  static const String phoneStatusLost = 'LOST';
  
  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
  
  // Map
  static const double defaultMapZoom = 15.0;
  static const double minMapZoom = 10.0;
  static const double maxMapZoom = 19.0;
}