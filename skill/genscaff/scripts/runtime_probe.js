/*
 * Run this in the rendered page context at desktop and mobile widths.
 * Save the returned `style_manifest` as JSON. Use `controls` as the complete
 * starting inventory for the separately observed control manifest; do not
 * mark controls functional until they have been activated and observed.
 */
(() => {
  const sourceFingerprint = String(
    globalThis.__GENSCAFF_SOURCE_FINGERPRINT__ || ""
  );

  const selectorFor = (element) => {
    if (element.id) return `#${CSS.escape(element.id)}`;
    const testId = element.getAttribute("data-testid");
    if (testId) return `[data-testid="${CSS.escape(testId)}"]`;
    const parts = [];
    let current = element;
    while (current && current.nodeType === Node.ELEMENT_NODE && parts.length < 5) {
      let part = current.localName;
      const siblings = current.parentElement
        ? [...current.parentElement.children].filter(
            (candidate) => candidate.localName === current.localName
          )
        : [];
      if (siblings.length > 1) {
        part += `:nth-of-type(${siblings.indexOf(current) + 1})`;
      }
      parts.unshift(part);
      current = current.parentElement;
    }
    return parts.join(" > ");
  };

  const visible = (element) => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return (
      style.display !== "none" &&
      style.visibility !== "hidden" &&
      Number(style.opacity) > 0 &&
      rect.width > 0 &&
      rect.height > 0
    );
  };

  const alphaOf = (color) => {
    const match = color.match(/rgba?\(([^)]+)\)/i);
    if (!match) return 1;
    const parts = match[1].split(/[\s,/]+/).filter(Boolean);
    if (parts.length < 4) return 1;
    const raw = parts[3];
    return raw.endsWith("%") ? Number(raw.slice(0, -1)) / 100 : Number(raw);
  };

  const gradientMatches = [];
  const backdropBlurMatches = [];
  const glassSurfaceMatches = [];
  const blurOrGlowMatches = [];

  const inspectStyle = (element, pseudo = null) => {
    const style = getComputedStyle(element, pseudo);
    const selector = `${selectorFor(element)}${pseudo || ""}`;
    const rect = element.getBoundingClientRect();
    const region = {
      x: Math.round(rect.x),
      y: Math.round(rect.y),
      width: Math.round(rect.width),
      height: Math.round(rect.height),
    };
    const backgroundImage = style.backgroundImage || "none";
    const backdropFilter =
      style.backdropFilter || style.webkitBackdropFilter || "none";
    const filter = style.filter || "none";
    const boxShadow = style.boxShadow || "none";
    if (/gradient\s*\(/i.test(backgroundImage)) {
      gradientMatches.push({ selector, backgroundImage, region });
    }
    if (backdropFilter !== "none") {
      backdropBlurMatches.push({ selector, backdropFilter, region });
    }
    const translucent = alphaOf(style.backgroundColor || "") < 0.94;
    const bordered = style.borderStyle !== "none" && style.borderWidth !== "0px";
    const elevated = boxShadow !== "none";
    if (translucent && (backdropFilter !== "none" || (bordered && elevated))) {
      glassSurfaceMatches.push({
        selector,
        backgroundColor: style.backgroundColor,
        backdropFilter,
        border: style.border,
        boxShadow,
        region,
      });
    }
    if (/blur\s*\(/i.test(filter) || /(?:0px\s+){0,2}(?:[3-9]\d|\d{3,})px/i.test(boxShadow)) {
      blurOrGlowMatches.push({ selector, filter, boxShadow, region });
    }
  };

  const elements = [...document.querySelectorAll("*")].filter(visible);
  for (const element of elements) {
    inspectStyle(element);
    for (const pseudo of ["::before", "::after"]) {
      const style = getComputedStyle(element, pseudo);
      if (style.content !== "none" || style.backgroundImage !== "none") {
        inspectStyle(element, pseudo);
      }
    }
  }

  const svgGradientOrBlurMatches = [
    ...document.querySelectorAll("linearGradient, radialGradient, feGaussianBlur"),
  ].map((element) => ({
    selector: selectorFor(element),
    kind: element.localName,
  }));

  const interactiveSelector = [
    "a[href]",
    "button",
    "input:not([type='hidden'])",
    "select",
    "textarea",
    "[role='button']",
    "[role='link']",
    "[role='tab']",
    "[role='checkbox']",
    "[role='radio']",
    "[role='switch']",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");
  const controls = [...document.querySelectorAll(interactiveSelector)]
    .filter(visible)
    .map((element) => ({
      selector: selectorFor(element),
      label: (
        element.innerText ||
        element.value ||
        element.getAttribute("aria-label") ||
        element.getAttribute("title") ||
        ""
      ).trim(),
      accessible_name: (
        element.getAttribute("aria-label") ||
        element.innerText ||
        element.value ||
        element.getAttribute("title") ||
        ""
      ).trim(),
      role:
        element.getAttribute("data-genscaff-role") ||
        element.getAttribute("role") ||
        element.localName,
      disabled:
        element.matches(":disabled") || element.getAttribute("aria-disabled") === "true",
      href: element.getAttribute("href") || "",
      behavior: "NOT_TESTED",
      meaningful_change: false,
      before_state_hash: "",
      after_state_hash: "",
      before_url: location.href,
      after_url: "",
      expected_result: "",
      observed_result: "",
      recovery: "",
    }));

  const claimPattern = /(?:\d[\d,.]*\s*(?:%|ms|s|x|k|m|b|users?|customers?|teams?)|certif|award|trusted by|used by|integrat|testimonial|uptime|faster|reduc|increase)/i;
  const claimCandidates = elements
    .filter((element) => {
      if (!/^(?:h[1-6]|p|li|td|th|blockquote|figcaption|dd|dt|span)$/i.test(element.localName)) {
        return false;
      }
      const text = (element.innerText || "").trim();
      return text.length >= 3 && text.length <= 500 && claimPattern.test(text);
    })
    .map((element) => ({
      selector: selectorFor(element),
      text: (element.innerText || "").trim(),
      status: "NOT_TESTED",
    }));

  const viewport = innerWidth <= 600 ? "mobile" : "desktop";
  const canvasCount = document.querySelectorAll("canvas").length;
  const styleManifest = {
    schema_version: 1,
    generated_by: "genscaff-computed-style-audit-v1",
    source_fingerprint: sourceFingerprint,
    viewport,
    captured_at: new Date().toISOString(),
    url: location.href,
    scanned_elements: elements.length,
    pseudo_elements_checked: true,
    canvas_and_svg_checked: true,
    canvas_count: canvasCount,
    canvas_elements_reviewed: canvasCount === 0,
    gradient_matches: gradientMatches,
    backdrop_blur_matches: backdropBlurMatches,
    glass_surface_matches: glassSurfaceMatches,
    blur_or_glow_matches: blurOrGlowMatches,
    svg_gradient_or_blur_matches: svgGradientOrBlurMatches,
    raster_visual_findings: [],
  };

  const result = { style_manifest: styleManifest, controls, claim_candidates: claimCandidates };
  globalThis.__GENSCAFF_AUDIT__ = result;
  return result;
})();
