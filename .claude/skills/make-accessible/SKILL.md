---
name: make-accessible
description: Accessibility improvement workflow auditing WCAG compliance, adding ARIA labels, improving keyboard nav, and screen reader support
allowed-tools:
  - Read
  - Edit
  - Bash
---

# Make Accessible Skill

Accessibility improvement workflow following WCAG 2.1 guidelines. Adds ARIA labels, improves keyboard navigation, ensures screen reader support, proper color contrast, and semantic HTML.

## WCAG Principles (POUR)

1. **Perceivable**: Information must be presentable to users
2. **Operable**: UI must be operable by all users
3. **Understandable**: Information must be understandable
4. **Robust**: Content must work with various assistive technologies

## Accessibility Checklist

### Keyboard Navigation
- [ ] All interactive elements keyboard accessible
- [ ] Logical tab order
- [ ] Visible focus indicators
- [ ] Skip to main content link
- [ ] No keyboard traps

```html
<!-- Skip link -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<!-- Visible focus -->
<style>
:focus {
  outline: 2px solid #4A90E2;
  outline-offset: 2px;
}
</style>
```

### ARIA Labels
```html
<!-- Buttons without visible text -->
<button aria-label="Close dialog">×</button>

<!-- Form inputs -->
<label for="email">Email</label>
<input id="email" type="email" aria-describedby="email-help" />
<span id="email-help">We'll never share your email</span>

<!-- Status messages -->
<div role="alert" aria-live="polite">Form submitted successfully</div>

<!-- Current page -->
<nav>
  <a href="/" aria-current="page">Home</a>
  <a href="/about">About</a>
</nav>
```

### Color Contrast
- Normal text: 4.5:1 minimum
- Large text (18pt+ or 14pt+ bold): 3:1 minimum
- UI components: 3:1 minimum

```css
/* Good contrast */
.text {
  color: #000000;
  background: #FFFFFF; /* 21:1 ratio */
}

/* Check with tools */
/* - WebAIM Contrast Checker */
/* - Chrome DevTools */
```

### Alt Text for Images
```html
<!-- Informative images -->
<img src="chart.png" alt="Sales increased 30% in Q4" />

<!-- Decorative images -->
<img src="decorative-border.png" alt="" />

<!-- Complex images -->
<img src="diagram.png" alt="System architecture diagram" 
     aria-describedby="diagram-description" />
<div id="diagram-description">
  Detailed description of the architecture...
</div>
```

### Semantic HTML
```html
<!-- Good -->
<header>
  <nav>
    <ul>
      <li><a href="/">Home</a></li>
    </ul>
  </nav>
</header>
<main>
  <article>
    <h1>Title</h1>
    <p>Content</p>
  </article>
</main>
<footer>
  <p>Copyright 2024</p>
</footer>

<!-- Bad -->
<div class="header">
  <div class="nav">
    <div class="nav-item">Home</div>
  </div>
</div>
```

### Form Accessibility
```html
<form>
  <fieldset>
    <legend>Personal Information</legend>

    <label for="name">Name *</label>
    <input 
      id="name" 
      type="text" 
      required 
      aria-required="true"
      aria-invalid="false"
      aria-describedby="name-error"
    />
    <span id="name-error" role="alert" style="display:none;">
      Name is required
    </span>
  </fieldset>

  <button type="submit">Submit</button>
</form>
```

### Screen Reader Testing
```bash
# macOS VoiceOver: Cmd+F5
# Windows Narrator: Win+Ctrl+Enter
# NVDA (Windows): Free download
# JAWS (Windows): Commercial
```

## Automated Testing

```bash
# axe-core
npm install --save-dev @axe-core/cli
axe https://example.com

# pa11y
npm install --save-dev pa11y
pa11y https://example.com

# Lighthouse
lighthouse https://example.com --only-categories=accessibility
```

```javascript
// Jest + jest-axe
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

test('should have no accessibility violations', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Best Practices
- Use semantic HTML first
- Test with keyboard only
- Test with screen readers
- Maintain 4.5:1 color contrast
- Provide text alternatives
- Make focus visible
- Use ARIA when needed (not always)
- Test with real users with disabilities
