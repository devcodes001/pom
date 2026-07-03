// pomodoro.js - Timer engine

const TimerState = {
  IDLE: 'idle',
  WORKING: 'working',
  SHORT_BREAK: 'short_break',
  LONG_BREAK: 'long_break',
  PAUSED: 'paused'
};

class PomodoroEngine {
  constructor() {
    this.state = TimerState.IDLE;
    this.currentSessionType = 'work'; // 'work', 'short_break', 'long_break'
    this.completedWorkSessions = 0;
    this.activeTaskId = null;
    
    this._totalSeconds = 0;
    this._remainingSeconds = 0;
    this._deadline = null;
    this._timerId = null;
    this._animFrameId = null;
    
    this.onTick = null; // (remaining, total, state)
    this.onSessionEnd = null; // (finishedState, completedNaturally)
    this.onSessionStart = null; // (state)
  }

  // --- Configuration ---
  
  _getDurations() {
    const settings = window.settingsManager.get();
    return {
      work: (settings.workMin || 25) * 60,
      short_break: (settings.shortBreakMin || 5) * 60,
      long_break: (settings.longBreakMin || 15) * 60,
      sessionsBeforeLong: settings.sessionsBeforeLong || 4
    };
  }

  _getDurationForState(type) {
    const d = this._getDurations();
    return d[type] || d.work;
  }

  // --- Public API ---

  start(taskId = null) {
    if (this.state === TimerState.PAUSED) {
      this.resume();
      return;
    }
    
    this.activeTaskId = taskId;
    this.currentSessionType = 'work';
    this._startSession(TimerState.WORKING, this._getDurationForState('work'));
  }

  pause() {
    if ([TimerState.WORKING, TimerState.SHORT_BREAK, TimerState.LONG_BREAK].includes(this.state)) {
      this._remainingSeconds = Math.max(0, (this._deadline - performance.now()) / 1000);
      this.state = TimerState.PAUSED;
      this._stopTimer();
    }
  }

  resume() {
    if (this.state === TimerState.PAUSED) {
      // Reconstruct state based on session type
      let resumeState = TimerState.WORKING;
      if (this.currentSessionType === 'short_break') resumeState = TimerState.SHORT_BREAK;
      if (this.currentSessionType === 'long_break') resumeState = TimerState.LONG_BREAK;
      
      this.state = resumeState;
      this._deadline = performance.now() + (this._remainingSeconds * 1000);
      this._startTimer();
    }
  }

  stop() {
    this._stopTimer();
    this.state = TimerState.IDLE;
    this.currentSessionType = 'work';
    this._totalSeconds = this._getDurationForState('work');
    this._remainingSeconds = this._totalSeconds;
    this._notifyTick();
  }

  skip() {
    if (this.state !== TimerState.IDLE) {
      this._finishSession(false);
    }
  }

  getRemaining() {
    if ([TimerState.WORKING, TimerState.SHORT_BREAK, TimerState.LONG_BREAK].includes(this.state)) {
      return Math.max(0, (this._deadline - performance.now()) / 1000);
    }
    return this._remainingSeconds;
  }

  // --- Internal ---

  _startSession(state, durationSec) {
    this.state = state;
    this._totalSeconds = durationSec;
    this._remainingSeconds = durationSec;
    this._deadline = performance.now() + (durationSec * 1000);
    
    if (this.onSessionStart) {
      this.onSessionStart(this.state);
    }
    
    this._startTimer();
  }

  _startTimer() {
    this._stopTimer(); // Ensure no duplicates
    
    // Low-frequency tick for logic/callbacks (every 250ms like Python)
    this._timerId = setInterval(() => {
      this._checkDeadline();
    }, 250);
    
    // High-frequency tick for smooth animation
    const animate = () => {
      if (this.state !== TimerState.PAUSED && this.state !== TimerState.IDLE) {
        this._notifyTick();
        this._animFrameId = requestAnimationFrame(animate);
      }
    };
    this._animFrameId = requestAnimationFrame(animate);
  }

  _stopTimer() {
    if (this._timerId) {
      clearInterval(this._timerId);
      this._timerId = null;
    }
    if (this._animFrameId) {
      cancelAnimationFrame(this._animFrameId);
      this._animFrameId = null;
    }
  }

  _checkDeadline() {
    const remaining = this.getRemaining();
    if (remaining <= 0) {
      this._finishSession(true);
    }
  }

  _finishSession(completedNaturally) {
    this._stopTimer();
    const finishedState = this.state;
    const settings = window.settingsManager.get();
    
    if (finishedState === TimerState.WORKING && completedNaturally) {
      this.completedWorkSessions++;
    }

    if (this.onSessionEnd) {
      this.onSessionEnd(finishedState, completedNaturally);
    }

    // State transition logic
    if (finishedState === TimerState.WORKING) {
      const d = this._getDurations();
      if (this.completedWorkSessions % d.sessionsBeforeLong === 0) {
        this.currentSessionType = 'long_break';
        if (settings.autoStartBreak) {
          this._startSession(TimerState.LONG_BREAK, d.long_break);
        } else {
          this.state = TimerState.IDLE;
          this._totalSeconds = d.long_break;
          this._remainingSeconds = this._totalSeconds;
          this._notifyTick();
        }
      } else {
        this.currentSessionType = 'short_break';
        if (settings.autoStartBreak) {
          this._startSession(TimerState.SHORT_BREAK, d.short_break);
        } else {
          this.state = TimerState.IDLE;
          this._totalSeconds = d.short_break;
          this._remainingSeconds = this._totalSeconds;
          this._notifyTick();
        }
      }
    } else if (finishedState === TimerState.SHORT_BREAK || finishedState === TimerState.LONG_BREAK) {
      this.currentSessionType = 'work';
      const d = this._getDurations();
      if (settings.autoStartWork) {
        this._startSession(TimerState.WORKING, d.work);
      } else {
        this.state = TimerState.IDLE;
        this._totalSeconds = d.work;
        this._remainingSeconds = this._totalSeconds;
        this._notifyTick();
      }
    }
  }

  _notifyTick() {
    if (this.onTick) {
      this.onTick(this.getRemaining(), this._totalSeconds, this.state);
    }
  }

  static formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
}

window.pomodoroEngine = new PomodoroEngine();
