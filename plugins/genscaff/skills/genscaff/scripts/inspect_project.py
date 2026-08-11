#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

LOCKFILES = {
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "package-lock.json": "npm",
    "bun.lock": "bun",
    "bun.lockb": "bun",
}
DEPENDENCY_SIGNALS = {
    "framework": {"next": "Next.js", "nuxt": "Nuxt", "@angular/core": "Angular", "svelte": "Svelte", "vue": "Vue", "react": "React"},
    "router": {"react-router": "React Router", "react-router-dom": "React Router", "vue-router": "Vue Router", "@tanstack/react-router": "TanStack Router"},
    "styling": {"tailwindcss": "Tailwind CSS", "styled-components": "styled-components", "@emotion/react": "Emotion", "sass": "Sass"},
    "state": {"redux": "Redux", "@reduxjs/toolkit": "Redux Toolkit", "zustand": "Zustand", "pinia": "Pinia", "xstate": "XState"},
    "data_fetching": {"@tanstack/react-query": "TanStack Query", "swr": "SWR", "@apollo/client": "Apollo Client"},
    "tests": {"vitest": "Vitest", "jest": "Jest", "@playwright/test": "Playwright", "cypress": "Cypress"},
}


def inspect(root: Path) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("target must be an existing directory")
    facts: dict[str, object] = {"project_root": str(root), "package_managers": [], "manifests": [], "scripts": {}, "config_files": []}
    uncertain: dict[str, list[str]] = {key: [] for key in DEPENDENCY_SIGNALS}

    for name, manager in LOCKFILES.items():
        if (root / name).is_file():
            facts["package_managers"].append(manager)

    manifest = root / "package.json"
    dependencies: dict[str, object] = {}
    if manifest.is_file():
        try:
            package = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            facts["manifest_error"] = str(error)
        else:
            facts["manifests"].append("package.json")
            facts["scripts"] = package.get("scripts", {}) if isinstance(package.get("scripts"), dict) else {}
            for field in ("dependencies", "devDependencies", "peerDependencies"):
                value = package.get(field, {})
                if isinstance(value, dict):
                    dependencies.update(value)
    for category, signals in DEPENDENCY_SIGNALS.items():
        uncertain[category] = sorted({label for dependency, label in signals.items() if dependency in dependencies})

    config_names = (
        "tsconfig.json", "jsconfig.json", "vite.config.js", "vite.config.ts", "next.config.js", "next.config.mjs",
        "next.config.ts", "nuxt.config.ts", "svelte.config.js", "angular.json", "tailwind.config.js",
        "tailwind.config.ts", "postcss.config.js", "eslint.config.js", "eslint.config.mjs", "playwright.config.ts",
    )
    facts["config_files"] = [name for name in config_names if (root / name).is_file()]
    facts["localization_files"] = sorted(path.name for path in root.glob("*i18n*.*") if path.is_file())
    facts["has_src"] = (root / "src").is_dir()
    facts["has_app_router"] = (root / "app").is_dir() or (root / "src" / "app").is_dir()
    facts["has_pages_router"] = (root / "pages").is_dir() or (root / "src" / "pages").is_dir()
    return {"facts": facts, "heuristic_detections": uncertain, "commands_executed": []}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read project metadata without executing project commands")
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    try:
        result = inspect(args.project)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
