---
name: build-component
description: Frontend component development workflow scaffolding React/Vue/Svelte components with logic, styles, tests, and Storybook stories following accessibility guidelines
allowed-tools:
  - Read
  - Bash
  - Edit
  - Write
---

# Build Component Skill

Frontend component development workflow for scaffolding, implementing, styling, testing, and documenting React, Vue, and Svelte components with accessibility built-in.

## React Component Workflow

### 1. Scaffold Component

```bash
mkdir -p src/components/Button
touch src/components/Button/Button.tsx
touch src/components/Button/Button.module.css
touch src/components/Button/Button.test.tsx
touch src/components/Button/Button.stories.tsx
touch src/components/Button/index.ts
```

### 2. Implement Component

```typescript
// Button.tsx
import React from 'react';
import styles from './Button.module.css';

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  ariaLabel?: string;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  children,
  onClick,
  type = 'button',
  ariaLabel
}) => {
  return (
    <button
      className={`${styles.button} ${styles[variant]} ${styles[size]}`}
      disabled={disabled || loading}
      onClick={onClick}
      type={type}
      aria-label={ariaLabel}
      aria-busy={loading}
    >
      {loading ? <span className={styles.spinner} aria-hidden="true" /> : null}
      <span className={loading ? styles.hiddenText : ''}>{children}</span>
    </button>
  );
};
```

### 3. Add Styles

```css
/* Button.module.css */
.button {
  font-family: inherit;
  font-weight: 600;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.button:focus {
  outline: 2px solid #4A90E2;
  outline-offset: 2px;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Variants */
.primary {
  background: #4A90E2;
  color: white;
}

.primary:hover:not(:disabled) {
  background: #357ABD;
}

.secondary {
  background: #E0E0E0;
  color: #333;
}

.danger {
  background: #E74C3C;
  color: white;
}

/* Sizes */
.small {
  padding: 6px 12px;
  font-size: 14px;
}

.medium {
  padding: 10px 20px;
  font-size: 16px;
}

.large {
  padding: 14px 28px;
  font-size: 18px;
}

/* Loading state */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.hiddenText {
  visibility: hidden;
}
```

### 4. Write Tests

```typescript
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} disabled>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('shows loading state', () => {
    render(<Button loading>Click me</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
  });

  it('applies correct variant classes', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    expect(screen.getByRole('button')).toHaveClass('primary');

    rerender(<Button variant="danger">Danger</Button>);
    expect(screen.getByRole('button')).toHaveClass('danger');
  });

  it('is accessible', async () => {
    const { container } = render(<Button>Accessible button</Button>);
    // Run axe accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### 5. Create Storybook Story

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger']
    },
    size: {
      control: 'select',
      options: ['small', 'medium', 'large']
    },
    disabled: { control: 'boolean' },
    loading: { control: 'boolean' }
  }
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    children: 'Primary Button',
    variant: 'primary'
  }
};

export const Secondary: Story = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary'
  }
};

export const Danger: Story = {
  args: {
    children: 'Delete',
    variant: 'danger'
  }
};

export const Loading: Story = {
  args: {
    children: 'Loading...',
    loading: true
  }
};

export const Disabled: Story = {
  args: {
    children: 'Disabled',
    disabled: true
  }
};

export const Sizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
      <Button size="small">Small</Button>
      <Button size="medium">Medium</Button>
      <Button size="large">Large</Button>
    </div>
  )
};
```

### 6. Export Component

```typescript
// index.ts
export { Button } from './Button';
export type { ButtonProps } from './Button';
```

## Accessibility Guidelines

### Keyboard Navigation
- All interactive elements must be keyboard accessible
- Use `tabIndex={0}` for custom interactive elements
- Implement keyboard event handlers (Enter, Space for buttons)

### ARIA Attributes
```typescript
// Good examples
<button aria-label="Close dialog">×</button>
<button aria-pressed={isPressed}>Toggle</button>
<div role="alert" aria-live="polite">{message}</div>
<input aria-describedby="email-help" />
<div id="email-help">Enter your email address</div>
```

### Focus Management
```typescript
// Trap focus in modal
const modalRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  if (isOpen) {
    const focusableElements = modalRef.current?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements?.[0] as HTMLElement;
    firstElement?.focus();
  }
}, [isOpen]);
```

### Color Contrast
- Ensure 4.5:1 contrast ratio for normal text
- 3:1 for large text (18pt+ or 14pt+ bold)
- Use tools like WebAIM Color Contrast Checker

### Semantic HTML
```typescript
// Good
<button onClick={handleClick}>Click me</button>
<nav><a href="/home">Home</a></nav>

// Bad (avoid)
<div onClick={handleClick}>Click me</div> // Not keyboard accessible
<div><span onClick={goHome}>Home</span></div> // Not semantic
```

## Vue Component Example

```vue
<!-- Button.vue -->
<template>
  <button
    :class="['btn', `btn-${variant}`, `btn-${size}`]"
    :disabled="disabled || loading"
    :aria-busy="loading"
    @click="$emit('click')"
  >
    <span v-if="loading" class="spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  disabled: false,
  loading: false
});

defineEmits<{
  (e: 'click'): void;
}>();
</script>

<style scoped>
/* Styles similar to React example */
</style>
```

## Svelte Component Example

```svelte
<!-- Button.svelte -->
<script lang="ts">
  export let variant: 'primary' | 'secondary' | 'danger' = 'primary';
  export let size: 'small' | 'medium' | 'large' = 'medium';
  export let disabled = false;
  export let loading = false;
</script>

<button
  class="btn btn-{variant} btn-{size}"
  {disabled}
  aria-busy={loading}
  on:click
>
  {#if loading}
    <span class="spinner" aria-hidden="true" />
  {/if}
  <slot />
</button>

<style>
  /* Styles similar to React example */
</style>
```

## Best Practices

- **Component composition**: Build small, reusable components
- **Props over config**: Prefer explicit props to configuration objects
- **Accessibility first**: Build it in from the start
- **Test behavior, not implementation**: Test what users see/do
- **Document with Storybook**: Visual documentation is powerful
- **Use TypeScript**: Catch errors early, better DX
- **CSS Modules or CSS-in-JS**: Scope styles to component
- **Responsive design**: Mobile-first approach
