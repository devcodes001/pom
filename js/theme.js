// theme.js - Theme and accent color manager

class ThemeManager {
  constructor() {
    this.subscribers = [];
    this.mode = 'dark';
    this.accentColor = '#6C63FF';
  }

  init() {
    const settings = window.db.getSettings();
    this.mode = settings.theme || 'dark';
    this.accentColor = settings.accentColor || '#6C63FF';
    this.apply();
  }

  toggleMode() {
    this.mode = this.mode === 'dark' ? 'light' : 'dark';
    window.db.updateSetting('theme', this.mode);
    this.apply();
    this.notify();
    return this.mode;
  }

  setAccent(hexColor) {
    this.accentColor = hexColor;
    window.db.updateSetting('accentColor', hexColor);
    this.apply();
    this.notify();
  }

  apply() {
    document.documentElement.setAttribute('data-theme', this.mode);
    
    // Set custom accent color variable
    document.documentElement.style.setProperty('--accent', this.accentColor);
    
    // Convert hex to rgb for rgba() usage
    const rgb = this.hexToRgb(this.accentColor);
    if (rgb) {
      document.documentElement.style.setProperty('--accent-rgb', `${rgb.r}, ${rgb.g}, ${rgb.b}`);
    }
  }

  subscribe(callback) {
    this.subscribers.push(callback);
  }

  notify() {
    this.subscribers.forEach(cb => {
      try {
        cb(this.mode, this.accentColor);
      } catch (e) {
        console.error('Theme subscriber error:', e);
      }
    });
  }

  hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }
}

window.themeManager = new ThemeManager();
