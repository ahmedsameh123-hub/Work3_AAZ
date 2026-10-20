import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import 'backend_url_service.dart';
import 'token_storage.dart';

class ApiException implements Exception {
  ApiException(this.statusCode, this.body);
  final int statusCode;
  final String body;

  @override
  String toString() => 'ApiException($statusCode): $body';
}

class ApiService {
  ApiService._();

  static const Duration _requestTimeout = Duration(seconds: 12);
  static const Duration _fallbackProbeTimeout = Duration(seconds: 3);

  static String _normalizeBase(String base) {
    return base.replaceAll(RegExp(r'/$'), '');
  }

  static Uri _uFromBase(String base, String path, [Map<String, String>? query]) {
    final p = path.startsWith('/') ? path : '/$path';
    return Uri.parse('${_normalizeBase(base)}$p').replace(queryParameters: query);
  }

  static Future<Map<String, String>> _headers({bool auth = false}) async {
    final h = <String, String>{
      'Content-Type': 'application/json; charset=utf-8',
    };
    if (auth) {
      final t = await TokenStorage.getToken();
      if (t != null && t.isNotEmpty) h['Authorization'] = 'Bearer $t';
    }
    return h;
  }

  static List<String> _candidateBases() {
    return BackendUrlService.instance.orderedCandidates();
  }

  static Future<http.Response> _requestWithFallback({
    required String path,
    required Map<String, String> headers,
    required Future<http.Response> Function(Uri uri, Map<String, String> headers)
    perform,
    Duration? requestTimeout,
  }) async {
    Object? lastError;
    final candidates = _candidateBases();

    if (candidates.isEmpty) {
      throw ApiException(
        0,
        'No backend URL configured. Open Settings → App settings → set server address, '
        'or connect phone and PC to the same Wi‑Fi and restart the app.',
      );
    }

    for (var i = 0; i < candidates.length; i++) {
      final base = candidates[i];
      try {
        final timeout = requestTimeout ??
            (i == 0 ? _requestTimeout : _fallbackProbeTimeout);
        final response = await perform(_uFromBase(base, path), headers).timeout(
          timeout,
        );
        await BackendUrlService.instance.rememberWorking(base);
        return response;
      } catch (e) {
        lastError = e;
      }
    }

    // Last resort: full network scan (splash may have missed a new IP).
    if (!BackendUrlService.instance.isDiscovering) {
      final found = await BackendUrlService.instance.discover(
        maxWait: const Duration(seconds: 10),
      );
      if (found != null) {
        try {
          final response = await perform(
            _uFromBase(found, path),
            headers,
          ).timeout(requestTimeout ?? _requestTimeout);
          await BackendUrlService.instance.rememberWorking(found);
          return response;
        } catch (e) {
          lastError = e;
        }
      }
    }

    if (lastError is TimeoutException) {
      throw ApiException(
        0,
        'Cannot reach the server. Same Wi‑Fi as the laptop, backend running with '
        'uvicorn app.main:app --host 0.0.0.0 --port 8000, then open Settings → '
        'App settings → Server address → Auto-find or enter http://<PC_IP>:8000',
      );
    }
    throw lastError ?? Exception('Unable to reach backend');
  }

  static Future<http.Response> get(String path, {bool auth = true}) async {
    final headers = await _headers(auth: auth);
    return _requestWithFallback(
      path: path,
      headers: headers,
      perform: (uri, h) => http.get(uri, headers: h),
    );
  }

  static Future<http.Response> post(
    String path, {
    Object? body,
    bool auth = false,
    Duration? requestTimeout,
  }) async {
    final headers = await _headers(auth: auth);
    return _requestWithFallback(
      path: path,
      headers: headers,
      requestTimeout: requestTimeout,
      perform: (uri, h) =>
          http.post(uri, headers: h, body: body == null ? null : jsonEncode(body)),
    );
  }

  static Future<http.Response> patch(
    String path, {
    Object? body,
    bool auth = true,
  }) async {
    final headers = await _headers(auth: auth);
    return _requestWithFallback(
      path: path,
      headers: headers,
      perform: (uri, h) =>
          http.patch(uri, headers: h, body: body == null ? null : jsonEncode(body)),
    );
  }

  static Future<http.Response> delete(String path, {bool auth = true}) async {
    final headers = await _headers(auth: auth);
    return _requestWithFallback(
      path: path,
      headers: headers,
      perform: (uri, h) => http.delete(uri, headers: h),
    );
  }

  static String parseErrorBody(http.Response r) {
    try {
      final j = jsonDecode(r.body) as Map<String, dynamic>?;
      final d = j?['detail'];
      if (d is String) return d;
      if (d is List && d.isNotEmpty && d.first is Map) {
        final m = d.first as Map;
        return m['msg']?.toString() ?? r.body;
      }
    } catch (_) {}
    return r.body.isEmpty ? 'Request failed (${r.statusCode})' : r.body;
  }

  static String? parseDetailString(http.Response r) {
    try {
      final j = jsonDecode(r.body) as Map<String, dynamic>?;
      final d = j?['detail'];
      if (d is String) return d;
    } catch (_) {}
    return null;
  }
}
