// timer-page.js

class TimerPage {
  constructor() {
    this.container = document.getElementById('page-timer');
    this.engine = window.pomodoroEngine;
    this.buildUI();
    this.bindEvents();
  }

  buildUI() {
    this.container.innerHTML = `
      <div class="timer-container">
        <svg class="timer-svg" viewBox="0 0 280 280">
          <circle class="timer-track" cx="140" cy="140" r="120" />
          <circle class="timer-progress" id="timer-progress" cx="140" cy="140" r="120" stroke-dasharray="753.98" stroke-dashoffset="0" />
        </svg>
        <div class="timer-text-container">
          <div class="timer-time" id="timer-time">25:00</div>
          <div class="timer-status" id="timer-status">
            <span class="status-dot" id="status-dot"></span>
            <span id="status-text">🍅 Focus Session</span>
          </div>
        </div>
      </div>
      
      <div class="timer-controls">
        <button class="btn-control btn-secondary" id="btn-reset">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
        </button>
        <button class="btn-control btn-primary" id="btn-main">
          <svg id="icon-play" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          <svg id="icon-pause" style="display:none;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
          <span id="btn-main-text">Start</span>
        </button>
        <button class="btn-control btn-secondary" id="btn-skip">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19"/></svg>
        </button>
      </div>

      <select class="task-selector" id="timer-task-selector">
        <option value="">No active task</option>
      </select>
    `;

    this.setTimerContainer = document.getElementById('page-set-timer');
    this.setTimerContainer.innerHTML = `
      <div style="font-size: 16px; font-weight: 700; margin-bottom: 16px;">Set Timer Presets</div>
      <div class="timer-presets" id="timer-presets" style="justify-content: flex-start; max-width: 100%;">
        <button class="preset-btn" data-work="60" data-break="0">
          <span class="preset-title">1 Hour Session</span>
          60 min / No Break
        </button>
        <button class="preset-btn" data-work="45" data-break="15">
          <span class="preset-title">Deep Work</span>
          45 / 15
        </button>
        <button class="preset-btn" data-work="50" data-break="10">
          <span class="preset-title">50 / 10 Rule</span>
          50 / 10
        </button>
        <button class="preset-btn" data-work="20" data-break="10">
          <span class="preset-title">Short Burst</span>
          20 / 10
        </button>
      </div>
      
      <div style="margin-top: 24px;">
        <div style="font-size: 14px; font-weight: 600; margin-bottom: 12px; color: var(--text-sec);">Custom</div>
        <div style="display: flex; gap: 12px; align-items: flex-end;">
          <div class="form-group" style="margin-bottom: 0; flex: 1;">
            <label class="form-label">Focus (min)</label>
            <input type="number" id="custom-focus-min" class="form-control" value="60" min="1">
          </div>
          <div class="form-group" style="margin-bottom: 0; flex: 1;">
            <label class="form-label">Break (min)</label>
            <input type="number" id="custom-break-min" class="form-control" value="0" min="0">
          </div>
          <button class="btn-control btn-secondary" id="btn-apply-custom" style="padding: 8px 16px; border-radius: 8px;">Apply</button>
        </div>
      </div>
    `;

    this.progressCircle = document.getElementById('timer-progress');
    this.timeDisplay = document.getElementById('timer-time');
    this.statusText = document.getElementById('status-text');
    this.statusDot = document.getElementById('status-dot');
    this.btnMain = document.getElementById('btn-main');
    this.btnMainText = document.getElementById('btn-main-text');
    this.iconPlay = document.getElementById('icon-play');
    this.iconPause = document.getElementById('icon-pause');
    this.btnReset = document.getElementById('btn-reset');
    this.btnSkip = document.getElementById('btn-skip');
    this.taskSelector = document.getElementById('timer-task-selector');
    this.presetBtns = document.querySelectorAll('.preset-btn');

    this.circumference = 2 * Math.PI * 120; // 753.98
    this.progressCircle.style.strokeDasharray = this.circumference;
    
    // Initial display
    this.updateDisplay(this.engine.getRemaining(), this.engine._totalSeconds || (25 * 60), this.engine.state);
  }

  bindEvents() {
    this.btnMain.addEventListener('click', () => {
      if (this.engine.state === TimerState.IDLE) {
        const selectedTaskId = this.taskSelector.value ? parseInt(this.taskSelector.value, 10) : null;
        this.engine.start(selectedTaskId);
      } else if (this.engine.state === TimerState.PAUSED) {
        this.engine.resume();
      } else {
        this.engine.pause();
      }
    });

    this.btnReset.addEventListener('click', () => {
      this.engine.stop();
    });

    this.btnSkip.addEventListener('click', () => {
      this.engine.skip();
    });
    
    // Preset Buttons
    this.presetBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const w = parseInt(btn.getAttribute('data-work'), 10);
        const b = parseInt(btn.getAttribute('data-break'), 10);
        this.applyTimerSettings(w, b);
      });
    });

    // Custom Timer apply button
    document.getElementById('btn-apply-custom').addEventListener('click', () => {
      const w = parseInt(document.getElementById('custom-focus-min').value, 10);
      const b = parseInt(document.getElementById('custom-break-min').value, 10);
      if (w > 0 && b >= 0) {
        this.applyTimerSettings(w, b);
      }
    });

    this.taskSelector.addEventListener('change', (e) => {
      if (this.engine.state === TimerState.IDLE) {
        this.engine.activeTaskId = e.target.value ? parseInt(e.target.value, 10) : null;
      }
    });

    // Wire engine callbacks
    this.engine.onTick = (remaining, total, state) => this.updateDisplay(remaining, total, state);
    this.engine.onSessionStart = (state) => {};
    this.engine.onSessionEnd = (finishedState, naturally) => {
      this.handleSessionEnd(finishedState, naturally);
    };
  }

  applyTimerSettings(w, b) {
    window.settingsManager.update('workMin', w);
    window.settingsManager.update('shortBreakMin', b);
    
    if (window.settingsPage) {
      window.settingsPage.loadSettings();
    }
    
    this.engine.stop();
    window.notifier.showToast("Timer Updated", `Set to ${w} min focus, ${b} min break.`);
    
    // Update custom input fields to match
    document.getElementById('custom-focus-min').value = w;
    document.getElementById('custom-break-min').value = b;
  }

  refreshTasks() {
    const tasks = window.taskManager.getTasks('pending');
    const currentValue = this.taskSelector.value;
    
    this.taskSelector.innerHTML = '<option value="">No active task</option>';
    tasks.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.textContent = t.title;
      this.taskSelector.appendChild(opt);
    });
    
    if (currentValue && tasks.find(t => t.id === parseInt(currentValue, 10))) {
      this.taskSelector.value = currentValue;
    }
  }

  updateDisplay(remaining, total, state) {
    this.timeDisplay.textContent = PomodoroEngine.formatTime(remaining);
    
    const fraction = total > 0 ? (total - remaining) / total : 0;
    const offset = this.circumference - (fraction * this.circumference);
    this.progressCircle.style.strokeDashoffset = offset;

    let typeStr = "🍅 Focus Session";
    let colorVar = "var(--accent)";
    
    if (this.engine.currentSessionType === 'short_break') {
      typeStr = "☕ Short Break";
      colorVar = "var(--success)";
    } else if (this.engine.currentSessionType === 'long_break') {
      typeStr = "🌙 Long Break";
      colorVar = "var(--success)";
    }
    
    this.statusText.textContent = typeStr;
    this.progressCircle.style.stroke = colorVar;
    this.statusDot.style.backgroundColor = colorVar;
    
    if (state === TimerState.WORKING || state === TimerState.SHORT_BREAK || state === TimerState.LONG_BREAK) {
      this.statusDot.classList.add('pulsing');
      this.btnMainText.textContent = "Pause";
      this.iconPlay.style.display = 'none';
      this.iconPause.style.display = 'inline-block';
    } else {
      this.statusDot.classList.remove('pulsing');
      this.btnMainText.textContent = state === TimerState.PAUSED ? "Resume" : "Start";
      this.iconPlay.style.display = 'inline-block';
      this.iconPause.style.display = 'none';
    }
  }

  handleSessionEnd(finishedState, naturally) {
    const settings = window.settingsManager.get();
    let title = "Session Complete";
    let msg = "Time is up!";
    
    if (finishedState === TimerState.WORKING) {
      title = "Focus Complete";
      msg = naturally ? "Great job focusing! Time for a break." : "Focus session skipped.";
      
      window.db.addSession({
        taskId: this.engine.activeTaskId,
        sessionType: 'work',
        durationSec: this.engine._totalSeconds
      });
      
      if (naturally) {
        if (this.engine.activeTaskId) {
          window.taskManager.registerPomodoroCompletion(this.engine.activeTaskId);
          if (window.tasksPage) window.tasksPage.refresh();
        }
        if (window.app) window.app.updateDailyGoalTracker();
      }
    } else {
      title = "Break Complete";
      msg = naturally ? "Break is over. Ready to focus?" : "Break skipped.";
      
      window.db.addSession({
        taskId: null,
        sessionType: finishedState === TimerState.SHORT_BREAK ? 'short_break' : 'long_break',
        durationSec: this.engine._totalSeconds
      });
    }

    window.notifier.notify(title, msg);
    if (window.statsPage) window.statsPage.refresh();
  }
}
