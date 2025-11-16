# Gemini Context

This file provides context for Gemini to understand the project.

## Project: cs-command-reference

A web-based command reference for Counter-Strike 2.

## Project Analysis

### Project Overview

This is a Blazor WebAssembly application designed to be a command reference for Counter-Strike 2. It allows users to browse and search for console commands. The application is deployed to GitHub Pages.

### Core Technologies

*   **Framework:** Blazor WebAssembly (standalone)
*   **Language:** C#
*   **.NET Version:** 9.0
*   **UI Framework:** Bootstrap 5
*   **Icon Library:** Bootstrap Icons
*   **Deployment:** GitHub Actions to GitHub Pages.

### Best Practices for CSS Sizing

**Rule: Use Relative Units When Possible**

Use **relative units** like `rem` and `em` instead of static `px` values. This ensures your website is responsive and accessible, as the layout will scale correctly with user preferences and different screen sizes.

* **`rem` for Global Sizing:** Use `rem` for things like `font-size`, `padding`, and `margin` on major components. This keeps your spacing consistent across the site, as `rem` is based on the root `<html>` font size.

* **`em` for Component-Specific Sizing:** Use `em` for elements that should scale relative to their parent, such as padding inside a button or the size of an icon next to text.

* **`px` for Fixed Sizes:** Use `px` only when a value should never change, like for a `1px` border or a tiny icon.

**Violation:** Using hard-coded `px` values for most layout and text sizing.