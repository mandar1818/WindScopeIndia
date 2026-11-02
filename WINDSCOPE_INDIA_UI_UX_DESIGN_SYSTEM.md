# WindScope India — UI/UX Design System & Human-Centred Specifications

**Document Reference:** `WINDSCOPE_INDIA_UI_UX_DESIGN_SYSTEM.md`  
**Date:** November 1, 2026  
**Status:** Certified Institutional Standard  
**Primary Working Directory:** `D:\WindScopeIndia`  

---

## Executive Summary

This document establishes the UI/UX design system and front-end interface architecture of **WindScope India**. It replaces commercial AI-template aesthetics with an institutional energy analytics design language: natural earth-toned authority, high information density, WCAG AA accessibility, unambiguous data provenance indicators, and strict elimination of decorative fluff.

---

## 1. Design System & Palette Specification

The visual identity is anchored in institutional utility operations and environmental governance:

| Token Name | Hex Code | Visual Tone | Semantic Usage |
| :--- | :--- | :--- | :--- |
| `nature-forest` | `#245B45` | Deep Forest Green | Primary brand identity, active tabs, primary buttons, headers |
| `nature-forest-light` | `#EBF2EE` | Soft Mint | Selected badge backgrounds, hover accents, subtle highlights |
| `nature-sage` | `#8FAE91` | Sage / Moss Green | Secondary chart series (Small Hydro, Biomass), metric card borders |
| `nature-bg` | `#F5F7F2` | Pale Mist Off-White | Canvas background; reduces visual fatigue compared to pure harsh white |
| `nature-surface` | `#FFFFFF` | Pure White | Elevated cards, tables, modals, input containers |
| `nature-border` | `#E1E8DF` | Muted Willow Grey | Structural dividers, table borders, card borders |
| `nature-text` | `#26332C` | Near-Black Slate | High-contrast body text, primary metrics, chart axes |
| `nature-muted` | `#748078` | Muted Charcoal | Secondary labels, units ($\text{MU, MW, m/s}$), table headers, timestamps |
| `nature-actual` | `#26966B` | Emerald Green | Actual metered generation outturn, `VERIFIED_OFFICIAL` badges |
| `nature-forecast` | `#5689B5` | Steel Blue | Forecast lines, weather data, ECMWF reanalysis indicators |
| `nature-risk` | `#D49A42` | Amber / Ochre | Overforecast short risk, `OFFICIAL_SOURCE_UNVERIFIED` warnings |
| `nature-danger` | `#C45A4A` | Burnt Sienna | Reconciliation discrepancies, missing blocks, `BLOCKED` status |

---

## 2. Elimination of AI-Generated Visual Tropes

To maintain credibility with grid operators, traders, and regulatory auditors, all generic AI templates have been eliminated:

| Rejected AI Trope | Institutional Replacement in WindScope India |
| :--- | :--- |
| Floating glowing orbs / pulsing particles | Static, clean 1px border dividers (`#E1E8DF`) |
| Purple / Magenta / Cyan neon gradients | Flat natural surfaces with restrained 1-level elevation |
| Vague marketing taglines ("Revolutionizing Power with AI") | Statutory descriptors ("CEA & Grid-India Statistical System") |
| Oversized cards with 50% empty whitespace | Compact, data-dense tabular rows with monospaced numbers |
| Concealed simulated telemetry | Prominent, persistent Provenance Badges on every page |

---

## 3. Component Architecture & Information Hierarchy

### 3.1 Top Navigation (`TopNav.tsx`)
* **Header Height:** Fixed 56px (`h-14`) with glassmorphism backdrop (`bg-white/95 backdrop-blur-sm`).
* **Title Hierarchy:** Displays page title, concise institutional subtitle, and current provenance status.
* **Dynamic Provenance Badge:** Shows real-time dataset mode (`CEA & Grid-India • Verified + Reanalysis`).

### 3.2 Collapsible Sidebar (`Sidebar.tsx`)
* **Dual-State Layout:** Full navigation drawer (256px / `w-64`) collapsible to compact icon bar (64px / `w-16`).
* **Category Partitioning:**
  1. *National Overview* (Overview, Map)
  2. *Geographic Intelligence* (State Explorer, Regional Comparison, Multi-Year Analytics)
  3. *Technology Intelligence* (Wind, Solar, Hydro, 500GW Target Tracker)
  4. *Predictive & Weather* (Forecasting Lab, Weather Intelligence)
  5. *Governance & Data* (Data Explorer, Quality & Provenance, Methodology)
  6. *Preserved Benchmark* (UK Benchmark — January 2026)

### 3.3 Data Visualization Standards (Recharts)
* **Monospaced Numbers:** All values in tables and tooltips use `font-mono` for vertical decimal alignment.
* **Consistent Axis Formatting:** Units are always displayed in parentheses: `Generation (MU)`, `Capacity (MW)`, `Wind Velocity (m/s)`.
* **Zero-Baseline Enforcement:** Bar and area charts always ground at 0.0 to prevent optical magnification of minor variances.

---

## 4. Accessibility & Responsiveness Certification

* **Contrast Ratio:** Body text (`#26332C` on `#F5F7F2`) achieves a **12.4:1 contrast ratio**, exceeding the WCAG AA requirement (4.5:1) and meeting WCAG AAA standard.
* **Viewport Support:** Verified responsive across 1280px (laptops), 1440px (workstations), and 1920px (trading desks).
* **Keyboard Navigation:** All interactive selectors, modals, and tabs support full keyboard tab navigation and focus rings.

