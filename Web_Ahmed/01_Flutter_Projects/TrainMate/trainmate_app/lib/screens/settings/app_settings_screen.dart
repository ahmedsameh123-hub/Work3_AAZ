import 'package:flutter/material.dart';

import '../../l10n/app_text.dart';
import '../../services/app_preferences_service.dart';
import '../../services/app_status_service.dart';
import '../../services/backend_url_service.dart';

class AppSettingsScreen extends StatefulWidget {
  const AppSettingsScreen({super.key});

  @override
  State<AppSettingsScreen> createState() => _AppSettingsScreenState();
}

class _AppSettingsScreenState extends State<AppSettingsScreen> {
  BackendHealth? _health;
  bool? _mlOnServer;
  bool _loadingDiag = true;
  late final TextEditingController _serverUrlCtrl;
  String? _serverMsg;
  bool _serverMsgOk = false;
  bool _busyServer = false;

  @override
  void initState() {
    super.initState();
    _serverUrlCtrl = TextEditingController(
      text: BackendUrlService.instance.displayUrl,
    );
    BackendUrlService.instance.addListener(_onBackendUrlChanged);
    _refreshDiagnostics();
  }

  @override
  void dispose() {
    BackendUrlService.instance.removeListener(_onBackendUrlChanged);
    _serverUrlCtrl.dispose();
    super.dispose();
  }

  void _onBackendUrlChanged() {
    if (!mounted) return;
    setState(() {
      _serverUrlCtrl.text = BackendUrlService.instance.displayUrl;
    });
  }

  Future<void> _refreshDiagnostics() async {
    setState(() => _loadingDiag = true);
    final h = await AppStatusService.instance.fetchBackendHealth();
    final m = await AppStatusService.instance.fetchMlServerAvailable();
    if (!mounted) return;
    setState(() {
      _health = h;
      _mlOnServer = m;
      _loadingDiag = false;
    });
  }

  Future<void> _autoFindServer(AppText t) async {
    setState(() {
      _busyServer = true;
      _serverMsg = t.tr('settings.discoveringServer');
      _serverMsgOk = false;
    });
    BackendUrlService.instance.invalidateResolved();
    final found = await BackendUrlService.instance.discover();
    if (!mounted) return;
    setState(() {
      _busyServer = false;
      if (found != null) {
        _serverUrlCtrl.text = found;
        _serverMsg = t.tr('settings.serverSaved');
        _serverMsgOk = true;
      } else {
        _serverMsg = t.tr('settings.serverTestFail');
        _serverMsgOk = false;
      }
    });
    await _refreshDiagnostics();
  }

  Future<void> _testServer(AppText t) async {
    setState(() {
      _busyServer = true;
      _serverMsg = null;
    });
    final ok = await BackendUrlService.instance.testUrl(_serverUrlCtrl.text);
    if (!mounted) return;
    setState(() {
      _busyServer = false;
      _serverMsgOk = ok;
      _serverMsg = ok ? t.tr('settings.serverTestOk') : t.tr('settings.serverTestFail');
    });
  }

  Future<void> _saveServerUrl(AppText t) async {
    setState(() {
      _busyServer = true;
      _serverMsg = null;
    });
    final ok = await BackendUrlService.instance.saveManualUrl(_serverUrlCtrl.text);
    if (!mounted) return;
    setState(() {
      _busyServer = false;
      _serverMsgOk = ok;
      _serverMsg = ok ? t.tr('settings.serverSaved') : t.tr('settings.serverTestFail');
    });
    if (ok) await _refreshDiagnostics();
  }

  @override
  Widget build(BuildContext context) {
    final prefs = AppPreferencesService.instance;
    return AnimatedBuilder(
      animation: prefs,
      builder: (context, child) {
        final t = AppText.of(context);
        final baseUrl = BackendUrlService.instance.displayUrl;
        final discovering = BackendUrlService.instance.isDiscovering;
        return Scaffold(
          appBar: AppBar(
            title: Text(t.tr('settings.appSettings')),
            actions: [
              IconButton(
                onPressed: _loadingDiag || _busyServer ? null : _refreshDiagnostics,
                icon: _loadingDiag
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.refresh_rounded),
                tooltip: t.tr('settings.refreshDiag'),
              ),
            ],
          ),
          body: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        t.tr('settings.backendDiagnostics'),
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        t.tr('settings.serverUrlHelp'),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              height: 1.35,
                            ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _serverUrlCtrl,
                        decoration: InputDecoration(
                          labelText: t.tr('settings.serverUrl'),
                          hintText: t.tr('settings.serverUrlHint'),
                          border: const OutlineInputBorder(),
                        ),
                        keyboardType: TextInputType.url,
                        autocorrect: false,
                        enabled: !_busyServer && !discovering,
                      ),
                      const SizedBox(height: 10),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          FilledButton.tonalIcon(
                            onPressed: _busyServer || discovering
                                ? null
                                : () => _autoFindServer(t),
                            icon: discovering
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  )
                                : const Icon(Icons.radar_rounded, size: 18),
                            label: Text(t.tr('settings.autoFindServer')),
                          ),
                          OutlinedButton(
                            onPressed: _busyServer || discovering
                                ? null
                                : () => _testServer(t),
                            child: Text(t.tr('settings.testServer')),
                          ),
                          FilledButton(
                            onPressed: _busyServer || discovering
                                ? null
                                : () => _saveServerUrl(t),
                            child: Text(t.tr('settings.saveServerUrl')),
                          ),
                        ],
                      ),
                      if (_serverMsg != null) ...[
                        const SizedBox(height: 10),
                        Text(
                          _serverMsg!,
                          style: TextStyle(
                            color: _serverMsgOk
                                ? Theme.of(context).colorScheme.tertiary
                                : Theme.of(context).colorScheme.error,
                            fontSize: 13,
                            height: 1.35,
                          ),
                        ),
                      ],
                      const SizedBox(height: 12),
                      SelectableText(
                        '${t.tr('settings.apiBaseUrl')}\n$baseUrl',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const SizedBox(height: 10),
                      if (_health == null)
                        Text(
                          t.tr('settings.backendUnreachable'),
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                            fontSize: 13,
                            height: 1.35,
                          ),
                        )
                      else ...[
                        Text(
                          t.tr(
                            'settings.backendOk',
                            args: {'status': _health!.status},
                          ),
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        const SizedBox(height: 6),
                        Text(
                          _health!.groqConfigured
                              ? t.tr('settings.groqOn')
                              : t.tr('settings.groqOff'),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: _health!.groqConfigured
                                    ? Theme.of(context).colorScheme.tertiary
                                    : Theme.of(context).colorScheme.onSurfaceVariant,
                                height: 1.35,
                              ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          _mlOnServer == true
                              ? t.tr('settings.mlServerOn')
                              : t.tr('settings.mlServerOff'),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                height: 1.35,
                              ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(t.tr('settings.theme')),
              const SizedBox(height: 8),
              SegmentedButton<ThemeMode>(
                segments: [
                  ButtonSegment(
                    value: ThemeMode.light,
                    label: Text(t.tr('settings.light')),
                  ),
                  ButtonSegment(
                    value: ThemeMode.dark,
                    label: Text(t.tr('settings.dark')),
                  ),
                ],
                selected: {prefs.themeMode},
                onSelectionChanged: (v) => prefs.setThemeMode(v.first),
              ),
              const SizedBox(height: 16),
              Text(t.tr('settings.language')),
              const SizedBox(height: 8),
              SegmentedButton<String>(
                segments: const [
                  ButtonSegment(value: 'en', label: Text('English')),
                  ButtonSegment(value: 'ar', label: Text('العربية')),
                ],
                selected: {prefs.locale.languageCode},
                onSelectionChanged: (v) =>
                    prefs.setLocale(Locale(v.first)),
              ),
              const SizedBox(height: 24),
              Text(t.tr('settings.workoutPreferences')),
              const SizedBox(height: 8),
              SegmentedButton<String>(
                segments: const [
                  ButtonSegment(value: 'kg', label: Text('KG')),
                  ButtonSegment(value: 'lb', label: Text('LB')),
                ],
                selected: {prefs.weightUnit},
                onSelectionChanged: (v) => prefs.setWeightUnit(v.first),
              ),
              const SizedBox(height: 12),
              Text(
                t.tr(
                  'settings.restTimer',
                  args: {'seconds': '${prefs.restTimerSeconds}'},
                ),
              ),
              Slider(
                value: prefs.restTimerSeconds.toDouble(),
                min: 30,
                max: 300,
                divisions: 9,
                label: '${prefs.restTimerSeconds}s',
                onChanged: (value) =>
                    prefs.setRestTimerSeconds(value.round()),
              ),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                value: prefs.aiExerciseOnlyMode,
                title: Text(t.tr('settings.aiExercisesOnly')),
                subtitle: Text(t.tr('settings.aiExercisesOnlySubtitle')),
                onChanged: (v) => prefs.setAiExerciseOnlyMode(v),
              ),
              const SizedBox(height: 12),
              Text(t.tr('settings.bodyGoal')),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: prefs.bodyGoal,
                decoration: InputDecoration(
                  labelText: t.tr('settings.bodyGoal'),
                ),
                items: [
                  DropdownMenuItem(
                    value: 'balanced_fitness',
                    child: Text(t.tr('goal.balanced_fitness')),
                  ),
                  DropdownMenuItem(
                    value: 'fat_loss',
                    child: Text(t.tr('goal.fat_loss')),
                  ),
                  DropdownMenuItem(
                    value: 'muscle_building',
                    child: Text(t.tr('goal.muscle_building')),
                  ),
                  DropdownMenuItem(
                    value: 'strength_performance',
                    child: Text(t.tr('goal.strength_performance')),
                  ),
                  DropdownMenuItem(
                    value: 'body_recomposition',
                    child: Text(t.tr('goal.body_recomposition')),
                  ),
                ],
                onChanged: (v) => prefs.setBodyGoal(v ?? prefs.bodyGoal),
              ),
              const SizedBox(height: 10),
              Text(
                t.tr(
                  'settings.trainingDaysPerWeek',
                  args: {'value': '${prefs.trainingDaysPerWeek}'},
                ),
              ),
              Slider(
                value: prefs.trainingDaysPerWeek.toDouble(),
                min: 2,
                max: 6,
                divisions: 4,
                label: '${prefs.trainingDaysPerWeek}',
                onChanged: (value) =>
                    prefs.setTrainingDaysPerWeek(value.round()),
              ),
            ],
          ),
        );
      },
    );
  }
}
