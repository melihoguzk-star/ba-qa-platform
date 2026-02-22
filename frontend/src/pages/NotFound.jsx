/**
 * NotFound — 404 error page
 */
import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <Result
        status="404"
        title="404"
        subTitle="Üzgünüz, aradığınız sayfa bulunamadı."
        extra={
          <div>
            <Button type="primary" onClick={() => navigate('/')}>
              Ana Sayfaya Dön
            </Button>
            <Button onClick={() => navigate(-1)} style={{ marginLeft: 8 }}>
              Geri Git
            </Button>
          </div>
        }
      />
    </div>
  );
}
