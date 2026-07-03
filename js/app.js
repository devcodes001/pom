// app.js - Main entry point for Dashboard

class App {
  constructor() {
    this.themeToggle = document.getElementById('theme-toggle');
    this.greeting = document.getElementById('greeting');
    this.goalProgress = document.getElementById('goal-progress');
    this.goalCount = document.getElementById('goal-count');
    
    // Settings modal
    this.settingsToggle = document.getElementById('settings-toggle');
    this.settingsModalOverlay = document.getElementById('settings-modal-overlay');
    this.settingsCloseBtn = document.getElementById('settings-close');

    this.init();
  }

  init() {
    // Initialize singletons
    window.themeManager.init();
    
    // Initialize all panels simultaneously (no tabs)
    window.timerPage = new TimerPage();
    window.tasksPage = new TasksPage();
    window.statsPage = new StatsPage();
    window.settingsPage = new SettingsPage();
    
    this.bindEvents();
    this.startClock();
    this.updateDailyGoalTracker();
  }

  bindEvents() {
    // Theme toggle button
    this.themeToggle.addEventListener('click', () => {
      window.themeManager.toggleMode();
    });

    // Settings Modal
    this.settingsToggle.addEventListener('click', () => {
      this.settingsModalOverlay.classList.add('active');
    });
    
    this.settingsCloseBtn.addEventListener('click', () => {
      this.settingsModalOverlay.classList.remove('active');
    });

    // Global keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      // Don't trigger if typing in an input
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;

      if (e.code === 'Space') {
        e.preventDefault();
        const state = window.pomodoroEngine.state;
        if (state === TimerState.IDLE) window.pomodoroEngine.start(window.pomodoroEngine.activeTaskId);
        else if (state === TimerState.PAUSED) window.pomodoroEngine.resume();
        else window.pomodoroEngine.pause();
      } else if (e.ctrlKey && (e.key === 't' || e.key === 'T')) {
        e.preventDefault();
        window.themeManager.toggleMode();
      }
    });
  }

  startClock() {
    const updateTime = () => {
      const now = new Date();
      
      // Update greeting
      const hour = now.getHours();
      let greet = 'Good evening';
      if (hour < 12) greet = 'Good morning';
      else if (hour < 17) greet = 'Good afternoon';
      
      const options = { weekday: 'short', month: 'short', day: 'numeric' };
      const dateStr = now.toLocaleDateString(undefined, options);
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      this.greeting.textContent = `${greet}! It's ${timeStr} on ${dateStr}.`;
    };
    
    updateTime();
    setInterval(updateTime, 1000);
  }

  updateDailyGoalTracker() {
    if (!this.goalCount || !this.goalProgress) return;
    
    const goal = window.settingsManager.get().dailyGoal || 8;
    const sessions = window.db.getSessions().filter(s => s.sessionType === 'work');
    
    // Count today's sessions
    const today = new Date().toDateString();
    const completedToday = sessions.filter(s => new Date(s.startedAt).toDateString() === today).length;
    
    this.goalCount.textContent = `${completedToday} / ${goal} Today`;
    
    // Build emoji string
    let emojis = '';
    for (let i = 0; i < goal; i++) {
      if (i < completedToday) emojis += '🍅';
      else emojis += '○○';
      emojis += '&#8203;';
    }
    
    // If completed > goal, add extra tomatoes
    if (completedToday > goal) {
      emojis += ' + ';
      for (let i = 0; i < completedToday - goal; i++) {
        emojis += '🍅';
      }
    }
    
    this.goalProgress.innerHTML = emojis;
  }
}

window.app = new App();
