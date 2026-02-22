/**
 * EmptyState — Reusable empty state component
 */
import { Empty, Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

export default function EmptyState({
  image = Empty.PRESENTED_IMAGE_SIMPLE,
  title = 'Veri Bulunamadı',
  description,
  actionText,
  onAction,
  actionIcon = <PlusOutlined />,
}) {
  return (
    <div style={{ padding: '60px 20px', textAlign: 'center' }}>
      <Empty
        image={image}
        description={
          <div>
            <div style={{ fontSize: 16, fontWeight: 500, marginBottom: 8 }}>{title}</div>
            {description && <div style={{ color: '#8c8c8c' }}>{description}</div>}
          </div>
        }
      >
        {actionText && onAction && (
          <Button type="primary" icon={actionIcon} onClick={onAction}>
            {actionText}
          </Button>
        )}
      </Empty>
    </div>
  );
}
