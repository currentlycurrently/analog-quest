interface DomainBadgeProps {
  domain: string;
  size?: 'sm' | 'md' | 'lg';
}

const DOMAIN_COLORS: Record<string, string> = {
  'econ': 'bg-cream-warm text-brown border-brown/20',
  'q-bio': 'bg-teal-light text-brown border-teal/30',
  'physics': 'bg-cream-mid text-brown border-brown/20',
  'cs': 'bg-cream-light text-brown border-brown/20',
  'nlin': 'bg-teal/10 text-brown border-teal/20',
  'unknown': 'bg-brown/5 text-brown/70 border-brown/10',
};

const DOMAIN_NAMES: Record<string, string> = {
  'econ': 'economics',
  'q-bio': 'biology',
  'physics': 'physics',
  'cs': 'computer science',
  'nlin': 'nonlinear dynamics',
  'unknown': 'other',
};

const SIZE_CLASSES = {
  sm: 'text-xs px-2 py-0.5 font-mono uppercase tracking-wide',
  md: 'text-sm px-3 py-1 font-mono uppercase tracking-wide',
  lg: 'text-base px-4 py-1.5 font-mono uppercase tracking-wide',
};

export default function DomainBadge({ domain, size = 'md' }: DomainBadgeProps) {
  const colorClasses = DOMAIN_COLORS[domain] || DOMAIN_COLORS['unknown'];
  const sizeClasses = SIZE_CLASSES[size];
  const displayName = DOMAIN_NAMES[domain] || domain;

  return (
    <span
      className={`inline-flex items-center border ${colorClasses} ${sizeClasses}`}
    >
      {displayName}
    </span>
  );
}
