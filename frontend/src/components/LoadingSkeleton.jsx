/**
 * LoadingSkeleton — Reusable loading skeleton components
 */
import { Skeleton, Card, Space } from 'antd';

/**
 * Generic page skeleton with title and content
 */
export function PageSkeleton() {
  return (
    <div>
      <Skeleton.Input active style={{ width: 200, marginBottom: 24 }} />
      <Skeleton active paragraph={{ rows: 4 }} />
    </div>
  );
}

/**
 * Table skeleton
 */
export function TableSkeleton({ rows = 5 }) {
  return (
    <div>
      <Skeleton.Input active style={{ width: 300, marginBottom: 16 }} />
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {Array.from({ length: rows }).map((_, i) => (
          <Skeleton key={i} active paragraph={{ rows: 1 }} />
        ))}
      </Space>
    </div>
  );
}

/**
 * Card skeleton
 */
export function CardSkeleton({ count = 3 }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i}>
          <Skeleton active paragraph={{ rows: 3 }} />
        </Card>
      ))}
    </div>
  );
}

/**
 * List skeleton
 */
export function ListSkeleton({ rows = 5 }) {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {Array.from({ length: rows }).map((_, i) => (
        <Card key={i} size="small">
          <Skeleton active avatar paragraph={{ rows: 2 }} />
        </Card>
      ))}
    </Space>
  );
}

/**
 * Form skeleton
 */
export function FormSkeleton({ fields = 6 }) {
  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {Array.from({ length: fields }).map((_, i) => (
        <div key={i}>
          <Skeleton.Input active style={{ width: 150, marginBottom: 8 }} size="small" />
          <Skeleton.Input active style={{ width: '100%' }} />
        </div>
      ))}
      <Skeleton.Button active style={{ width: 100 }} />
    </Space>
  );
}

/**
 * Default export is PageSkeleton
 */
export default PageSkeleton;
