#!/usr/bin/env node
"use strict";

/**
 * Genscaff gate-owned browser audit.
 *
 * Usage:
 *   node live_audit.js --config <config.json>
 *   Get-Content config.json -Raw | node live_audit.js --config -
 *
 * On success stdout contains exactly one JSON object. Diagnostics and fatal
 * errors go to stderr and use a non-zero exit code.
 */

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

const RUNNER_PATH = fs.realpathSync(__filename);
const RUNNER_SHA256 = sha256(fs.readFileSync(RUNNER_PATH));
const DEFAULT_VIEWPORTS = [
  { name: "desktop", width: 1280, height: 800 },
  { name: "mobile", width: 390, height: 844 },
];

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function parseArguments(argv) {
  const args = {};
  for (let index = 2; index < argv.length; index += 1) {
    const item = argv[index];
    if (item === "--config" && argv[index + 1]) {
      args.config = argv[index + 1];
      index += 1;
    } else if (item === "--help" || item === "-h") {
      args.help = true;
    } else {
      throw new Error(`Unknown or incomplete argument: ${item}`);
    }
  }
  return args;
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf8");
}

async function readConfig(configArgument) {
  if (!configArgument) throw new Error("--config <config.json> is required");
  if (configArgument === "-") {
    const raw = await readStdin();
    return {
      raw,
      configPath: "<stdin>",
      configDir: process.cwd(),
      configSha256: sha256(Buffer.from(raw, "utf8")),
      value: JSON.parse(raw),
    };
  }
  const resolved = path.resolve(configArgument);
  const rawBuffer = fs.readFileSync(resolved);
  return {
    raw: rawBuffer.toString("utf8"),
    configPath: fs.realpathSync(resolved),
    configDir: path.dirname(resolved),
    configSha256: sha256(rawBuffer),
    value: JSON.parse(rawBuffer.toString("utf8")),
  };
}

function assertConfig(config) {
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("Config must be a JSON object");
  }
  if (config.schema_version !== 1) {
    throw new Error("Config schema_version must be 1");
  }
  if (typeof config.entry_url !== "string" || !config.entry_url.trim()) {
    throw new Error("Config entry_url is required");
  }
  if (typeof config.source_fingerprint !== "string" || !config.source_fingerprint.trim()) {
    throw new Error("Config source_fingerprint is required");
  }
  const flow = config.primary_flow;
  for (const key of ["selector", "feedback_selector", "terminal_selector", "recovery_selector"]) {
    if (!flow || typeof flow[key] !== "string" || !flow[key].trim()) {
      throw new Error(`Config primary_flow.${key} is required`);
    }
  }
  if (config.viewports !== undefined) {
    if (!Array.isArray(config.viewports) || config.viewports.length < 2) {
      throw new Error("Config viewports must contain at least desktop and mobile entries");
    }
    for (const viewport of config.viewports) {
      if (!viewport || !viewport.name || !Number.isInteger(viewport.width) || !Number.isInteger(viewport.height)) {
        throw new Error("Each viewport needs name and integer width/height");
      }
      if (viewport.width < 240 || viewport.height < 240) {
        throw new Error(`Viewport ${viewport.name} is too small`);
      }
    }
  }
  for (const key of ["domain_signal_selectors", "decision_selectors"]) {
    if (config[key] !== undefined && !Array.isArray(config[key])) {
      throw new Error(`Config ${key} must be an array`);
    }
  }
  if (config.control_scenarios !== undefined && !Array.isArray(config.control_scenarios)) {
    throw new Error("Config control_scenarios must be an array");
  }
  for (const [index, scenario] of (config.control_scenarios || []).entries()) {
    if (!scenario || typeof scenario !== "object" || Array.isArray(scenario)) {
      throw new Error(`Config control_scenarios[${index}] must be an object`);
    }
    if (typeof scenario.selector !== "string" || !scenario.selector.trim()) {
      throw new Error(`Config control_scenarios[${index}].selector is required`);
    }
    const action = scenario.action || "click";
    if (!["click", "fill", "select", "check", "press"].includes(action)) {
      throw new Error(`Config control_scenarios[${index}].action is unsupported`);
    }
    if (["fill", "select"].includes(action) && typeof scenario.value !== "string") {
      throw new Error(`Config control_scenarios[${index}].value is required for ${action}`);
    }
    if (action === "press" && typeof scenario.key !== "string") {
      throw new Error(`Config control_scenarios[${index}].key is required for press`);
    }
    if (scenario.expected_checked !== undefined && typeof scenario.expected_checked !== "boolean") {
      throw new Error(`Config control_scenarios[${index}].expected_checked must be boolean`);
    }
    for (const key of ["expected_selector", "expected_url_pattern", "expected_value", "setup"]) {
      if (scenario[key] !== undefined && typeof scenario[key] !== "string") {
        throw new Error(`Config control_scenarios[${index}].${key} must be a string`);
      }
    }
    if (![undefined, "default", "primary-feedback", "primary-terminal"].includes(scenario.setup)) {
      throw new Error(`Config control_scenarios[${index}].setup is invalid`);
    }
    if (!scenario.expected_selector && !scenario.expected_url_pattern && scenario.expected_value === undefined && scenario.expected_checked === undefined) {
      throw new Error(`Config control_scenarios[${index}] needs an observable expected outcome`);
    }
    if (scenario.expected_url_pattern) {
      try {
        new RegExp(scenario.expected_url_pattern);
      } catch (error) {
        throw new Error(`Config control_scenarios[${index}].expected_url_pattern is invalid: ${error.message || error}`);
      }
    }
  }
}

function resolveEntryUrl(raw, configDir) {
  let url;
  try {
    url = new URL(raw);
  } catch (_) {
    url = pathToFileURL(path.resolve(configDir, raw));
  }
  return url;
}

function defaultRouteUrl(entryUrl, allowNonDefaultRoute) {
  const normalized = new URL(entryUrl.href);
  if (!allowNonDefaultRoute) {
    normalized.search = "";
    normalized.hash = "";
  }
  return normalized.href;
}

function resolveOutputDirectory(raw, configDir) {
  if (!raw) return null;
  return path.isAbsolute(raw) ? path.normalize(raw) : path.resolve(configDir, raw);
}

function normalizeSelectorSpec(item, index) {
  if (typeof item === "string") return { id: `selector-${index + 1}`, selector: item };
  if (item && typeof item === "object" && typeof item.selector === "string") {
    return { id: String(item.id || item.name || `selector-${index + 1}`), selector: item.selector };
  }
  throw new Error(`Invalid selector spec at index ${index}`);
}

function scanText(text, source) {
  if (!text) return [];
  let normalized = String(text).replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f\u200b-\u200f\u2060\ufeff]/g, "");
  normalized = normalized.replace(/\\([0-9a-f]{1,6})\s?/gi, (_, hex) => {
    try {
      return String.fromCodePoint(parseInt(hex, 16));
    } catch (_) {
      return "";
    }
  });
  normalized = normalized.replace(/\\([\s\S])/g, "$1");
  const checks = [
    ["css-gradient", /(?:repeating\s*-\s*)?(?:linear|radial|conic)\s*-?\s*gradient\s*\(/i],
    ["svg-gradient", /<(?:svg:)?(?:linearGradient|radialGradient)\b/i],
    ["svg-gaussian-blur", /<(?:svg:)?feGaussianBlur\b/i],
    ["backdrop-filter", /(?:-webkit-)?backdrop\s*-?\s*filter\s*:/i],
    ["filter-blur", /(?:^|[;{\s])filter\s*:[^;{}]*\bblur\s*\(/i],
    ["canvas-gradient", /create(?:Linear|Radial|Conic)Gradient\s*\(/i],
  ];
  return checks
    .filter(([, pattern]) => pattern.test(normalized))
    .map(([kind]) => ({ kind, source, sha256: sha256(Buffer.from(normalized, "utf8")) }));
}

function extractDataUris(text, source, maxDecodedBytes) {
  if (!text) return [];
  const input = String(text);
  const candidates = [];
  const seenCandidates = new Set();
  const addCandidate = (candidate) => {
    const value = String(candidate || "").trim().slice(0, 8 * 1024 * 1024);
    if (!/^data:/i.test(value) || seenCandidates.has(value)) return;
    seenCandidates.add(value);
    candidates.push(value);
  };
  const cssUrlPattern = /url\(\s*(?:(["'])(data:[\s\S]*?)\1|(data:[^)]*))\s*\)/gi;
  let wrapper;
  while ((wrapper = cssUrlPattern.exec(input)) !== null) addCandidate(wrapper[2] || wrapper[3]);
  const genericPattern = /data:[^\s)>]+/gi;
  let generic;
  while ((generic = genericPattern.exec(input)) !== null) addCandidate(generic[0].replace(/["']+$/, ""));

  const matches = [];
  for (const candidate of candidates) {
    const match = candidate.match(/^data:([^;,]*)(?:;charset=[^;,]*)?(;base64)?,([\s\S]*)$/i);
    if (!match) continue;
    const mime_type = (match[1] || "text/plain").toLowerCase();
    const isBase64 = Boolean(match[2]);
    let decoded;
    let decode_error = "";
    try {
      if (isBase64) {
        decoded = Buffer.from(match[3], "base64");
      } else {
        let value = match[3];
        for (let round = 0; round < 3; round += 1) {
          const next = decodeURIComponent(value);
          if (next === value) break;
          value = next;
        }
        decoded = Buffer.from(value, "utf8");
      }
    } catch (error) {
      decode_error = String(error.message || error);
      decoded = Buffer.alloc(0);
    }
    const clipped = decoded.subarray(0, maxDecodedBytes);
    const decodedText = clipped.toString("utf8");
    matches.push({
      source,
      mime_type,
      encoding: isBase64 ? "base64" : "percent",
      byte_length: decoded.length,
      truncated: decoded.length > clipped.length,
      sha256: sha256(decoded),
      decode_error,
      decoded_text: decodedText,
      scan_findings: scanText(decodedText, `${source}#decoded-data-uri`),
    });
  }
  return matches;
}

function isTextualContentType(contentType, url) {
  if (/^(?:text\/|application\/(?:javascript|json|xml|xhtml\+xml)|image\/svg\+xml)/i.test(contentType || "")) {
    return true;
  }
  return /\.(?:css|html?|js|mjs|cjs|json|svg|xml|txt)(?:[?#]|$)/i.test(url || "");
}

function sniffResourceType(body) {
  if (!body || body.length < 2) return "";
  if (body.length >= 8 && body.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) return "image/png";
  if (body.length >= 3 && body[0] === 0xff && body[1] === 0xd8 && body[2] === 0xff) return "image/jpeg";
  const prefix = body.subarray(0, 12).toString("ascii");
  if (prefix.startsWith("GIF87a") || prefix.startsWith("GIF89a")) return "image/gif";
  if (body.length >= 12 && prefix.startsWith("RIFF") && prefix.slice(8, 12) === "WEBP") return "image/webp";
  if (body.length >= 2 && prefix.startsWith("BM")) return "image/bmp";
  if (body.length >= 12 && body.subarray(4, 8).toString("ascii") === "ftyp") {
    const brands = body.subarray(8, Math.min(body.length, 40)).toString("ascii");
    if (/(?:avif|avis)/.test(brands)) return "image/avif";
  }
  const textPrefix = body.subarray(0, Math.min(body.length, 4096)).toString("utf8").replace(/^\uFEFF/, "").trimStart();
  if (/^(?:<\?xml[^>]*>\s*)?<svg\b/i.test(textPrefix)) return "image/svg+xml";
  return "";
}

function isFirstParty(resourceUrl, entryUrl) {
  let parsed;
  try {
    parsed = new URL(resourceUrl);
  } catch (_) {
    return false;
  }
  if (["data:", "blob:"].includes(parsed.protocol)) return true;
  if (entryUrl.protocol === "file:") return parsed.protocol === "file:";
  return parsed.origin === entryUrl.origin;
}

const INIT_SCRIPT = `
(() => {
  const calls = [];
  Object.defineProperty(globalThis, "__GENSCAFF_CANVAS_GRADIENT_CALLS__", {
    configurable: false,
    enumerable: false,
    get: () => calls.slice(),
  });
  const proto = globalThis.CanvasRenderingContext2D && globalThis.CanvasRenderingContext2D.prototype;
  if (proto) {
    for (const method of ["createLinearGradient", "createRadialGradient", "createConicGradient"]) {
      if (typeof proto[method] !== "function") continue;
      const original = proto[method];
      Object.defineProperty(proto, method, {
        configurable: true,
        writable: true,
        value: function (...args) {
          calls.push({ method, args: args.map((value) => Number.isFinite(value) ? value : String(value)), at: Date.now() });
          return Reflect.apply(original, this, args);
        },
      });
    }
  }

  const asyncRecords = [];
  const timerRecords = new Map();
  let asyncSequence = 0;
  let asyncOverflow = false;
  const remember = (record) => {
    asyncRecords.push(record);
    if (asyncRecords.length > 10000) {
      asyncRecords.shift();
      asyncOverflow = true;
    }
    return record;
  };
  const snapshot = () => ({
    next_sequence: asyncSequence,
    overflow: asyncOverflow,
    records: asyncRecords.map((record) => ({ ...record })),
  });
  Object.defineProperty(globalThis, "__GENSCAFF_ASYNC_ACTIVITY__", {
    configurable: false,
    enumerable: false,
    get: snapshot,
  });
  const originalSetTimeout = globalThis.setTimeout.bind(globalThis);
  const originalClearTimeout = globalThis.clearTimeout.bind(globalThis);
  const originalSetInterval = globalThis.setInterval.bind(globalThis);
  const originalClearInterval = globalThis.clearInterval.bind(globalThis);
  const invoke = (handler, args) => typeof handler === "function"
    ? handler(...args)
    : (0, eval)(String(handler));
  globalThis.setTimeout = (handler, delay = 0, ...args) => {
    const record = remember({ sequence: asyncSequence++, kind: "timeout", delay: Number(delay) || 0, active: true });
    const id = originalSetTimeout(() => {
      record.active = false;
      record.fired = true;
      invoke(handler, args);
    }, delay);
    record.id = Number(id);
    timerRecords.set(Number(id), record);
    return id;
  };
  globalThis.setInterval = (handler, delay = 0, ...args) => {
    const record = remember({ sequence: asyncSequence++, kind: "interval", delay: Number(delay) || 0, active: true, fire_count: 0 });
    const id = originalSetInterval(() => {
      record.fire_count += 1;
      invoke(handler, args);
    }, delay);
    record.id = Number(id);
    timerRecords.set(Number(id), record);
    return id;
  };
  const markCleared = (id) => {
    const record = timerRecords.get(Number(id));
    if (record) {
      record.active = false;
      record.cleared = true;
    }
  };
  globalThis.clearTimeout = (id) => { markCleared(id); return originalClearTimeout(id); };
  globalThis.clearInterval = (id) => { markCleared(id); return originalClearInterval(id); };
  if (typeof globalThis.requestAnimationFrame === "function") {
    const originalRequestAnimationFrame = globalThis.requestAnimationFrame.bind(globalThis);
    const originalCancelAnimationFrame = globalThis.cancelAnimationFrame.bind(globalThis);
    globalThis.requestAnimationFrame = (handler) => {
      const record = remember({ sequence: asyncSequence++, kind: "animation-frame", delay: 0, active: true });
      const id = originalRequestAnimationFrame((timestamp) => {
        record.active = false;
        record.fired = true;
        handler(timestamp);
      });
      record.id = Number(id);
      timerRecords.set(Number(id), record);
      return id;
    };
    globalThis.cancelAnimationFrame = (id) => { markCleared(id); return originalCancelAnimationFrame(id); };
  }
})();
`;

const PAGE_SCANNER = `
(() => {
  const q = (value) => {
    if (globalThis.CSS && typeof globalThis.CSS.escape === "function") return globalThis.CSS.escape(value);
    return String(value).replace(/[^a-zA-Z0-9_-]/g, (char) => "\\\\" + char);
  };
  const unique = (selector) => {
    try { return document.querySelectorAll(selector).length === 1; } catch (_) { return false; }
  };
  const selectorFor = (element) => {
    if (element.id && unique("#" + q(element.id))) return "#" + q(element.id);
    for (const attribute of ["data-testid", "data-genscaff-control", "name"]) {
      const value = element.getAttribute(attribute);
      if (!value) continue;
      const selector = "[" + attribute + "=\\\"" + q(value) + "\\\"]";
      if (unique(selector)) return selector;
    }
    const parts = [];
    let current = element;
    while (current && current.nodeType === Node.ELEMENT_NODE) {
      let part = current.localName;
      const parent = current.parentElement;
      if (parent) {
        const siblings = [...parent.children].filter((candidate) => candidate.localName === current.localName);
        if (siblings.length > 1) part += ":nth-of-type(" + (siblings.indexOf(current) + 1) + ")";
      }
      parts.unshift(part);
      const candidate = parts.join(" > ");
      if (unique(candidate)) return candidate;
      current = parent;
    }
    return parts.join(" > ");
  };
  const visible = (element) => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
  };
  const accessibleName = (element) => {
    const labelledBy = (element.getAttribute("aria-labelledby") || "").trim();
    if (labelledBy) {
      const value = labelledBy.split(/\\s+/).map((id) => document.getElementById(id)?.innerText || "").join(" ").trim();
      if (value) return value;
    }
    const id = element.id;
    if (id) {
      const label = document.querySelector("label[for=\\\"" + q(id) + "\\\"]");
      if (label && label.innerText.trim()) return label.innerText.trim();
    }
    const wrappingLabel = element.closest("label");
    return (element.getAttribute("aria-label") || wrappingLabel?.innerText || element.innerText || element.value || element.getAttribute("alt") || element.getAttribute("title") || "").trim();
  };
  const alphaOf = (color) => {
    const match = String(color).match(/rgba?\\(([^)]+)\\)/i);
    if (!match) return 1;
    const parts = match[1].split(/[\\s,/]+/).filter(Boolean);
    if (parts.length < 4) return 1;
    return parts[3].endsWith("%") ? Number(parts[3].slice(0, -1)) / 100 : Number(parts[3]);
  };
  const findings = [];
  const dataUriValues = [];
  const all = [...document.querySelectorAll("*")];
  const properties = ["backgroundImage", "maskImage", "webkitMaskImage", "borderImageSource", "listStyleImage", "content"];
  const inspect = (element, pseudo) => {
    const style = getComputedStyle(element, pseudo || null);
    const selector = selectorFor(element) + (pseudo || "");
    const rect = element.getBoundingClientRect();
    const region = { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) };
    for (const property of properties) {
      const value = style[property] || "none";
      if (/gradient\\s*\\(/i.test(value)) findings.push({ kind: "computed-gradient", selector, property, value, region });
      if (/data:/i.test(value)) dataUriValues.push({ selector, property, value });
    }
    const backdrop = style.backdropFilter || style.webkitBackdropFilter || "none";
    if (backdrop !== "none") findings.push({ kind: "computed-backdrop-filter", selector, property: "backdropFilter", value: backdrop, region });
    const filter = style.filter || "none";
    if (/blur\\s*\\(/i.test(filter)) findings.push({ kind: "computed-filter-blur", selector, property: "filter", value: filter, region });
    const shadow = style.boxShadow || "none";
    if (/(?:rgba?\\([^)]*\\)|#[0-9a-f]{3,8}|[a-z]+)\\s+(?:-?\\d+px\\s+){2,4}(?:[2-9]\\d|\\d{3,})px/i.test(shadow)) {
      findings.push({ kind: "computed-glow-candidate", selector, property: "boxShadow", value: shadow, region });
    }
    const alpha = alphaOf(style.backgroundColor || "");
    const translucent = alpha > 0 && alpha < 0.94;
    const bordered = style.borderStyle !== "none" && style.borderWidth !== "0px";
    if (translucent && (backdrop !== "none" || (bordered && shadow !== "none"))) {
      findings.push({ kind: "computed-glass-candidate", selector, backgroundColor: style.backgroundColor, backdropFilter: backdrop, border: style.border, boxShadow: shadow, region });
    }
  };
  for (const element of all) {
    inspect(element, null);
    inspect(element, "::before");
    inspect(element, "::after");
  }
  const svgFindings = [...document.querySelectorAll("linearGradient, radialGradient, feGaussianBlur")].map((element) => ({
    kind: element.localName.toLowerCase() === "fegaussianblur" ? "svg-gaussian-blur" : "svg-gradient",
    selector: selectorFor(element),
    element: element.localName,
  }));
  const interactive = [
    "a[href]", "button", "input:not([type=hidden])", "select", "textarea", "summary",
    "[role=button]", "[role=link]", "[role=tab]", "[role=checkbox]", "[role=radio]", "[role=switch]",
    "[role=menuitem]", "[role=option]", "[tabindex]:not([tabindex=\\\"-1\\\"])"
  ].join(",");
  const controls = [...new Set(document.querySelectorAll(interactive))].filter(visible).map((element) => ({
    selector: selectorFor(element),
    accessible_name: accessibleName(element),
    label: (element.innerText || element.value || element.getAttribute("aria-label") || "").trim(),
    role: element.getAttribute("role") || element.localName,
    tag_name: element.localName,
    type: element.getAttribute("type") || "",
    disabled: element.matches(":disabled") || element.getAttribute("aria-disabled") === "true",
    href: element.getAttribute("href") || "",
    visible: true,
  }));
  const claimPattern = /(?:[$€£¥₩]\\s*\\d|\\d[\\d,.]*\\s*(?:%|ms|초|분|시간|days?|x|배|k|m|b|users?|customers?|teams?|명|개)|certif|award|trusted by|used by|customers?|clients?|testimonial|uptime|faster|reduc|increase|saved?|soc\\s*2|iso\\s*\\d|gdpr|사용자|고객|추천사|인증|수상|가동률|절감|감소|증가|향상|연동)/i;
  const claimCandidates = all.filter((element) => visible(element) && /^(?:h[1-6]|p|li|td|th|blockquote|figcaption|dd|dt|span|strong|em)$/i.test(element.localName))
    .map((element) => ({ selector: selectorFor(element), text: (element.innerText || "").trim() }))
    .filter((item) => item.text.length >= 2 && item.text.length <= 600 && claimPattern.test(item.text));
  const bodyText = (document.body?.innerText || "").replace(/\\s+/g, " ").trim();
  return {
    url: location.href,
    title: document.title,
    visible_text: bodyText,
    dom: document.documentElement.outerHTML,
    element_count: all.length,
    computed_style_findings: findings,
    svg_findings: svgFindings,
    data_uri_values: dataUriValues,
    canvas_gradient_calls: Array.isArray(globalThis.__GENSCAFF_CANVAS_GRADIENT_CALLS__) ? globalThis.__GENSCAFF_CANVAS_GRADIENT_CALLS__ : [],
    canvas_count: document.querySelectorAll("canvas").length,
    controls,
    claim_candidates: claimCandidates,
    focused_selector: document.activeElement && document.activeElement !== document.body ? selectorFor(document.activeElement) : "",
  };
})()
`;

async function scanFrames(page) {
  const frames = [];
  for (const [index, frame] of page.frames().entries()) {
    try {
      const value = await frame.evaluate(PAGE_SCANNER);
      frames.push({ frame_index: index, frame_url: frame.url(), ...value });
    } catch (error) {
      frames.push({ frame_index: index, frame_url: frame.url(), scan_error: String(error.message || error) });
    }
  }
  return frames;
}

async function inspectConfiguredSelectors(page, rawSpecs) {
  const results = [];
  for (const [index, raw] of (rawSpecs || []).entries()) {
    const spec = normalizeSelectorSpec(raw, index);
    try {
      const locator = page.locator(spec.selector);
      const count = await locator.count();
      const matches = [];
      for (let itemIndex = 0; itemIndex < count; itemIndex += 1) {
        const item = locator.nth(itemIndex);
        const geometry = await item.evaluate((element) => {
          const rect = element.getBoundingClientRect();
          const style = getComputedStyle(element);
          const identityFor = (node) => {
            if (node.id) return `#${node.id}`;
            const parts = [];
            for (let current = node; current && current.nodeType === Node.ELEMENT_NODE; current = current.parentElement) {
              let part = current.localName;
              if (current.parentElement) {
                const siblings = [...current.parentElement.children].filter((candidate) => candidate.localName === current.localName);
                if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(current) + 1})`;
              }
              parts.unshift(part);
            }
            return parts.join(" > ");
          };
          const alphaOf = (color) => {
            const match = String(color || "").match(/rgba?\(([^)]+)\)/i);
            if (!match) return String(color || "").toLowerCase() === "transparent" ? 0 : 1;
            const parts = match[1].split(/[\s,/]+/).filter(Boolean);
            if (parts.length < 4) return 1;
            return parts[3].endsWith("%") ? Number(parts[3].slice(0, -1)) / 100 : Number(parts[3]);
          };
          const effectiveOpacityOf = (node) => {
            let opacity = 1;
            for (let current = node; current && current.nodeType === Node.ELEMENT_NODE; current = current.parentElement) {
              const currentStyle = getComputedStyle(current);
              opacity *= Number.parseFloat(currentStyle.opacity || "1");
            }
            return opacity;
          };
          const ancestors = [];
          for (let current = element; current && current.nodeType === Node.ELEMENT_NODE; current = current.parentElement) {
            ancestors.push(current);
          }
          const ariaHidden = ancestors.some((node) => node.getAttribute("aria-hidden") === "true");
          const clipped = ancestors.some((node) => {
            const currentStyle = getComputedStyle(node);
            return currentStyle.contentVisibility === "hidden" ||
              /opacity\(\s*0(?:[\s%)]|\.0)/i.test(currentStyle.filter || "");
          });
          const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
          const textRects = [];
          let textNode;
          while ((textNode = walker.nextNode())) {
            if (!textNode.nodeValue || !textNode.nodeValue.trim()) continue;
            const parent = textNode.parentElement;
            if (!parent) continue;
            const parentStyle = getComputedStyle(parent);
            const textOpacity = effectiveOpacityOf(parent);
            const colorAlpha = Math.min(
              alphaOf(parentStyle.color),
              alphaOf(parentStyle.webkitTextFillColor || parentStyle.color)
            );
            if (parentStyle.display === "none" || parentStyle.visibility === "hidden" ||
                Number.parseFloat(parentStyle.fontSize || "0") < 10 || textOpacity < 0.5 || colorAlpha < 0.5) continue;
            const range = document.createRange();
            range.selectNodeContents(textNode);
            for (const textRect of range.getClientRects()) {
              const left = Math.max(0, rect.left, textRect.left);
              const top = Math.max(0, rect.top, textRect.top);
              const right = Math.min(innerWidth, rect.right, textRect.right);
              const bottom = Math.min(innerHeight, rect.bottom, textRect.bottom);
              if (right <= left || bottom <= top) continue;
              const x = Math.min(innerWidth - 1, Math.max(0, (left + right) / 2));
              const y = Math.min(innerHeight - 1, Math.max(0, (top + bottom) / 2));
              const topElement = document.elementFromPoint(x, y);
              const unoccluded = Boolean(topElement && (element.contains(topElement) || topElement.contains(element)));
              textRects.push({ width: right - left, height: bottom - top, unoccluded, color_alpha: colorAlpha, opacity: textOpacity });
            }
          }
          const textArea = textRects.reduce((total, item) => total + item.width * item.height, 0);
          const unoccludedArea = textRects.reduce((total, item) => total + (item.unoccluded ? item.width * item.height : 0), 0);
          return {
            x: rect.x,
            y: rect.y,
            width: rect.width,
            height: rect.height,
            font_size: Number.parseFloat(style.fontSize || "0"),
            opacity: Number.parseFloat(style.opacity || "0"),
            effective_opacity: effectiveOpacityOf(element),
            element_identity: identityFor(element),
            clip_path_declared: ancestors.some((node) => {
              const value = getComputedStyle(node).clipPath;
              return value && value !== "none";
            }),
            in_document_flow: style.position !== "fixed" || rect.width > 0,
            intersects_viewport: rect.bottom > 0 && rect.right > 0 && rect.top < innerHeight && rect.left < innerWidth,
            aria_hidden: ariaHidden,
            clipped,
            visible_text_rect_count: textRects.length,
            visible_text_pixel_area: textArea,
            unoccluded_text_ratio: textArea > 0 ? unoccludedArea / textArea : 0,
            minimum_text_color_alpha: textRects.length ? Math.min(...textRects.map((item) => item.color_alpha)) : 0,
          };
        }).catch(() => ({}));
        matches.push({
          index: itemIndex,
          visible: await item.isVisible().catch(() => false),
          text: ((await item.innerText().catch(() => "")) || "").replace(/\s+/g, " ").trim(),
          ...geometry,
        });
      }
      results.push({ ...spec, count, matches });
    } catch (error) {
      results.push({ ...spec, count: 0, matches: [], selector_error: String(error.message || error) });
    }
  }
  return results;
}

function aggregateInventory(frameScans, field) {
  const result = [];
  const seen = new Set();
  for (const frame of frameScans) {
    if (!Array.isArray(frame[field])) continue;
    for (const item of frame[field]) {
      const identity = `${frame.frame_url}\u0000${item.selector}\u0000${item.accessible_name || item.text || ""}`;
      if (seen.has(identity)) continue;
      seen.add(identity);
      result.push({ frame_url: frame.frame_url, ...item });
    }
  }
  return result;
}

async function captureState(page, viewportName, stage, outputDirectory, scanLimits) {
  const frames = await scanFrames(page);
  const screenshot = await page.screenshot({ fullPage: true, animations: "disabled" });
  const screenshotSha256 = sha256(screenshot);
  let screenshotPath = "";
  if (outputDirectory) {
    screenshotPath = path.join(outputDirectory, `${viewportName}-${stage}.png`);
    fs.writeFileSync(screenshotPath, screenshot);
  }
  const combinedDom = frames.map((frame) => frame.dom || "").join("\n<!-- GENSCAFF_FRAME -->\n");
  const combinedText = frames.map((frame) => frame.visible_text || "").join("\n").trim();
  const dataUris = [];
  for (const frame of frames) {
    dataUris.push(...extractDataUris(frame.dom || "", `${viewportName}:${stage}:${frame.frame_url}:dom`, scanLimits.maxDecodedBytes));
    for (const value of frame.data_uri_values || []) {
      dataUris.push(...extractDataUris(value.value, `${viewportName}:${stage}:${frame.frame_url}:${value.selector}:${value.property}`, scanLimits.maxDecodedBytes));
    }
  }
  return {
    stage,
    captured_at: new Date().toISOString(),
    url: page.url(),
    url_sha256: sha256(Buffer.from(page.url(), "utf8")),
    dom_sha256: sha256(Buffer.from(combinedDom, "utf8")),
    visible_text_sha256: sha256(Buffer.from(combinedText, "utf8")),
    screenshot_sha256: screenshotSha256,
    screenshot_path: screenshotPath,
    focused_selector: frames[0]?.focused_selector || "",
    visible_text: combinedText,
    frames,
    controls: aggregateInventory(frames, "controls"),
    claim_candidates: aggregateInventory(frames, "claim_candidates"),
    data_uris: dataUris,
  };
}

async function waitForVisible(page, selector, timeout, label) {
  try {
    await page.locator(selector).first().waitFor({ state: "visible", timeout });
  } catch (error) {
    throw new Error(`${label} selector did not become visible: ${selector}; ${error.message || error}`);
  }
}

async function performPrimaryFlow(page, config, viewportName, outputDirectory, scanLimits) {
  const flow = config.primary_flow;
  const clickTimeout = Number(flow.click_timeout_ms || 5000);
  const feedbackTimeout = Number(flow.feedback_timeout_ms || 3000);
  const terminalTimeout = Number(flow.terminal_timeout_ms || 10000);
  const recoveryTimeout = Number(flow.recovery_timeout_ms || 5000);
  const states = [];
  await waitForVisible(page, flow.selector, clickTimeout, "primary");
  states.push(await captureState(page, viewportName, "start", outputDirectory, scanLimits));
  await page.locator(flow.selector).first().click({ timeout: clickTimeout });
  await waitForVisible(page, flow.feedback_selector, feedbackTimeout, "feedback");
  states.push(await captureState(page, viewportName, "feedback", outputDirectory, scanLimits));
  await waitForVisible(page, flow.terminal_selector, terminalTimeout, "terminal");
  states.push(await captureState(page, viewportName, "terminal", outputDirectory, scanLimits));
  await waitForVisible(page, flow.recovery_selector, recoveryTimeout, "recovery control");
  await page.locator(flow.recovery_selector).first().click({ timeout: clickTimeout });
  const recoveredSelector = flow.recovered_selector || flow.selector;
  await waitForVisible(page, recoveredSelector, recoveryTimeout, "recovered state");
  states.push(await captureState(page, viewportName, "recovery", outputDirectory, scanLimits));
  return {
    selector: flow.selector,
    feedback_selector: flow.feedback_selector,
    terminal_selector: flow.terminal_selector,
    recovery_selector: flow.recovery_selector,
    recovered_selector: recoveredSelector,
    ordered_stages: states.map((state) => state.stage),
    states,
  };
}

function stateEvidence(state) {
  if (!state) return null;
  return {
    captured_at: state.captured_at,
    url: state.url,
    url_sha256: state.url_sha256,
    dom_sha256: state.dom_sha256,
    visible_text_sha256: state.visible_text_sha256,
    screenshot_sha256: state.screenshot_sha256,
    screenshot_path: state.screenshot_path,
    focused_selector: state.focused_selector,
    visible_text: state.visible_text,
  };
}

function fullStateFindings(state) {
  if (!state) return { computed: [], svg: [], canvas: [], dataUris: [] };
  return {
    computed: state.frames.flatMap((frame) =>
      (frame.computed_style_findings || []).map((finding) => ({
        stage: state.stage,
        frame_url: frame.frame_url,
        ...finding,
      }))
    ),
    svg: state.frames.flatMap((frame) =>
      (frame.svg_findings || []).map((finding) => ({
        stage: state.stage,
        frame_url: frame.frame_url,
        ...finding,
      }))
    ),
    canvas: state.frames.flatMap((frame) =>
      (frame.canvas_gradient_calls || []).map((call) => ({
        stage: state.stage,
        frame_url: frame.frame_url,
        ...call,
      }))
    ),
    dataUris: state.data_uris || [],
  };
}

async function selectorVisible(page, selector) {
  if (!selector) return null;
  try {
    const locator = page.locator(selector).first();
    return (await locator.count()) > 0 && (await locator.isVisible());
  } catch (_) {
    return false;
  }
}

async function targetFormState(locator) {
  const element = await locator.evaluate((node) => ({
    tag_name: node.localName || "",
    type: (node.getAttribute("type") || "").toLowerCase(),
    disabled: node.matches(":disabled") || node.getAttribute("aria-disabled") === "true",
    supports_value: ["input", "textarea", "select"].includes(node.localName),
    supports_checked: node.localName === "input" && ["checkbox", "radio"].includes((node.getAttribute("type") || "").toLowerCase()),
  })).catch(() => null);
  if (!element) return null;
  let value = null;
  let checked = null;
  if (element.supports_value) value = await locator.inputValue().catch(() => null);
  if (element.supports_checked) checked = await locator.isChecked().catch(() => null);
  return { ...element, value, checked };
}

async function prepareScenarioState(page, config, setup) {
  const flow = config.primary_flow;
  const mode = setup || "default";
  if (mode === "default") return;
  const clickTimeout = Number(flow.click_timeout_ms || 5000);
  await waitForVisible(page, flow.selector, clickTimeout, "scenario setup primary");
  await page.locator(flow.selector).first().click({ timeout: clickTimeout });
  await waitForVisible(page, flow.feedback_selector, Number(flow.feedback_timeout_ms || 3000), "scenario setup feedback");
  if (mode === "primary-terminal") {
    await waitForVisible(page, flow.terminal_selector, Number(flow.terminal_timeout_ms || 10000), "scenario setup terminal");
  }
}

async function performScenarioAction(target, scenario, timeout) {
  const action = scenario.action || "click";
  if (action === "click") return target.click({ timeout });
  if (action === "fill") return target.fill(scenario.value, { timeout });
  if (action === "select") return target.selectOption(scenario.value, { timeout });
  if (action === "check") return target.check({ timeout });
  if (action === "press") return target.press(scenario.key, { timeout });
  throw new Error(`Unsupported control scenario action: ${action}`);
}

async function asyncActivitySnapshot(page) {
  return page.evaluate(() => globalThis.__GENSCAFF_ASYNC_ACTIVITY__ || {
    next_sequence: 0,
    overflow: true,
    records: [],
  }).catch(() => ({ next_sequence: 0, overflow: true, records: [] }));
}

async function drainResponsePromises(responsePromises) {
  const resources = [];
  let cursor = 0;
  while (cursor < responsePromises.length) {
    const batch = responsePromises.slice(cursor);
    cursor = responsePromises.length;
    resources.push(...(await Promise.all(batch)).filter(Boolean));
    await new Promise((resolve) => setTimeout(resolve, 0));
  }
  return resources;
}

function compileExpectedUrlPattern(raw) {
  if (!raw) return null;
  try {
    return new RegExp(raw);
  } catch (error) {
    throw new Error(`Invalid expected_url_pattern ${JSON.stringify(raw)}: ${error.message || error}`);
  }
}

async function runControlScenario(browser, config, entryUrl, viewport, scenario, scenarioIndex, outputDirectory, limits) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    deviceScaleFactor: Number(viewport.device_scale_factor || 1),
    reducedMotion: "reduce",
    colorScheme: config.color_scheme || "light",
  });
  await context.addInitScript({ content: INIT_SCRIPT });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const requestErrors = [];
  const responsePromises = [];
  page.on("console", (message) => {
    if (["error", "assert", "warning"].includes(message.type())) {
      consoleErrors.push({ type: message.type(), text: message.text(), location: message.location() });
    }
  });
  page.on("pageerror", (error) => pageErrors.push({ name: error.name, message: error.message, stack: error.stack || "" }));
  page.on("requestfailed", (request) => requestErrors.push({
    url: request.url(),
    method: request.method(),
    resource_type: request.resourceType(),
    failure: request.failure()?.errorText || "unknown",
  }));
  page.on("response", (response) => responsePromises.push(collectResponse(response, entryUrl, limits)));
  const scenarioId = String(scenario.id || `control-${scenarioIndex + 1}`);
  const stagePrefix = `control-${String(scenarioIndex + 1).padStart(3, "0")}`;
  const timeout = Number(scenario.timeout_ms || 5000);
  const action = scenario.action || "click";
  const setup = scenario.setup || "default";
  const expectedUrlRegex = compileExpectedUrlPattern(scenario.expected_url_pattern || "");
  let before = null;
  let after = null;
  let matchedCount = 0;
  let disabled = null;
  let expectedSelectorVisibleBefore = null;
  let expectedSelectorVisibleAfter = null;
  let expectedUrlMatchedBefore = null;
  let expectedUrlMatchedAfter = null;
  let targetStateBefore = null;
  let targetStateAfter = null;
  let asyncActivityBefore = null;
  let asyncActivityAfter = null;
  let resources = [];
  let errorMessage = "";
  try {
    const route = defaultRouteUrl(entryUrl, Boolean(config.allow_non_default_route));
    const response = await page.goto(route, {
      waitUntil: "domcontentloaded",
      timeout: Number(config.navigation_timeout_ms || 15000),
    });
    if (response && response.status() >= 400) throw new Error(`Default route returned HTTP ${response.status()}`);
    if (config.wait_for_selector) {
      await waitForVisible(page, config.wait_for_selector, Number(config.navigation_timeout_ms || 15000), "application readiness");
    }
    await page.addStyleTag({ content: "*,*::before,*::after{animation-duration:0s!important;animation-delay:0s!important;transition:none!important;scroll-behavior:auto!important}" });
    await prepareScenarioState(page, config, setup);
    const locator = page.locator(scenario.selector);
    matchedCount = await locator.count();
    if (matchedCount !== 1) throw new Error(`Control selector must match exactly one element; matched ${matchedCount}: ${scenario.selector}`);
    const target = locator.first();
    disabled = (await target.isDisabled().catch(() => false)) || (await target.getAttribute("aria-disabled")) === "true";
    targetStateBefore = await targetFormState(target);
    expectedSelectorVisibleBefore = await selectorVisible(page, scenario.expected_selector || "");
    expectedUrlMatchedBefore = expectedUrlRegex ? expectedUrlRegex.test(page.url()) : null;
    before = await captureState(page, viewport.name, `${stagePrefix}-before`, outputDirectory, limits);
    asyncActivityBefore = await asyncActivitySnapshot(page);
    if (disabled) throw new Error(`Control is disabled: ${scenario.selector}`);

    await performScenarioAction(target, scenario, timeout);
    if (scenario.expected_selector) {
      await waitForVisible(page, scenario.expected_selector, timeout, "control scenario expected state");
    }
    if (expectedUrlRegex) {
      await page.waitForURL((url) => expectedUrlRegex.test(url.href), { timeout });
    }
    const observationMs = Math.max(750, Number(scenario.settle_ms || config.control_settle_ms || 0));
    await page.waitForTimeout(observationMs);
    await page.waitForLoadState("networkidle", {
      timeout: Math.max(3000, Number(config.control_network_idle_timeout_ms || 0)),
    });
    asyncActivityAfter = await asyncActivitySnapshot(page);
  } catch (error) {
    errorMessage = String(error.message || error);
  }

  try {
    after = await captureState(page, viewport.name, `${stagePrefix}-after`, outputDirectory, limits);
    expectedSelectorVisibleAfter = await selectorVisible(page, scenario.expected_selector || "");
    expectedUrlMatchedAfter = expectedUrlRegex ? expectedUrlRegex.test(page.url()) : null;
    const targetAfter = page.locator(scenario.selector).first();
    targetStateAfter = (await targetAfter.count().catch(() => 0)) > 0 ? await targetFormState(targetAfter) : null;
  } catch (captureError) {
    const message = `after-state capture failed: ${captureError.message || captureError}`;
    errorMessage = errorMessage ? `${errorMessage}; ${message}` : message;
  } finally {
    if (!asyncActivityAfter) asyncActivityAfter = await asyncActivitySnapshot(page);
    resources = await drainResponsePromises(responsePromises);
    await context.close();
  }

  const documentChanged = Boolean(
    before && after && (
      before.url_sha256 !== after.url_sha256 ||
      before.dom_sha256 !== after.dom_sha256 ||
      before.visible_text_sha256 !== after.visible_text_sha256
    )
  );
  const valueChanged = Boolean(targetStateBefore && targetStateAfter && targetStateBefore.value !== targetStateAfter.value);
  const checkedChanged = Boolean(targetStateBefore && targetStateAfter && targetStateBefore.checked !== targetStateAfter.checked);
  const changed = documentChanged || valueChanged || checkedChanged;
  const expectedSelectorPassed = scenario.expected_selector
    ? expectedSelectorVisibleBefore === false && expectedSelectorVisibleAfter === true
    : true;
  const expectedUrlPassed = expectedUrlRegex
    ? expectedUrlMatchedBefore === false && expectedUrlMatchedAfter === true
    : true;
  const expectedValuePassed = scenario.expected_value !== undefined
    ? targetStateBefore?.value !== scenario.expected_value && targetStateAfter?.value === scenario.expected_value
    : true;
  const expectedCheckedPassed = scenario.expected_checked !== undefined
    ? targetStateBefore?.checked !== scenario.expected_checked && targetStateAfter?.checked === scenario.expected_checked
    : true;
  const asyncMarker = Number(asyncActivityBefore?.next_sequence || 0);
  const pendingActionAsync = (asyncActivityAfter?.records || []).filter(
    (record) => Number(record.sequence) >= asyncMarker && record.active === true
  );
  const failures = [];
  if (matchedCount !== 1) failures.push(`control selector matched ${matchedCount} elements instead of exactly one`);
  if (disabled === true) failures.push("control is disabled");
  if (!before || !after) failures.push("before/after evidence is incomplete");
  if (!changed) failures.push("action produced no meaningful URL, DOM, visible-text, value, or checked-state change");
  if (!expectedSelectorPassed) failures.push("expected selector did not transition from hidden to visible");
  if (!expectedUrlPassed) failures.push("expected URL pattern did not transition from unmatched to matched");
  if (!expectedValuePassed) failures.push("expected value was already present or was not produced by the action");
  if (!expectedCheckedPassed) failures.push("expected checked state was already present or was not produced by the action");
  if (asyncActivityAfter?.overflow) failures.push("action async-activity evidence overflowed");
  if (pendingActionAsync.length) failures.push(`action left ${pendingActionAsync.length} unsettled timer or animation task(s)`);
  if (consoleErrors.length) failures.push(`action emitted ${consoleErrors.length} console warning/error(s)`);
  if (pageErrors.length) failures.push(`action emitted ${pageErrors.length} page error(s)`);
  if (requestErrors.length) failures.push(`action emitted ${requestErrors.length} failed request(s)`);
  const finalError = [errorMessage, ...failures].filter(Boolean).join("; ");
  const passed = !finalError;
  return {
    publicResult: {
      id: scenarioId,
      selector: scenario.selector,
      action,
      setup,
      value: scenario.value ?? null,
      key: scenario.key ?? null,
      expected_selector: scenario.expected_selector || "",
      expected_url_pattern: scenario.expected_url_pattern || "",
      expected_value: scenario.expected_value ?? null,
      expected_checked: scenario.expected_checked ?? null,
      matched_count: matchedCount,
      disabled,
      expected_selector_visible_before: expectedSelectorVisibleBefore,
      expected_selector_visible_after: expectedSelectorVisibleAfter,
      expected_url_matched_before: expectedUrlMatchedBefore,
      expected_url_matched_after: expectedUrlMatchedAfter,
      target_state_before: targetStateBefore,
      target_state_after: targetStateAfter,
      document_change: documentChanged,
      value_change: valueChanged,
      checked_change: checkedChanged,
      async_activity_marker: asyncMarker,
      pending_action_async: pendingActionAsync,
      meaningful_change: changed,
      browser_errors: { console: consoleErrors, page: pageErrors, request: requestErrors },
      before: stateEvidence(before),
      after: stateEvidence(after),
      passed,
      error: finalError,
    },
    states: [before, after].filter(Boolean),
    resources,
    errors: { console: consoleErrors, page: pageErrors, request: requestErrors },
  };
}

async function collectResponse(response, entryUrl, limits) {
  const url = response.url();
  const firstParty = isFirstParty(url, entryUrl);
  const headers = await response.allHeaders().catch(() => ({}));
  const contentType = String(headers["content-type"] || "").split(";")[0].trim().toLowerCase();
  const status = response.status();
  if (status >= 300 && status < 400) {
    const empty = Buffer.alloc(0);
    return {
      url,
      first_party: firstParty,
      status,
      resource_type: response.request().resourceType(),
      content_type: contentType,
      sniffed_type: "",
      redirect: true,
      redirect_location: String(headers.location || ""),
      body_error: "",
      sha256: sha256(empty),
      byte_length: 0,
      body: "",
      encoding: "base64",
      body_truncated: false,
      scan_findings: [],
      data_uris: [],
    };
  }
  let body;
  try {
    body = await response.body();
  } catch (error) {
    return {
      url,
      first_party: firstParty,
      status,
      resource_type: response.request().resourceType(),
      content_type: contentType,
      sniffed_type: "",
      body_error: String(error.message || error),
      sha256: "",
      byte_length: 0,
      body: "",
      encoding: "",
      body_truncated: false,
      scan_findings: [],
      data_uris: [],
    };
  }
  const clipped = body.subarray(0, limits.maxResourceBodyBytes);
  const textual = isTextualContentType(contentType, url);
  const bodyValue = textual ? clipped.toString("utf8") : clipped.toString("base64");
  const scannableText = clipped.toString("utf8");
  return {
    url,
    first_party: firstParty,
    status,
    resource_type: response.request().resourceType(),
    content_type: contentType,
    sniffed_type: sniffResourceType(body),
    sha256: sha256(body),
    byte_length: body.length,
    body: bodyValue,
    encoding: textual ? "utf8" : "base64",
    body_truncated: body.length > clipped.length,
    scan_findings: scanText(scannableText, url),
    data_uris: extractDataUris(scannableText, url, limits.maxDecodedBytes),
  };
}

async function runViewport(browser, config, entryUrl, viewport, outputDirectory, limits) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    deviceScaleFactor: Number(viewport.device_scale_factor || 1),
    reducedMotion: "reduce",
    colorScheme: config.color_scheme || "light",
  });
  await context.addInitScript({ content: INIT_SCRIPT });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const requestErrors = [];
  const responsePromises = [];
  page.on("console", (message) => {
    if (["error", "assert", "warning"].includes(message.type())) {
      consoleErrors.push({ type: message.type(), text: message.text(), location: message.location() });
    }
  });
  page.on("pageerror", (error) => pageErrors.push({ name: error.name, message: error.message, stack: error.stack || "" }));
  page.on("requestfailed", (request) => requestErrors.push({
    url: request.url(),
    method: request.method(),
    resource_type: request.resourceType(),
    failure: request.failure()?.errorText || "unknown",
  }));
  page.on("response", (response) => responsePromises.push(collectResponse(response, entryUrl, limits)));

  const route = defaultRouteUrl(entryUrl, Boolean(config.allow_non_default_route));
  try {
    const response = await page.goto(route, {
      waitUntil: "domcontentloaded",
      timeout: Number(config.navigation_timeout_ms || 15000),
    });
    if (response && response.status() >= 400) throw new Error(`Default route returned HTTP ${response.status()}`);
    if (config.wait_for_selector) {
      await waitForVisible(page, config.wait_for_selector, Number(config.navigation_timeout_ms || 15000), "application readiness");
    }
    await page.addStyleTag({ content: "*,*::before,*::after{animation-duration:0s!important;animation-delay:0s!important;transition:none!important;scroll-behavior:auto!important}" });
    const domainSignals = await inspectConfiguredSelectors(page, config.domain_signal_selectors || []);
    const decisionSignals = await inspectConfiguredSelectors(page, config.decision_selectors || []);
    const primaryFlow = await performPrimaryFlow(page, config, viewport.name, outputDirectory, limits);
    await page.waitForTimeout(Number(config.resource_settle_ms || 100));
    const computedStyleFindings = primaryFlow.states.flatMap((state) =>
      state.frames.flatMap((frame) => (frame.computed_style_findings || []).map((finding) => ({ stage: state.stage, frame_url: frame.frame_url, ...finding })))
    );
    const svgFindings = primaryFlow.states.flatMap((state) =>
      state.frames.flatMap((frame) => (frame.svg_findings || []).map((finding) => ({ stage: state.stage, frame_url: frame.frame_url, ...finding })))
    );
    const canvasGradientCalls = primaryFlow.states.flatMap((state) =>
      state.frames.flatMap((frame) => (frame.canvas_gradient_calls || []).map((call) => ({ stage: state.stage, frame_url: frame.frame_url, ...call })))
    );
    const controlScenarioRuns = [];
    for (const [scenarioIndex, scenario] of (config.control_scenarios || []).entries()) {
      controlScenarioRuns.push(
        await runControlScenario(browser, config, entryUrl, viewport, scenario, scenarioIndex, outputDirectory, limits)
      );
    }
    const resources = [
      ...(await drainResponsePromises(responsePromises)),
      ...controlScenarioRuns.flatMap((run) => run.resources || []),
    ];
    const deduplicatedResources = [];
    const resourceKeys = new Set();
    for (const resource of resources) {
      const key = `${resource.url}\u0000${resource.sha256}`;
      if (resourceKeys.has(key)) continue;
      resourceKeys.add(key);
      deduplicatedResources.push(resource);
    }
    const dataUris = [
      ...primaryFlow.states.flatMap((state) => state.data_uris || []),
      ...deduplicatedResources.flatMap((resource) => resource.data_uris || []),
    ];
    const auditedStates = [
      ...primaryFlow.states,
      ...controlScenarioRuns.flatMap((run) => run.states),
    ];
    const allControls = aggregateInventory(
      auditedStates.flatMap((state) => state.frames || []),
      "controls"
    );
    const allClaims = aggregateInventory(
      auditedStates.flatMap((state) => state.frames || []),
      "claim_candidates"
    );
    const scenarioFindings = controlScenarioRuns.flatMap((run) => run.states.map(fullStateFindings));
    computedStyleFindings.push(...scenarioFindings.flatMap((finding) => finding.computed));
    svgFindings.push(...scenarioFindings.flatMap((finding) => finding.svg));
    canvasGradientCalls.push(...scenarioFindings.flatMap((finding) => finding.canvas));
    dataUris.push(...scenarioFindings.flatMap((finding) => finding.dataUris));
    return {
      name: viewport.name,
      width: viewport.width,
      height: viewport.height,
      device_scale_factor: Number(viewport.device_scale_factor || 1),
      default_route_url: route,
      final_url: page.url(),
      domain_signals: domainSignals,
      decision_signals: decisionSignals,
      primary_flow: primaryFlow,
      control_scenarios: controlScenarioRuns.map((run) => run.publicResult),
      controls: allControls,
      claim_candidates: allClaims,
      computed_style_findings: computedStyleFindings,
      svg_findings: svgFindings,
      canvas_gradient_calls: canvasGradientCalls,
      data_uris: dataUris,
      first_party_resources: deduplicatedResources.filter((resource) => resource.first_party),
      external_resources: deduplicatedResources.filter((resource) => !resource.first_party),
      errors: {
        console: [...consoleErrors, ...controlScenarioRuns.flatMap((run) => run.errors?.console || [])],
        page: [...pageErrors, ...controlScenarioRuns.flatMap((run) => run.errors?.page || [])],
        request: [...requestErrors, ...controlScenarioRuns.flatMap((run) => run.errors?.request || [])],
      },
    };
  } finally {
    await context.close();
  }
}

async function launchBrowser(config) {
  let playwright;
  try {
    playwright = require("playwright");
  } catch (error) {
    throw new Error(`Playwright is required but could not be loaded: ${error.message || error}`);
  }
  const options = { headless: true, args: Array.isArray(config.browser_args) ? config.browser_args : [] };
  if (config.executable_path) options.executablePath = config.executable_path;
  try {
    return await playwright.chromium.launch(options);
  } catch (firstError) {
    const chrome = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
    if (!options.executablePath && fs.existsSync(chrome)) {
      return playwright.chromium.launch({ ...options, executablePath: chrome });
    }
    throw firstError;
  }
}

async function main() {
  const args = parseArguments(process.argv);
  if (args.help) {
    process.stderr.write("Usage: node live_audit.js --config <config.json>\n");
    return;
  }
  const loaded = await readConfig(args.config);
  const config = loaded.value;
  assertConfig(config);
  const entryUrl = resolveEntryUrl(config.entry_url, loaded.configDir);
  const outputDirectory = resolveOutputDirectory(config.output_dir, loaded.configDir);
  if (outputDirectory) fs.mkdirSync(outputDirectory, { recursive: true });
  const limits = {
    maxResourceBodyBytes: Math.max(16384, Number(config.max_resource_body_bytes || 1024 * 1024)),
    maxDecodedBytes: Math.max(4096, Number(config.max_decoded_data_uri_bytes || 512 * 1024)),
  };
  const browser = await launchBrowser(config);
  const startedAt = new Date().toISOString();
  try {
    const browserVersion = browser.version();
    const viewports = config.viewports || DEFAULT_VIEWPORTS;
    const results = [];
    for (const viewport of viewports) {
      results.push(await runViewport(browser, config, entryUrl, viewport, outputDirectory, limits));
    }
    const userAgentContext = await browser.newContext();
    const userAgentPage = await userAgentContext.newPage();
    const userAgent = await userAgentPage.evaluate(() => navigator.userAgent);
    await userAgentContext.close();
    const bundle = {
      schema_version: 1,
      generated_by: "genscaff-live-audit-v1",
      run_id: crypto.randomUUID(),
      started_at: startedAt,
      completed_at: new Date().toISOString(),
      runner: { path: RUNNER_PATH, sha256: RUNNER_SHA256 },
      config: { path: loaded.configPath, sha256: loaded.configSha256 },
      source_fingerprint: config.source_fingerprint,
      entry_url_requested: config.entry_url,
      entry_url_default: defaultRouteUrl(entryUrl, Boolean(config.allow_non_default_route)),
      browser: { engine: "chromium", version: browserVersion, user_agent: userAgent },
      viewports: results,
    };
    bundle.prohibited_finding_counts = {
      computed_style: results.reduce((total, item) => total + item.computed_style_findings.length, 0),
      svg: results.reduce((total, item) => total + item.svg_findings.length, 0),
      canvas_gradient: results.reduce((total, item) => total + item.canvas_gradient_calls.length, 0),
      data_uri: results.reduce((total, item) => total + item.data_uris.reduce((count, uri) => count + uri.scan_findings.length, 0), 0),
      loaded_resource: results.reduce((total, item) => total + [...item.first_party_resources, ...item.external_resources].reduce((count, resource) => count + resource.scan_findings.length, 0), 0),
    };
    bundle.bundle_sha256 = sha256(Buffer.from(canonicalJson(bundle), "utf8"));
    if (outputDirectory) {
      fs.writeFileSync(path.join(outputDirectory, "live-audit-bundle.json"), `${JSON.stringify(bundle, null, 2)}\n`, "utf8");
    }
    process.stdout.write(`${JSON.stringify(bundle)}\n`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  process.stderr.write(`GENSCAFF_LIVE_AUDIT_ERROR: ${error && (error.stack || error.message) ? error.stack || error.message : String(error)}\n`);
  process.exitCode = 1;
});
