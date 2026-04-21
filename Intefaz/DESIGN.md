# Design System Documentation: Clinical Precision & The Diagnostic Canvas

## 1. Overview & Creative North Star
This design system is built upon a Creative North Star we call **"The Diagnostic Canvas."** 

In the high-stakes world of AI-powered radiology, we must move beyond the "SaaS template" aesthetic. Our goal is to create a digital environment that feels as authoritative as a medical journal and as precise as a surgical instrument. We achieve this through **Editorial Sophistication**: utilizing intentional asymmetry, high-contrast typography scales, and layered depth to guide a radiologist’s eye toward what matters most—the data.

The system rejects the "boxed-in" feel of traditional medical software. Instead, it utilizes breathing room, tonal shifts, and "Glassmorphism" to create a workspace that feels expansive, modern, and profoundly trustworthy.

---

## 2. Colors & Tonal Architecture
The palette is rooted in a clinical white base, punctuated by a commanding "Medical Blue" and a sophisticated range of grays.

### The "No-Line" Rule
To maintain a premium, editorial feel, **1px solid borders are strictly prohibited for sectioning.** We do not "box" content. Boundaries must be defined through:
*   **Background Shifts:** e.g., a `surface-container-low` section sitting on a `surface` background.
*   **Tonal Transitions:** Using subtle shifts in the gray scale to denote a change in context.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—like stacked sheets of frosted glass. 
*   **Surface (Base):** `#f8f9fb`. The main canvas.
*   **Surface-Container-Low:** Used for large secondary sidebars or background grouping.
*   **Surface-Container-Lowest:** `#ffffff`. Reserved for primary "Result Cards" or "X-ray Viewers" to make them pop against the base.
*   **Surface-Container-Highest:** `#e0e3e5`. Used for interactive elements like input fields or inactive probability bar tracks.

### Signature Textures (The Glass & Gradient Rule)
*   **Medical Blue Depth:** For main CTAs and the primary "Analyze" button, use a subtle linear gradient from `primary` (#0058bf) to `primary_container` (#006fee). This adds a "jewel" quality that feels more premium than flat color.
*   **The Glass Overlay:** When placing diagnostic tools over an X-ray image, use a semi-transparent `surface_container_lowest` with a 12px `backdrop-blur`. This ensures the UI feels integrated into the image, not pasted on top.

---

## 3. Typography
We use a dual-font strategy to balance authority with accessibility.

*   **Display & Headlines (Manrope):** A modern, geometric sans-serif. Use this for diagnostic results and high-level patient headers. Its wide stance conveys stability and technological advancement.
*   **Body & Labels (Public Sans):** A neutral, highly legible sans-serif designed for clarity. Use this for all medical data, probability percentages, and instructional text.

**Hierarchy Strategy:**
*   **Display-LG (3.5rem):** Use for the primary probability percentage (e.g., "98%").
*   **Headline-SM (1.5rem):** Use for diagnosis titles (e.g., "Pneumonia Detected").
*   **Label-MD (0.75rem):** Use for metadata, such as timestamps and DICOM tags, in all-caps with 0.05em letter spacing.

---

## 4. Elevation & Depth
In this system, depth equals importance. We achieve this through **Tonal Layering** rather than traditional structural lines.

*   **The Layering Principle:** Place a `surface-container-lowest` card (Pure White) on top of a `surface-container-low` section to create a soft, natural lift.
*   **Ambient Shadows:** For floating elements (like a diagnostic tooltip), use a 32px blur with 6% opacity, tinted with the `on_surface` color (#191c1e). This mimics natural clinical lighting.
*   **The Ghost Border Fallback:** If a border is required for accessibility (e.g., a focused input), use the `outline_variant` token at **20% opacity**. Never use 100% opaque borders.

---

## 5. Components

### The Diagnostic Card
*   **Structure:** No dividers. Use `title-md` for the patient name and `body-sm` for the ID.
*   **Status Indicators:** Instead of a simple colored dot, use a vertical "Signal Bar" (4px wide) on the far left of the card.
    *   **Healthy:** `secondary` (#445e92)
    *   **Pneumonia:** `tertiary` (#994200)
    *   **COVID-19:** `error` (#ba1a1a)

### Medical Image Viewer
*   **The Frame:** Use `surface_container_highest` as the background for the viewer to provide a "darkroom" contrast for X-rays.
*   **Overlays:** Use the Glassmorphism rule for zoom/pan controls.

### Horizontal Probability Bars
*   **Track:** 8px height, `surface_container_high` with a `lg` (0.5rem) corner radius.
*   **Fill:** A vibrant gradient of the status color.
*   **Animation:** Always animate from 0% to the target % on page load to signify the AI "calculating."

### Upload Area
*   **Style:** An expansive area using `surface_container_low`. 
*   **Border:** Use a "Ghost Border" (Dashed, `outline_variant` at 40% opacity).
*   **Vibe:** Minimalist. A single `display-sm` icon of a document and a `title-sm` call to action.

### Buttons
*   **Primary:** Gradient fill, `xl` (0.75rem) corner radius. High-contrast `on_primary` text.
*   **Secondary:** Ghost style. No background, `primary` text, and a `surface_container_high` hover state.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use whitespace as a separator. If you think you need a line, add 16px of extra padding instead.
*   **Do** use `manrope` for numbers to make the AI's "confidence" feel like a headline.
*   **Do** lean into asymmetry. A wider left margin for navigation and a tighter right-side for metadata creates a modern, editorial rhythm.

### Don’t:
*   **Don't** use pure black (#000000). Use `on_surface` (#191c1e) for all "black" text to keep the interface soft.
*   **Don't** use standard shadows. If an element doesn't look "lifted" enough with tonal shifts, re-evaluate the surface hierarchy.
*   **Don't** use bright, saturated greens for "Healthy." Use our refined `secondary` blue-gray tones to keep the vibe clinical and calm.