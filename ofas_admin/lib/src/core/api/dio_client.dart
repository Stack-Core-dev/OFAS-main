import 'package:dio/dio.dart';
import 'package:ofas_admin/src/core/constants/app_constants.dart';
import 'package:ofas_admin/src/core/storage/secure_storage.dart';

class DioClient {
  static Dio? _instance;
  
  static Dio get instance {
    _instance ??= _createDio();
    return _instance!;
  }
  
  static Dio _createDio() {
    final dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.baseUrl,
        connectTimeout: AppConstants.apiTimeout,
        receiveTimeout: AppConstants.apiTimeout,
        sendTimeout: AppConstants.apiTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );
    
    dio.interceptors.addAll([
      _AuthInterceptor(),
      _LoggingInterceptor(),
      _ErrorInterceptor(),
    ]);
    
    return dio;
  }
  
  static void reset() {
    _instance = null;
  }
}

class _AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final accessToken = SecureStorage.getAccessToken();
    if (accessToken != null && accessToken.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    return handler.next(options);
  }
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      final refreshed = await _tryRefreshToken();
      if (refreshed) {
        final newToken = SecureStorage.getAccessToken();
        if (newToken != null) {
          err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
          final cloneReq = await DioClient.instance.fetch(err.requestOptions);
          return handler.resolve(cloneReq);
        }
      }
      await SecureStorage.clearAll();
    }
    return handler.next(err);
  }
  
  Future<bool> _tryRefreshToken() async {
    final refreshToken = SecureStorage.getRefreshToken();
    if (refreshToken == null) return false;
    
    try {
      final dio = Dio(
        BaseOptions(
          baseUrl: AppConstants.baseUrl,
          connectTimeout: AppConstants.apiTimeout,
        ),
      );
      
      final response = await dio.post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );
      
      if (response.statusCode == 200) {
        final tokens = response.data;
        await SecureStorage.saveTokens(
          tokens['access_token'],
          tokens['refresh_token'],
        );
        return true;
      }
    } catch (_) {}
    return false;
  }
}

class _LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // debugPrint('🌐 REQUEST[${options.method}] => ${options.uri}');
    // if (options.data != null) {
    //   debugPrint('📤 DATA: ${options.data}');
    // }
    return handler.next(options);
  }
  
  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    // debugPrint('✅ RESPONSE[${response.statusCode}] => ${response.requestOptions.uri}');
    return handler.next(response);
  }
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // debugPrint('❌ ERROR[${err.response?.statusCode}] => ${err.requestOptions.uri}');
    // if (err.response?.data != null) {
    //   debugPrint('📥 ERROR DATA: ${err.response?.data}');
    // }
    return handler.next(err);
  }
}

class _ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    String message;
    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        message = 'Connection timeout. Please check your internet.';
        break;
      case DioExceptionType.badResponse:
        final statusCode = err.response?.statusCode;
        final data = err.response?.data;
        if (data is Map && data.containsKey('detail')) {
          message = data['detail'].toString();
        } else if (data is Map && data.containsKey('message')) {
          message = data['message'].toString();
        } else {
          message = 'Server error: $statusCode';
        }
        break;
      case DioExceptionType.cancel:
        message = 'Request cancelled';
        break;
      case DioExceptionType.unknown:
        message = 'Network error. Please check your connection.';
        break;
      default:
        message = 'An unexpected error occurred';
    }
    // Create a new error instead of modifying the final field
    final apiError = ApiError(message: message, originalError: err);
    // We can't modify err.error as it's final, so we just pass the error through
    handler.next(err);
  }
}

class ApiError implements Exception {
  final String message;
  final DioException? originalError;
  
  ApiError({required this.message, this.originalError});
  
  @override
  String toString() => message;
}