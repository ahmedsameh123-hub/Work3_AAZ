class AppConstants {
  static const String appName = "TrainMate";

  /// Optional compile-time override (rare). Prefer Settings → server URL in the app.
  static const String devApiBaseUrlOverride = '';

  /// From `--dart-define=API_BASE_URL=...` or empty.
  static String get compileTimeApiBaseUrl {
    final o = devApiBaseUrlOverride.trim();
    if (o.isNotEmpty) return o;
    const env = String.fromEnvironment('API_BASE_URL');
    if (env.trim().isNotEmpty) return env.trim();
    return '(auto-discover on launch)';
  }

  @Deprecated('Use BackendUrlService.instance.orderedCandidates()')
  static List<String> get apiBaseUrlCandidates =>
      const [String.fromEnvironment('API_BASE_URL')];
}
