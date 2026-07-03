// tasks.js - Task manager

const TaskFilter = {
  ALL: 'all',
  PENDING: 'pending',
  COMPLETED: 'completed'
};

class TaskManager {
  constructor() {
    this.tasks = [];
    this.refresh();
  }

  refresh() {
    this.tasks = window.db.getTasks();
    this.tasks.sort((a, b) => a.sortOrder - b.sortOrder);
  }

  getTasks(filter = TaskFilter.ALL, search = '') {
    let filtered = this.tasks;
    
    if (filter === TaskFilter.PENDING) {
      filtered = filtered.filter(t => !t.completed);
    } else if (filter === TaskFilter.COMPLETED) {
      filtered = filtered.filter(t => t.completed);
    }
    
    if (search.trim()) {
      const q = search.toLowerCase();
      filtered = filtered.filter(t => 
        t.title.toLowerCase().includes(q) || 
        t.description.toLowerCase().includes(q)
      );
    }
    
    return filtered;
  }

  getTask(id) {
    return this.tasks.find(t => t.id === id);
  }

  addTask(taskData) {
    const newTask = window.db.addTask(taskData);
    this.refresh();
    return newTask;
  }

  updateTask(id, updates) {
    const updated = window.db.updateTask(id, updates);
    if (updated) {
      this.refresh();
    }
    return updated;
  }

  deleteTask(id) {
    window.db.deleteTask(id);
    this.refresh();
  }

  toggleComplete(id) {
    const task = this.getTask(id);
    if (task) {
      return this.updateTask(id, { completed: !task.completed });
    }
  }

  registerPomodoroCompletion(id) {
    const task = this.getTask(id);
    if (task) {
      const newCount = task.completedPomodoros + 1;
      const updates = { completedPomodoros: newCount };
      if (newCount >= task.estimatedPomodoros) {
        updates.completed = true;
      }
      return this.updateTask(id, updates);
    }
  }

  reorder(orderedIds) {
    // orderedIds is an array of task IDs in the new desired order
    const currentTasks = window.db.getTasks();
    
    // Create a map for quick lookup
    const idToIndex = new Map();
    orderedIds.forEach((id, index) => {
      idToIndex.set(parseInt(id, 10), index);
    });
    
    // Update sortOrder for all tasks
    const updatedTasks = currentTasks.map(t => {
      const newIndex = idToIndex.get(t.id);
      if (newIndex !== undefined) {
        return { ...t, sortOrder: newIndex };
      }
      return t;
    });
    
    window.db.saveTasks(updatedTasks);
    this.refresh();
  }
}

window.taskManager = new TaskManager();
