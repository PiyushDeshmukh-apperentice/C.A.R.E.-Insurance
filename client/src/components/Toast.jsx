import React, { useState, useCallback } from 'react';
import { X } from 'lucide-react';

/**
 * Toast Notification Component
 * Replaces alert() calls with themed notifications
 * Supports success, error, and info variants
 */

export const Toast = ({ 
  id, 
  message, 
  type = 'info', 
  onClose,
  autoClose = true,
  duration = 3000 
}) => {
  const [isVisible, setIsVisible] = useState(true);

  React.useEffect(() => {
    if (!autoClose) return;

    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose?.(id);
    }, duration);

    return () => clearTimeout(timer);
  }, [autoClose, duration, id, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    onClose?.(id);
  };

  if (!isVisible) return null;

  // Theme colors
  const themes = {
    success: {
      bg: '#3DB68A',
      border: '#2A9770',
      icon: '✓'
    },
    error: {
      bg: '#E63946',
      border: '#D62828',
      icon: '✕'
    },
    info: {
      bg: '#0C204B',
      border: '#081B3D',
      icon: 'ℹ'
    }
  };

  const theme = themes[type] || themes.info;

  return (
    <div
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        backgroundColor: theme.bg,
        borderLeft: `4px solid ${theme.border}`,
        color: '#FFFFFF',
        padding: '16px 20px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        maxWidth: '400px',
        animation: 'slideIn 0.3s ease-out',
        fontFamily: '"Outfit", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        fontSize: '14px',
        fontWeight: '500',
        zIndex: 9999,
        minHeight: '48px'
      }}
    >
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        @keyframes slideOut {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(400px);
            opacity: 0;
          }
        }
      `}</style>

      <span style={{ fontSize: '18px', flexShrink: 0 }}>
        {type === 'success' && '✓'}
        {type === 'error' && '✕'}
        {type === 'info' && 'ℹ'}
      </span>

      <span style={{ flex: 1 }}>{message}</span>

      <button
        onClick={handleClose}
        style={{
          background: 'none',
          border: 'none',
          color: '#FFFFFF',
          cursor: 'pointer',
          padding: '4px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'opacity 0.2s ease',
          opacity: 0.7,
          flexShrink: 0
        }}
        onMouseEnter={(e) => (e.target.style.opacity = '1')}
        onMouseLeave={(e) => (e.target.style.opacity = '0.7')}
      >
        <X size={18} />
      </button>
    </div>
  );
};

/**
 * Toast Container Component
 * Manages multiple toasts
 */
export const ToastContainer = ({ toasts, onRemove }) => {
  return (
    <div style={{ position: 'fixed', top: 0, right: 0, zIndex: 9999 }}>
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          {...toast}
          onClose={onRemove}
        />
      ))}
    </div>
  );
};

/**
 * Hook to use toast notifications
 * Usage:
 * const { showToast } = useToast();
 * showToast('Success!', 'success');
 */
export const useToast = () => {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now();
    const newToast = { id, message, type, autoClose: true, duration };
    
    setToasts((prev) => [...prev, newToast]);

    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  return {
    toasts,
    showToast,
    removeToast,
    success: (message, duration) => showToast(message, 'success', duration),
    error: (message, duration) => showToast(message, 'error', duration),
    info: (message, duration) => showToast(message, 'info', duration)
  };
};

/**
 * Global Toast Context for App-wide access
 */
export const ToastContext = React.createContext();

export const ToastProvider = ({ children }) => {
  const toast = useToast();

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <ToastContainer toasts={toast.toasts} onRemove={toast.removeToast} />
    </ToastContext.Provider>
  );
};

/**
 * Hook to use toast from context
 * Usage:
 * const toast = useToastContext();
 * toast.success('User created!');
 */
export const useToastContext = () => {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToastContext must be used within ToastProvider');
  }
  return context;
};

export default Toast;
