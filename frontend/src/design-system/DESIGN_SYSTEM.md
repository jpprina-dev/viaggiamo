# Viajamos — Design System "Ruta Gaucha"

> **Cómo actualizar la UI:** Este documento es la fuente de verdad. Para cambiar un aspecto visual, actualizá primero los tokens aquí, luego aplicá los cambios en `tailwind.config.js` (colors/radii/shadows) y `globals.css` (CSS variables). Los componentes usan las clases Tailwind generadas de esos tokens.

---

## 1. Dirección Creativa: "The Trusted Path"

La UI de Viajamos se construye sobre el concepto del **vecino que te lleva a Córdoba**: confiable, cálido, sin frialdad corporativa. El diseño rechaza la rigidez de los grids genéricos a favor de:

- **Asymmetric Layering** — elementos superpuestos con márgenes asimétricos
- **Soft-Touch Surfaces** — capas tonales en lugar de bordes explícitos
- **Editorial Spacing** — espaciado generoso que guía el ojo con ritmo
- **Glassmorphism** — elementos flotantes con blur para profundidad

---

## 2. Paleta de Colores

### Colores Primarios

| Token | Clase Tailwind | Valor Hex | Uso |
|-------|---------------|-----------|-----|
| Primary | `text-primary` / `bg-primary` | `#006d33` | Verde oscuro base, texto de links |
| Primary Container | `bg-primary-container` | `#7ce495` | **CTA principal**, highlights, borders activos |
| On-Primary Fixed | `text-primary-on-fixed` | `#00210b` | Texto sobre primary-container |

### Colores Secundarios (Teal)

| Token | Clase Tailwind | Valor Hex | Uso |
|-------|---------------|-----------|-----|
| Secondary | `bg-secondary` | `#006a64` | Teal oscuro, acciones secundarias |
| Secondary Container | `bg-secondary-container` | `#96f3e9` | Badges, chips, iconos bg |
| On-Secondary Fixed | `text-secondary-on-fixed` | `#00201e` | Texto sobre secondary-container |

### Colores Terciarios (Naranja / Madera)

| Token | Clase Tailwind | Valor Hex | Uso |
|-------|---------------|-----------|-----|
| Tertiary | `text-tertiary` | `#8e4e14` | Acento cálido, precios, énfasis |
| Tertiary Container | `bg-tertiary-container` | `#ffc295` | Badges de estado, acento en cards |

### Anchor Dark

| Token | Clase Tailwind | Valor Hex | Uso |
|-------|---------------|-----------|-----|
| Anchor Dark | `bg-anchor-dark` | `#21212b` | **NavBar, Hero, secciones oscuras, Footer** |

### Superficies (Surface Hierarchy)

> Regla: separar contenido con cambio de superficie, **nunca con bordes `1px solid`**.

| Token | Clase Tailwind | Valor Hex | Uso |
|-------|---------------|-----------|-----|
| Surface | `bg-surface` | `#fcf8ff` | Fondo general de páginas |
| Container Lowest | `bg-surface-container-lowest` | `#ffffff` | Cards flotantes, modals |
| Container Low | `bg-surface-container-low` | `#f5f2ff` | Secciones secundarias |
| Container | `bg-surface-container` | `#efecfa` | Contenedores de formulario |
| Container High | `bg-surface-container-high` | `#e9e6f5` | Input backgrounds (filled style) |
| Container Highest | `bg-surface-container-highest` | `#e3e1ef` | Hover states, seleccionados |

### On-Surface y Outline

| Token | Clase Tailwind | Valor Hex | Uso |
|-------|---------------|-----------|-----|
| On-Surface | `text-on-surface` | `#1b1b24` | Texto principal (**nunca negro puro**) |
| On-Surface Variant | `text-on-surface-variant` | `#3e4a3f` | Texto secundario, placeholders |
| Outline Variant | `border-outline-variant` | `#becabc` | Ghost borders (usar al 15% opacity) |

---

## 3. Tipografía

**Font:** Plus Jakarta Sans (cargado via `next/font/google`)

| Rol | Clase Tailwind | Tamaño | Peso | Uso |
|-----|---------------|--------|------|-----|
| Display LG | `text-display-lg` | 3.5rem | 700 | Hero headlines |
| Display MD | `text-display-md` | 2.75rem | 700 | Page heroes |
| Headline LG | `text-headline-lg` | 2rem | 700 | Sección principal |
| Headline MD | `text-headline-md` | 1.75rem | 700 | Subtítulos de sección |
| Headline SM | `text-headline-sm` | 1.5rem | 700 | Card titles, precios |
| Title LG | `text-title-lg` | 1.25rem | 700 | Sub-headers |
| Title MD | `text-title-md` | 1.125rem | 700 | NavBar links |
| Title SM | `text-title-sm` | 1rem | 700 | Labels prominentes |
| Body LG | `text-body-lg` | 1rem | 400 | Texto de lectura |
| Body MD | `text-body-md` | 0.875rem | 400 | Descripciones, meta |
| Label MD | `text-label-md` | 0.75rem | 700 | Tags, overlines |

**Filosofía:** Usar escala de contraste alto. Un `display-lg` junto a un `body-md` crea el ritmo editorial que guía el ojo.

---

## 4. Border Radius

| Token | Clase Tailwind | Valor | Uso |
|-------|---------------|-------|-----|
| md | `rounded-md` | 12px | Inputs, chips pequeños |
| lg | `rounded-lg` | 16px | Cards, contenedores |
| xl | `rounded-xl` | 24px | **Botones primarios**, panels |
| 2xl | `rounded-2xl` | 32px | Modals, overlays grandes |
| full | `rounded-full` | 9999px | Avatares, badges circulares |

> **Regla:** Mínimo `rounded-lg` (16px). Nunca usar `rounded` (8px) ni `rounded-sm` (6px) para elementos interactivos principales.

---

## 5. Sombras

| Nombre | Clase Tailwind | Uso |
|--------|---------------|-----|
| Ambient | `shadow-ambient` | Cards flotantes, panels |
| Ambient LG | `shadow-ambient-lg` | Modals, drawers |
| Glass | `shadow-glass` | NavBar sticky, glassmorphism elements |

**Regla:** Las sombras usan `rgba(27,27,36, 0.06-0.09)` — nunca negro puro. Efecto de luz natural.

---

## 6. Patrones de Componentes

### Botones

```tsx
// Primario — CTA principal (mint green)
<Button variant="primary">Buscar</Button>
// bg: #7ce495 (primary-container), text: #00210b, radius: xl

// Secundario — acción de apoyo (teal claro)
<Button variant="secondary">Ver más</Button>
// bg: #96f3e9 (secondary-container), text: #00716a, radius: xl

// Fantasma — acción de baja prominencia
<Button variant="ghost">Cancelar</Button>
// sin bg, text: primary, radius: xl

// Dark — sobre fondos oscuros (anchor-dark sections)
<Button variant="dark">Publicar Viaje</Button>
// bg: #7ce495, text: #00210b, radius: xl

// Peligro
<Button variant="danger">Eliminar</Button>
// bg: error (#ba1a1a), text: white, radius: xl
```

### Cards

```tsx
// Tonal — card estándar (no usar shadow explícita, usar bg diferente al padre)
<Card variant="tonal">contenido</Card>
// bg: surface-container-lowest (#fff) sobre surface-container-low (#f5f2ff)

// Ambient — card con sombra suave
<Card variant="ambient">contenido</Card>
// bg: #fff, shadow-ambient, radius: lg

// Sin bordes explícitos — usar color shift para separar
```

### Inputs

```tsx
// Filled — estilo Ruta Gaucha
<Input variant="filled" label="Origen" />
// bg: surface-container-high, sin border, bottom-border-2 en focus con primary-container
// radius: md (12px)
```

### NavBar

```tsx
// Fondo: anchor-dark (#21212b)
// Logo: GradientIcon + "Viajamos" en text-gradient-primary
// Links: texto blanco, hover: text-primary-container
// Sticky con glassmorfismo: glass-dark + backdrop-blur-[20px]
```

### AuthLayout

```tsx
// Full screen con imagen de paisaje argentino + overlay anchor-dark/60
// Card centrado: glass (backdrop-blur-[20px] bg-white/85)
// Logo + Viajamos + form
```

---

## 7. Patrones de Layout

### Landing Page (Desktop)

```
[NavBar — anchor-dark]
[Hero — anchor-dark, bg-pin-watermark]
  → Headline display-lg
  → SearchBar flotante glass + shadow-ambient-lg
[PopularTrips — surface-container-low]
  → Cards tonales (container-lowest sobre container-low)
[HowItWorks — surface]
  → 4 pasos sin divisores, spacing-12 entre ítems
[Benefits — surface-container-low]
  → 4 cards con icon-circle secondary-container
[CTA — anchor-dark]
  → Botones primary + secondary
[Footer — anchor-dark]
```

### Páginas de App (Mobile-first)

```
[NavBar anchor-dark sticky]
[Content en surface]
  → Secciones con bg shift (surface → surface-container-low)
  → Cards: container-lowest con shadow-ambient
[Bottom action button fijo]
  → primary variant, full width, radius-xl
```

---

## 8. Do's & Don'ts

### Hacer:
- ✅ Usar `anchor-dark` (#21212b) para fondos oscuros, **nunca `#000000`**
- ✅ Separar secciones con cambio de `surface-*`, nunca con bordes
- ✅ Mínimo `rounded-lg` (16px) para elementos interactivos
- ✅ Íconos con terminals redondeadas (Lucide React — estilo rounded)
- ✅ Espaciado generoso entre secciones (`py-16 md:py-24`)
- ✅ Glassmorfismo en elementos flotantes (NavBar sticky, cards de auth)

### No hacer:
- ❌ Bordes `border-1 border-gray-200` para separar contenido
- ❌ `#000000` para texto oscuro — usar `text-on-surface` (#1b1b24)
- ❌ `rounded` (8px) para botones o cards principales
- ❌ Fotos de stock — usar avatares con iniciales sobre `secondary-fixed` bg
- ❌ Múltiples colores de acento en la misma sección

---

## 9. Actualizar este sistema

Para cambiar un token:
1. Actualizá el valor en la tabla correspondiente de este archivo
2. Actualizá `frontend/tailwind.config.js` → `theme.extend.colors`
3. Actualizá `frontend/src/app/globals.css` → `:root { --color-* }`
4. Si afecta componentes globales, actualizá los archivos en `src/components/ui/`

Para agregar un nuevo componente:
1. Documentalo en la sección 6 con variantes, colores y radio
2. Creá el archivo en `src/components/ui/NombreComponente/NombreComponente.tsx`
3. Exportalo desde `src/components/ui/index.ts`
