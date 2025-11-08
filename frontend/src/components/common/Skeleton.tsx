import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string;
  height?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  variant = 'text',
  width,
  height,
}) => {
  const baseClasses = 'animate-pulse bg-gray-200';

  const variantClasses = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };

  const style: React.CSSProperties = {};
  if (width) style.width = width;
  if (height) style.height = height;

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={style}
    />
  );
};

// Pre-built skeleton patterns
export const SkeletonCard: React.FC = () => (
  <div className="bg-white rounded-lg shadow p-6 space-y-4">
    <Skeleton variant="rectangular" height="200px" />
    <Skeleton width="60%" />
    <Skeleton width="40%" />
    <Skeleton width="80%" />
  </div>
);

export const SkeletonExerciseCard: React.FC = () => (
  <div className="bg-white rounded-lg shadow overflow-hidden animate-fade-in">
    <div className="md:flex">
      <div className="md:w-1/3 bg-gray-100 flex items-center justify-center p-4">
        <Skeleton variant="rectangular" width="100%" height="200px" />
      </div>
      <div className="md:w-2/3 p-6 space-y-4">
        <Skeleton width="70%" height="32px" />
        <div className="space-y-2">
          <Skeleton width="50%" />
          <Skeleton width="40%" />
        </div>
        <div className="space-y-2">
          <Skeleton width="30%" height="20px" />
          <div className="flex gap-2">
            <Skeleton variant="rectangular" width="80px" height="28px" />
            <Skeleton variant="rectangular" width="80px" height="28px" />
            <Skeleton variant="rectangular" width="80px" height="28px" />
          </div>
        </div>
      </div>
    </div>
  </div>
);

export const SkeletonTable: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div className="space-y-2">
    <div className="flex gap-4 p-4 bg-gray-50 rounded">
      <Skeleton width="20%" height="16px" />
      <Skeleton width="20%" height="16px" />
      <Skeleton width="15%" height="16px" />
      <Skeleton width="20%" height="16px" />
      <Skeleton width="15%" height="16px" />
    </div>
    {Array.from({ length: rows }).map((_, idx) => (
      <div key={idx} className="flex gap-4 p-4 bg-white rounded border">
        <Skeleton width="20%" />
        <Skeleton width="20%" />
        <Skeleton width="15%" />
        <Skeleton width="20%" />
        <Skeleton width="15%" />
      </div>
    ))}
  </div>
);

export const SkeletonStatCard: React.FC = () => (
  <div className="bg-white rounded-lg shadow p-6 space-y-2">
    <Skeleton width="60%" height="14px" />
    <Skeleton width="40%" height="32px" />
  </div>
);
