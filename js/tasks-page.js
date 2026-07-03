// tasks-page.js

class TasksPage {
  constructor() {
    this.container = document.getElementById('page-tasks');
    this.currentFilter = 'all';
    this.searchQuery = '';
    this.draggedId = null;
    this.buildUI();
    this.bindEvents();
    this.refresh();
  }

  buildUI() {
    this.container.innerHTML = `
      <div class="tasks-header">
        <div class="search-bar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" id="task-search" placeholder="Search tasks...">
        </div>
        <div class="filter-pills" id="task-filters">
          <button class="filter-pill active" data-filter="all">All</button>
          <button class="filter-pill" data-filter="pending">Pending</button>
          <button class="filter-pill" data-filter="completed">Completed</button>
        </div>
      </div>
      
      <div class="task-list" id="task-list">
        <!-- Tasks will be injected here -->
      </div>
      
      <button class="fab" id="btn-add-task" title="Add Task (Ctrl+N)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
      </button>

      <!-- Modal overlay -->
      <div class="modal-overlay" id="task-modal-overlay">
        <div class="modal" id="task-modal">
          <div class="modal-title" id="modal-title">New Task</div>
          
          <input type="hidden" id="modal-task-id">
          
          <div class="form-group">
            <label class="form-label">Title</label>
            <input type="text" class="form-control" id="modal-title-input" placeholder="What needs to be done?">
          </div>
          
          <div class="form-group">
            <label class="form-label">Description (optional)</label>
            <textarea class="form-control" id="modal-desc-input" rows="3" placeholder="Add some details..."></textarea>
          </div>
          
          <div class="form-group">
            <label class="form-label">Priority</label>
            <select class="form-control" id="modal-priority-input">
              <option value="2">High</option>
              <option value="1" selected>Medium</option>
              <option value="0">Low</option>
            </select>
          </div>
          
          <div class="form-group" style="display:flex; gap: 16px;">
            <div style="flex: 1;">
              <label class="form-label">Deadline (optional)</label>
              <input type="date" class="form-control" id="modal-deadline-input">
            </div>
            <div style="flex: 1;">
              <label class="form-label">Est. Pomodoros</label>
              <input type="number" class="form-control" id="modal-est-input" min="1" value="1">
            </div>
          </div>
          
          <div style="color: var(--danger); font-size: 13px; min-height: 20px;" id="modal-error"></div>
          
          <div class="modal-actions">
            <button class="btn-control btn-secondary" id="modal-cancel">Cancel</button>
            <button class="btn-control btn-primary" id="modal-save">Save Task</button>
          </div>
        </div>
      </div>
    `;

    this.searchInput = document.getElementById('task-search');
    this.filterBtns = document.querySelectorAll('.filter-pill');
    this.taskList = document.getElementById('task-list');
    this.btnAdd = document.getElementById('btn-add-task');
    
    // Modal elements
    this.modalOverlay = document.getElementById('task-modal-overlay');
    this.modalTitle = document.getElementById('modal-title');
    this.modalInputId = document.getElementById('modal-task-id');
    this.modalInputTitle = document.getElementById('modal-title-input');
    this.modalInputDesc = document.getElementById('modal-desc-input');
    this.modalInputPriority = document.getElementById('modal-priority-input');
    this.modalInputDeadline = document.getElementById('modal-deadline-input');
    this.modalInputEst = document.getElementById('modal-est-input');
    this.modalError = document.getElementById('modal-error');
    this.btnModalCancel = document.getElementById('modal-cancel');
    this.btnModalSave = document.getElementById('modal-save');
  }

  bindEvents() {
    this.searchInput.addEventListener('input', (e) => {
      this.searchQuery = e.target.value;
      this.refresh();
    });

    this.filterBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentFilter = btn.getAttribute('data-filter');
        this.refresh();
      });
    });

    this.btnAdd.addEventListener('click', () => this.openModal());
    this.btnModalCancel.addEventListener('click', () => this.closeModal());
    
    this.btnModalSave.addEventListener('click', () => {
      const title = this.modalInputTitle.value.trim();
      if (!title) {
        this.modalError.textContent = "Title is required.";
        return;
      }
      
      const data = {
        title: title,
        description: this.modalInputDesc.value.trim(),
        priority: parseInt(this.modalInputPriority.value, 10),
        deadline: this.modalInputDeadline.value,
        estimatedPomodoros: parseInt(this.modalInputEst.value, 10) || 1
      };
      
      const id = this.modalInputId.value;
      if (id) {
        window.taskManager.updateTask(parseInt(id, 10), data);
      } else {
        window.taskManager.addTask(data);
      }
      
      this.closeModal();
      this.refresh();
      if (window.timerPage) window.timerPage.refreshTasks();
    });

    // Global shortcut Ctrl+N
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey && (e.key === 'n' || e.key === 'N')) {
        e.preventDefault();
        this.openModal();
      }
    });
  }

  openModal(task = null) {
    this.modalError.textContent = '';
    if (task) {
      this.modalTitle.textContent = "Edit Task";
      this.modalInputId.value = task.id;
      this.modalInputTitle.value = task.title;
      this.modalInputDesc.value = task.description;
      this.modalInputPriority.value = task.priority;
      this.modalInputDeadline.value = task.deadline;
      this.modalInputEst.value = task.estimatedPomodoros;
    } else {
      this.modalTitle.textContent = "New Task";
      this.modalInputId.value = '';
      this.modalInputTitle.value = '';
      this.modalInputDesc.value = '';
      this.modalInputPriority.value = '1';
      this.modalInputDeadline.value = '';
      this.modalInputEst.value = '1';
    }
    this.modalOverlay.classList.add('active');
    this.modalInputTitle.focus();
  }

  closeModal() {
    this.modalOverlay.classList.remove('active');
  }

  getPriorityData(level) {
    if (level === 2) return { label: 'High', class: 'priority-high' };
    if (level === 1) return { label: 'Medium', class: 'priority-medium' };
    return { label: 'Low', class: 'priority-low' };
  }

  refresh() {
    const tasks = window.taskManager.getTasks(this.currentFilter, this.searchQuery);
    
    if (tasks.length === 0) {
      let msg = "No tasks yet — add your first one!";
      if (this.currentFilter === 'pending') msg = "No pending tasks. You're all caught up!";
      if (this.currentFilter === 'completed') msg = "No completed tasks yet.";
      if (this.searchQuery) msg = "No tasks match your search.";
      
      this.taskList.innerHTML = `
        <div style="text-align: center; padding: 48px; color: var(--text-sec);">
          <svg style="margin: 0 auto 16px; opacity: 0.5;" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          <div>${msg}</div>
        </div>
      `;
      return;
    }

    this.taskList.innerHTML = '';
    
    tasks.forEach(task => {
      const pData = this.getPriorityData(task.priority);
      const progressPercent = Math.min(100, (task.completedPomodoros / task.estimatedPomodoros) * 100);
      
      const el = document.createElement('div');
      el.className = `task-card ${task.completed ? 'completed' : ''}`;
      el.setAttribute('draggable', 'true');
      el.setAttribute('data-id', task.id);
      
      el.innerHTML = `
        <div class="task-checkbox ${task.completed ? 'checked' : ''}" data-action="toggle">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        
        <div class="task-content">
          <div class="task-title">${this.escapeHtml(task.title)}</div>
          <div class="task-meta">
            <span class="priority-badge ${pData.class}">${pData.label}</span>
            <span>🍅 ${task.completedPomodoros} / ${task.estimatedPomodoros}</span>
            ${task.deadline ? `<span title="Deadline">📅 ${task.deadline}</span>` : ''}
            <div class="task-progress-bar">
              <div class="task-progress-fill" style="width: ${progressPercent}%;"></div>
            </div>
          </div>
        </div>
        
        <div class="task-actions">
          <button class="btn-icon" data-action="edit" title="Edit">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="16 3 21 8 8 21 3 21 3 16 16 3"/></svg>
          </button>
          <button class="btn-icon danger" data-action="delete" title="Delete">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
          </button>
        </div>
      `;

      // Actions
      el.querySelector('[data-action="toggle"]').addEventListener('click', () => {
        window.taskManager.toggleComplete(task.id);
        this.refresh();
      });
      el.querySelector('[data-action="edit"]').addEventListener('click', () => {
        this.openModal(task);
      });
      el.querySelector('[data-action="delete"]').addEventListener('click', () => {
        if (confirm("Are you sure you want to delete this task?")) {
          window.taskManager.deleteTask(task.id);
          this.refresh();
          if (window.timerPage) window.timerPage.refreshTasks();
          if (window.statsPage) window.statsPage.refresh();
        }
      });

      // Drag and Drop implementation
      el.addEventListener('dragstart', (e) => {
        this.draggedId = task.id;
        e.dataTransfer.effectAllowed = 'move';
        setTimeout(() => el.classList.add('dragging'), 0);
      });
      
      el.addEventListener('dragend', () => {
        el.classList.remove('dragging');
        this.draggedId = null;
        
        // Re-calculate order and save
        const orderedIds = Array.from(this.taskList.querySelectorAll('.task-card')).map(card => card.getAttribute('data-id'));
        window.taskManager.reorder(orderedIds);
      });
      
      this.taskList.appendChild(el);
    });

    // Setup drag over container
    this.taskList.addEventListener('dragover', (e) => {
      e.preventDefault();
      const dragging = this.taskList.querySelector('.dragging');
      if (!dragging) return;
      
      const afterElement = this.getDragAfterElement(this.taskList, e.clientY);
      if (afterElement == null) {
        this.taskList.appendChild(dragging);
      } else {
        this.taskList.insertBefore(dragging, afterElement);
      }
    });
  }

  getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.task-card:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      } else {
        return closest;
      }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
  }

  escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
  }
}
