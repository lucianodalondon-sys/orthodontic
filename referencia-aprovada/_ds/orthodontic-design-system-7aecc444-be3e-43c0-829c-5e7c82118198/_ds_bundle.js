/* @ds-bundle: {"format":4,"namespace":"OrthoDonticDesignSystem_7aecc4","components":[{"name":"Button","sourcePath":"components/actions/Button.jsx"},{"name":"IconButton","sourcePath":"components/actions/IconButton.jsx"},{"name":"Icon","sourcePath":"components/brand/Icon.jsx"},{"name":"Logo","sourcePath":"components/brand/Logo.jsx"},{"name":"Badge","sourcePath":"components/content/Badge.jsx"},{"name":"Bubble","sourcePath":"components/content/Bubble.jsx"},{"name":"Card","sourcePath":"components/content/Card.jsx"},{"name":"Rating","sourcePath":"components/content/Rating.jsx"},{"name":"Tag","sourcePath":"components/content/Tag.jsx"},{"name":"Dialog","sourcePath":"components/feedback/Dialog.jsx"},{"name":"Toast","sourcePath":"components/feedback/Toast.jsx"},{"name":"Tooltip","sourcePath":"components/feedback/Tooltip.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"Radio","sourcePath":"components/forms/Radio.jsx"},{"name":"Select","sourcePath":"components/forms/Select.jsx"},{"name":"Switch","sourcePath":"components/forms/Switch.jsx"},{"name":"Tabs","sourcePath":"components/navigation/Tabs.jsx"}],"sourceHashes":{"components/actions/Button.jsx":"572ca05ddad3","components/actions/IconButton.jsx":"23ea5fb55f6b","components/brand/Icon.jsx":"d49d1060da59","components/brand/Logo.jsx":"fba03a6b0ce8","components/content/Badge.jsx":"44d3284997a3","components/content/Bubble.jsx":"3eda8c5a4464","components/content/Card.jsx":"cb259f242aa8","components/content/Rating.jsx":"8ee06120d56a","components/content/Tag.jsx":"855c82deb3a6","components/feedback/Dialog.jsx":"041c649e3a9e","components/feedback/Toast.jsx":"94e8bcbb5193","components/feedback/Tooltip.jsx":"d4f853581323","components/forms/Checkbox.jsx":"14509743f3b0","components/forms/Input.jsx":"ebb057a2640d","components/forms/Radio.jsx":"669afb837bb0","components/forms/Select.jsx":"6d480368a549","components/forms/Switch.jsx":"fa64588aa644","components/navigation/Tabs.jsx":"cfbb21cb9aeb"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.OrthoDonticDesignSystem_7aecc4 = window.OrthoDonticDesignSystem_7aecc4 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/actions/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Inject component CSS once (uses design-system tokens for all values). */
const CSS = `
.od-btn{
  --_ring: var(--ring);
  display:inline-flex; align-items:center; justify-content:center; gap:.6em;
  font-family:var(--font-sans); font-weight:var(--fw-bold);
  letter-spacing:var(--tracking-wide); line-height:1; white-space:nowrap;
  border:0; border-radius:var(--radius-pill); cursor:pointer; text-decoration:none;
  transition:transform var(--dur) var(--ease-bounce), box-shadow var(--dur) var(--ease-standard),
             background-color var(--dur) var(--ease-standard), color var(--dur) var(--ease-standard),
             filter var(--dur) var(--ease-standard);
  -webkit-user-select:none; user-select:none;
}
.od-btn:focus-visible{ outline:none; box-shadow:var(--ring); }
.od-btn:active{ transform:scale(.97); }
.od-btn__ic{ display:inline-flex; align-items:center; }
.od-btn__ic svg{ width:1.15em; height:1.15em; display:block; }

.od-btn--sm{ font-size:var(--text-sm); padding:.6rem 1.05rem; }
.od-btn--md{ font-size:var(--text-base); padding:.8rem 1.5rem; }
.od-btn--lg{ font-size:var(--text-lg); padding:1rem 2rem; }
.od-btn--block{ width:100%; }
.od-btn--square{ border-radius:var(--radius-md); }

.od-btn--primary{ background:var(--grad-cyan); color:var(--text-on-primary); box-shadow:var(--shadow-sm); }
.od-btn--primary:hover{ transform:translateY(-1px); box-shadow:var(--shadow-cyan); }
.od-btn--secondary{ background:var(--od-navy); color:#fff; box-shadow:var(--shadow-sm); }
.od-btn--secondary:hover{ transform:translateY(-1px); background:var(--od-navy-600); box-shadow:var(--shadow-md); }
.od-btn--outline{ background:transparent; color:var(--od-navy); box-shadow:inset 0 0 0 2px var(--od-navy); }
.od-btn--outline:hover{ background:var(--od-navy); color:#fff; }
.od-btn--ghost{ background:transparent; color:var(--od-cyan-600); }
.od-btn--ghost:hover{ background:var(--od-cyan-050); }
.od-btn--magenta{ background:var(--grad-magenta); color:#fff; box-shadow:var(--shadow-sm); }
.od-btn--magenta:hover{ transform:translateY(-1px); box-shadow:var(--shadow-magenta); }
.od-btn--yellow{ background:var(--grad-yellow); color:var(--od-navy); box-shadow:var(--shadow-sm); }
.od-btn--yellow:hover{ transform:translateY(-1px); box-shadow:var(--shadow-yellow); }
.od-btn--teal{ background:var(--grad-teal); color:#fff; box-shadow:var(--shadow-sm); }
.od-btn--teal:hover{ transform:translateY(-1px); box-shadow:var(--shadow-md); }

.od-btn[disabled], .od-btn[aria-disabled="true"]{
  background:var(--od-line); color:var(--od-gray-300); box-shadow:none;
  cursor:not-allowed; transform:none; filter:none; pointer-events:none;
}
`;
if (typeof document !== "undefined" && !document.getElementById("od-btn-css")) {
  const s = document.createElement("style");
  s.id = "od-btn-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}

/**
 * OrthoDontic Button — the pill-shaped CTA seen across the brand's
 * marketing ("Saiba Mais") and product UI.
 */
function Button({
  children,
  variant = "primary",
  size = "md",
  block = false,
  square = false,
  iconLeft = null,
  iconRight = null,
  disabled = false,
  href,
  type = "button",
  className = "",
  ...rest
}) {
  const cls = ["od-btn", `od-btn--${variant}`, `od-btn--${size}`, block ? "od-btn--block" : "", square ? "od-btn--square" : "", className].filter(Boolean).join(" ");
  const inner = /*#__PURE__*/React.createElement(React.Fragment, null, iconLeft ? /*#__PURE__*/React.createElement("span", {
    className: "od-btn__ic"
  }, iconLeft) : null, children ? /*#__PURE__*/React.createElement("span", null, children) : null, iconRight ? /*#__PURE__*/React.createElement("span", {
    className: "od-btn__ic"
  }, iconRight) : null);
  if (href && !disabled) {
    return /*#__PURE__*/React.createElement("a", _extends({
      href: href,
      className: cls
    }, rest), inner);
  }
  return /*#__PURE__*/React.createElement("button", _extends({
    type: type,
    className: cls,
    disabled: disabled,
    "aria-disabled": disabled || undefined
  }, rest), inner);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/actions/Button.jsx", error: String((e && e.message) || e) }); }

// components/actions/IconButton.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-iconbtn{
  display:inline-flex; align-items:center; justify-content:center;
  border:0; cursor:pointer; padding:0; color:inherit;
  border-radius:var(--radius-circle); background:transparent;
  transition:transform var(--dur) var(--ease-bounce), box-shadow var(--dur) var(--ease-standard),
             background-color var(--dur) var(--ease-standard), color var(--dur) var(--ease-standard);
}
.od-iconbtn svg{ width:1.25em; height:1.25em; display:block; }
.od-iconbtn:focus-visible{ outline:none; box-shadow:var(--ring); }
.od-iconbtn:active{ transform:scale(.92); }
.od-iconbtn--rounded{ border-radius:var(--radius-md); }

.od-iconbtn--sm{ width:2rem; height:2rem; font-size:14px; }
.od-iconbtn--md{ width:2.6rem; height:2.6rem; font-size:18px; }
.od-iconbtn--lg{ width:3.2rem; height:3.2rem; font-size:22px; }

.od-iconbtn--solid{ background:var(--od-cyan); color:#fff; box-shadow:var(--shadow-sm); }
.od-iconbtn--solid:hover{ background:var(--od-cyan-600); box-shadow:var(--shadow-cyan); }
.od-iconbtn--navy{ background:var(--od-navy); color:#fff; }
.od-iconbtn--navy:hover{ background:var(--od-navy-600); }
.od-iconbtn--soft{ background:var(--od-sky); color:var(--od-navy); }
.od-iconbtn--soft:hover{ background:#CFE0F4; }
.od-iconbtn--ghost{ background:transparent; color:var(--od-navy); }
.od-iconbtn--ghost:hover{ background:var(--od-cyan-050); }
.od-iconbtn--outline{ background:transparent; color:var(--od-navy); box-shadow:inset 0 0 0 2px var(--border-strong); }
.od-iconbtn--outline:hover{ box-shadow:inset 0 0 0 2px var(--od-cyan); color:var(--od-cyan-600); }

.od-iconbtn[disabled]{ color:var(--od-gray-300); background:var(--od-line); cursor:not-allowed; box-shadow:none; transform:none; pointer-events:none; }
.od-iconbtn--ghost[disabled], .od-iconbtn--outline[disabled]{ background:transparent; }
`;
if (typeof document !== "undefined" && !document.getElementById("od-iconbtn-css")) {
  const s = document.createElement("style");
  s.id = "od-iconbtn-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}

/** Circular (or rounded) icon-only button. Requires an accessible label. */
function IconButton({
  icon,
  label,
  variant = "ghost",
  size = "md",
  rounded = false,
  disabled = false,
  className = "",
  ...rest
}) {
  const cls = ["od-iconbtn", `od-iconbtn--${variant}`, `od-iconbtn--${size}`, rounded ? "od-iconbtn--rounded" : "", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("button", _extends({
    type: "button",
    className: cls,
    "aria-label": label,
    title: label,
    disabled: disabled
  }, rest), icon);
}
Object.assign(__ds_scope, { IconButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/actions/IconButton.jsx", error: String((e && e.message) || e) }); }

// components/brand/Icon.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Lazy-load Lucide (the system's chosen icon set) once, from CDN. */
let _lucidePromise = null;
function ensureLucide() {
  if (typeof window !== "undefined" && window.lucide) return Promise.resolve();
  if (!_lucidePromise) {
    _lucidePromise = new Promise(resolve => {
      const s = document.createElement("script");
      s.src = "https://unpkg.com/lucide@latest/dist/umd/lucide.min.js";
      s.onload = resolve;
      s.onerror = resolve;
      document.head.appendChild(s);
    });
  }
  return _lucidePromise;
}

/**
 * Icon — a wrapper around Lucide (this system's chosen icon set).
 * Renders any Lucide icon by `name` (e.g. "calendar", "arrow-right").
 */
function Icon({
  name,
  size = 20,
  color = "currentColor",
  strokeWidth = 2,
  className = "",
  style,
  ...rest
}) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    let alive = true;
    ensureLucide().then(() => {
      if (!alive || !ref.current || !window.lucide) return;
      ref.current.innerHTML = "";
      const el = document.createElement("i");
      el.setAttribute("data-lucide", name);
      ref.current.appendChild(el);
      try {
        window.lucide.createIcons({
          attrs: {
            width: size,
            height: size,
            stroke: color,
            "stroke-width": strokeWidth
          }
        });
      } catch (e) {/* noop */}
    });
    return () => {
      alive = false;
    };
  }, [name, size, color, strokeWidth]);
  return /*#__PURE__*/React.createElement("span", _extends({
    ref: ref,
    className: ["od-icon", className].filter(Boolean).join(" "),
    style: {
      display: "inline-flex",
      width: size,
      height: size,
      color,
      ...style
    }
  }, rest));
}
Object.assign(__ds_scope, { Icon });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/Icon.jsx", error: String((e && e.message) || e) }); }

// components/brand/Logo.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Resolve the assets folder from the bundle's own URL so <Logo> works wherever
   the design system is mounted. Override with window.__OD_ASSETS_BASE if needed. */
let ASSET_BASE = "assets/logos";
try {
  const src = document.currentScript && document.currentScript.src || "";
  const m = src.match(/^(.*\/)_ds_bundle\.js/);
  if (m) ASSET_BASE = m[1] + "assets/logos";
} catch (e) {/* noop */}
const FILES = {
  horizontal: "logo-horizontal.png",
  vertical: "logo-vertical.png",
  symbol: "symbol.png",
  "horizontal-white": "logo-horizontal-white.png",
  "symbol-white": "symbol-white.png"
};

/**
 * OrthoDontic logo. Renders the real extracted brand asset — never a redraw.
 * Use the -white variants on cyan / navy / photographic backgrounds.
 */
function Logo({
  variant = "horizontal",
  height,
  width,
  basePath,
  alt = "OrthoDontic",
  className = "",
  style,
  ...rest
}) {
  const base = basePath || typeof window !== "undefined" && window.__OD_ASSETS_BASE || ASSET_BASE;
  const file = FILES[variant] || FILES.horizontal;
  const isSymbol = variant.indexOf("symbol") === 0;
  const st = {
    display: "block",
    height: height || (isSymbol ? 40 : 34),
    width: width || "auto",
    ...style
  };
  return /*#__PURE__*/React.createElement("img", _extends({
    src: `${base}/${file}`,
    alt: alt,
    className: ["od-logo", className].filter(Boolean).join(" "),
    style: st
  }, rest));
}
Object.assign(__ds_scope, { Logo });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/Logo.jsx", error: String((e && e.message) || e) }); }

// components/content/Badge.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-badge{
  display:inline-flex; align-items:center; gap:.35em; font-family:var(--font-sans);
  font-weight:var(--fw-bold); font-size:var(--text-xs); line-height:1;
  padding:.4em .7em; border-radius:var(--radius-pill); letter-spacing:.01em; white-space:nowrap;
}
.od-badge svg{ width:1.1em; height:1.1em; }
.od-badge--sm{ font-size:11px; padding:.35em .6em; }

/* solid */
.od-badge--cyan{ background:var(--od-cyan); color:#fff; }
.od-badge--navy{ background:var(--od-navy); color:#fff; }
.od-badge--magenta{ background:var(--od-magenta); color:#fff; }
.od-badge--success{ background:var(--color-success); color:#fff; }
.od-badge--warning{ background:var(--color-warning); color:#fff; }
.od-badge--danger{ background:var(--color-danger); color:#fff; }
.od-badge--neutral{ background:var(--od-gray-500); color:#fff; }

/* soft */
.od-badge--soft.od-badge--cyan{ background:var(--od-cyan-050); color:var(--od-cyan-600); }
.od-badge--soft.od-badge--navy{ background:var(--od-sky); color:var(--od-navy); }
.od-badge--soft.od-badge--magenta{ background:#FCE7EE; color:var(--od-magenta); }
.od-badge--soft.od-badge--success{ background:var(--color-success-bg); color:#1E8C79; }
.od-badge--soft.od-badge--warning{ background:var(--color-warning-bg); color:#C9741F; }
.od-badge--soft.od-badge--danger{ background:var(--color-danger-bg); color:var(--color-danger); }
.od-badge--soft.od-badge--neutral{ background:var(--od-mist); color:var(--od-gray-700); }
`;
if (typeof document !== "undefined" && !document.getElementById("od-badge-css")) {
  const s = document.createElement("style");
  s.id = "od-badge-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}

/** Small status / label pill. `soft` for a tinted low-emphasis variant. */
function Badge({
  children,
  tone = "cyan",
  soft = false,
  size = "md",
  icon = null,
  className = "",
  ...rest
}) {
  const cls = ["od-badge", `od-badge--${tone}`, soft ? "od-badge--soft" : "", size === "sm" ? "od-badge--sm" : "", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("span", _extends({
    className: cls
  }, rest), icon, children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Badge.jsx", error: String((e && e.message) || e) }); }

// components/content/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-card{
  background:var(--surface-card); border-radius:var(--radius-md); color:var(--text-default);
  box-shadow:var(--shadow-md); overflow:hidden;
  transition:transform var(--dur) var(--ease-out), box-shadow var(--dur) var(--ease-standard);
}
.od-card--outline{ box-shadow:none; border:1.5px solid var(--border-default); }
.od-card--tinted{ background:var(--od-sky); box-shadow:none; }
.od-card--cream{ background:var(--surface-cream); box-shadow:var(--shadow-sm); }
.od-card--glass{
  background:var(--glass-fill); -webkit-backdrop-filter:var(--glass-blur); backdrop-filter:var(--glass-blur);
  border:1px solid var(--glass-border); border-radius:var(--radius-lg); box-shadow:var(--shadow-lg);
}
.od-card--lg{ border-radius:var(--radius-xl); }
.od-card__pad--none{ padding:0; }
.od-card__pad--sm{ padding:var(--space-4); }
.od-card__pad--md{ padding:var(--space-6); }
.od-card__pad--lg{ padding:var(--space-8); }
.od-card--interactive{ cursor:pointer; }
.od-card--interactive:hover{ transform:translateY(-3px); box-shadow:var(--shadow-lg); }
`;
if (typeof document !== "undefined" && !document.getElementById("od-card-css")) {
  const s = document.createElement("style");
  s.id = "od-card-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}

/** Surface container. The default is a white, softly-elevated 16px card. */
function Card({
  children,
  variant = "elevated",
  padding = "md",
  interactive = false,
  large = false,
  className = "",
  ...rest
}) {
  const cls = ["od-card", variant !== "elevated" ? `od-card--${variant}` : "", `od-card__pad--${padding}`, large ? "od-card--lg" : "", interactive ? "od-card--interactive" : "", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("div", _extends({
    className: cls
  }, rest), children);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Card.jsx", error: String((e && e.message) || e) }); }

// components/content/Rating.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-rating{ display:inline-flex; align-items:center; gap:.15em; line-height:0; }
.od-rating__stars{ position:relative; display:inline-flex; }
.od-rating__row{ display:inline-flex; }
.od-rating__row svg{ width:1em; height:1em; display:block; }
.od-rating__base svg{ color:var(--od-line); }
.od-rating__fill{ position:absolute; inset:0; overflow:hidden; white-space:nowrap; }
.od-rating__fill svg{ color:var(--od-yellow); }
.od-rating{ font-size:1.25rem; }
.od-rating--sm{ font-size:.95rem; }
.od-rating--lg{ font-size:1.7rem; }
.od-rating__btns{ position:absolute; inset:0; display:flex; }
.od-rating__btn{ flex:1; background:transparent; border:0; padding:0; cursor:pointer; }
.od-rating__num{ font-family:var(--font-sans); font-weight:var(--fw-bold); font-size:.7em; color:var(--od-navy); margin-left:.5em; line-height:1; }
`;
if (typeof document !== "undefined" && !document.getElementById("od-rating-css")) {
  const s = document.createElement("style");
  s.id = "od-rating-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}
const Star = () => /*#__PURE__*/React.createElement("svg", {
  viewBox: "0 0 24 24",
  fill: "currentColor"
}, /*#__PURE__*/React.createElement("path", {
  d: "M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 18.9 6.2 21l1.1-6.5L2.6 9.9l6.5-.9z"
}));

/** 5-star rating. Read-only display by default; pass `onChange` to make it interactive. */
function Rating({
  value = 5,
  max = 5,
  size = "md",
  showValue = false,
  onChange,
  className = "",
  ...rest
}) {
  const pct = Math.max(0, Math.min(1, value / max)) * 100;
  const interactive = typeof onChange === "function";
  const cls = ["od-rating", size !== "md" ? `od-rating--${size}` : "", className].filter(Boolean).join(" ");
  const stars = Array.from({
    length: max
  });
  return /*#__PURE__*/React.createElement("span", _extends({
    className: cls,
    role: "img",
    "aria-label": `${value} de ${max}`
  }, rest), /*#__PURE__*/React.createElement("span", {
    className: "od-rating__stars"
  }, /*#__PURE__*/React.createElement("span", {
    className: "od-rating__row od-rating__base"
  }, stars.map((_, i) => /*#__PURE__*/React.createElement(Star, {
    key: i
  }))), /*#__PURE__*/React.createElement("span", {
    className: "od-rating__fill",
    style: {
      width: pct + "%"
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "od-rating__row"
  }, stars.map((_, i) => /*#__PURE__*/React.createElement(Star, {
    key: i
  })))), interactive ? /*#__PURE__*/React.createElement("span", {
    className: "od-rating__btns"
  }, stars.map((_, i) => /*#__PURE__*/React.createElement("button", {
    key: i,
    type: "button",
    className: "od-rating__btn",
    "aria-label": `${i + 1} estrelas`,
    onClick: () => onChange(i + 1)
  }))) : null), showValue ? /*#__PURE__*/React.createElement("span", {
    className: "od-rating__num"
  }, value.toFixed(1)) : null);
}
Object.assign(__ds_scope, { Rating });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Rating.jsx", error: String((e && e.message) || e) }); }

// components/content/Bubble.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-bubble{
  position:relative; display:inline-block; max-width:300px; font-family:var(--font-sans);
  padding:16px 18px; border-radius:var(--radius-lg);
}
.od-bubble--glass{
  background:var(--glass-fill); -webkit-backdrop-filter:var(--glass-blur); backdrop-filter:var(--glass-blur);
  border:1px solid var(--glass-border); box-shadow:var(--shadow-lg);
}
.od-bubble--white{ background:#fff; box-shadow:var(--shadow-lg); }
.od-bubble--navy{ background:var(--od-navy); color:#fff; box-shadow:var(--shadow-lg); }
.od-bubble__x{
  position:absolute; top:9px; right:10px; width:20px; height:20px; border:0; border-radius:6px; padding:0;
  display:grid; place-items:center; background:rgba(0,30,120,.06); color:var(--text-muted); cursor:pointer;
  transition:background-color var(--dur);
}
.od-bubble--navy .od-bubble__x{ background:rgba(255,255,255,.16); color:#fff; }
.od-bubble__x:hover{ background:rgba(0,30,120,.14); }
.od-bubble__x svg{ width:12px; height:12px; }
.od-bubble__title{ font-weight:var(--fw-bold); font-size:var(--text-lg); line-height:1.25; color:var(--od-navy); }
.od-bubble--navy .od-bubble__title{ color:#fff; }
.od-bubble__body{ font-size:var(--text-sm); color:var(--text-muted); margin-top:4px; line-height:1.4; }
.od-bubble--navy .od-bubble__body{ color:rgba(255,255,255,.8); }
.od-bubble__rating{ margin-top:9px; }
`;
if (typeof document !== "undefined" && !document.getElementById("od-bubble-css")) {
  const s = document.createElement("style");
  s.id = "od-bubble-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}
const X = () => /*#__PURE__*/React.createElement("svg", {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: "3",
  strokeLinecap: "round"
}, /*#__PURE__*/React.createElement("line", {
  x1: "18",
  y1: "6",
  x2: "6",
  y2: "18"
}), /*#__PURE__*/React.createElement("line", {
  x1: "6",
  y1: "6",
  x2: "18",
  y2: "18"
}));

/**
 * Campaign benefit callout — the glassy chat-bubble from the KV pages.
 * Optional close affordance and a star-rating row.
 */
function Bubble({
  title,
  children,
  rating,
  tone = "glass",
  onClose,
  className = "",
  ...rest
}) {
  const cls = ["od-bubble", `od-bubble--${tone}`, className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("div", _extends({
    className: cls
  }, rest), onClose ? /*#__PURE__*/React.createElement("button", {
    type: "button",
    className: "od-bubble__x",
    "aria-label": "Fechar",
    onClick: onClose
  }, /*#__PURE__*/React.createElement(X, null)) : null, title ? /*#__PURE__*/React.createElement("div", {
    className: "od-bubble__title"
  }, title) : null, children ? /*#__PURE__*/React.createElement("div", {
    className: "od-bubble__body"
  }, children) : null, typeof rating === "number" ? /*#__PURE__*/React.createElement("div", {
    className: "od-bubble__rating"
  }, /*#__PURE__*/React.createElement(__ds_scope.Rating, {
    value: rating,
    size: "sm"
  })) : null);
}
Object.assign(__ds_scope, { Bubble });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Bubble.jsx", error: String((e && e.message) || e) }); }

// components/content/Tag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-tag{
  display:inline-flex; align-items:center; gap:.45em; font-family:var(--font-sans);
  font-weight:var(--fw-semibold); font-size:var(--text-sm); line-height:1; color:var(--od-navy);
  background:var(--od-sky); border:1px solid transparent; padding:.5em .85em; border-radius:var(--radius-pill);
  transition:background-color var(--dur) var(--ease-standard);
}
.od-tag--outline{ background:transparent; border-color:var(--border-strong); color:var(--od-gray-700); }
.od-tag__x{
  display:inline-flex; align-items:center; justify-content:center; width:1.15em; height:1.15em;
  border-radius:50%; border:0; background:transparent; color:currentColor; cursor:pointer; opacity:.6; padding:0;
  transition:opacity var(--dur), background-color var(--dur);
}
.od-tag__x:hover{ opacity:1; background:rgba(0,30,120,.10); }
.od-tag__x svg{ width:.85em; height:.85em; }
.od-tag__dot{ width:.5em; height:.5em; border-radius:50%; background:var(--od-cyan); }
`;
if (typeof document !== "undefined" && !document.getElementById("od-tag-css")) {
  const s = document.createElement("style");
  s.id = "od-tag-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}
const X = () => /*#__PURE__*/React.createElement("svg", {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: "3",
  strokeLinecap: "round"
}, /*#__PURE__*/React.createElement("line", {
  x1: "18",
  y1: "6",
  x2: "6",
  y2: "18"
}), /*#__PURE__*/React.createElement("line", {
  x1: "6",
  y1: "6",
  x2: "18",
  y2: "18"
}));

/** Chip / tag. Set `onRemove` for a removable chip; `dot` for a leading status dot. */
function Tag({
  children,
  variant = "soft",
  dot = false,
  onRemove,
  className = "",
  ...rest
}) {
  const cls = ["od-tag", variant === "outline" ? "od-tag--outline" : "", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("span", _extends({
    className: cls
  }, rest), dot ? /*#__PURE__*/React.createElement("span", {
    className: "od-tag__dot"
  }) : null, children, onRemove ? /*#__PURE__*/React.createElement("button", {
    type: "button",
    className: "od-tag__x",
    "aria-label": "Remover",
    onClick: onRemove
  }, /*#__PURE__*/React.createElement(X, null)) : null);
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Tag.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Dialog.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
@keyframes od-dialog-overlay-in{ from{ opacity:0; } to{ opacity:1; } }
@keyframes od-dialog-panel-in{ from{ opacity:0; transform:translateY(12px) scale(.97); } to{ opacity:1; transform:none; } }
.od-dialog__overlay{
  position:fixed; inset:0; z-index:1000; display:flex; align-items:center; justify-content:center; padding:24px;
  background:rgba(0,20,61,.5); -webkit-backdrop-filter:blur(4px); backdrop-filter:blur(4px);
  animation:od-dialog-overlay-in var(--dur) var(--ease-standard);
}
.od-dialog{
  background:#fff; border-radius:var(--radius-xl); box-shadow:var(--shadow-xl);
  width:100%; max-width:460px; max-height:90vh; overflow:auto; font-family:var(--font-sans);
  animation:od-dialog-panel-in var(--dur-slow) var(--ease-out);
}
.od-dialog__head{ display:flex; align-items:flex-start; justify-content:space-between; gap:16px; padding:24px 24px 0; }
.od-dialog__title{ font-family:var(--font-heading); font-weight:var(--fw-black); color:var(--od-navy); font-size:var(--text-2xl); line-height:1.15; letter-spacing:var(--tracking-tight); }
.od-dialog__x{ flex:none; width:34px; height:34px; border:0; border-radius:50%; background:var(--od-mist); color:var(--od-navy); cursor:pointer; display:grid; place-items:center; transition:background-color var(--dur); }
.od-dialog__x:hover{ background:var(--od-sky); }
.od-dialog__x svg{ width:16px; height:16px; }
.od-dialog__body{ padding:12px 24px 4px; color:var(--text-default); font-size:var(--text-base); line-height:var(--leading-normal); }
.od-dialog__foot{ display:flex; justify-content:flex-end; gap:12px; padding:20px 24px 24px; }
@media (prefers-reduced-motion: reduce){ .od-dialog, .od-dialog__overlay{ animation:none; } }
`;
if (typeof document !== "undefined" && !document.getElementById("od-dialog-css")) {
  const s = document.createElement("style");
  s.id = "od-dialog-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}
const X = () => /*#__PURE__*/React.createElement("svg", {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: "2.5",
  strokeLinecap: "round"
}, /*#__PURE__*/React.createElement("line", {
  x1: "18",
  y1: "6",
  x2: "6",
  y2: "18"
}), /*#__PURE__*/React.createElement("line", {
  x1: "6",
  y1: "6",
  x2: "18",
  y2: "18"
}));

/** Centered modal dialog. Controlled with `open`; `onClose` fires on ✕, backdrop click and Esc. */
function Dialog({
  open,
  onClose,
  title,
  children,
  footer,
  className = "",
  ...rest
}) {
  React.useEffect(() => {
    if (!open) return;
    const onKey = e => {
      if (e.key === "Escape" && onClose) onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);
  if (!open) return null;
  return /*#__PURE__*/React.createElement("div", {
    className: "od-dialog__overlay",
    onClick: e => {
      if (e.target === e.currentTarget && onClose) onClose();
    }
  }, /*#__PURE__*/React.createElement("div", _extends({
    className: ["od-dialog", className].filter(Boolean).join(" "),
    role: "dialog",
    "aria-modal": "true",
    "aria-label": typeof title === "string" ? title : undefined
  }, rest), /*#__PURE__*/React.createElement("div", {
    className: "od-dialog__head"
  }, title ? /*#__PURE__*/React.createElement("div", {
    className: "od-dialog__title"
  }, title) : /*#__PURE__*/React.createElement("span", null), onClose ? /*#__PURE__*/React.createElement("button", {
    type: "button",
    className: "od-dialog__x",
    "aria-label": "Fechar",
    onClick: onClose
  }, /*#__PURE__*/React.createElement(X, null)) : null), /*#__PURE__*/React.createElement("div", {
    className: "od-dialog__body"
  }, children), footer ? /*#__PURE__*/React.createElement("div", {
    className: "od-dialog__foot"
  }, footer) : null));
}
Object.assign(__ds_scope, { Dialog });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Dialog.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Toast.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-toast{
  display:flex; align-items:flex-start; gap:12px; font-family:var(--font-sans);
  background:#fff; border-radius:var(--radius-md); box-shadow:var(--shadow-lg);
  padding:14px 16px; min-width:280px; max-width:400px; border-left:5px solid var(--od-cyan);
}
.od-toast__ic{ flex:none; width:26px; height:26px; border-radius:50%; display:grid; place-items:center; color:#fff; margin-top:1px; }
.od-toast__ic svg{ width:15px; height:15px; }
.od-toast--info .od-toast__ic{ background:var(--od-cyan); }
.od-toast--success{ border-left-color:var(--color-success); }
.od-toast--success .od-toast__ic{ background:var(--color-success); }
.od-toast--warning{ border-left-color:var(--color-warning); }
.od-toast--warning .od-toast__ic{ background:var(--color-warning); }
.od-toast--danger{ border-left-color:var(--color-danger); }
.od-toast--danger .od-toast__ic{ background:var(--color-danger); }
.od-toast__body{ flex:1; min-width:0; }
.od-toast__title{ font-weight:var(--fw-bold); color:var(--od-navy); font-size:var(--text-sm); }
.od-toast__msg{ color:var(--text-muted); font-size:var(--text-sm); margin-top:2px; line-height:1.4; }
.od-toast__x{ flex:none; border:0; background:transparent; color:var(--od-gray-300); cursor:pointer; padding:2px; border-radius:6px; }
.od-toast__x:hover{ color:var(--od-navy); background:var(--od-mist); }
.od-toast__x svg{ width:15px; height:15px; }
`;
if (typeof document !== "undefined" && !document.getElementById("od-toast-css")) {
  const s = document.createElement("style");
  s.id = "od-toast-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}
const ICONS = {
  info: /*#__PURE__*/React.createElement("svg", {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "3",
    strokeLinecap: "round"
  }, /*#__PURE__*/React.createElement("line", {
    x1: "12",
    y1: "11",
    x2: "12",
    y2: "16"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: "12",
    cy: "7.5",
    r: ".5",
    fill: "currentColor",
    stroke: "none"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: "12",
    cy: "7.5",
    r: "1.2",
    fill: "currentColor",
    stroke: "none"
  })),
  success: /*#__PURE__*/React.createElement("svg", {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "3",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }, /*#__PURE__*/React.createElement("polyline", {
    points: "20 6 9 17 4 12"
  })),
  warning: /*#__PURE__*/React.createElement("svg", {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "3",
    strokeLinecap: "round"
  }, /*#__PURE__*/React.createElement("line", {
    x1: "12",
    y1: "8",
    x2: "12",
    y2: "13"
  }), /*#__PURE__*/React.createElement("line", {
    x1: "12",
    y1: "16.5",
    x2: "12",
    y2: "16.5"
  })),
  danger: /*#__PURE__*/React.createElement("svg", {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "3",
    strokeLinecap: "round"
  }, /*#__PURE__*/React.createElement("line", {
    x1: "18",
    y1: "6",
    x2: "6",
    y2: "18"
  }), /*#__PURE__*/React.createElement("line", {
    x1: "6",
    y1: "6",
    x2: "18",
    y2: "18"
  }))
};
const X = () => /*#__PURE__*/React.createElement("svg", {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: "2.5",
  strokeLinecap: "round"
}, /*#__PURE__*/React.createElement("line", {
  x1: "18",
  y1: "6",
  x2: "6",
  y2: "18"
}), /*#__PURE__*/React.createElement("line", {
  x1: "6",
  y1: "6",
  x2: "18",
  y2: "18"
}));

/** Notification toast. Position via a container/portal in your app. */
function Toast({
  tone = "info",
  title,
  children,
  onClose,
  className = "",
  ...rest
}) {
  const cls = ["od-toast", `od-toast--${tone}`, className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("div", _extends({
    className: cls,
    role: "status"
  }, rest), /*#__PURE__*/React.createElement("span", {
    className: "od-toast__ic"
  }, ICONS[tone] || ICONS.info), /*#__PURE__*/React.createElement("div", {
    className: "od-toast__body"
  }, title ? /*#__PURE__*/React.createElement("div", {
    className: "od-toast__title"
  }, title) : null, children ? /*#__PURE__*/React.createElement("div", {
    className: "od-toast__msg"
  }, children) : null), onClose ? /*#__PURE__*/React.createElement("button", {
    type: "button",
    className: "od-toast__x",
    "aria-label": "Fechar",
    onClick: onClose
  }, /*#__PURE__*/React.createElement(X, null)) : null);
}
Object.assign(__ds_scope, { Toast });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Toast.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Tooltip.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-tt{ position:relative; display:inline-flex; }
.od-tt__pop{
  position:absolute; z-index:50; pointer-events:none; opacity:0; transform:translateY(4px);
  background:var(--od-navy); color:#fff; font-family:var(--font-sans); font-size:var(--text-xs); font-weight:var(--fw-medium);
  padding:.45rem .65rem; border-radius:var(--radius-sm); white-space:nowrap; box-shadow:var(--shadow-md);
  transition:opacity var(--dur) var(--ease-standard), transform var(--dur) var(--ease-standard);
}
.od-tt__pop::after{ content:""; position:absolute; width:8px; height:8px; background:var(--od-navy); transform:rotate(45deg); }
.od-tt:hover .od-tt__pop, .od-tt:focus-within .od-tt__pop{ opacity:1; transform:translateY(0); }
.od-tt__pop--top{ bottom:calc(100% + 8px); left:50%; translate:-50% 0; }
.od-tt__pop--top::after{ bottom:-4px; left:50%; margin-left:-4px; }
.od-tt__pop--bottom{ top:calc(100% + 8px); left:50%; translate:-50% 0; }
.od-tt__pop--bottom::after{ top:-4px; left:50%; margin-left:-4px; }
.od-tt__pop--left{ right:calc(100% + 8px); top:50%; translate:0 -50%; }
.od-tt__pop--left::after{ right:-4px; top:50%; margin-top:-4px; }
.od-tt__pop--right{ left:calc(100% + 8px); top:50%; translate:0 -50%; }
.od-tt__pop--right::after{ left:-4px; top:50%; margin-top:-4px; }
`;
if (typeof document !== "undefined" && !document.getElementById("od-tt-css")) {
  const s = document.createElement("style");
  s.id = "od-tt-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}

/** Hover / focus tooltip wrapper. Wrap the trigger; pass label text via `content`. */
function Tooltip({
  content,
  side = "top",
  children,
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    className: ["od-tt", className].filter(Boolean).join(" ")
  }, rest), children, /*#__PURE__*/React.createElement("span", {
    className: `od-tt__pop od-tt__pop--${side}`,
    role: "tooltip"
  }, content));
}
Object.assign(__ds_scope, { Tooltip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Tooltip.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-check{ display:inline-flex; align-items:flex-start; gap:.6rem; font-family:var(--font-sans); cursor:pointer; -webkit-user-select:none; user-select:none; }
.od-check input{ position:absolute; opacity:0; width:0; height:0; }
.od-check__box{
  flex:none; width:1.35rem; height:1.35rem; margin-top:.05rem; border-radius:6px;
  border:2px solid var(--border-strong); background:#fff; display:grid; place-items:center;
  transition:background-color var(--dur) var(--ease-standard), border-color var(--dur) var(--ease-standard), transform var(--dur) var(--ease-bounce);
}
.od-check__box svg{ width:.9rem; height:.9rem; color:#fff; opacity:0; transform:scale(.5); transition:opacity var(--dur), transform var(--dur) var(--ease-bounce); }
.od-check:hover .od-check__box{ border-color:var(--od-cyan); }
.od-check input:checked + .od-check__box{ background:var(--od-cyan); border-color:var(--od-cyan); }
.od-check input:checked + .od-check__box svg{ opacity:1; transform:scale(1); }
.od-check input:focus-visible + .od-check__box{ box-shadow:var(--ring); }
.od-check input:disabled ~ *{ opacity:.5; }
.od-check input:disabled + .od-check__box{ background:var(--od-mist); border-color:var(--od-line); }
.od-check__label{ font-size:var(--text-base); color:var(--text-default); line-height:1.35; }
`;
if (typeof document !== "undefined" && !document.getElementById("od-check-css")) {
  const s = document.createElement("style");
  s.id = "od-check-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}
const Tick = () => /*#__PURE__*/React.createElement("svg", {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: "3.5",
  strokeLinecap: "round",
  strokeLinejoin: "round"
}, /*#__PURE__*/React.createElement("polyline", {
  points: "20 6 9 17 4 12"
}));

/** Checkbox with label. Works controlled (`checked`) or uncontrolled (`defaultChecked`). */
function Checkbox({
  label,
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: ["od-check", className].filter(Boolean).join(" ")
  }, /*#__PURE__*/React.createElement("input", _extends({
    type: "checkbox"
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "od-check__box"
  }, /*#__PURE__*/React.createElement(Tick, null)), label ? /*#__PURE__*/React.createElement("span", {
    className: "od-check__label"
  }, label) : null);
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-field{ display:flex; flex-direction:column; gap:.4rem; font-family:var(--font-sans); }
.od-field__label{ font-size:var(--text-sm); font-weight:var(--fw-bold); color:var(--od-navy); }
.od-field__req{ color:var(--color-danger); margin-left:.15em; }
.od-inputwrap{ position:relative; display:flex; align-items:center; }
.od-inputwrap__ic{ position:absolute; left:.9rem; display:inline-flex; color:var(--od-gray-300); pointer-events:none; }
.od-inputwrap__ic svg{ width:1.15em; height:1.15em; }
.od-input{
  width:100%; font-family:inherit; color:var(--text-default); background:#fff;
  border:1.5px solid var(--border-default); border-radius:var(--radius-md);
  transition:border-color var(--dur) var(--ease-standard), box-shadow var(--dur) var(--ease-standard), background-color var(--dur);
  -webkit-appearance:none; appearance:none;
}
.od-input::placeholder{ color:var(--od-gray-300); }
.od-input:hover{ border-color:var(--border-strong); }
.od-input:focus{ outline:none; border-color:var(--od-cyan); box-shadow:var(--ring); background:#fff; }
.od-input--sm{ font-size:var(--text-sm); padding:.55rem .8rem; }
.od-input--md{ font-size:var(--text-base); padding:.75rem 1rem; }
.od-input--lg{ font-size:var(--text-lg); padding:.95rem 1.15rem; }
.od-inputwrap--icon .od-input{ padding-left:2.7rem; }
.od-input:disabled{ background:var(--od-mist); color:var(--od-gray-300); cursor:not-allowed; border-color:var(--od-line); }
.od-field--error .od-input{ border-color:var(--color-danger); }
.od-field--error .od-input:focus{ box-shadow:0 0 0 3px var(--color-danger-bg); }
.od-field__msg{ font-size:var(--text-xs); color:var(--text-muted); }
.od-field--error .od-field__msg{ color:var(--color-danger); font-weight:var(--fw-medium); }
`;
if (typeof document !== "undefined" && !document.getElementById("od-input-css")) {
  const s = document.createElement("style");
  s.id = "od-input-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}
let _uid = 0;
/** Text input with label, hint / error state and optional leading icon. */
function Input({
  label,
  hint,
  error,
  size = "md",
  iconLeft = null,
  required = false,
  id,
  className = "",
  ...rest
}) {
  const inputId = id || `od-input-${++_uid}`;
  const wrapCls = ["od-inputwrap", iconLeft ? "od-inputwrap--icon" : ""].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("div", {
    className: ["od-field", error ? "od-field--error" : "", className].filter(Boolean).join(" ")
  }, label ? /*#__PURE__*/React.createElement("label", {
    className: "od-field__label",
    htmlFor: inputId
  }, label, required ? /*#__PURE__*/React.createElement("span", {
    className: "od-field__req"
  }, "*") : null) : null, /*#__PURE__*/React.createElement("div", {
    className: wrapCls
  }, iconLeft ? /*#__PURE__*/React.createElement("span", {
    className: "od-inputwrap__ic"
  }, iconLeft) : null, /*#__PURE__*/React.createElement("input", _extends({
    id: inputId,
    className: `od-input od-input--${size}`,
    required: required,
    "aria-invalid": !!error
  }, rest))), error ? /*#__PURE__*/React.createElement("span", {
    className: "od-field__msg"
  }, error) : hint ? /*#__PURE__*/React.createElement("span", {
    className: "od-field__msg"
  }, hint) : null);
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/Radio.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-radio{ display:inline-flex; align-items:flex-start; gap:.6rem; font-family:var(--font-sans); cursor:pointer; -webkit-user-select:none; user-select:none; }
.od-radio input{ position:absolute; opacity:0; width:0; height:0; }
.od-radio__dot{
  flex:none; width:1.35rem; height:1.35rem; margin-top:.05rem; border-radius:50%;
  border:2px solid var(--border-strong); background:#fff; display:grid; place-items:center;
  transition:border-color var(--dur) var(--ease-standard);
}
.od-radio__dot::after{ content:""; width:.7rem; height:.7rem; border-radius:50%; background:var(--od-cyan); transform:scale(0); transition:transform var(--dur) var(--ease-bounce); }
.od-radio:hover .od-radio__dot{ border-color:var(--od-cyan); }
.od-radio input:checked + .od-radio__dot{ border-color:var(--od-cyan); }
.od-radio input:checked + .od-radio__dot::after{ transform:scale(1); }
.od-radio input:focus-visible + .od-radio__dot{ box-shadow:var(--ring); }
.od-radio input:disabled ~ *{ opacity:.5; }
.od-radio__label{ font-size:var(--text-base); color:var(--text-default); line-height:1.35; }
`;
if (typeof document !== "undefined" && !document.getElementById("od-radio-css")) {
  const s = document.createElement("style");
  s.id = "od-radio-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}

/** Radio button with label. Group by sharing the same `name`. */
function Radio({
  label,
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: ["od-radio", className].filter(Boolean).join(" ")
  }, /*#__PURE__*/React.createElement("input", _extends({
    type: "radio"
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "od-radio__dot"
  }), label ? /*#__PURE__*/React.createElement("span", {
    className: "od-radio__label"
  }, label) : null);
}
Object.assign(__ds_scope, { Radio });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Radio.jsx", error: String((e && e.message) || e) }); }

// components/forms/Select.jsx
try { (() => {
const CSS = `
.od-select{
  position:relative; display:inline-flex; align-items:center; width:100%;
}
.od-select select{
  width:100%; font-family:var(--font-sans); font-size:var(--text-base); color:var(--text-default);
  background:#fff; border:1.5px solid var(--border-default); border-radius:var(--radius-md);
  padding:.75rem 2.6rem .75rem 1rem; cursor:pointer; -webkit-appearance:none; appearance:none;
  transition:border-color var(--dur) var(--ease-standard), box-shadow var(--dur) var(--ease-standard);
}
.od-select select:hover{ border-color:var(--border-strong); }
.od-select select:focus{ outline:none; border-color:var(--od-cyan); box-shadow:var(--ring); }
.od-select select:disabled{ background:var(--od-mist); color:var(--od-gray-300); cursor:not-allowed; }
.od-select--sm select{ font-size:var(--text-sm); padding:.55rem 2.4rem .55rem .8rem; }
.od-select--lg select{ font-size:var(--text-lg); padding:.95rem 2.8rem .95rem 1.15rem; }
.od-select__chev{ position:absolute; right:1rem; pointer-events:none; color:var(--od-navy); display:inline-flex; }
.od-select__chev svg{ width:1.1em; height:1.1em; }
`;
if (typeof document !== "undefined" && !document.getElementById("od-select-css")) {
  const s = document.createElement("style");
  s.id = "od-select-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}
const Chevron = () => /*#__PURE__*/React.createElement("svg", {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: "2.5",
  strokeLinecap: "round",
  strokeLinejoin: "round"
}, /*#__PURE__*/React.createElement("polyline", {
  points: "6 9 12 15 18 9"
}));

/** Styled native select. Pass `options` (array of {value,label} or strings) or children. */
function Select({
  options,
  size = "md",
  placeholder,
  children,
  className = "",
  ...rest
}) {
  const cls = ["od-select", `od-select--${size}`, className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("div", {
    className: cls
  }, /*#__PURE__*/React.createElement("select", rest, placeholder ? /*#__PURE__*/React.createElement("option", {
    value: "",
    disabled: true
  }, placeholder) : null, options ? options.map((o, i) => {
    const val = typeof o === "string" ? o : o.value;
    const lab = typeof o === "string" ? o : o.label;
    return /*#__PURE__*/React.createElement("option", {
      key: i,
      value: val
    }, lab);
  }) : children), /*#__PURE__*/React.createElement("span", {
    className: "od-select__chev"
  }, /*#__PURE__*/React.createElement(Chevron, null)));
}
Object.assign(__ds_scope, { Select });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Select.jsx", error: String((e && e.message) || e) }); }

// components/forms/Switch.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const CSS = `
.od-switch{ display:inline-flex; align-items:center; gap:.65rem; font-family:var(--font-sans); cursor:pointer; -webkit-user-select:none; user-select:none; }
.od-switch input{ position:absolute; opacity:0; width:0; height:0; }
.od-switch__track{
  flex:none; width:3rem; height:1.7rem; border-radius:var(--radius-pill); background:var(--od-line);
  padding:2px; display:flex; align-items:center;
  transition:background-color var(--dur) var(--ease-standard);
}
.od-switch__knob{
  width:1.3rem; height:1.3rem; border-radius:50%; background:#fff; box-shadow:var(--shadow-sm);
  transition:transform var(--dur) var(--ease-bounce);
}
.od-switch input:checked + .od-switch__track{ background:var(--od-cyan); }
.od-switch input:checked + .od-switch__track .od-switch__knob{ transform:translateX(1.3rem); }
.od-switch input:focus-visible + .od-switch__track{ box-shadow:var(--ring); }
.od-switch input:disabled + .od-switch__track{ opacity:.5; }
.od-switch__label{ font-size:var(--text-base); color:var(--text-default); }
`;
if (typeof document !== "undefined" && !document.getElementById("od-switch-css")) {
  const s = document.createElement("style");
  s.id = "od-switch-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}

/** Pill toggle switch. Controlled (`checked`) or uncontrolled (`defaultChecked`). */
function Switch({
  label,
  className = "",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: ["od-switch", className].filter(Boolean).join(" ")
  }, /*#__PURE__*/React.createElement("input", _extends({
    type: "checkbox",
    role: "switch"
  }, rest)), /*#__PURE__*/React.createElement("span", {
    className: "od-switch__track"
  }, /*#__PURE__*/React.createElement("span", {
    className: "od-switch__knob"
  })), label ? /*#__PURE__*/React.createElement("span", {
    className: "od-switch__label"
  }, label) : null);
}
Object.assign(__ds_scope, { Switch });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Switch.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Tabs.jsx
try { (() => {
const CSS = `
.od-tabs{ font-family:var(--font-sans); }
.od-tabs__list{ display:inline-flex; gap:4px; }
.od-tabs--underline .od-tabs__list{ gap:8px; border-bottom:2px solid var(--od-line); display:flex; }
.od-tabs--full .od-tabs__list{ display:flex; width:100%; }
.od-tab{
  display:inline-flex; align-items:center; gap:.5em; border:0; background:transparent; cursor:pointer;
  font-family:inherit; font-weight:var(--fw-bold); font-size:var(--text-base); color:var(--text-muted);
  padding:.7rem 1rem; border-radius:var(--radius-pill); transition:color var(--dur), background-color var(--dur);
  white-space:nowrap;
}
.od-tab svg{ width:1.1em; height:1.1em; }
.od-tabs--full .od-tab{ flex:1; justify-content:center; }

/* pill variant */
.od-tabs--pill .od-tabs__list{ background:var(--od-mist); padding:5px; border-radius:var(--radius-pill); }
.od-tabs--pill .od-tab:hover{ color:var(--od-navy); }
.od-tabs--pill .od-tab[aria-selected="true"]{ background:#fff; color:var(--od-navy); box-shadow:var(--shadow-sm); }

/* underline variant */
.od-tabs--underline .od-tab{ border-radius:0; padding:.7rem .35rem; margin-bottom:-2px; border-bottom:3px solid transparent; }
.od-tabs--underline .od-tab:hover{ color:var(--od-navy); }
.od-tabs--underline .od-tab[aria-selected="true"]{ color:var(--od-cyan-600); border-bottom-color:var(--od-cyan); }
.od-tab:focus-visible{ outline:none; box-shadow:var(--ring); }
`;
if (typeof document !== "undefined" && !document.getElementById("od-tabs-css")) {
  const s = document.createElement("style");
  s.id = "od-tabs-css";
  s.textContent = CSS;
  document.head.appendChild(s);
}

/** Tab bar. Controlled via `value`+`onChange`, or uncontrolled via `defaultValue`. */
function Tabs({
  items = [],
  value,
  defaultValue,
  onChange,
  variant = "pill",
  fullWidth = false,
  className = ""
}) {
  const [internal, setInternal] = React.useState(defaultValue ?? (items[0] && items[0].id));
  const active = value !== undefined ? value : internal;
  const select = id => {
    if (value === undefined) setInternal(id);
    if (onChange) onChange(id);
  };
  const cls = ["od-tabs", `od-tabs--${variant}`, fullWidth ? "od-tabs--full" : "", className].filter(Boolean).join(" ");
  return /*#__PURE__*/React.createElement("div", {
    className: cls
  }, /*#__PURE__*/React.createElement("div", {
    className: "od-tabs__list",
    role: "tablist"
  }, items.map(t => /*#__PURE__*/React.createElement("button", {
    key: t.id,
    type: "button",
    role: "tab",
    "aria-selected": active === t.id,
    className: "od-tab",
    onClick: () => select(t.id)
  }, t.icon, t.label))));
}
Object.assign(__ds_scope, { Tabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Tabs.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.IconButton = __ds_scope.IconButton;

__ds_ns.Icon = __ds_scope.Icon;

__ds_ns.Logo = __ds_scope.Logo;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Bubble = __ds_scope.Bubble;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.Rating = __ds_scope.Rating;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.Dialog = __ds_scope.Dialog;

__ds_ns.Toast = __ds_scope.Toast;

__ds_ns.Tooltip = __ds_scope.Tooltip;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.Radio = __ds_scope.Radio;

__ds_ns.Select = __ds_scope.Select;

__ds_ns.Switch = __ds_scope.Switch;

__ds_ns.Tabs = __ds_scope.Tabs;

})();
