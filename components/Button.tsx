import React from 'react';
import Link from 'next/link';

/**
 * Button Component - Analog Quest Design System
 *
 * Standardized button styles using design tokens.
 * Supports primary, secondary, and tertiary variants.
 * Can render as button or link (Next.js Link).
 */

type ButtonVariant = 'primary' | 'secondary' | 'tertiary';
type ButtonSize = 'sm' | 'md' | 'lg';

interface BaseButtonProps {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  className?: string;
  disabled?: boolean;
}

interface ButtonAsButton extends BaseButtonProps {
  as?: 'button';
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  href?: never;
}

interface ButtonAsLink extends BaseButtonProps {
  as: 'link';
  href: string;
  onClick?: never;
  type?: never;
}

type ButtonProps = ButtonAsButton | ButtonAsLink;

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  as = 'button',
  ...props
}) => {
  // Base styles (always applied)
  const baseStyles = 'inline-block font-mono text-sm uppercase tracking-wide transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-brown focus:ring-offset-2';

  // Variant styles
  const variantStyles = {
    primary: 'bg-brown-dark text-cream hover:bg-brown disabled:bg-brown/50 disabled:cursor-not-allowed',
    secondary: 'bg-transparent text-brown border border-brown/20 hover:border-brown/40 disabled:border-brown/10 disabled:text-brown/50 disabled:cursor-not-allowed',
    tertiary: 'bg-transparent text-brown-dark hover:text-brown disabled:text-brown/50 disabled:cursor-not-allowed',
  };

  // Size styles
  const sizeStyles = {
    sm: 'px-4 py-2 text-xs',
    md: 'px-8 py-3 text-sm',
    lg: 'px-10 py-4 text-base',
  };

  const combinedStyles = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`.trim();

  // Render as Link (Next.js)
  if (as === 'link' && 'href' in props && props.href) {
    return (
      <Link href={props.href} className={combinedStyles}>
        {children}
      </Link>
    );
  }

  // Render as button
  return (
    <button
      type={props.type || 'button'}
      onClick={props.onClick}
      disabled={disabled}
      className={combinedStyles}
    >
      {children}
    </button>
  );
};

export default Button;
