/**
 * Error Handler — Centralized error handling utilities
 */
import { notification } from 'antd';

/**
 * Show error notification for API errors
 */
export function showErrorNotification(error, defaultMessage = 'Bir hata oluştu') {
  const title = 'Hata';
  let description = defaultMessage;

  // Extract error message from different error formats
  if (error?.response?.data?.detail) {
    // FastAPI error format
    if (typeof error.response.data.detail === 'string') {
      description = error.response.data.detail;
    } else if (Array.isArray(error.response.data.detail)) {
      // Validation errors
      description = error.response.data.detail
        .map((err) => `${err.loc?.join('.')}: ${err.msg}`)
        .join('\n');
    }
  } else if (error?.response?.data?.message) {
    description = error.response.data.message;
  } else if (error?.message) {
    description = error.message;
  }

  notification.error({
    message: title,
    description,
    duration: 5,
    placement: 'topRight',
  });

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('API Error:', error);
  }
}

/**
 * Show success notification
 */
export function showSuccessNotification(message, description) {
  notification.success({
    message,
    description,
    duration: 3,
    placement: 'topRight',
  });
}

/**
 * Show warning notification
 */
export function showWarningNotification(message, description) {
  notification.warning({
    message,
    description,
    duration: 4,
    placement: 'topRight',
  });
}

/**
 * Show info notification
 */
export function showInfoNotification(message, description) {
  notification.info({
    message,
    description,
    duration: 3,
    placement: 'topRight',
  });
}

/**
 * Handle network errors (offline, timeout, etc.)
 */
export function handleNetworkError(error) {
  if (!navigator.onLine) {
    notification.error({
      message: 'Bağlantı Hatası',
      description: 'İnternet bağlantınızı kontrol edin.',
      duration: 0, // Don't auto-close
      placement: 'topRight',
    });
    return;
  }

  if (error?.code === 'ECONNABORTED' || error?.message?.includes('timeout')) {
    notification.error({
      message: 'Zaman Aşımı',
      description: 'İstek zaman aşımına uğradı. Lütfen tekrar deneyin.',
      duration: 5,
      placement: 'topRight',
    });
    return;
  }

  showErrorNotification(error);
}
