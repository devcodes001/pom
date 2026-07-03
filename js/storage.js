// storage.js - LocalStorage wrapper replacing SQLite Database

const STORAGE_KEYS = {
  TASKS: 'ff_tasks',
  SESSIONS: 'ff_sessions',
  SETTINGS: 'ff_settings',
  NEXT_ID: 'ff_next_id'
};

const DEFAULT_SETTINGS = {
  workMin: 25,
  shortBreakMin: 5,
  longBreakMin: 15,
  sessionsBeforeLong: 4,
  autoStartBreak: true,
  autoStartWork: false,
  notifyEnabled: true,
  soundEnabled: true,
  dailyGoal: 8,
  theme: 'dark',
  accentColor: '#6C63FF' // Default indigo
};

class Storage {
  constructor() {
    this._init();
  }

  _init() {
    if (!localStorage.getItem(STORAGE_KEYS.TASKS)) {
      localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify([]));
    }
    if (!localStorage.getItem(STORAGE_KEYS.SESSIONS)) {
      localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify([]));
    }
    if (!localStorage.getItem(STORAGE_KEYS.SETTINGS)) {
      localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(DEFAULT_SETTINGS));
    }
    if (!localStorage.getItem(STORAGE_KEYS.NEXT_ID)) {
      localStorage.setItem(STORAGE_KEYS.NEXT_ID, '1');
    }
  }

  _generateId() {
    const nextId = parseInt(localStorage.getItem(STORAGE_KEYS.NEXT_ID), 10);
    localStorage.setItem(STORAGE_KEYS.NEXT_ID, (nextId + 1).toString());
    return nextId;
  }

  // --- Tasks ---

  getTasks() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.TASKS) || '[]');
  }

  saveTasks(tasks) {
    localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify(tasks));
  }

  addTask(taskData) {
    const tasks = this.getTasks();
    const newTask = {
      id: this._generateId(),
      title: taskData.title,
      description: taskData.description || '',
      priority: taskData.priority || 1, // 0=Low, 1=Medium, 2=High
      deadline: taskData.deadline || '',
      estimatedPomodoros: parseInt(taskData.estimatedPomodoros, 10) || 1,
      completedPomodoros: 0,
      completed: false,
      sortOrder: tasks.length,
      createdAt: new Date().toISOString()
    };
    tasks.push(newTask);
    this.saveTasks(tasks);
    return newTask;
  }

  updateTask(id, updates) {
    const tasks = this.getTasks();
    const index = tasks.findIndex(t => t.id === id);
    if (index !== -1) {
      tasks[index] = { ...tasks[index], ...updates };
      this.saveTasks(tasks);
      return tasks[index];
    }
    return null;
  }

  deleteTask(id) {
    const tasks = this.getTasks();
    const filtered = tasks.filter(t => t.id !== id);
    this.saveTasks(filtered);
  }

  // --- Sessions ---

  getSessions() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.SESSIONS) || '[]');
  }

  addSession(sessionData) {
    const sessions = this.getSessions();
    const newSession = {
      id: this._generateId(),
      taskId: sessionData.taskId || null,
      sessionType: sessionData.sessionType, // 'work' | 'short_break' | 'long_break'
      durationSec: sessionData.durationSec,
      startedAt: new Date().toISOString()
    };
    sessions.push(newSession);
    localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(sessions));
    return newSession;
  }

  // --- Settings ---

  getSettings() {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEYS.SETTINGS) || '{}');
    return { ...DEFAULT_SETTINGS, ...saved };
  }

  saveSettings(settings) {
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
  }

  updateSetting(key, value) {
    const settings = this.getSettings();
    settings[key] = value;
    this.saveSettings(settings);
  }
}

// Export singleton instance
window.db = new Storage();
