// settings.js - Settings manager

class SettingsManager {
  constructor() {}

  get() {
    return window.db.getSettings();
  }

  update(key, value) {
    window.db.updateSetting(key, value);
    // If it's a theme setting, apply it immediately
    if (key === 'theme' || key === 'accentColor') {
      if (key === 'theme') window.themeManager.mode = value;
      if (key === 'accentColor') window.themeManager.setAccent(value);
      window.themeManager.apply();
    }
  }
}

window.settingsManager = new SettingsManager();
