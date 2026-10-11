import 'package:shared_preferences/shared_preferences.dart';
import 'package:ofas_admin/src/core/constants/app_constants.dart';

class SecureStorage {
  static SharedPreferences? _prefs;
  
  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }
  
  static SharedPreferences get _instance {
    if (_prefs == null) {
      throw StateError('SecureStorage not initialized. Call SecureStorage.init() first.');
    }
    return _prefs!;
  }
  
  // Tokens
  static Future<void> saveTokens(String accessToken, String refreshToken) async {
    await _instance.setString(AppConstants.tokenKey, accessToken);
    await _instance.setString(AppConstants.refreshTokenKey, refreshToken);
  }
  
  static String? getAccessToken() {
    return _instance.getString(AppConstants.tokenKey);
  }
  
  static String? getRefreshToken() {
    return _instance.getString(AppConstants.refreshTokenKey);
  }
  
  static Future<void> clearTokens() async {
    await _instance.remove(AppConstants.tokenKey);
    await _instance.remove(AppConstants.refreshTokenKey);
  }
  
  // User
  static Future<void> saveUser(Map<String, dynamic> userJson) async {
    await _instance.setString(AppConstants.userKey, userJson.toString());
  }
  
  static Map<String, dynamic>? getUser() {
    final userStr = _instance.getString(AppConstants.userKey);
    if (userStr == null) return null;
    // In production, use proper JSON parsing
    return {'data': userStr};
  }
  
  static Future<void> clearUser() async {
    await _instance.remove(AppConstants.userKey);
  }
  
  // Biometric
  static Future<void> setBiometricEnabled(bool enabled) async {
    await _instance.setBool(AppConstants.biometricEnabledKey, enabled);
  }
  
  static bool isBiometricEnabled() {
    return _instance.getBool(AppConstants.biometricEnabledKey) ?? false;
  }
  
  // Generic
  static Future<void> setString(String key, String value) async {
    await _instance.setString(key, value);
  }
  
  static String? getString(String key) {
    return _instance.getString(key);
  }
  
  static Future<void> setBool(String key, bool value) async {
    await _instance.setBool(key, value);
  }
  
  static bool? getBool(String key) {
    return _instance.getBool(key);
  }
  
  static Future<void> setInt(String key, int value) async {
    await _instance.setInt(key, value);
  }
  
  static int? getInt(String key) {
    return _instance.getInt(key);
  }
  
  static Future<void> remove(String key) async {
    await _instance.remove(key);
  }
  
  static Future<void> clearAll() async {
    await _instance.clear();
  }
}