import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:network_info_plus/network_info_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/constants.dart';

/// Resolves, remembers, and exposes the backend base URL (no hardcoded PC IP).
class BackendUrlService extends ChangeNotifier {
  BackendUrlService._();
  static final BackendUrlService instance = BackendUrlService._();

  static const _savedUrlKey = 'backend_resolved_url_v2';
  static const _manualUrlKey = 'backend_manual_url_v2';
  static const _probePath = '/api/health';
  static const _probeTimeout = Duration(seconds: 2);

  String? _resolvedUrl;
  String? _manualUrl;
  bool _discovering = false;
  Future<String?>? _discoverFuture;

  bool get isDiscovering => _discovering;
  String? get resolvedUrl => _resolvedUrl;
  String? get manualUrl => _manualUrl;

  /// URL shown in settings / diagnostics.
  String get displayUrl =>
      _normalize(_resolvedUrl) ??
      _normalize(_manualUrl) ??
      AppConstants.compileTimeApiBaseUrl;

  bool get hasWorkingUrl => _normalize(_resolvedUrl) != null;

  Future<void> load() async {
    final p = await SharedPreferences.getInstance();
    _resolvedUrl = _normalize(p.getString(_savedUrlKey));
    _manualUrl = _normalize(p.getString(_manualUrlKey));
  }

  /// Call on app start — finds backend automatically on the local network.
  Future<String?> ensureResolved({Duration maxWait = const Duration(seconds: 18)}) async {
    if (_normalize(_resolvedUrl) != null) {
      final ok = await _probe(_resolvedUrl!);
      if (ok) return _resolvedUrl;
    }
    if (_normalize(_manualUrl) != null) {
      final ok = await _probe(_manualUrl!);
      if (ok) {
        await _persistResolved(_manualUrl!);
        return _resolvedUrl;
      }
    }
    return discover(maxWait: maxWait);
  }

  /// Parallel scan of likely URLs (saved, manual, compile-time, subnet, emulator).
  Future<String?> discover({Duration maxWait = const Duration(seconds: 18)}) async {
    if (_discovering && _discoverFuture != null) {
      return _discoverFuture;
    }
    _discovering = true;
    notifyListeners();

    _discoverFuture = _runDiscover(maxWait);
    try {
      return await _discoverFuture;
    } finally {
      _discovering = false;
      _discoverFuture = null;
      notifyListeners();
    }
  }

  Future<String?> _runDiscover(Duration maxWait) async {
    try {
      final candidates = await _allCandidates();
      final deadline = DateTime.now().add(maxWait);

      // Priority pass — one at a time, fast.
      for (final url in _priorityCandidates(candidates)) {
        if (DateTime.now().isAfter(deadline)) break;
        if (await _probe(url)) {
          await _persistResolved(url);
          return url;
        }
      }

      // Parallel batches for subnet / fallback hosts.
      final rest = candidates
          .where((c) => !_priorityCandidates(candidates).contains(c))
          .toList();
      const batchSize = 14;
      for (var i = 0; i < rest.length; i += batchSize) {
        if (DateTime.now().isAfter(deadline)) break;
        final batch = rest.skip(i).take(batchSize).toList();
        final found = await _probeFirst(batch);
        if (found != null) {
          await _persistResolved(found);
          return found;
        }
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  Future<bool> testUrl(String raw) async {
    final url = _normalize(raw);
    if (url == null) return false;
    return _probe(url);
  }

  Future<bool> saveManualUrl(String raw) async {
    final url = _normalize(raw);
    if (url == null) return false;
    if (!await _probe(url)) return false;
    _manualUrl = url;
    final p = await SharedPreferences.getInstance();
    await p.setString(_manualUrlKey, url);
    await _persistResolved(url);
    notifyListeners();
    return true;
  }

  Future<void> clearManualUrl() async {
    _manualUrl = null;
    final p = await SharedPreferences.getInstance();
    await p.remove(_manualUrlKey);
    notifyListeners();
  }

  /// Called after any successful API request.
  Future<void> rememberWorking(String base) async {
    final url = _normalize(base);
    if (url == null || url == _resolvedUrl) return;
    await _persistResolved(url);
    notifyListeners();
  }

  void invalidateResolved() {
    _resolvedUrl = null;
    notifyListeners();
  }

  /// Order for [ApiService] retries.
  List<String> orderedCandidates() {
    final seen = <String>{};
    final out = <String>[];
    void add(String? v) {
      final n = _normalize(v);
      if (n == null || !seen.add(n)) return;
      out.add(n);
    }

    add(_resolvedUrl);
    add(_manualUrl);
    add(AppConstants.devApiBaseUrlOverride);
    final env = const String.fromEnvironment('API_BASE_URL').trim();
    if (env.isNotEmpty) add(env);
    for (final c in _staticFallbacks()) {
      add(c);
    }
    return out;
  }

  List<String> _priorityCandidates(List<String> all) {
    final p = <String>[];
    void tryAdd(String? v) {
      final n = _normalize(v);
      if (n != null && all.contains(n) && !p.contains(n)) p.add(n);
    }

    tryAdd(_resolvedUrl);
    tryAdd(_manualUrl);
    tryAdd(AppConstants.devApiBaseUrlOverride);
    tryAdd(const String.fromEnvironment('API_BASE_URL'));
    tryAdd('http://10.0.2.2:8000');
    tryAdd('http://127.0.0.1:8000');
    return p;
  }

  Future<List<String>> _allCandidates() async {
    final seen = <String>{};
    final out = <String>[];
    void add(String? v) {
      final n = _normalize(v);
      if (n == null || !seen.add(n)) return;
      out.add(n);
    }

    add(_resolvedUrl);
    add(_manualUrl);
    add(AppConstants.devApiBaseUrlOverride);
    add(const String.fromEnvironment('API_BASE_URL'));

    for (final url in await _subnetCandidates()) {
      add(url);
    }
    for (final url in _staticFallbacks()) {
      add(url);
    }
    return out;
  }

  List<String> _staticFallbacks() => [
        'http://10.0.2.2:8000',
        'http://127.0.0.1:8000',
        'http://localhost:8000',
        'http://192.168.137.1:8000',
      ];

  Future<List<String>> _subnetCandidates() async {
    final urls = <String>[];
    try {
      final info = NetworkInfo();
      final wifiIp = await info.getWifiIP();
      if (wifiIp != null && wifiIp.contains('.')) {
        final parts = wifiIp.split('.');
        if (parts.length == 4) {
          final prefix = '${parts[0]}.${parts[1]}.${parts[2]}';
          final phoneLast = int.tryParse(parts[3]) ?? 0;
          final hosts = <int>{
            1,
            2,
            3,
            4,
            5,
            8,
            9,
            10,
            11,
            20,
            50,
            100,
            101,
            102,
            103,
            254,
            phoneLast,
          };
          for (final h in hosts) {
            if (h > 0 && h < 255) {
              urls.add('http://$prefix.$h:8000');
            }
          }
        }
      }
    } catch (_) {}
    return urls;
  }

  Future<String?> _probeFirst(List<String> urls) async {
    if (urls.isEmpty) return null;
    final completer = Completer<String?>();
    var pending = urls.length;

    void finish(String? result) {
      pending--;
      if (result != null && !completer.isCompleted) {
        completer.complete(result);
      } else if (pending == 0 && !completer.isCompleted) {
        completer.complete(null);
      }
    }

    for (final url in urls) {
      _probe(url).then((ok) => finish(ok ? url : null));
    }
    return completer.future;
  }

  Future<bool> _probe(String base) async {
    final normalized = _normalize(base);
    if (normalized == null) return false;
    try {
      final uri = Uri.parse('$normalized$_probePath');
      final r = await http.get(uri).timeout(_probeTimeout);
      if (r.statusCode != 200) return false;
      final j = jsonDecode(r.body);
      if (j is Map && j['status'] == 'ok') return true;
    } catch (_) {}
    return false;
  }

  Future<void> _persistResolved(String base) async {
    final url = _normalize(base);
    if (url == null) return;
    _resolvedUrl = url;
    final p = await SharedPreferences.getInstance();
    await p.setString(_savedUrlKey, url);
  }

  String? _normalize(String? raw) {
    if (raw == null) return null;
    var s = raw.trim();
    if (s.isEmpty) return null;
    if (!s.startsWith('http://') && !s.startsWith('https://')) {
      s = 'http://$s';
    }
    s = s.replaceAll(RegExp(r'/+$'), '');
    if (s.endsWith('/api')) {
      s = s.substring(0, s.length - 4);
    }
    return s;
  }
}
