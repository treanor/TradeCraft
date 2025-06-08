---
applyTo: '**'
---
# Copilot & Contributor Instructions

This project is a Vue 3 + TypeScript single-page app for a personal trading journal and analytics dashboard.

---

## Coding Standards

* **Use Vue 3 Composition API and `<script setup lang="ts">` syntax.**
* **All new files should use TypeScript for type safety.**
* **Organize all components in `/src/components`, composables in `/src/composables`, and stores in `/src/stores`.**
* **State management should use Pinia, not Vuex or global variables.**
* **Use the official Vue Router for all navigation.**
* **Use ESLint and Prettier for code linting and formatting; all code must pass linting before merging.**

---

## Project Structure

```
/src
  /components   // Reusable Vue components
  /pages        // Top-level page components (routed)
  /composables  // Custom hooks for logic reuse
  /stores       // Pinia stores for app state
  /assets       // Images, icons, etc.
  /utils        // General-purpose TypeScript utilities
  /types        // Global type declarations
  App.vue
  main.ts
```

---

## SOLID Principles for Web

* **Single Responsibility:**
  Each component, composable, or service should do *one thing* well. Split up large logic into smaller, focused units.
* **Open/Closed:**
  Components and composables should be extensible via props, slots, or injection, not by editing their source.
* **Liskov Substitution:**
  Favor base components with slot-based composition and type-safe props; all children must work with parent contracts.
* **Interface Segregation:**
  Only expose the props/methods/components a consumer needs. Avoid "god objects."
* **Dependency Inversion:**
  Use dependency injection for services (e.g., API clients), and composables for logic, not direct imports in components.

---

## Best Practices

* **Components:**

  * Small, focused, and reusable.
  * Name with PascalCase, e.g., `TradeTable.vue`.
  * Use props/emit for communication; avoid global events.
* **Pinia Stores:**

  * Use for shared app state; keep UI state local to components.
  * Strongly type with TypeScript interfaces.
* **Composables:**

  * For logic reused across components (e.g., useTradeStats, useLocalStorage).
* **APIs & Services:**

  * Centralize all API logic in `/src/services`.
  * Handle errors gracefully; never let unhandled exceptions bubble to UI.
* **Styling:**

  * Use `<style scoped>` in components, or global styles in `/src/assets/styles`.
  * Prefer CSS variables and utility classes for consistency.
* **Testing:**

  * All critical utilities and stores should have unit tests (Vitest).
* **Documentation:**

  * Add JSDoc/type comments for all public composables, stores, and utilities.
  * All components should have a brief description as a comment at the top.
* **Accessibility:**

  * Use semantic HTML, proper labels, and keyboard navigation where possible.

---

## Code Review Checklist

* [ ] TypeScript type safety is enforced in all files.
* [ ] All components are single-responsibility and focused.
* [ ] No direct mutation of Pinia state outside store actions.
* [ ] Code is linted and formatted with Prettier/ESLint.
* [ ] All reusable logic is in composables/services, not duplicated in components.
* [ ] Documentation and comments are up to date.

---

## Additional Notes

* When in doubt, prefer *clarity and maintainability* over cleverness.
* All new features should be designed to scale (anticipate growth in data/features).

---

*Please follow these instructions to ensure a scalable, clean, and maintainable codebase. Thank you!*
