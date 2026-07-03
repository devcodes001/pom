// settings-page.js

const ACCENT_PRESETS = [
  { color: '#6C63FF', name: 'Indigo' },
  { color: '#EF4444', name: 'Coral' },
  { color: '#4ECDC4', name: 'Teal' },
  { color: '#F59E0B', name: 'Gold' },
  { color: '#22C55E', name: 'Green' },
  { color: '#FF8A5C', name: 'Tangerine' },
  { color: '#A855F7', name: 'Purple' },
  { color: '#38BDF8', name: 'Sky' }
];

class SettingsPage {
  constructor() {
    this.container = document.getElementById('page-settings');
    this.buildUI();
    this.loadSettings();
    this.bindEvents();
  }

  buildUI() {
    this.container.innerHTML = `
      <div class="settings-section">
        <div class="settings-title">Appearance</div>
        
        <div class="settings-row">
          <div class="settings-label">Theme Mode</div>
          <div style="display: flex; gap: 8px;">
            <button class="btn-control btn-secondary" id="btn-theme-dark" style="border-radius: 8px; padding: 6px 12px;">Dark</button>
            <button class="btn-control btn-secondary" id="btn-theme-light" style="border-radius: 8px; padding: 6px 12px;">Light</button>
          </div>
        </div>
        
        <div class="settings-row">
          <div class="settings-label">Accent Color</div>
          <div class="accent-grid" id="accent-grid">
            ${ACCENT_PRESETS.map(p => `
              <button class="accent-btn" data-color="${p.color}" style="background-color: ${p.color}" title="${p.name}"></button>
            `).join('')}
            <input type="color" id="custom-color-picker" style="width: 32px; height: 32px; padding: 0; border: none; border-radius: 50%; cursor: pointer; background: none;">
          </div>
        </div>
      </div>

      <div class="settings-section">
        <div class="settings-title">Timer Durations</div>
        
        <div class="settings-row">
          <div class="settings-label">Focus (minutes)</div>
          <div style="display:flex; align-items:center; gap: 12px;">
            <input type="range" id="setting-workMin" min="1" max="90" step="1">
            <span id="val-workMin" style="width: 30px; text-align: right; font-variant-numeric: tabular-nums;">25</span>
          </div>
        </div>
        
        <div class="settings-row">
          <div class="settings-label">Short Break (minutes)</div>
          <div style="display:flex; align-items:center; gap: 12px;">
            <input type="range" id="setting-shortBreakMin" min="1" max="30" step="1">
            <span id="val-shortBreakMin" style="width: 30px; text-align: right; font-variant-numeric: tabular-nums;">5</span>
          </div>
        </div>
        
        <div class="settings-row">
          <div class="settings-label">Long Break (minutes)</div>
          <div style="display:flex; align-items:center; gap: 12px;">
            <input type="range" id="setting-longBreakMin" min="1" max="60" step="1">
            <span id="val-longBreakMin" style="width: 30px; text-align: right; font-variant-numeric: tabular-nums;">15</span>
          </div>
        </div>
        
        <div class="settings-row">
          <div class="settings-label">Sessions before Long Break</div>
          <div style="display:flex; align-items:center; gap: 12px;">
            <input type="range" id="setting-sessionsBeforeLong" min="1" max="10" step="1">
            <span id="val-sessionsBeforeLong" style="width: 30px; text-align: right; font-variant-numeric: tabular-nums;">4</span>
          </div>
        </div>
      </div>

      <div class="settings-section">
        <div class="settings-title">Behavior & Notifications</div>
        
        <div class="settings-row">
          <div class="settings-label">Auto-start Breaks</div>
          <label class="switch">
            <input type="checkbox" id="setting-autoStartBreak">
            <span class="slider"></span>
          </label>
        </div>
        
        <div class="settings-row">
          <div class="settings-label">Auto-start Focus Sessions</div>
          <label class="switch">
            <input type="checkbox" id="setting-autoStartWork">
            <span class="slider"></span>
          </label>
        </div>
        
        <div class="settings-row">
          <div class="settings-label">Desktop Notifications</div>
          <label class="switch">
            <input type="checkbox" id="setting-notifyEnabled">
            <span class="slider"></span>
          </label>
        </div>
        
        <div class="settings-row">
          <div class="settings-label">Alarm Sound</div>
          <label class="switch">
            <input type="checkbox" id="setting-soundEnabled">
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <div class="settings-section">
        <div class="settings-title">Goals</div>
        
        <div class="settings-row">
          <div class="settings-label">Daily Pomodoro Goal</div>
          <div style="display:flex; align-items:center; gap: 12px;">
            <input type="range" id="setting-dailyGoal" min="1" max="16" step="1">
            <span id="val-dailyGoal" style="width: 30px; text-align: right; font-variant-numeric: tabular-nums;">8</span>
          </div>
        </div>
      </div>
    `;

    this.themeBtns = {
      dark: document.getElementById('btn-theme-dark'),
      light: document.getElementById('btn-theme-light')
    };
    
    this.accentBtns = document.querySelectorAll('.accent-btn');
    this.customPicker = document.getElementById('custom-color-picker');
    
    this.ranges = ['workMin', 'shortBreakMin', 'longBreakMin', 'sessionsBeforeLong', 'dailyGoal'];
    this.switches = ['autoStartBreak', 'autoStartWork', 'notifyEnabled', 'soundEnabled'];
  }

  loadSettings() {
    const s = window.settingsManager.get();
    
    // Theme buttons
    this.updateThemeButtons(s.theme);
    
    // Accent buttons
    this.updateAccentSelection(s.accentColor);
    
    // Ranges
    this.ranges.forEach(key => {
      const el = document.getElementById(`setting-${key}`);
      const valEl = document.getElementById(`val-${key}`);
      if (el && valEl) {
        el.value = s[key];
        valEl.textContent = s[key];
      }
    });
    
    // Switches
    this.switches.forEach(key => {
      const el = document.getElementById(`setting-${key}`);
      if (el) el.checked = s[key];
    });
  }

  bindEvents() {
    // Theme toggle
    this.themeBtns.dark.addEventListener('click', () => {
      window.settingsManager.update('theme', 'dark');
      this.updateThemeButtons('dark');
    });
    this.themeBtns.light.addEventListener('click', () => {
      window.settingsManager.update('theme', 'light');
      this.updateThemeButtons('light');
    });
    
    window.themeManager.subscribe((mode, accent) => {
      this.updateThemeButtons(mode);
      this.updateAccentSelection(accent);
    });

    // Accent selection
    this.accentBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const color = e.target.getAttribute('data-color');
        window.settingsManager.update('accentColor', color);
      });
    });
    
    this.customPicker.addEventListener('change', (e) => {
      window.settingsManager.update('accentColor', e.target.value);
    });

    // Ranges
    this.ranges.forEach(key => {
      const el = document.getElementById(`setting-${key}`);
      const valEl = document.getElementById(`val-${key}`);
      el.addEventListener('input', (e) => {
        valEl.textContent = e.target.value;
      });
      el.addEventListener('change', (e) => {
        window.settingsManager.update(key, parseInt(e.target.value, 10));
        // Reset timer if idle to apply new durations
        if (['workMin', 'shortBreakMin', 'longBreakMin'].includes(key)) {
          if (window.pomodoroEngine.state === TimerState.IDLE) {
            window.pomodoroEngine.stop(); // forces reset
          }
        }
        if (key === 'dailyGoal' && window.app) {
          window.app.updateDailyGoalTracker();
        }
      });
    });

    // Switches
    this.switches.forEach(key => {
      const el = document.getElementById(`setting-${key}`);
      el.addEventListener('change', (e) => {
        window.settingsManager.update(key, e.target.checked);
        if (key === 'notifyEnabled' && e.target.checked) {
          window.notifier._requestPermission();
        }
      });
    });
  }

  updateThemeButtons(mode) {
    this.themeBtns.dark.style.borderColor = mode === 'dark' ? 'var(--accent)' : 'transparent';
    this.themeBtns.light.style.borderColor = mode === 'light' ? 'var(--accent)' : 'transparent';
  }

  updateAccentSelection(color) {
    this.accentBtns.forEach(btn => {
      if (btn.getAttribute('data-color').toUpperCase() === color.toUpperCase()) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
    
    // Check if it's a custom color
    const isPreset = Array.from(this.accentBtns).some(btn => btn.getAttribute('data-color').toUpperCase() === color.toUpperCase());
    if (!isPreset) {
      this.customPicker.value = color;
    }
  }
}
