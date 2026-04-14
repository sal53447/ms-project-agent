# Requirements — Website Redesign

## Functional Requirements

### FR-01 — Content Management
- Marketing team must be able to create, edit, and publish pages without developer involvement.
- CMS must support rich text, images, video embeds, and reusable components.
- Content previews must be available before publishing.

### FR-02 — Page Coverage
- All pages in the agreed page inventory (v1.2) must be redesigned and migrated.
- Pages: Home, About, Products (all sub-pages), Pricing, Blog, Contact, Careers.

### FR-03 — SEO
- All pages must have editable meta titles, descriptions, and Open Graph tags.
- XML sitemap must be auto-generated and submitted to Google Search Console.
- Structured data (JSON-LD) for key page types (Organisation, Product, BlogPosting).

### FR-04 — Analytics & Tracking
- GA4 and Hotjar must be instrumented on all pages.
- Events: page views, CTA clicks, form submissions, scroll depth.

### FR-05 — Forms & Integrations
- All lead-capture forms must push to HubSpot.
- Form submissions must trigger the existing HubSpot workflows without interruption.

### FR-06 — URL Redirects
- A redirect map must be created covering all old URLs → new URLs.
- All redirects must return HTTP 301 and be live at the same time as go-live.

## Non-Functional Requirements

### NFR-01 — Performance
- Core Web Vitals: LCP < 2.5s, CLS < 0.1, FID < 100ms (desktop and mobile).
- Lighthouse performance score >= 85 on all page templates.

### NFR-02 — Accessibility
- WCAG 2.1 AA compliance across all pages.
- Automated a11y audit must pass with zero critical violations before launch.

### NFR-03 — Responsiveness
- All pages must be fully responsive: desktop (1440px), tablet (768px), mobile (375px).

### NFR-04 — Browser Support
- Chrome 120+, Firefox 120+, Safari 16+, Edge 120+.
- No IE11 support required.

### NFR-05 — Security
- HTTPS enforced on all pages.
- CSP headers configured.
- No PII stored client-side.
