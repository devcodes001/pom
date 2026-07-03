// stats-page.js

class StatsPage {
  constructor() {
    this.container = document.getElementById('page-stats');
    this.currentTab = 'daily'; // daily, weekly, monthly
    this.chartInstance = null;
    this.buildUI();
    this.bindEvents();
    // Refresh is called from App.js when switching to this page
  }

  buildUI() {
    this.container.innerHTML = `
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value" id="stat-today">0m</div>
          <div class="stat-label">Today's Focus</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" id="stat-tasks">0</div>
          <div class="stat-label">Completed Tasks</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" id="stat-current-streak">0 days</div>
          <div class="stat-label">Current Streak</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" id="stat-total-pomo">0</div>
          <div class="stat-label">Total Pomodoros</div>
        </div>
      </div>
      
      <div class="chart-container">
        <div class="chart-tabs" id="chart-tabs">
          <div class="chart-tab active" data-tab="daily">Daily (Last 7 Days)</div>
          <div class="chart-tab" data-tab="weekly">Weekly (Last 8 Weeks)</div>
          <div class="chart-tab" data-tab="monthly">Monthly (Last 12 Months)</div>
        </div>
        <div style="height: 300px; width: 100%;">
          <canvas id="stats-chart"></canvas>
        </div>
      </div>
    `;

    this.statToday = document.getElementById('stat-today');
    this.statTasks = document.getElementById('stat-tasks');
    this.statCurrentStreak = document.getElementById('stat-current-streak');
    this.statTotalPomo = document.getElementById('stat-total-pomo');
    
    this.chartTabs = document.querySelectorAll('.chart-tab');
    this.ctx = document.getElementById('stats-chart').getContext('2d');
  }

  bindEvents() {
    this.chartTabs.forEach(tab => {
      tab.addEventListener('click', (e) => {
        this.chartTabs.forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        this.currentTab = e.target.getAttribute('data-tab');
        this.renderChart();
      });
    });

    window.themeManager.subscribe(() => {
      // Re-render chart on theme change to update colors
      this.renderChart();
    });
  }

  refresh() {
    const sessions = window.db.getSessions().filter(s => s.sessionType === 'work');
    const tasks = window.db.getTasks();
    
    // Compute Today's Focus
    const todayStr = new Date().toDateString();
    let todaySec = 0;
    sessions.forEach(s => {
      if (new Date(s.startedAt).toDateString() === todayStr) {
        todaySec += s.durationSec;
      }
    });
    this.statToday.textContent = this.formatDuration(todaySec);
    
    // Compute Tasks & Pomos
    const completedTasks = tasks.filter(t => t.completed).length;
    this.statTasks.textContent = completedTasks;
    
    const totalPomos = tasks.reduce((sum, t) => sum + t.completedPomodoros, 0);
    // Add orphaned sessions too (deleted tasks or no task)
    const extraPomos = sessions.filter(s => s.taskId === null || !tasks.find(t => t.id === s.taskId)).length;
    this.statTotalPomo.textContent = totalPomos + extraPomos;
    
    // Compute Streaks
    this.statCurrentStreak.textContent = `${this.computeStreak(sessions)} days`;
    
    this.renderChart(sessions);
  }

  formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  }

  computeStreak(sessions) {
    if (sessions.length === 0) return 0;
    
    // Unique dates sorted descending
    const dates = [...new Set(sessions.map(s => new Date(s.startedAt).toDateString()))]
      .map(d => new Date(d))
      .sort((a, b) => b - a);
      
    let streak = 0;
    const today = new Date();
    today.setHours(0,0,0,0);
    
    // Check if streak is active (today or yesterday)
    const mostRecent = dates[0];
    const diffDays = Math.floor((today - mostRecent) / (1000 * 60 * 60 * 24));
    
    if (diffDays > 1) return 0; // Streak broken
    
    streak = 1;
    for (let i = 1; i < dates.length; i++) {
      const diff = Math.floor((dates[i-1] - dates[i]) / (1000 * 60 * 60 * 24));
      if (diff === 1) streak++;
      else break;
    }
    
    return streak;
  }

  renderChart(sessionsInput = null) {
    if (!window.Chart) return; // Not loaded yet
    
    const sessions = sessionsInput || window.db.getSessions().filter(s => s.sessionType === 'work');
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    
    // Colors from CSS variables
    const style = getComputedStyle(document.documentElement);
    const textColor = style.getPropertyValue('--text-sec').trim() || (isDark ? '#A1A1A6' : '#6E6E73');
    const gridColor = style.getPropertyValue('--border').trim() || (isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)');
    const accentColor = style.getPropertyValue('--accent').trim() || '#6C63FF';
    
    let labels = [];
    let data = [];
    
    if (this.currentTab === 'daily') {
      // Last 7 days
      for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dayStr = d.toDateString();
        labels.push(d.toLocaleDateString(undefined, { weekday: 'short' }));
        
        let sec = 0;
        sessions.forEach(s => {
          if (new Date(s.startedAt).toDateString() === dayStr) sec += s.durationSec;
        });
        data.push(sec / 3600); // Hours
      }
    } else if (this.currentTab === 'weekly') {
      // Last 8 weeks
      // Simplified: group by past 7-day intervals
      const now = new Date();
      now.setHours(23,59,59,999);
      for (let i = 7; i >= 0; i--) {
        const end = new Date(now.getTime() - (i * 7 * 24 * 60 * 60 * 1000));
        const start = new Date(end.getTime() - (6 * 24 * 60 * 60 * 1000));
        start.setHours(0,0,0,0);
        
        labels.push(`${start.getDate()} ${start.toLocaleDateString(undefined, {month:'short'})}`);
        
        let sec = 0;
        sessions.forEach(s => {
          const sd = new Date(s.startedAt);
          if (sd >= start && sd <= end) sec += s.durationSec;
        });
        data.push(sec / 3600);
      }
    } else {
      // Monthly - last 12 months
      const now = new Date();
      for (let i = 11; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        labels.push(d.toLocaleDateString(undefined, { month: 'short' }));
        
        let sec = 0;
        sessions.forEach(s => {
          const sd = new Date(s.startedAt);
          if (sd.getMonth() === d.getMonth() && sd.getFullYear() === d.getFullYear()) {
            sec += s.durationSec;
          }
        });
        data.push(sec / 3600);
      }
    }

    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    this.chartInstance = new Chart(this.ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Focus Hours',
          data: data,
          backgroundColor: accentColor,
          borderRadius: 4,
          barThickness: 'flex',
          maxBarThickness: 32
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.raw.toFixed(1)} hours`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: gridColor },
            ticks: { color: textColor },
            border: { display: false }
          },
          x: {
            grid: { display: false },
            ticks: { color: textColor },
            border: { display: false }
          }
        }
      }
    });
  }
}
