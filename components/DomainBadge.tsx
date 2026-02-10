interface DomainBadgeProps {
  domain: string;
  size?: 'sm' | 'md' | 'lg';
}

const DOMAIN_COLORS: Record<string, string> = {
  'econ': 'bg-blue-100 text-blue-800 border-blue-200',
  'q-bio': 'bg-green-100 text-green-800 border-green-200',
  'physics': 'bg-purple-100 text-purple-800 border-purple-200',
  'cs': 'bg-orange-100 text-orange-800 border-orange-200',
  'nlin': 'bg-red-100 text-red-800 border-red-200',
  'unknown': 'bg-gray-100 text-gray-800 border-gray-200',
};

const DOMAIN_NAMES: Record<string, string> = {
  'econ': 'Economics',
  'q-bio': 'Biology',
  'physics': 'Physics',
  'cs': 'Computer Science',
  'nlin': 'Nonlinear Dynamics',
  'unknown': 'Other',
};

const SIZE_CLASSES = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-sm px-3 py-1',
  lg: 'text-base px-4 py-1.5',
};

export default function DomainBadge({ domain, size = 'md' }: DomainBadgeProps) {
  const colorClasses = DOMAIN_COLORS[domain] || DOMAIN_COLORS['unknown'];
  const sizeClasses = SIZE_CLASSES[size];
  const displayName = DOMAIN_NAMES[domain] || domain;

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium border ${colorClasses} ${sizeClasses}`}
    >
      {displayName}
    </span>
  );
}
