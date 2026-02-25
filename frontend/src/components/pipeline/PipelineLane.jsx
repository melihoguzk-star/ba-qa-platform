/**
 * PipelineLane — Horizontal lane wrapper for Kanban board
 */
import { Typography, Badge } from 'antd';
import { Children } from 'react';

const { Text } = Typography;

export default function PipelineLane({ title, icon, color, children }) {
  // Count completed cards among children
  const childArray = Children.toArray(children);
  const completedCount = childArray.filter(
    child => child.props?.status === 'completed'
  ).length;

  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <span style={{ color, fontSize: 18 }}>{icon}</span>
        <Text strong style={{ fontSize: 15 }}>{title}</Text>
        {completedCount > 0 && (
          <Badge count={completedCount} style={{ backgroundColor: color }} />
        )}
        <Text type="secondary" style={{ fontSize: 12 }}>
          ({completedCount}/{childArray.length})
        </Text>
      </div>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        {children}
      </div>
    </div>
  );
}
