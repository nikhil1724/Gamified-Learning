# Design System Usage Guide

## Quick Reference

### Colors
```css
/* Primary Actions */
color: var(--color-primary);           /* #2563eb */

/* Text */
color: var(--color-text-primary);      /* #0f172a - Main text */
color: var(--color-text-secondary);    /* #475569 - Secondary text */

/* Backgrounds */
background: var(--color-bg-primary);   /* #ffffff */
background: var(--color-bg-secondary); /* #f8fafc */

/* Borders */
border: 1px solid var(--color-border);
```

### Typography
```css
/* Font Sizes */
font-size: var(--font-size-base);    /* 1rem - Default */
font-size: var(--font-size-lg);      /* 1.125rem - Subheading */
font-size: var(--font-size-2xl);     /* 1.75rem - Page title */

/* Font Weights */
font-weight: var(--font-weight-bold); /* 700 - Headings */
font-weight: var(--font-weight-semibold); /* 600 - Labels */
```

### Spacing
```css
/* Use 8px grid */
padding: var(--spacing-4);           /* 32px */
margin: var(--spacing-3);            /* 24px */
gap: var(--spacing-2);               /* 16px */
```

### Shadows
```css
/* Card shadows */
box-shadow: var(--shadow-md);        /* Medium shadow */
box-shadow: var(--shadow-lg);        /* Large shadow */
```

### Animations
```css
/* Smooth transitions */
transition: all var(--transition-base); /* 200ms smooth */
transition: transform var(--transition-fast); /* 150ms */
```

---

## Component Classes

### Buttons
```html
<!-- Primary button -->
<button class="button button--primary">Click Me</button>

<!-- Secondary button -->
<button class="button button--secondary">Cancel</button>

<!-- Outline button -->
<button class="button button--outline">Learn More</button>

<!-- Large button -->
<button class="button button--primary button--lg">Full Size</button>

<!-- Loading state -->
<button class="button button--primary" disabled>
  <span class="button--loading"></span>
  Processing...
</button>
```

### Cards
```html
<!-- Elevated card -->
<div class="card card--elevated">
  <div class="card__header">
    <h3>Title</h3>
  </div>
  <div class="card__content">
    Content here
  </div>
</div>

<!-- Interactive card (with hover effect) -->
<div class="card card--interactive">
  Content here
</div>
```

### Badges
```html
<!-- Primary badge -->
<span class="badge badge--primary">New</span>

<!-- Success badge -->
<span class="badge badge--success">Completed</span>

<!-- Small badge -->
<span class="badge badge--sm badge--secondary">Tag</span>
```

### Forms
```html
<!-- Form group with label -->
<div class="form-group">
  <label class="form-label" for="email">Email</label>
  <input 
    type="email" 
    id="email"
    class="form-input"
    placeholder="Enter email"
  />
  <div class="form-help">We'll never share your email</div>
</div>

<!-- Required field -->
<label class="form-label required">Password</label>

<!-- Error state -->
<input class="form-input error" />

<!-- Success state -->
<input class="form-input success" />

<!-- Checkbox -->
<label class="form-check">
  <input type="checkbox" class="form-checkbox" />
  <span>Agree to terms</span>
</label>
```

---

## Common Patterns

### Page Header
```jsx
<div className="page-header">
  <span className="badge badge--primary">Learning Tracks</span>
  <h1>Courses</h1>
  <p>Pick a path and start learning</p>
</div>
```

### Stat Card
```jsx
<div className="card card--elevated">
  <div className="stat-card">
    <h6>Total XP</h6>
    <p className="stat-value">1,250</p>
  </div>
</div>
```

### Role Selection Card
```jsx
<div className="card card--interactive">
  <div className="role-option__icon">🎓</div>
  <h3>Student</h3>
  <p>Learn courses and participate in quizzes</p>
  <button className="button button--primary">Continue</button>
</div>
```

### Search Input
```jsx
<input 
  className="form-input"
  type="text"
  placeholder="Search courses..."
/>
```

---

## Theme Variables for Future Use

### Light Mode (Current)
```css
--color-bg-primary: #ffffff;
--color-text-primary: #0f172a;
```

### Dark Mode (Ready to implement)
```css
/* To implement: Update these variables */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #1e293b;
    --color-text-primary: #f8fafc;
  }
}
```

---

## Responsive Design

### Breakpoints (Bootstrap compatible)
```css
/* Small devices */
@media (max-width: 576px) { }

/* Medium devices */
@media (max-width: 768px) { }

/* Large devices */
@media (max-width: 992px) { }

/* Extra large */
@media (max-width: 1200px) { }
```

### Grid Layout
```css
/* Responsive grid */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-5);
}
```

---

## Best Practices

### ✅ DO
- Use CSS variables for all colors, spacing, and timings
- Follow the 8px spacing grid consistently
- Use existing component classes
- Apply consistent shadows to cards
- Use design system animations

### ❌ DON'T
- Hardcode colors (use variables)
- Mix spacing values (stick to grid)
- Create custom components (reuse existing ones)
- Override transition timings
- Use inline styles for design tokens

### Example: Right Way
```css
/* ✅ Good */
.my-badge {
  background: var(--color-primary-light);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-full);
  transition: all var(--transition-base);
}

/* ❌ Avoid */
.my-badge {
  background: #dbeafe;
  padding: 8px 12px;
  border-radius: 999px;
  transition: transform 0.2s ease;
}
```

---

## Accessibility Checklist

- [x] Focus states visible on all interactive elements
- [x] Color contrast meets WCAG AA standards
- [x] Font sizes readable (minimum 14px for body text)
- [x] Touch targets minimum 44x44px
- [x] Labels associated with form inputs
- [x] Semantic HTML usage
- [x] Keyboard navigation support
- [x] Screen reader friendly

---

## Performance Tips

1. **CSS Variables**: Reduce file size with variables (no repetition)
2. **Shadow System**: Pre-defined shadows = consistent rendering
3. **Animation Timing**: Consistent transitions = smooth experience
4. **Minimal Specificity**: Use class-based selectors
5. **Component Reuse**: Share styles across pages

---

## Color Reference Card

```
PRIMARY: #2563eb (Blue) - Main actions
DARK:    #1d4ed8 (Dark Blue) - Pressed states
LIGHT:   #dbeafe (Light Blue) - Badges, backgrounds

SUCCESS: #16a34a (Green) - Positive feedback
WARNING: #ea580c (Orange) - Warnings
ERROR:   #dc2626 (Red) - Errors

TEXT PRIMARY:   #0f172a (Dark slate)
TEXT SECONDARY: #475569 (Medium slate)
TEXT MUTED:     #94a3b8 (Light slate)

BG PRIMARY:   #ffffff (White)
BG SECONDARY: #f8fafc (Off-white)
BORDER:       #e2e8f0 (Light gray)
```

---

## Quick Start Template

```jsx
import React from 'react';
import './MyComponent.css';

export default function MyComponent() {
  return (
    <div className="page">
      {/* Header */}
      <div className="page-header">
        <span className="badge badge--primary">Category</span>
        <h1>Title</h1>
      </div>

      {/* Grid of cards */}
      <div className="grid">
        <div className="card card--interactive">
          <h3>Item 1</h3>
          <p>Description</p>
          <button className="button button--primary">Action</button>
        </div>
      </div>
    </div>
  );
}
```

```css
/* MyComponent.css */
/* Use CSS variables for any custom styling */
.page {
  padding: var(--spacing-6);
}

.page-header {
  margin-bottom: var(--spacing-8);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-5);
}
```

---

## Support

For questions about the design system:
1. Check this file first
2. Review [globals.css](src/styles/globals.css) for available variables
3. Look at existing page implementations for patterns
4. Refer to [UI_SYSTEM_COMPLETION.md](UI_SYSTEM_COMPLETION.md) for full documentation
