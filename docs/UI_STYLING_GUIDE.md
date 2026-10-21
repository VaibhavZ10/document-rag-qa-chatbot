# Frontend styling

The application uses React, Tailwind CSS, and Framer Motion. Shared styles are defined in [`globals.css`](../frontend/src/styles/globals.css), with theme tokens in [`tailwind.config.ts`](../frontend/tailwind.config.ts).

## Theme

- The `accent` palette contains orange shades from 50 to 950.
- Highlighted text and icons use `accent-300` and `accent-400`.
- Primary buttons use a pale orange gradient and `text-accent-950`.
- Dark backgrounds, translucent surfaces, borders, and backdrop blur provide the shared glass-card appearance.
- Success and error states retain their semantic colors.
- Shared shadow tokens include `glass`, `glass-lg`, `glow`, and `glow-lg`.

## Components

| Concern | Implementation |
| --- | --- |
| Buttons, variants, sizes, ripple and shine | [`button.tsx`](../frontend/src/components/ui/button.tsx) |
| Shared card surfaces | [`glass-card.tsx`](../frontend/src/components/ui/glass-card.tsx) |
| Viewport reveals and staggered children | [`scroll-reveal.tsx`](../frontend/src/components/ui/scroll-reveal.tsx) |
| Image loading skeleton and fallback | [`safe-image.tsx`](../frontend/src/components/ui/safe-image.tsx) |
| Chat message presentation | [`chat-message.tsx`](../frontend/src/components/chat/chat-message.tsx) |
| Toast presentation | [`app-toast.tsx`](../frontend/src/lib/app-toast.tsx) |
| Responsive navigation and title | [`header.tsx`](../frontend/src/components/layout/header.tsx) |

## Interaction and layout

The shared `Button` exposes `default`, `destructive`, `outline`, `secondary`, `ghost`, and `link` variants, with `default`, `sm`, `lg`, and `icon` sizes. Ripple is enabled by default; shine is opt-in for the default variant.

`ScrollReveal` supports `up`, `down`, `left`, `right`, and `none` directions. Its default duration is 0.65 seconds and `once` defaults to false. The hero implements additional scroll-linked movement in [`hero-section.tsx`](../frontend/src/components/sections/hero-section.tsx).

The header displays `DRC` below 480px and the full application name at wider widths. Preserve the full accessible link label, visible focus styles, readable contrast, and mobile layouts when modifying shared components.

Extend the existing components and theme tokens when adding UI. The current routes are Home, Chat, and About; there is no frontend API-status dashboard.
