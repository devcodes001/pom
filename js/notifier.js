// notifier.js - Desktop notifications and audio alarm

class Notifier {
  constructor() {
    this.audio = new Audio('assets/notification.wav');
    this._requestPermission();
  }

  _requestPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }

  notify(title, message) {
    const settings = window.settingsManager.get();
    
    // Play sound
    if (settings.soundEnabled) {
      this.audio.play().catch(e => console.log('Audio play failed:', e));
    }
    
    // Show desktop notification
    if (settings.notifyEnabled && 'Notification' in window && Notification.permission === 'granted') {
      try {
        new Notification(title, {
          body: message,
          icon: 'assets/icon.png'
        });
      } catch (e) {
        console.log('Notification failed:', e);
      }
    }
    
    // Also show in-app toast
    this.showToast(title, message);
  }

  showToast(title, message) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = `${title} - ${message}`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(20px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, 4000);
  }
}

window.notifier = new Notifier();
