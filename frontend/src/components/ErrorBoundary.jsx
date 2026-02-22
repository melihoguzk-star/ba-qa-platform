/**
 * ErrorBoundary — Global error boundary for React errors
 */
import { Component } from 'react';
import { Result, Button } from 'antd';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '50px', textAlign: 'center' }}>
          <Result
            status="500"
            title="Bir Hata Oluştu"
            subTitle="Üzgünüz, beklenmeyen bir hata oluştu. Lütfen sayfayı yenileyin veya ana sayfaya dönün."
            extra={
              <div>
                <Button type="primary" onClick={this.handleReset}>
                  Ana Sayfaya Dön
                </Button>
                <Button onClick={() => window.location.reload()} style={{ marginLeft: 8 }}>
                  Sayfayı Yenile
                </Button>
              </div>
            }
          />
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ marginTop: 20, textAlign: 'left', maxWidth: 600, margin: '20px auto' }}>
              <summary>Error Details (Development Only)</summary>
              <pre style={{ background: '#f5f5f5', padding: 10, borderRadius: 4, overflow: 'auto' }}>
                {this.state.error.toString()}
                {this.state.error.stack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
