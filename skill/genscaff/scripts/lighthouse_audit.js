#!/usr/bin/env node
"use strict";

/**
 * Gate-owned Lighthouse runner.
 *
 * Usage:
 *   node lighthouse_audit.js --config <live-audit-config.json>
 *
 * A file:// entry is exposed from its containing directory through a
 * short-lived loopback-only static server because Lighthouse audits HTTP(S)
 * navigation. Successful stdout is exactly one complete Lighthouse JSON
 * object. Diagnostics and failures are written only to stderr.
 */

const crypto = require("crypto");
const fs = require("fs");
const http = require("http");
const os = require("os");
const path = require("path");
const { pathToFileURL, fileURLToPath } = require("url");

const RUNNER_PATH = fs.realpathSync(__filename);
const RUNNER_SHA256 = sha256(fs.readFileSync(RUNNER_PATH));
const ONLY_CATEGORIES = ["performance", "accessibility", "best-practices", "seo"];
const DEFAULT_TIMEOUT_MS = 180_000;

const MIME_TYPES = new Map([
  [".avif", "image/avif"],
  [".css", "text/css; charset=utf-8"],
  [".gif", "image/gif"],
  [".htm", "text/html; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".ico", "image/x-icon"],
  [".jpeg", "image/jpeg"],
  [".jpg", "image/jpeg"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".mjs", "text/javascript; charset=utf-8"],
  [".png", "image/png"],
  [".svg", "image/svg+xml; charset=utf-8"],
  [".txt", "text/plain; charset=utf-8"],
  [".wasm", "application/wasm"],
  [".webmanifest", "application/manifest+json; charset=utf-8"],
  [".webp", "image/webp"],
  [".woff", "font/woff"],
  [".woff2", "font/woff2"],
  [".xml", "application/xml; charset=utf-8"],
]);

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function parseArguments(argv) {
  let configPath = null;
  for (let index = 2; index < argv.length; index += 1) {
    const item = argv[index];
    if (item === "--config" && argv[index + 1]) {
      if (configPath !== null) throw new Error("--config may be supplied only once");
      configPath = argv[index + 1];
      index += 1;
      continue;
    }
    if (item === "--help" || item === "-h") {
      process.stderr.write("Usage: node lighthouse_audit.js --config <live-audit-config.json>\n");
      process.exit(0);
    }
    throw new Error(`Unknown or incomplete argument: ${item}`);
  }
  if (!configPath) throw new Error("--config <live-audit-config.json> is required");
  return { configPath };
}

function readConfig(configArgument) {
  const resolved = path.resolve(configArgument);
  const raw = fs.readFileSync(resolved);
  let config;
  try {
    config = JSON.parse(raw.toString("utf8"));
  } catch (error) {
    throw new Error(`Invalid config JSON: ${error.message || error}`);
  }
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("Config root must be a JSON object");
  }
  if (typeof config.entry_url !== "string" || !config.entry_url.trim()) {
    throw new Error("Config entry_url is required");
  }
  const timeout = config.lighthouse_timeout_ms;
  if (
    timeout !== undefined &&
    (!Number.isInteger(timeout) || timeout < 10_000 || timeout > 600_000)
  ) {
    throw new Error("Config lighthouse_timeout_ms must be an integer from 10000 to 600000");
  }
  if (config.chrome_path !== undefined && typeof config.chrome_path !== "string") {
    throw new Error("Config chrome_path must be a string when supplied");
  }
  return {
    config,
    configDir: path.dirname(resolved),
    configSha256: sha256(raw),
  };
}

function resolveEntryUrl(rawEntryUrl, configDir) {
  let entryUrl;
  try {
    entryUrl = new URL(rawEntryUrl);
  } catch (_) {
    entryUrl = pathToFileURL(path.resolve(configDir, rawEntryUrl));
  }
  if (!["file:", "http:", "https:"].includes(entryUrl.protocol)) {
    throw new Error(`Unsupported entry_url protocol: ${entryUrl.protocol}`);
  }
  return entryUrl;
}

function isPathInside(root, candidate) {
  const relative = path.relative(root, candidate);
  return relative === "" || (!relative.startsWith(`..${path.sep}`) && relative !== "..");
}

function closeServer(server) {
  if (!server) return Promise.resolve();
  return new Promise((resolve) => {
    server.close(() => resolve());
    if (typeof server.closeAllConnections === "function") server.closeAllConnections();
  });
}

async function createStaticServer(entryUrl) {
  const cleanEntryUrl = new URL(entryUrl.href);
  cleanEntryUrl.search = "";
  cleanEntryUrl.hash = "";
  let entryPath = fileURLToPath(cleanEntryUrl);
  const entryStats = fs.statSync(entryPath);
  if (entryStats.isDirectory()) entryPath = path.join(entryPath, "index.html");
  if (!fs.statSync(entryPath).isFile()) throw new Error(`file:// entry is not a file: ${entryPath}`);

  const root = fs.realpathSync(path.dirname(entryPath));
  const realEntryPath = fs.realpathSync(entryPath);
  const entryName = path.basename(realEntryPath);

  const server = http.createServer((request, response) => {
    try {
      if (request.method !== "GET" && request.method !== "HEAD") {
        response.writeHead(405, { Allow: "GET, HEAD" });
        response.end();
        return;
      }

      const requestUrl = new URL(request.url || "/", "http://127.0.0.1");
      let pathname;
      try {
        pathname = decodeURIComponent(requestUrl.pathname);
      } catch (_) {
        response.writeHead(400);
        response.end("Bad request");
        return;
      }
      if (pathname.includes("\0")) {
        response.writeHead(400);
        response.end("Bad request");
        return;
      }
      const relative = pathname === "/" ? entryName : pathname.replace(/^\/+/, "");
      let candidate = path.resolve(root, relative);
      if (!isPathInside(root, candidate)) {
        response.writeHead(403);
        response.end("Forbidden");
        return;
      }
      let stats;
      try {
        stats = fs.statSync(candidate);
        if (stats.isDirectory()) {
          candidate = path.join(candidate, "index.html");
          stats = fs.statSync(candidate);
        }
        candidate = fs.realpathSync(candidate);
      } catch (_) {
        response.writeHead(404);
        response.end("Not found");
        return;
      }
      if (!stats.isFile() || !isPathInside(root, candidate)) {
        response.writeHead(403);
        response.end("Forbidden");
        return;
      }

      const headers = {
        "Cache-Control": "no-store, max-age=0",
        "Content-Length": String(stats.size),
        "Content-Type": MIME_TYPES.get(path.extname(candidate).toLowerCase()) || "application/octet-stream",
        "X-Content-Type-Options": "nosniff",
      };
      response.writeHead(200, headers);
      if (request.method === "HEAD") {
        response.end();
        return;
      }
      const stream = fs.createReadStream(candidate);
      stream.on("error", () => response.destroy());
      stream.pipe(response);
    } catch (_) {
      if (!response.headersSent) response.writeHead(500);
      response.end("Internal server error");
    }
  });

  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      server.removeListener("error", reject);
      resolve();
    });
  });
  const address = server.address();
  if (!address || typeof address === "string") {
    await closeServer(server);
    throw new Error("Unable to determine static server address");
  }
  return {
    server,
    auditedUrl: `http://127.0.0.1:${address.port}/${encodeURIComponent(entryName)}`,
  };
}

function firstExistingFile(candidates) {
  for (const candidate of candidates) {
    if (!candidate) continue;
    try {
      if (fs.statSync(candidate).isFile()) return fs.realpathSync(candidate);
    } catch (_) {
      // Continue through deterministic fallbacks.
    }
  }
  return null;
}

function resolveChromePath(config) {
  const localAppData = process.env.LOCALAPPDATA;
  return firstExistingFile([
    config.chrome_path && path.resolve(config.chrome_path),
    process.env.CHROME_PATH,
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    localAppData && path.join(localAppData, "Google", "Chrome", "Application", "chrome.exe"),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
  ]);
}

async function importWithFallback(specifier, fallbackPaths) {
  try {
    return await import(specifier);
  } catch (primaryError) {
    for (const candidate of fallbackPaths) {
      if (!candidate || !fs.existsSync(candidate)) continue;
      try {
        return await import(pathToFileURL(candidate).href);
      } catch (_) {
        // Preserve the primary package-resolution error below.
      }
    }
    throw new Error(`Unable to load ${specifier}: ${primaryError.message || primaryError}`);
  }
}

function nodeModuleRoots() {
  const configured = [
    process.env.GENSCAFF_NODE_MODULES,
    ...(process.env.NODE_PATH ? process.env.NODE_PATH.split(path.delimiter) : []),
  ];
  return [...new Set([
    path.join(__dirname, "node_modules"),
    path.join(path.dirname(__dirname), "node_modules"),
    ...configured,
  ].filter(Boolean).map((candidate) => path.resolve(candidate)))];
}

function packageEntryFallbacks(packageName, ...entryParts) {
  return nodeModuleRoots().map((root) => path.join(root, packageName, ...entryParts));
}

async function loadLighthouseRuntime() {
  const lighthouseModule = await importWithFallback(
    "lighthouse",
    packageEntryFallbacks("lighthouse", "core", "index.js"),
  );
  const launcherModule = await importWithFallback(
    "chrome-launcher",
    packageEntryFallbacks("chrome-launcher", "dist", "index.js"),
  );
  if (typeof lighthouseModule.default !== "function") {
    throw new Error("The loaded Lighthouse module has no default runner function");
  }
  if (typeof launcherModule.launch !== "function") {
    throw new Error("The loaded chrome-launcher module has no launch function");
  }
  return { lighthouse: lighthouseModule.default, chromeLauncher: launcherModule };
}

async function withTimeout(promise, timeoutMs) {
  let timer;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(`Lighthouse timed out after ${timeoutMs} ms`)), timeoutMs);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

async function settleWithin(promise, timeoutMs) {
  let timer;
  try {
    await Promise.race([
      Promise.resolve(promise).catch(() => undefined),
      new Promise((resolve) => {
        timer = setTimeout(resolve, timeoutMs);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

function writeStream(stream, value) {
  return new Promise((resolve, reject) => {
    stream.write(value, (error) => {
      if (error) reject(error);
      else resolve();
    });
  });
}

async function run() {
  const { configPath } = parseArguments(process.argv);
  const { config, configDir, configSha256 } = readConfig(configPath);
  const entryUrl = resolveEntryUrl(config.entry_url, configDir);
  const timeoutMs = config.lighthouse_timeout_ms || DEFAULT_TIMEOUT_MS;

  let server = null;
  let chrome = null;
  let cleaning = false;
  let serializedResult = null;

  const cleanup = async () => {
    if (cleaning) return;
    cleaning = true;
    try {
      if (chrome) await settleWithin(chrome.kill(), 10_000);
    } catch (_) {
      // Cleanup is best-effort; the audit failure remains the primary error.
    }
    try {
      await settleWithin(closeServer(server), 5_000);
    } catch (_) {
      // Cleanup is best-effort; the audit failure remains the primary error.
    }
  };

  const onSignal = (signal) => {
    cleanup().finally(() => process.exit(signal === "SIGINT" ? 130 : 143));
  };
  process.once("SIGINT", onSignal);
  process.once("SIGTERM", onSignal);

  try {
    let auditedUrl = entryUrl.href;
    if (entryUrl.protocol === "file:") {
      const staticHost = await createStaticServer(entryUrl);
      server = staticHost.server;
      auditedUrl = staticHost.auditedUrl;
    }

    const { lighthouse, chromeLauncher } = await loadLighthouseRuntime();
    const chromePath = resolveChromePath(config);
    const launchOptions = {
      chromeFlags: [
        "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
      ],
      logLevel: "silent",
    };
    if (chromePath) launchOptions.chromePath = chromePath;
    chrome = await chromeLauncher.launch(launchOptions);

    const flags = {
      port: chrome.port,
      hostname: "127.0.0.1",
      output: "json",
      logLevel: "silent",
      onlyCategories: ONLY_CATEGORIES,
      enableErrorReporting: false,
      maxWaitForLoad: Math.min(90_000, timeoutMs - 1_000),
    };
    const result = await withTimeout(lighthouse(auditedUrl, flags), timeoutMs);
    if (!result || !result.lhr || typeof result.lhr !== "object") {
      throw new Error("Lighthouse returned no standard LHR JSON object");
    }

    const lhr = result.lhr;
    for (const category of ONLY_CATEGORIES) {
      if (!lhr.categories || !lhr.categories[category]) {
        throw new Error(`Lighthouse result is missing categories.${category}`);
      }
    }
    lhr._genscaff_provenance = {
      runner_sha256: RUNNER_SHA256,
      config_sha256: configSha256,
      audited_url: lhr.finalUrl || auditedUrl,
    };
    serializedResult = `${JSON.stringify(lhr)}\n`;
  } finally {
    process.removeListener("SIGINT", onSignal);
    process.removeListener("SIGTERM", onSignal);
    await cleanup();
  }

  if (serializedResult !== null) {
    await writeStream(process.stdout, serializedResult);
  }
}

run().then(
  () => process.exit(0),
  (error) => {
    const message = `LIGHTHOUSE_AUDIT_ERROR: ${error && error.stack ? error.stack : error}\n`;
    process.stderr.write(message, () => process.exit(1));
  },
);
