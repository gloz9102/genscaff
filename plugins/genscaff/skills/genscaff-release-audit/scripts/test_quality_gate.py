#!/usr/bin/env python3
"""Regression tests for the strict frontend quality gate."""

from __future__ import annotations

import copy
import base64
import hashlib
import http.server
import json
import os
import subprocess
import struct
import sys
import tempfile
import threading
import unittest
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import quality_gate as gate


def make_png(path: Path, width: int, height: int, seed: int) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        row = bytearray(bytes((247, 247, 245)) * width)

        def paint(left: int, right: int, color: tuple[int, int, int]) -> None:
            left = max(0, min(width, left))
            right = max(left, min(width, right))
            row[left * 3 : right * 3] = bytes(color) * (right - left)

        if y < max(10, height // 12):
            paint(0, width, (24, 27, 31))
        if height // 6 < y < height - height // 10:
            paint(width // 24, width // 5, (226, 227, 224))
        for row_index in range(5):
            top = height // 5 + row_index * max(8, height // 10)
            if top <= y < top + max(3, height // 35):
                paint(width // 4, width - width // 12, (58, 63, 70))
        if height - height // 7 <= y < height - height // 18:
            paint(width * 2 // 3, width - width // 12, (40 + seed * 29 % 150, 92, 76))
        state_top = height // 3
        if state_top <= y < state_top + max(6, height // 14):
            paint(width // 2, width - width // 10, (225 - seed * 31 % 150, 220, 214))
        raw.extend(row)

    def chunk(kind: bytes, payload: bytes) -> bytes:
        checksum = zlib.crc32(kind + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)

    content = b"\x89PNG\r\n\x1a\n"
    content += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    content += chunk(b"IDAT", zlib.compress(bytes(raw)))
    content += chunk(b"IEND", b"")
    path.write_bytes(content)


def make_noise_png(path: Path, width: int, height: int) -> None:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(
                (
                    (x * 73 + y * 151) % 256,
                    (x * 149 + y * 61) % 256,
                    (x * 199 + y * 107) % 256,
                )
            )

    def chunk(kind: bytes, payload: bytes) -> bytes:
        checksum = zlib.crc32(kind + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)

    content = b"\x89PNG\r\n\x1a\n"
    content += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    content += chunk(b"IDAT", zlib.compress(bytes(raw)))
    content += chunk(b"IEND", b"")
    path.write_bytes(content)


def evidence(
    artifact: Path,
    region: str = "Model comparison capability rows",
    observation: str = (
        "The interface exposes model context limits, price units, deployment states, "
        "and a saved selection result."
    ),
) -> dict[str, str]:
    return {"artifact": str(artifact), "region": region, "observation": observation}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iso_at(moment: datetime, seconds: int) -> str:
    return (moment + timedelta(seconds=seconds)).isoformat()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def build_valid_report(root: Path) -> tuple[dict[str, object], Path]:
    target = root / "visual-target.md"
    target.write_text(
        "# ModelScope visual target\n\n"
        "## Product contract\n\n"
        "Production engineers compare language models using context window limits, input and "
        "output token price units, modality support, deployment availability, and workload "
        "constraints. The primary task is to compare two language models and save the selected "
        "model to a persistent shortlist without losing the workload profile. Success means the "
        "saved shortlist names the model, retained constraints, and recovery controls.\n\n"
        "## Structural direction\n\n"
        "Use a pairwise capability table instead of a generic marketing hero or repeated feature "
        "cards. Put selectors, verified units, availability states, and the Save selected model "
        "control in the first task surface. Mobile uses a focused pairwise stack with the same "
        "decision evidence and no hidden primary action.\n\n"
        "## Action and states\n\n"
        "The sequence is comparison start, named pending feedback, saved terminal result, and a "
        "remove or replace recovery state. Long model names and long workload constraints must wrap "
        "without hiding price units. Empty, error, loading, disabled, success, and long-content "
        "states are documented with honest not-applicable rationales where the deterministic fixture "
        "does not contain that branch.\n\n"
        "## Anti-slop policy\n\n"
        "The implementation uses solid semantic surfaces, explicit hierarchy, restrained borders, "
        "and product-specific language. It contains no decorative color effects, translucent glass "
        "surface, backdrop blur, abstract orb, vague aspirational copy, fake metric, testimonial, "
        "logo strip, or nested card soup.\n",
        encoding="utf-8",
    )
    target_time = datetime.fromtimestamp(target.stat().st_mtime, timezone.utc)
    created_at = target_time.isoformat()

    source = root / "index.html"
    source.write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ModelScope comparison</title>
  <style>
    :root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; color: #202522; background: #f3f0e8; }
    header { padding: 18px clamp(20px, 5vw, 72px); background: #1e2823; color: #fff; }
    header strong { letter-spacing: .04em; }
    main { width: min(1080px, calc(100% - 32px)); margin: 30px auto 60px; }
    .eyebrow { color: #476152; font-size: .78rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
    h1 { max-width: 760px; margin: 8px 0 10px; font: 750 clamp(2rem, 6vw, 4.5rem)/.98 Georgia, serif; }
    .intro { max-width: 760px; color: #4c5650; font-size: 1.05rem; line-height: 1.65; }
    .workbench { margin-top: 28px; border: 1px solid #b8b9b2; background: #fffdf7; }
    .workbench h2 { margin: 0; padding: 18px 22px; border-bottom: 1px solid #c9cac4; font-size: 1rem; }
    dl { display: grid; grid-template-columns: 180px 1fr; margin: 0; }
    dt, dd { margin: 0; padding: 16px 22px; border-bottom: 1px solid #deded8; line-height: 1.5; }
    dt { color: #566159; font-weight: 700; }
    dd strong { color: #214c38; }
    #decision-point { padding: 18px 22px; background: #e9eee9; line-height: 1.55; }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; padding: 18px 22px; }
    button { min-height: 44px; border: 1px solid #284c3b; padding: 10px 15px; background: #fffdf7; color: #203f31; font: inherit; font-weight: 700; cursor: pointer; }
    button.primary { background: #244d3a; color: #fff; }
    button:focus-visible { outline: 3px solid #b56b2f; outline-offset: 3px; }
    [hidden] { display: none !important; }
    .state, .detail { margin: 0 22px 20px; padding: 14px 16px; border-left: 4px solid #9a5527; background: #f5eadc; line-height: 1.55; }
    #shortlist { border-left-color: #2c664a; background: #e5eee8; }
    .disclosure { margin: 16px 22px 22px; color: #626962; font-size: .86rem; }
    @media (max-width: 620px) {
      main { width: min(100% - 24px, 520px); margin-top: 22px; }
      h1 { font-size: 2.55rem; }
      dl { grid-template-columns: 1fr; }
      dt { padding-bottom: 4px; border-bottom: 0; }
      dd { padding-top: 4px; }
      .actions { align-items: stretch; flex-direction: column; }
      button { width: 100%; }
    }
  </style>
</head>
<body>
  <header><strong>ModelScope / production shortlist</strong></header>
  <main>
    <p class="eyebrow">Workload-first model selection</p>
    <h1>Compare production language models</h1>
    <p class="intro">Review language-model context windows, token prices, modality support, and deployment availability before saving a workload-specific choice.</p>
    <section class="workbench" aria-labelledby="comparison-title">
      <h2 id="comparison-title">Orion 2 versus Cedar Large</h2>
      <dl>
        <dt>Context windows</dt>
        <dd id="context-window"><strong>128K tokens</strong> for each selected model input.</dd>
        <dt>Token prices</dt>
        <dd id="token-price"><strong>Input $5 per million tokens</strong>; output $15 per million tokens.</dd>
        <dt>Deployment availability</dt>
        <dd id="deployment-path">API and managed hosting are available; private deployment requires review.</dd>
      </dl>
      <p id="decision-point"><strong>Decision:</strong> choose a language model using context requirement, modality, token price, deployment availability, and workload filter. Saving adds the model and workload constraints to the persistent shortlist.</p>
      <div class="actions">
        <button class="primary" id="save-model" data-action="save-model">Save selected model</button>
        <button id="show-assumptions">Inspect workload assumptions</button>
        <button id="show-cost">Inspect token-cost basis</button>
        <button id="show-long">Test long model content</button>
      </div>
      <p class="state" id="save-feedback" role="status" hidden>Saving Orion 2 with the production workload constraints…</p>
      <section class="state" id="shortlist" hidden>
        <h2>Selection confirmed</h2>
        <p>Orion 2 is in the shortlist with context, modality, price, and deployment constraints retained.</p>
        <button id="remove-model">Remove selected model</button>
      </section>
      <p class="state" id="recovered-state" hidden>Orion 2 was removed; the comparison and workload constraints remain editable.</p>
      <p class="detail" id="assumptions-panel" hidden>Workload assumption: long technical documents, structured extraction, and managed API deployment are required.</p>
      <p class="detail" id="cost-panel" hidden>Cost basis: input $5 per million tokens and output $15 per million tokens are deterministic fixture values.</p>
      <p class="detail" id="long-panel" hidden>Long-content fixture: Orion Production Reasoning and Retrieval Model, regional managed hosting availability under enterprise change-control requirements.</p>
      <p class="disclosure">All names, availability states, and prices on this page are deterministic demo fixtures, not current market claims.</p>
    </section>
  </main>
  <script>
    const save = document.querySelector('#save-model');
    const feedback = document.querySelector('#save-feedback');
    const shortlist = document.querySelector('#shortlist');
    const recovered = document.querySelector('#recovered-state');
    save.addEventListener('click', () => {
      recovered.hidden = true;
      save.disabled = true;
      feedback.hidden = false;
      window.setTimeout(() => {
        feedback.hidden = true;
        save.hidden = true;
        shortlist.hidden = false;
      }, 220);
    });
    document.querySelector('#remove-model').addEventListener('click', () => {
      shortlist.hidden = true;
      save.hidden = false;
      save.disabled = false;
      recovered.hidden = false;
    });
    for (const [button, panel] of [
      ['#show-assumptions', '#assumptions-panel'],
      ['#show-cost', '#cost-panel'],
      ['#show-long', '#long-panel'],
    ]) {
      document.querySelector(button).addEventListener('click', () => {
        document.querySelector(panel).hidden = false;
      });
    }
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )
    verifier = root / "verify-fixture.cjs"
    verifier.write_text(
        "const fs = require('fs');\n"
        "const html = fs.readFileSync('index.html', 'utf8');\n"
        "for (const token of ['#save-model', '#remove-model', '128K tokens', '$5 per million tokens']) {\n"
        "  if (!html.includes(token)) { console.error('missing fixture token:', token); process.exit(1); }\n"
        "}\n"
        "console.log('fixture source contract verified');\n",
        encoding="utf-8",
    )
    source_fingerprint = gate.hard_gate.calculate_source_fingerprint(
        gate.hard_gate.iter_source_files(root)
    )
    evidence_dir = root / "live-evidence"
    live_config = root / "live-audit-config.json"
    live_config.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "entry_url": source.resolve().as_uri(),
                "source_fingerprint": source_fingerprint,
                "output_dir": str(evidence_dir),
                "viewports": [
                    {"name": "desktop", "width": 1280, "height": 800},
                    {"name": "mobile", "width": 390, "height": 844},
                ],
                "wait_for_selector": "#save-model",
                "domain_signal_selectors": [
                    "#context-window",
                    "#token-price",
                    "#deployment-path",
                ],
                "decision_selectors": ["#decision-point"],
                "primary_flow": {
                    "selector": "#save-model",
                    "feedback_selector": "#save-feedback",
                    "terminal_selector": "#shortlist",
                    "recovery_selector": "#remove-model",
                    "recovered_selector": "#recovered-state",
                },
                "control_scenarios": [
                    {
                        "id": "workload-assumptions",
                        "selector": "#show-assumptions",
                        "action": "click",
                        "expected_selector": "#assumptions-panel",
                    },
                    {
                        "id": "cost-basis",
                        "selector": "#show-cost",
                        "action": "click",
                        "expected_selector": "#cost-panel",
                    },
                    {
                        "id": "long-content",
                        "selector": "#show-long",
                        "action": "click",
                        "expected_selector": "#long-panel",
                    },
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    runner = Path(__file__).resolve().with_name("live_audit.js")
    completed = subprocess.run(
        ["node", str(runner), "--config", str(live_config)],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Live fixture audit failed: {completed.stderr}")
    live_bundle = json.loads(completed.stdout)

    desktop = evidence_dir / "desktop-start.png"
    mobile = evidence_dir / "mobile-start.png"
    desktop_feedback = evidence_dir / "desktop-feedback.png"
    desktop_terminal = evidence_dir / "desktop-terminal.png"
    desktop_recovery = evidence_dir / "desktop-recovery.png"
    mobile_feedback = evidence_dir / "mobile-feedback.png"
    mobile_terminal = evidence_dir / "mobile-terminal.png"
    mobile_recovery = evidence_dir / "mobile-recovery.png"
    pass_one = evidence_dir / "desktop-control-001-after.png"
    pass_two = evidence_dir / "desktop-control-002-after.png"
    long_content = evidence_dir / "desktop-control-003-after.png"
    build_log = root / "build.log"
    build_log.write_text(
        "fixture source contract verified; required controls and domain values are present.\n",
        encoding="utf-8",
    )
    lighthouse = root / "lighthouse.json"
    lighthouse_runner = Path(__file__).resolve().with_name("lighthouse_audit.js")
    lighthouse_run = subprocess.run(
        ["node", str(lighthouse_runner), "--config", str(live_config)],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=240,
        check=False,
    )
    if lighthouse_run.returncode != 0:
        raise RuntimeError(f"Lighthouse fixture audit failed: {lighthouse_run.stderr}")
    lighthouse_data = json.loads(lighthouse_run.stdout)
    lighthouse.write_text(json.dumps(lighthouse_data), encoding="utf-8")

    report = copy.deepcopy(gate.TEMPLATE)
    report["evidence_catalog"] = {}
    report["context"] = {
        "work_type": "new",
        "scope": "screen",
        "product_name": "ModelScope",
        "product_type": "LLM comparison workspace",
        "target_user": "Engineers selecting a language model for production workloads",
        "user_need": (
            "Compare verified model capabilities and choose a suitable model without "
            "opening separate documentation pages."
        ),
        "primary_task": (
            "Compare two language models and save the model that fits the selected "
            "workload constraints."
        ),
        "success_outcome": (
            "The chosen model appears in a saved shortlist with the selected workload "
            "constraints retained."
        ),
        "primary_cta": "Save selected model",
        "constraints": [
            "Preserve verified capability units and readable comparison behavior on desktop and mobile."
        ],
        "differentiators": [
            "Capability rows expose model context, modality, price units, and deployment availability.",
            "Workload filters change recommendation evidence rather than decorating generic feature cards.",
        ],
        "domain_objects": ["language models", "context windows", "token prices"],
        "task_traits": ["selection", "persistence"],
        "assumptions": [],
    }
    report["visual_target"] = {
        "created_before_coding": True,
        "expanded_design_brief_created": True,
        "artifact": str(target),
        "created_at": created_at,
        "baseline_context": (
            "A new standalone comparison screen with no existing component system and "
            "a verified model-data contract."
        ),
        "brief_summary": (
            "A task-first LLM comparison screen centered on verified capability rows "
            "and a recoverable saved-shortlist result."
        ),
        "summary": (
            "A restrained comparison surface with model selection, evidence rows, and "
            "a persistent save action."
        ),
        "direction_options": [
            {
                "name": "Comparison table",
                "product_fit": (
                    "Aligned capability rows support expert model selection and expose "
                    "technical units directly."
                ),
                "tradeoff": (
                    "Small screens require a focused pairwise view rather than every model column."
                ),
            },
            {
                "name": "Guided selector",
                "product_fit": (
                    "A workload questionnaire reduces options and provides one recommendation "
                    "with evidence."
                ),
                "tradeoff": (
                    "The guided path makes broad side-by-side inspection slower for experienced users."
                ),
            },
        ],
        "selected_direction": "Comparison table",
        "selection_rationale": (
            "The target user already understands model terminology and needs aligned "
            "evidence more than onboarding, so pairwise comparison shortens the decision path."
        ),
        "benchmark_principles": [
            {
                "source": "Linear product interface",
                "principle": (
                    "Show the operational work surface and realistic metadata before marketing decoration."
                ),
                "relevance": (
                    "Both products support expert operational decisions through dense but predictable metadata."
                ),
                "application": (
                    "The first viewport opens on model selectors and capability rows with concrete units."
                ),
                "non_copy_boundary": (
                    "Do not copy Linear branding, palette, proprietary layout, labels, or assets."
                ),
            }
        ],
        "risk_hypotheses": [
            "A generic AI hero could hide the comparison task below decorative positioning copy.",
            "Unverified model metrics could create convincing but misleading product evidence.",
            "Mobile columns could compress until model names and numeric units become unreadable.",
        ],
        "primary_cta": "Save selected model",
        "token_strategy": (
            "Use semantic neutral, accent, status, spacing, type, radius, and interaction "
            "tokens before component styling."
        ),
    }

    base = evidence(desktop)
    requirement_ids = [
        "primary-task",
        "primary-cta",
        "constraint-1",
        "differentiator-1",
        "differentiator-2",
    ]
    report["requirement_trace"] = [
        {
            "id": requirement_id,
            "requirement": (
                f"{requirement_id} is implemented through the model comparison and saved shortlist workflow."
            ),
            "source": "user" if requirement_id.startswith("primary") else "derived",
            "implementation": (
                "Implemented in model selectors, capability rows, workload controls, and the saved shortlist."
            ),
            "status": "verified",
            "evidence": [base],
        }
        for requirement_id in requirement_ids
    ]
    report["product_specificity"] = {
        "domain_signals": [
            {
                "element": "Context-window row",
                "selector": "#context-window",
                "domain_detail": "Each selected model shows a numeric token limit with a consistent unit.",
                "decision_enabled": (
                    "Engineers can reject models that cannot hold the required prompt and document size."
                ),
                "evidence": base,
            },
            {
                "element": "Token-price row",
                "selector": "#token-price",
                "domain_detail": (
                    "Input and output token prices use separate per-million-token units."
                ),
                "decision_enabled": (
                    "Engineers can compare expected inference cost for their workload balance."
                ),
                "evidence": base,
            },
            {
                "element": "Deployment availability",
                "selector": "#deployment-path",
                "domain_detail": (
                    "Each model exposes API and hosting availability beside modality support."
                ),
                "decision_enabled": (
                    "Engineers can exclude models unavailable in the required deployment path."
                ),
                "evidence": base,
            },
        ],
        "decision_points": [
            {
                "decision": (
                    "Choose which language model should be saved for the current production workload."
                ),
                "selector": "#decision-point",
                "inputs": (
                    "Context requirement, modality, token price, deployment availability, and workload filter."
                ),
                "consequence": (
                    "The selected model and workload constraints are added to the persistent shortlist."
                ),
                "evidence": base,
            }
        ],
        "substitution_test": {
            "comparisons": [
                {
                    "alternate_product": "Pet adoption marketplace",
                    "still_fits": False,
                    "far_from_target": True,
                    "distance_rationale": (
                        "Animal adoption inventory, welfare states, and household matching have no shared "
                        "decision model with production language-model capability selection."
                    ),
                    "breaking_signals": [
                        "Token context limits cannot describe an adoptable animal profile.",
                        "Per-million-token prices cannot support a pet adoption decision.",
                    ],
                    "axes": {
                        "information_architecture": {
                            "breaks": True,
                            "reason": "Model comparison rows cannot organize animal profiles and household fit.",
                        },
                        "data_schema": {
                            "breaks": True,
                            "reason": "Context windows and token prices do not map to animal age or care needs.",
                        },
                        "state_transitions": {
                            "breaks": True,
                            "reason": "Saving a model shortlist cannot represent application and adoption review states.",
                        },
                        "action_sequence": {
                            "breaks": True,
                            "reason": "Pairwise model selection cannot complete household matching and application steps.",
                        },
                        "failure_recovery": {
                            "breaks": True,
                            "reason": "Model replacement controls cannot recover a rejected adoption application.",
                        },
                    },
                },
                {
                    "alternate_product": "Restaurant reservation service",
                    "still_fits": False,
                    "far_from_target": True,
                    "distance_rationale": (
                        "Restaurant time inventory, party capacity, and booking confirmation are unrelated "
                        "to evaluating deployment and inference constraints for language models."
                    ),
                    "breaking_signals": [
                        "Model modality and deployment states cannot describe restaurant inventory.",
                        "Workload constraints cannot produce a reservation time or party-size outcome.",
                    ],
                    "axes": {
                        "information_architecture": {
                            "breaks": True,
                            "reason": "Capability comparison rows cannot organize dates, tables, or party capacity.",
                        },
                        "data_schema": {
                            "breaks": True,
                            "reason": "Deployment and modality fields do not map to seating inventory or timeslots.",
                        },
                        "state_transitions": {
                            "breaks": True,
                            "reason": "A saved model shortlist cannot represent held, confirmed, and cancelled bookings.",
                        },
                        "action_sequence": {
                            "breaks": True,
                            "reason": "Model comparison cannot collect party size, date, time, and guest details.",
                        },
                        "failure_recovery": {
                            "breaks": True,
                            "reason": "Replacing a model cannot recover from unavailable reservation inventory.",
                        },
                    },
                },
            ],
            "verdict": "product-specific",
            "rationale": (
                "The decision depends on capability units, workload constraints, and deployment "
                "states that cannot survive superficial relabeling into either unrelated category."
            ),
        },
        "generic_elements_found": [],
    }
    report["action_trace"] = {
        "interaction_mode": "functional",
        "primary": {
            "label": "Save selected model",
            "location": "Persistent action below pairwise comparison results",
            "start_state": (
                "Two models and a workload profile are selected with comparison rows visible."
            ),
            "information_scent": (
                "The verb and object state that the current model selection will be added "
                "to a saved shortlist."
            ),
            "steps": [
                {
                    "action": "Activate Save selected model after reviewing capability rows.",
                    "feedback": (
                        "The control enters a pending state and confirms the selected model name."
                    ),
                    "result": (
                        "The selected model appears in the shortlist with workload constraints."
                    ),
                    "evidence": evidence(desktop_feedback),
                }
            ],
            "terminal_state": (
                "The shortlist confirms the model and retained workload profile with edit controls."
            ),
            "recovery_path": (
                "Remove the saved item or return to comparison and replace the selection."
            ),
            "checkpoints": {
                "start": evidence(desktop),
                "feedback": evidence(desktop_feedback),
                "terminal": evidence(desktop_terminal),
                "recovery": evidence(desktop_recovery),
            },
            "verified": True,
        },
        "dead_end_controls": [],
        "control_inventory": [
            {
                "label": "Save selected model",
                "accessible_name": "Save selected model",
                "selector": "#save-model",
                "role": "primary",
                "location": "Below the pairwise model comparison results",
                "behavior": "functional",
                "result_or_prerequisite": (
                    "Adds the selected model and workload context to the saved shortlist."
                ),
                "evidence": base,
            },
            {
                "label": "Inspect workload assumptions",
                "accessible_name": "Inspect workload assumptions",
                "selector": "#show-assumptions",
                "role": "secondary",
                "location": "Below the pairwise model comparison results",
                "behavior": "functional",
                "result_or_prerequisite": "Reveals the production workload assumptions used by this comparison.",
                "evidence": evidence(pass_one),
            },
            {
                "label": "Inspect token-cost basis",
                "accessible_name": "Inspect token-cost basis",
                "selector": "#show-cost",
                "role": "secondary",
                "location": "Below the pairwise model comparison results",
                "behavior": "functional",
                "result_or_prerequisite": "Reveals the deterministic token price basis used by the fixture.",
                "evidence": evidence(pass_two),
            },
            {
                "label": "Test long model content",
                "accessible_name": "Test long model content",
                "selector": "#show-long",
                "role": "secondary",
                "location": "Below the pairwise model comparison results",
                "behavior": "functional",
                "result_or_prerequisite": "Reveals a long model and deployment description for wrapping inspection.",
                "evidence": evidence(long_content),
            },
            {
                "label": "Remove selected model",
                "accessible_name": "Remove selected model",
                "selector": "#remove-model",
                "role": "secondary",
                "location": "Inside the saved shortlist terminal state",
                "behavior": "functional",
                "result_or_prerequisite": "Removes the chosen model and restores the retained comparison state.",
                "evidence": evidence(desktop_terminal),
            },
        ],
        "prototype_disclosure": "",
    }
    report["state_coverage"] = []
    for state_name in sorted(gate.REQUIRED_STATE_NAMES):
        implemented = state_name in {"success", "long-content"}
        report["state_coverage"].append(
            {
                "state": state_name,
                "surface": "Model comparison and shortlist surface",
                "status": "implemented" if implemented else "not-applicable",
                "rationale": (
                    "The state is rendered and verified in the comparison workflow."
                    if implemented
                    else (
                        "This deterministic fixture has no asynchronous or unavailable-data "
                        "branch for this state."
                    )
                ),
                "evidence": (
                    [evidence(desktop_terminal)]
                    if state_name == "success"
                    else [evidence(long_content)]
                    if state_name == "long-content"
                    else []
                ),
            }
        )
    report["task_walkthroughs"] = []
    for viewport, artifact, feedback_artifact, terminal_artifact, recovery_artifact in (
        (
            "desktop",
            desktop,
            desktop_feedback,
            desktop_terminal,
            desktop_recovery,
        ),
        ("mobile", mobile, mobile_feedback, mobile_terminal, mobile_recovery),
    ):
        walkthrough_evidence = evidence(
            artifact,
            f"{viewport} comparison and shortlist state",
            (
                "The selected model moves into the saved shortlist with retained workload "
                "context and recovery controls."
            ),
        )
        report["task_walkthroughs"].append(
            {
                "viewport": viewport,
                "start_state": (
                    "Two models are selected with all required capability rows visible."
                ),
                "steps": [
                    {
                        "action": "Activate Save selected model from the comparison result.",
                        "expected_feedback": (
                            "The control acknowledges the save and names the selected model."
                        ),
                        "observed_result": (
                            "The selected model appears in the shortlist with workload context."
                        ),
                        "evidence": evidence(feedback_artifact),
                    }
                ],
                "terminal_state": (
                    "The shortlist contains the model with edit and remove recovery controls."
                ),
                "failure_or_correction_path": (
                    "Removing the item returns to an unsaved comparison state without losing selections."
                ),
                "checkpoints": {
                    "start": evidence(artifact),
                    "feedback": evidence(feedback_artifact),
                    "terminal": evidence(terminal_artifact),
                    "recovery": evidence(recovery_artifact),
                },
                "result": "pass",
                "evidence": [evidence(terminal_artifact)],
            }
        )

    report["visual_review"] = {
        "desktop_checked": True,
        "mobile_checked": True,
        "brand_reference_compared": True,
        "ai_slop_visual_compared": True,
        "ui_craft_compared": True,
        "comparison_notes": (
            "The review compared workflow visibility, capability-table density, restrained "
            "tokens, CTA information scent, substitution resistance, mobile wrapping, and "
            "the absence of generic AI decoration."
        ),
        "screenshots": {"desktop": str(desktop), "mobile": str(mobile)},
        "console_errors": 0,
        "layout_issues_open": 0,
        "iteration_log": [
            {
                "pass": 1,
                "focus": (
                    "Primary task continuity, product specificity, hierarchy, and mobile structure."
                ),
                "screenshot": str(pass_one),
                "findings": [
                    {
                        "id": "named-feedback",
                        "severity": "major",
                        "symptom": (
                            "The pending save feedback omitted the selected model name and weakened clarity."
                        ),
                        "criterion": (
                            "Primary action feedback must identify the affected domain object."
                        ),
                        "evidence": evidence(
                            pass_one,
                            "Save action pending state",
                            (
                                "The pending feedback acknowledged activity but omitted the "
                                "selected model name."
                            ),
                        ),
                    }
                ],
                "changes": [
                    {
                        "resolves": ["named-feedback"],
                        "change": (
                            "Added the selected model name to pending and success feedback beside the control."
                        ),
                        "reason": (
                            "Specific feedback connects the trigger to the changed shortlist object."
                        ),
                        "files": [str(source)],
                        "evidence": evidence(
                            pass_two,
                            "Save action feedback state",
                            (
                                "Pending and success feedback now identify the selected model "
                                "before the shortlist appears."
                            ),
                        ),
                    }
                ],
                "evidence": [
                    evidence(
                        pass_one,
                        "First-pass comparison surface",
                        (
                            "The first pass exposed the primary task and revealed object-feedback ambiguity."
                        ),
                    )
                ],
            },
            {
                "pass": 2,
                "focus": (
                    "Typography, wrapping, token consistency, feedback wording, and substitution review."
                ),
                "screenshot": str(pass_two),
                "findings": [],
                "changes": [],
                "evidence": [
                    evidence(
                        pass_two,
                        "Final comparison surface",
                        (
                            "The final pass confirms named feedback, aligned units, wrapping, "
                            "and a stable terminal state."
                        ),
                    )
                ],
            },
        ],
        "open_findings": [],
        "independent_review": {
            "performed": True,
            "reviewer": "subagent",
            "reviewer_name": "Independent UI reviewer",
            "product_specificity_verdict": "pass",
            "action_continuity_verdict": "pass",
            "findings": [],
            "notes": (
                "The reviewer identified an LLM comparison tool for engineers, cited capability "
                "units and workload decisions as non-cosmetic signals, and followed the save "
                "action to a recoverable shortlist result."
            ),
            "evidence": [base],
        },
    }
    report["measurements"] = {
        "lighthouse": {
            "report": str(lighthouse),
            "scores": {
                "performance": round(lighthouse_data["categories"]["performance"]["score"] * 100),
                "accessibility": round(lighthouse_data["categories"]["accessibility"]["score"] * 100),
                "best_practices": round(lighthouse_data["categories"]["best-practices"]["score"] * 100),
                "seo": round(lighthouse_data["categories"]["seo"]["score"] * 100),
            },
        },
        "commands": [
            {
                "command": "node verify-fixture.cjs",
                "exit_code": 0,
                "result": "pass",
                "summary": (
                    "The repository verifier found the required controls and domain values in source."
                ),
                "artifact": str(build_log),
            }
        ],
        "lighthouse_is_technical_floor": True,
    }
    report["judgment"] = {
        "verdict": "pass",
        "product_specificity_score": 4,
        "action_continuity_score": 4,
        "visual_coherence_score": 4,
        "content_integrity_score": 4,
        "rationale": (
            "The final surface is grounded in model capability units, workload decisions, and "
            "deployment states; the primary action reaches a named, recoverable shortlist "
            "result on both target widths while hierarchy and copy stay restrained."
        ),
        "limitations": (
            "This verifies artifacts and documented judgment but cannot prove authorship, "
            "universal originality, or representative user outcomes without actual target-user research."
        ),
        "residual_risks": [],
    }
    report["checks"] = {key: True for key in gate.REQUIRED_CHECKS}

    live_by_path: dict[Path, dict[str, object]] = {}
    live_viewports = {item["name"]: item for item in live_bundle["viewports"]}
    for viewport_data in live_bundle["viewports"]:
        for state in viewport_data["primary_flow"]["states"]:
            live_by_path[Path(state["screenshot_path"]).resolve()] = state
        for scenario in viewport_data["control_scenarios"]:
            for state_name in ("before", "after"):
                state = scenario[state_name]
                live_by_path[Path(state["screenshot_path"]).resolve()] = state

    capture_specs = [
        (desktop, "desktop", "comparison-start", "primary-start"),
        (desktop_feedback, "desktop", "save-pending", "primary-feedback"),
        (desktop_terminal, "desktop", "shortlist-saved", "primary-terminal"),
        (desktop_recovery, "desktop", "shortlist-recovered", "primary-recovery"),
        (mobile, "mobile", "comparison-start", "primary-start"),
        (mobile_feedback, "mobile", "save-pending", "primary-feedback"),
        (mobile_terminal, "mobile", "shortlist-saved", "primary-terminal"),
        (mobile_recovery, "mobile", "shortlist-recovered", "primary-recovery"),
        (pass_one, "desktop", "visual-iteration-one", "visual-pass-1"),
        (pass_two, "desktop", "visual-iteration-two", "visual-pass-2"),
        (long_content, "desktop", "long-content", "long-content"),
    ]
    captures = []
    for artifact, viewport, state, checkpoint in capture_specs:
        decoded = gate.hard_gate.decode_png(artifact, str(artifact), [])
        assert decoded is not None
        live_state = live_by_path[artifact.resolve()]
        captures.append(
            {
                "artifact": str(artifact),
                "sha256": live_state["screenshot_sha256"],
                "width": decoded["width"],
                "height": decoded["height"],
                "viewport": viewport,
                "route": source.resolve().as_uri(),
                "state": state,
                "checkpoint": checkpoint,
                "captured_at": live_state["captured_at"],
            }
        )
    captures.sort(key=lambda item: item["captured_at"])
    capture_manifest = root / "capture-manifest.json"
    capture_manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_by": gate.hard_gate.CAPTURE_GENERATOR,
                "source_fingerprint": source_fingerprint,
                "captures": captures,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    style_manifests = []
    for viewport in ("desktop", "mobile"):
        viewport_data = live_viewports[viewport]
        start_state = viewport_data["primary_flow"]["states"][0]
        start_frames = start_state["frames"]
        style_manifest = root / f"style-{viewport}.json"
        style_manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "generated_by": gate.hard_gate.STYLE_GENERATOR,
                    "live_run_id": live_bundle["run_id"],
                    "source_fingerprint": source_fingerprint,
                    "viewport": viewport,
                    "captured_at": start_state["captured_at"],
                    "url": viewport_data["default_route_url"],
                    "scanned_elements": sum(frame.get("element_count", 0) for frame in start_frames),
                    "pseudo_elements_checked": True,
                    "canvas_and_svg_checked": True,
                    "canvas_count": sum(frame.get("canvas_count", 0) for frame in start_frames),
                    "canvas_elements_reviewed": True,
                    "gradient_matches": [],
                    "backdrop_blur_matches": [],
                    "glass_surface_matches": [],
                    "blur_or_glow_matches": [],
                    "svg_gradient_or_blur_matches": [],
                    "raster_visual_findings": [],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        style_manifests.append(str(style_manifest))

    control_manifests = []
    for viewport in ("desktop", "mobile"):
        viewport_data = live_viewports[viewport]
        actual_by_selector = {item["selector"]: item for item in viewport_data["controls"]}
        flow_states = {item["stage"]: item for item in viewport_data["primary_flow"]["states"]}
        scenarios = {item["selector"]: item for item in viewport_data["control_scenarios"]}
        rendered_controls = []
        for report_control in report["action_trace"]["control_inventory"]:
            selector = report_control["selector"]
            actual = actual_by_selector[selector]
            if selector == "#save-model":
                before_state = flow_states["start"]
                after_state = flow_states["terminal"]
            elif selector == "#remove-model":
                before_state = flow_states["terminal"]
                after_state = flow_states["recovery"]
            else:
                before_state = scenarios[selector]["before"]
                after_state = scenarios[selector]["after"]
            rendered_controls.append(
                {
                    "label": report_control["label"],
                    "accessible_name": actual["accessible_name"],
                    "role": report_control["role"],
                    "selector": selector,
                    "behavior": report_control["behavior"],
                    "href": actual["href"],
                    "meaningful_change": True,
                    "before_state_hash": before_state["dom_sha256"],
                    "after_state_hash": after_state["dom_sha256"],
                    "before_url": before_state["url"],
                    "after_url": after_state["url"],
                    "expected_result": report_control["result_or_prerequisite"],
                    "observed_result": report_control["result_or_prerequisite"],
                    "recovery": "Reload the deterministic comparison route to restore its initial state.",
                }
            )
        control_manifest = root / f"controls-{viewport}.json"
        control_manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "generated_by": gate.hard_gate.CONTROL_GENERATOR,
                    "live_run_id": live_bundle["run_id"],
                    "source_fingerprint": source_fingerprint,
                    "viewport": viewport,
                    "captured_at": live_bundle["completed_at"],
                    "all_visible_controls_tested": True,
                    "dead_controls": [],
                    "unreported_controls": [],
                    "controls": rendered_controls,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        control_manifests.append(str(control_manifest))

    live_claims: dict[tuple[str, str], dict[str, object]] = {}
    for viewport_data in live_bundle["viewports"]:
        for claim in viewport_data["claim_candidates"]:
            live_claims[(claim["selector"], " ".join(claim["text"].casefold().split()))] = claim
    content_manifest = root / "content-manifest.json"
    content_manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_by": gate.hard_gate.CONTENT_GENERATOR,
                "live_run_id": live_bundle["run_id"],
                "source_fingerprint": source_fingerprint,
                "captured_at": live_bundle["completed_at"],
                "inventory_complete": True,
                "visible_claims": [
                    {
                        "text": claim["text"],
                        "selector": claim["selector"],
                        "claim_type": "mock-data",
                        "source_type": "fixture",
                        "source": "ModelScope deterministic browser fixture",
                        "disclosure": (
                            "All names, availability states, and prices are visibly disclosed as deterministic demo fixtures."
                        ),
                        "evidence_capture_sha256": sha256(
                            pass_two if claim["selector"] == "#cost-panel" else desktop
                        ),
                    }
                    for claim in live_claims.values()
                ],
                "unverified_claims": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    review_artifact = root / "independent-review.json"
    review_artifact.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_by": gate.hard_gate.REVIEW_GENERATOR,
                "reviewer_type": "subagent",
                "reviewer_id": "independent-ui-reviewer",
                "implementer_id": "fixture-implementer",
                "prompt_blind": True,
                "intended_verdict_disclosed": False,
                "neutral_prompt": (
                    "Inspect only the supplied source fingerprint, browser captures, computed-style "
                    "results, and control traces. Identify the product and primary task without relying "
                    "on its name, then challenge every control, terminal state, recovery path, and "
                    "generic visual pattern. Record failures before stating separate verdicts."
                ),
                "source_fingerprint": source_fingerprint,
                "reviewed_capture_sha256": [capture["sha256"] for capture in captures[:8]],
                "finished_at": (
                    datetime.fromisoformat(live_bundle["completed_at"].replace("Z", "+00:00"))
                    + timedelta(seconds=1)
                ).isoformat(),
                "identity_probe": {
                    "branding_ignored": True,
                    "branding_required": False,
                    "identified_product_type": (
                        "A production language-model capability comparison workspace"
                    ),
                    "identified_primary_task": (
                        "Compare two models and save one with retained workload constraints"
                    ),
                    "non_cosmetic_signals": [
                        "Context-window limits with token units",
                        "Separate input and output token pricing",
                        "Deployment availability tied to workload selection",
                    ],
                    "verdict": "pass",
                },
                "action_probe": {
                    "trigger_label": "Save selected model",
                    "predicted_outcome": (
                        "The current model and workload context will enter a persistent shortlist."
                    ),
                    "observed_feedback": (
                        "Pending feedback names the selected model before the shortlist changes."
                    ),
                    "observed_terminal_state": (
                        "The shortlist confirms the model and retained workload constraints."
                    ),
                    "observed_recovery": (
                        "Removing the entry restores an editable comparison without lost selections."
                    ),
                    "verdict": "pass",
                },
                "anti_slop_probe": {
                    "source_scan_reviewed": True,
                    "runtime_style_reviewed": True,
                    "screenshots_reviewed": True,
                    "violations": [],
                    "verdict": "pass",
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    execution_manifest = root / "execution-manifest.json"
    execution_manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_by": gate.hard_gate.EXECUTION_GENERATOR,
                "source_fingerprint": source_fingerprint,
                "runs": [
                    {
                        "command": "node verify-fixture.cjs",
                        "cwd": str(root),
                        "started_at": (
                            datetime.fromisoformat(live_bundle["completed_at"].replace("Z", "+00:00"))
                            + timedelta(seconds=2)
                        ).isoformat(),
                        "finished_at": (
                            datetime.fromisoformat(live_bundle["completed_at"].replace("Z", "+00:00"))
                            + timedelta(seconds=3)
                        ).isoformat(),
                        "exit_code": 0,
                        "log": str(build_log),
                        "log_sha256": sha256(build_log),
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    report["implementation_audit"] = {
        "project_root": str(root),
        "source_roots": [str(source)],
        "rendered_roots": [str(source)],
        "source_fingerprint": source_fingerprint,
        "live_audit_config": str(live_config),
        "capture_manifest": str(capture_manifest),
        "runtime_style_manifests": style_manifests,
        "control_manifests": control_manifests,
        "content_manifest": str(content_manifest),
    }
    report["visual_review"]["independent_review"]["review_artifact"] = str(
        review_artifact
    )
    report["measurements"]["execution_manifest"] = str(execution_manifest)
    report_path = root / "report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report, report_path


class ProgressiveDisclosureTests(unittest.TestCase):
    def test_generic_source_skills_are_not_bundled(self) -> None:
        skill_root = Path(__file__).resolve().parent.parent
        bundled = list((skill_root / "references").glob("original-*.md"))
        bundled.extend((skill_root / "references").glob("original-*.yaml"))
        self.assertEqual([], bundled)
        self.assertLessEqual(len((skill_root / "SKILL.md").read_text(encoding="utf-8")), 15_000)


class ProfileTests(unittest.TestCase):
    @staticmethod
    def standard_context() -> dict[str, str]:
        return {
            "target_user": "Operations analyst",
            "primary_task": "Review a failed import",
            "success_outcome": "Failure details are visible",
            "primary_cta": "Inspect failed import",
            "recovery": "Return to the import queue",
        }

    def verified_standard_report(self, root: Path) -> dict[str, object]:
        report = gate.profile_template("standard")
        report["completion_status"] = "VERIFIED_STANDARD"
        report["context"] = self.standard_context()
        for index, (viewport, state) in enumerate(
            (
                ("desktop", "start"),
                ("desktop", "terminal"),
                ("desktop", "focus"),
                ("mobile", "start"),
                ("mobile", "terminal"),
                ("mobile", "focus"),
            ),
            start=1,
        ):
            screenshot = root / f"{viewport}-{state}.png"
            make_png(screenshot, 320 + index, 180, index)
            report["evidence"][viewport][state] = {
                "artifact": str(screenshot),
                "observation": f"{viewport} {state} state visibly shows the import workflow",
            }
        report["checks"] = {key: True for key in report["checks"]}
        report["verification_dimensions"].update(
            {"render": "observed", "flow": "observed", "keyboard": "observed", "focus": "observed"}
        )
        report["interaction_cost"].update(
            {
                "required_decisions": 1,
                "actions_to_primary_success": 2,
                "default_selection_rationale": "No safe default exists for the import target.",
            }
        )
        report["runtime_checks"] = {
            viewport: {
                "inner_width": width,
                "scroll_width": width,
                "console_errors": 0,
                "console_warnings": 0,
                "primary_action_verified": True,
                "recovery_verified": True,
                "keyboard_path_verified": True,
                "focus_visible_verified": True,
                "focus_not_obscured_verified": True,
            }
            for viewport, width in (("desktop", 1440), ("mobile", 390))
        }
        return report

    def test_standard_template_is_default_and_lightweight(self) -> None:
        report = gate.profile_template("standard")
        self.assertEqual(5, report["schema_version"])
        self.assertEqual("standard", report["profile"])
        self.assertEqual("IMPLEMENTED_UNVERIFIED", report["completion_status"])
        self.assertNotIn("measurements", report)
        self.assertNotIn("visual_review", report)

    def test_verified_standard_requires_and_accepts_two_viewport_start_and_terminal_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-") as directory:
            root = Path(directory)
            report = self.verified_standard_report(root)
            self.assertEqual([], gate.validate(report, root / "report.json"))

    def test_verified_render_and_flow_are_distinct_levels(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-") as directory:
            root = Path(directory)
            report = self.verified_standard_report(root)
            report["completion_status"] = "VERIFIED_RENDER"
            report["evidence"] = {
                viewport: {"start": states["start"]}
                for viewport, states in report["evidence"].items()
            }
            report["verification_dimensions"].update(
                {"flow": "not_tested", "keyboard": "not_tested", "focus": "not_tested"}
            )
            self.assertEqual([], gate.validate(report, root / "report.json"))

            flow = self.verified_standard_report(root)
            flow["completion_status"] = "VERIFIED_FLOW"
            flow["evidence"] = {
                viewport: {key: states[key] for key in ("start", "terminal")}
                for viewport, states in flow["evidence"].items()
            }
            flow["verification_dimensions"].update(
                {"keyboard": "static_only", "focus": "static_only"}
            )
            self.assertEqual([], gate.validate(flow, root / "report.json"))

    def test_verified_standard_rejects_boolean_only_keyboard_claim(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-") as directory:
            root = Path(directory)
            report = self.verified_standard_report(root)
            report["verification_dimensions"]["keyboard"] = "static_only"
            report["runtime_checks"]["desktop"]["keyboard_path_verified"] = False
            errors = gate.validate(report, root / "report.json")
            self.assertIn("verification_dimensions.keyboard must be observed", errors)
            self.assertIn(
                "runtime_checks.desktop.keyboard_path_verified must be true for VERIFIED_STANDARD",
                errors,
            )

    def test_verified_standard_requires_distinct_focus_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-") as directory:
            root = Path(directory)
            report = self.verified_standard_report(root)
            report["evidence"]["mobile"]["focus"] = copy.deepcopy(
                report["evidence"]["desktop"]["focus"]
            )
            self.assertTrue(
                any("evidence artifacts must be distinct" in error for error in gate.validate(report, root / "report.json"))
            )

    def test_fabricated_friction_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-") as directory:
            root = Path(directory)
            report = gate.profile_template("standard")
            report["context"] = self.standard_context()
            report["interaction_cost"]["fabricated_friction"] = [
                "Disabled the primary CTA only to demonstrate an unselected state."
            ]
            self.assertIn(
                "FABRICATED_FRICTION: fabricated_friction must be empty",
                gate.validate(report, root / "report.json"),
            )

    def test_schema4_verified_standard_downgrades_to_flow(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-v4-") as directory:
            root = Path(directory)
            report = self.verified_standard_report(root)
            report["schema_version"] = 4
            report["completion_status"] = "VERIFIED_STANDARD"
            for viewport in ("desktop", "mobile"):
                report["evidence"][viewport].pop("focus", None)
            report.pop("verification_dimensions", None)
            report.pop("interaction_cost", None)
            for viewport in ("desktop", "mobile"):
                for field in (
                    "keyboard_path_verified",
                    "focus_visible_verified",
                    "focus_not_obscured_verified",
                ):
                    report["runtime_checks"][viewport].pop(field, None)
            report["checks"]["keyboard_focus_checked"] = True
            report_path = root / "report.json"
            write_json(report_path, report)
            completed = subprocess.run(
                [sys.executable, str(Path(gate.__file__)), "--report", str(report_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("COMPLETION_STATUS=VERIFIED_FLOW", completed.stdout)
            self.assertIn("SCHEMA_V4_DOWNGRADED_TO_VERIFIED_FLOW", completed.stdout)
            self.assertIn("GENSCAFF_STANDARD_REPORT_VALID", completed.stdout)
            self.assertNotIn("STRUCTURAL_EVIDENCE_INVARIANTS_VERIFIED", completed.stdout)

    def test_verified_standard_fails_without_browser_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-") as directory:
            root = Path(directory)
            report = gate.profile_template("standard")
            report["completion_status"] = "VERIFIED_STANDARD"
            report["context"] = self.standard_context()
            report["checks"] = {key: True for key in report["checks"]}
            report["runtime_checks"] = {
                viewport: {
                    "inner_width": width,
                    "scroll_width": width,
                    "console_errors": 0,
                    "console_warnings": 0,
                    "primary_action_verified": True,
                    "recovery_verified": True,
                    "keyboard_path_verified": True,
                    "focus_visible_verified": True,
                    "focus_not_obscured_verified": True,
                }
                for viewport, width in (("desktop", 1440), ("mobile", 390))
            }
            self.assertIn(
                "evidence.desktop.start.artifact is required",
                gate.validate(report, root / "report.json"),
            )

    def test_unverified_standard_passes_without_browser_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-") as directory:
            root = Path(directory)
            report = gate.profile_template("standard")
            report["context"] = self.standard_context()
            self.assertEqual([], gate.validate(report, root / "report.json"))

    def test_unverified_standard_cli_reports_browser_gap(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-") as directory:
            root = Path(directory)
            report_path = root / "report.json"
            report = gate.profile_template("standard")
            report["context"] = self.standard_context()
            write_json(report_path, report)
            completed = subprocess.run(
                [sys.executable, str(Path(gate.__file__)), "--report", str(report_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(0, completed.returncode)
            self.assertIn("COMPLETION_STATUS=IMPLEMENTED_UNVERIFIED", completed.stdout)
            self.assertIn("STANDARD_BROWSER_EVIDENCE_UNVERIFIED", completed.stdout)

    def test_verified_standard_rejects_horizontal_overflow(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-") as directory:
            root = Path(directory)
            report = self.verified_standard_report(root)
            report["runtime_checks"]["mobile"]["scroll_width"] = 391
            self.assertIn(
                "runtime_checks.mobile.scroll_width must not exceed inner_width",
                gate.validate(report, root / "report.json"),
            )

    def test_verified_standard_rejects_console_failures(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-standard-") as directory:
            root = Path(directory)
            report = self.verified_standard_report(root)
            report["runtime_checks"]["desktop"]["console_warnings"] = 1
            self.assertIn(
                "runtime_checks.desktop.console_warnings must be 0 for VERIFIED_STANDARD",
                gate.validate(report, root / "report.json"),
            )

    def test_strict_cli_refuses_active_browser_without_operator_flag(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-strict-cli-") as directory:
            root = Path(directory)
            report_path = root / "report.json"
            write_json(report_path, gate.profile_template("strict"))
            completed = subprocess.run(
                [sys.executable, str(Path(gate.__file__)), "--report", str(report_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("ACTIVE_BROWSER_AUDIT_SKIPPED_UNTRUSTED", completed.stdout)


class QualityGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory(prefix="quality-gate-test-")
        cls.fixture_root = Path(cls.temp_dir.name)
        build_valid_report(cls.fixture_root)
        cls.baseline_files = {}
        for path in cls.fixture_root.rglob("*"):
            if path.is_file():
                stat = path.stat()
                cls.baseline_files[path.relative_to(cls.fixture_root)] = (
                    path.read_bytes(),
                    stat.st_atime_ns,
                    stat.st_mtime_ns,
                )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def setUp(self) -> None:
        self.root = self.fixture_root
        baseline_paths = {self.root / relative for relative in self.baseline_files}
        for path in sorted(self.root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
            if path.is_file() and path not in baseline_paths:
                path.unlink()
            elif path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass
        for relative, (content, atime_ns, mtime_ns) in self.baseline_files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            os.utime(path, ns=(atime_ns, mtime_ns))
        self.report_path = self.root / "report.json"
        self.report = read_json(self.report_path)
        self.live_bundle = read_json(self.root / "live-evidence" / "live-audit-bundle.json")
        self.lighthouse_bundle = read_json(self.root / "lighthouse.json")

    def errors(self) -> list[str]:
        return gate.validate(
            self.report,
            self.report_path,
            _live_bundle_override=copy.deepcopy(self.live_bundle),
            _lighthouse_bundle_override=copy.deepcopy(self.lighthouse_bundle),
        )

    def errors_live(self) -> list[str]:
        return gate.validate(
            self.report,
            self.report_path,
            _lighthouse_bundle_override=copy.deepcopy(self.lighthouse_bundle),
        )

    def errors_with_command_execution(self) -> list[str]:
        return gate.validate(
            self.report,
            self.report_path,
            _live_bundle_override=copy.deepcopy(self.live_bundle),
            _lighthouse_bundle_override=copy.deepcopy(self.lighthouse_bundle),
            execute_approved_commands=True,
        )

    def assert_has_error(self, needle: str) -> None:
        errors = self.errors()
        self.assertTrue(
            any(needle in error for error in errors),
            f"Expected an error containing {needle!r}; got: {errors}",
        )

    def assert_has_live_error(self, needle: str) -> None:
        errors = self.errors_live()
        self.assertTrue(
            any(needle in error for error in errors),
            f"Expected a live error containing {needle!r}; got: {errors}",
        )

    def test_valid_evidence_report_passes(self) -> None:
        self.assertEqual([], self.errors())

    def test_schema3_cli_cannot_authorize_command_execution(self) -> None:
        write_json(self.report_path, self.report)
        completed = subprocess.run(
            [sys.executable, str(Path(gate.__file__)), "--report", str(self.report_path), "--allow-active-browser-audit", "--execute-approved-commands"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
        )
        self.assertEqual(1, completed.returncode)
        self.assertIn("legacy schema v3 cannot authorize command execution", completed.stdout)

    def test_catalog_evidence_reference_passes(self) -> None:
        self.report["evidence_catalog"] = {
            "desktop-primary": evidence(
                Path(self.report["visual_review"]["screenshots"]["desktop"])
            )
        }
        for item in self.report["requirement_trace"]:
            item["evidence"] = ["desktop-primary"]
        self.assertEqual([], self.errors())

    def test_unknown_catalog_evidence_reference_fails(self) -> None:
        self.report["requirement_trace"][0]["evidence"] = ["missing-evidence"]
        self.assert_has_error("Unknown evidence reference")

    def test_blank_template_fails(self) -> None:
        self.report = copy.deepcopy(gate.TEMPLATE)
        self.assert_has_error("context.product_name")

    def test_trivial_text_fails(self) -> None:
        self.report["context"]["product_name"] = "x"
        self.assert_has_error("context.product_name")

    def test_invalid_number_ranges_fail(self) -> None:
        self.report["visual_review"]["console_errors"] = -1
        self.report["visual_review"]["layout_issues_open"] = -9
        self.report["measurements"]["lighthouse"]["scores"]["performance"] = 999
        self.assert_has_error("visual_review.console_errors")
        self.assert_has_error("visual_review.layout_issues_open")
        self.assert_has_error("must be <= 100")

    def test_non_finite_score_fails(self) -> None:
        self.report["measurements"]["lighthouse"]["scores"]["performance"] = float("nan")
        self.assert_has_error("not finite")

    def test_duplicate_desktop_mobile_screenshot_fails(self) -> None:
        self.report["visual_review"]["screenshots"]["mobile"] = self.report["visual_review"][
            "screenshots"
        ]["desktop"]
        self.assert_has_error("Desktop and mobile screenshots must be different")

    def test_lighthouse_score_mismatch_fails(self) -> None:
        self.report["measurements"]["lighthouse"]["scores"]["performance"] = 91
        self.assert_has_error("does not match artifact score")

    def test_generic_primary_cta_fails(self) -> None:
        self.report["context"]["primary_cta"] = "Learn more"
        self.report["visual_target"]["primary_cta"] = "Learn more"
        self.report["action_trace"]["primary"]["label"] = "Learn more"
        self.report["action_trace"]["control_inventory"][0]["label"] = "Learn more"
        self.assert_has_error("weak information scent")

    def test_substitution_that_still_fits_fails(self) -> None:
        self.report["product_specificity"]["substitution_test"]["comparisons"][0][
            "still_fits"
        ] = True
        self.assert_has_error("still_fits must be false")

    def test_dead_end_control_fails(self) -> None:
        self.report["action_trace"]["dead_end_controls"] = ["Unimplemented pricing link"]
        self.assert_has_error("action_trace.dead_end_controls must be empty")

    def test_missing_required_state_evidence_fails(self) -> None:
        success = next(
            item for item in self.report["state_coverage"] if item["state"] == "success"
        )
        success["status"] = "not-applicable"
        success["evidence"] = []
        self.assert_has_error("state_coverage.success must be implemented")

    def test_target_created_after_review_fails(self) -> None:
        target = Path(self.report["visual_target"]["artifact"])
        latest = max(
            Path(item["screenshot"]).stat().st_mtime
            for item in self.report["visual_review"]["iteration_log"]
        )
        os.utime(target, (latest + 10, latest + 10))
        self.assert_has_error("must predate the first visual iteration screenshot")

    def test_missing_independent_review_fails(self) -> None:
        self.report["visual_review"]["independent_review"]["performed"] = False
        self.assert_has_error("independent_review.performed")

    def test_gradient_and_glass_source_fails_even_when_checks_are_true(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        source.write_text(
            "<style>.hero{background:linear-gradient(red,blue)}"
            ".glass{background:rgba(255,255,255,.4);backdrop-filter:blur(24px)}</style>",
            encoding="utf-8",
        )
        self.assertTrue(all(self.report["checks"].values()))
        self.assert_has_error("Forbidden gradient-function pattern")
        self.assert_has_error("Forbidden backdrop-filter pattern")

    def test_svg_gradient_and_blur_filter_fail(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        source.write_text(
            "<svg><defs><linearGradient id='g'/><filter><feGaussianBlur stdDeviation='8'/></filter>"
            "</defs></svg>",
            encoding="utf-8",
        )
        self.assert_has_error("Forbidden svg-gradient pattern")
        self.assert_has_error("Forbidden svg-blur pattern")

    def test_computed_style_gradient_fails(self) -> None:
        path = Path(self.report["implementation_audit"]["runtime_style_manifests"][0])
        manifest = read_json(path)
        manifest["gradient_matches"] = [
            {"selector": ".hero::before", "backgroundImage": "linear-gradient(red, blue)"}
        ]
        write_json(path, manifest)
        self.assert_has_error("gradient_matches must be an empty list")

    def test_obfuscated_runtime_gradient_is_caught_by_fresh_browser(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        content = source.read_text(encoding="utf-8")
        content = content.replace(
            "const save = document.querySelector('#save-model');",
            "document.body.style.backgroundImage = ['linear', 'gradient'].join('-') + '(red, blue)';\n"
            "    const save = document.querySelector('#save-model');",
        )
        source.write_text(content, encoding="utf-8")
        self.assert_has_live_error("prohibited computed_style")

    def test_inert_real_control_is_caught_by_fresh_browser(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        content = source.read_text(encoding="utf-8")
        content = content.replace(
            "document.querySelector(panel).hidden = false;",
            "if (panel !== '#cost-panel') document.querySelector(panel).hidden = false;",
        )
        source.write_text(content, encoding="utf-8")
        self.assert_has_live_error("control scenario failed: #show-cost")

    def test_expected_state_must_be_caused_by_the_control_action(self) -> None:
        for viewport in self.live_bundle["viewports"]:
            scenario = next(
                item
                for item in viewport["control_scenarios"]
                if item["selector"] == "#show-cost"
            )
            scenario["expected_selector_visible_before"] = True
        self.assert_has_error("expected selector did not transition for: #show-cost")

    def test_live_disabled_state_must_match_report_in_both_directions(self) -> None:
        for viewport in self.live_bundle["viewports"]:
            control = next(
                item for item in viewport["controls"] if item["selector"] == "#show-cost"
            )
            control["disabled"] = True
        self.assert_has_error("control is unexpectedly disabled: #show-cost")

    def test_declared_disabled_control_needs_no_action_scenario(self) -> None:
        report_control = next(
            item
            for item in self.report["action_trace"]["control_inventory"]
            if item["selector"] == "#show-cost"
        )
        report_control["behavior"] = "disabled"

        for manifest_value in self.report["implementation_audit"]["control_manifests"]:
            manifest_path = Path(manifest_value)
            manifest = read_json(manifest_path)
            manifest_control = next(
                item for item in manifest["controls"] if item["selector"] == "#show-cost"
            )
            manifest_control["behavior"] = "disabled"
            write_json(manifest_path, manifest)

        config_path = Path(self.report["implementation_audit"]["live_audit_config"])
        config = read_json(config_path)
        config["control_scenarios"] = [
            item for item in config["control_scenarios"] if item["selector"] != "#show-cost"
        ]
        write_json(config_path, config)
        config_digest = sha256(config_path)

        for viewport in self.live_bundle["viewports"]:
            control = next(
                item for item in viewport["controls"] if item["selector"] == "#show-cost"
            )
            control["disabled"] = True
            viewport["control_scenarios"] = [
                item
                for item in viewport["control_scenarios"]
                if item["selector"] != "#show-cost"
            ]
        self.live_bundle["config"]["sha256"] = config_digest

        lighthouse_path = Path(self.report["measurements"]["lighthouse"]["report"])
        lighthouse = read_json(lighthouse_path)
        lighthouse["_genscaff_provenance"]["config_sha256"] = config_digest
        write_json(lighthouse_path, lighthouse)
        self.lighthouse_bundle["_genscaff_provenance"]["config_sha256"] = config_digest

        self.assertEqual([], self.errors())

    def test_external_mutable_raster_resource_fails(self) -> None:
        payload = b"\x89PNG\r\n\x1a\n" + b"opaque-raster-payload" * 8
        for viewport in self.live_bundle["viewports"]:
            viewport["external_resources"].append(
                {
                    "url": "https://cdn.example.test/asset",
                    "first_party": False,
                    "status": 200,
                    "resource_type": "image",
                    "content_type": "application/octet-stream",
                    "sniffed_type": "image/png",
                    "body_error": "",
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "byte_length": len(payload),
                    "body": base64.b64encode(payload).decode("ascii"),
                    "encoding": "base64",
                    "body_truncated": False,
                    "scan_findings": [],
                    "data_uris": [],
                }
            )
        self.assert_has_error("uses an externally mutable raster resource")

    def test_unmanifested_live_claim_is_caught_by_fresh_browser(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        content = source.read_text(encoding="utf-8").replace(
            "<section class=\"workbench\"",
            "<p id=\"forged-proof\">Trusted by 10,000 teams with 99.99% uptime and SOC 2.</p>"
            "<section class=\"workbench\"",
        )
        source.write_text(content, encoding="utf-8")
        self.assert_has_live_error("visible claim inventory differs")

    def test_generic_replacement_is_caught_by_live_semantic_crosscheck(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        content = source.read_text(encoding="utf-8")
        replacements = {
            "Compare production language models": "Organize all work in one flexible workspace",
            "Review language-model context windows, token prices, modality support, and deployment availability before saving a workload-specific choice.": "Bring people, projects, and ideas together with a simple experience designed for every modern team.",
            "<strong>128K tokens</strong> for each selected model input.": "Shared views keep everyone aligned around the latest work.",
            "<strong>Input $5 per million tokens</strong>; output $15 per million tokens.": "Flexible options adapt as an organization grows and changes.",
            "API and managed hosting are available; private deployment requires review.": "Connected collaboration works wherever the team gets things done.",
            "choose a language model using context requirement, modality, token price, deployment availability, and workload filter. Saving adds the model and workload constraints to the persistent shortlist.": "choose the option that feels right for the team, then continue into a flexible shared workspace.",
        }
        for before, after in replacements.items():
            content = content.replace(before, after)
        source.write_text(content, encoding="utf-8")
        self.assert_has_live_error("domain selector text does not substantiate")

    def test_offscreen_product_signal_is_caught_by_fresh_browser(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        content = source.read_text(encoding="utf-8").replace(
            "</head>",
            "<style>#context-window{position:fixed!important;left:-10000px!important;top:0!important}</style></head>",
        )
        source.write_text(content, encoding="utf-8")
        self.assert_has_live_error("domain selector is visually concealed or trivial: #context-window")

    def test_transparent_decision_signal_is_caught_by_fresh_browser(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        content = source.read_text(encoding="utf-8").replace(
            "</head>",
            "<style>#decision-point{color:transparent!important}</style></head>",
        )
        source.write_text(content, encoding="utf-8")
        self.assert_has_live_error("decision selector is visually concealed or trivial")

    def test_fully_visible_clip_path_is_not_a_false_concealment(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        content = source.read_text(encoding="utf-8").replace(
            "</head>",
            "<style>#context-window{clip-path:inset(0)}</style></head>",
        )
        source.write_text(content, encoding="utf-8")
        errors = self.errors_live()
        self.assertFalse(
            any(
                "domain selector is visually concealed or trivial: #context-window" in error
                for error in errors
            ),
            errors,
        )

    def test_product_evidence_selectors_cannot_collapse_to_body(self) -> None:
        for signal in self.report["product_specificity"]["domain_signals"]:
            signal["selector"] = "body"
        self.assert_has_error("domain_signals selectors must be unique")
        self.assert_has_error("overbroad application container: body")

    def test_distinct_selectors_cannot_resolve_to_the_same_signal_element(self) -> None:
        for viewport in self.live_bundle["viewports"]:
            signals = viewport["domain_signals"]
            signals[1]["matches"][0]["element_identity"] = signals[0]["matches"][0][
                "element_identity"
            ]
        self.assert_has_error("selectors collapse onto the same DOM element")

    def test_hidden_audit_route_decoy_cannot_replace_default_index(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        decoy = self.root / "audit.html"
        decoy.write_bytes(source.read_bytes())
        config_path = Path(self.report["implementation_audit"]["live_audit_config"])
        config = read_json(config_path)
        config["entry_url"] = decoy.resolve().as_uri()
        write_json(config_path, config)
        self.assert_has_error("must be an existing rendered-root index.html")

    def test_nested_rendered_root_decoy_cannot_replace_project_index(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        decoy = self.root / "audit-surface" / "index.html"
        decoy.parent.mkdir()
        decoy.write_bytes(source.read_bytes())
        self.report["implementation_audit"]["rendered_roots"] = [str(decoy.parent)]
        config_path = Path(self.report["implementation_audit"]["live_audit_config"])
        config = read_json(config_path)
        config["entry_url"] = decoy.resolve().as_uri()
        write_json(config_path, config)
        self.assert_has_error("must use the canonical project index")

    def test_canonical_index_cannot_redirect_live_audit_to_nested_decoy(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        decoy = self.root / "audit-surface" / "index.html"
        decoy.parent.mkdir()
        decoy.write_bytes(source.read_bytes())
        source.write_text(
            "<!doctype html><html><head><meta http-equiv='refresh' content='0; url=audit-surface/index.html'></head>"
            "<body><p>Loading the default project surface.</p></body></html>",
            encoding="utf-8",
        )
        self.assert_has_live_error("start state redirected away from the canonical project index")

    def test_live_runner_executes_form_and_state_dependent_actions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-control-actions-") as directory:
            root = Path(directory)
            source = root / "index.html"
            source.write_text(
                """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Control action fixture</title><style>body{font:16px sans-serif;color:#171717;background:#f5f2ea}button,input,select{margin:8px;padding:8px}</style></head>
<body><main><h1>Configure deployment policy</h1>
<button id="start">Start policy review</button><p id="feedback" hidden>Policy review started.</p>
<label>Policy name <input id="policy-name"></label>
<label><input id="approval" type="checkbox"> Require approval</label>
<label>Region <select id="region"><option value="us">US</option><option value="eu">EU</option></select></label>
<section id="terminal" hidden><p>Policy review is ready.</p><button id="terminal-action">Confirm policy</button>
<p id="terminal-proof" hidden>Policy confirmed.</p><button id="recover">Reset policy review</button></section>
<p id="recovered" hidden>Policy review reset.</p></main>
<script>
const start=document.querySelector('#start'); const feedback=document.querySelector('#feedback'); const terminal=document.querySelector('#terminal');
start.addEventListener('click',()=>{feedback.hidden=false;setTimeout(()=>{terminal.hidden=false},25)});
document.querySelector('#terminal-action').addEventListener('click',()=>{document.querySelector('#terminal-proof').hidden=false});
document.querySelector('#recover').addEventListener('click',()=>{terminal.hidden=true;feedback.hidden=true;document.querySelector('#recovered').hidden=false});
</script></body></html>""",
                encoding="utf-8",
            )
            config_path = root / "config.json"
            write_json(
                config_path,
                {
                    "schema_version": 1,
                    "entry_url": source.resolve().as_uri(),
                    "source_fingerprint": "a" * 64,
                    "output_dir": str(root / "evidence"),
                    "viewports": [
                        {"name": "desktop", "width": 1100, "height": 760},
                        {"name": "mobile", "width": 390, "height": 760},
                    ],
                    "wait_for_selector": "#start",
                    "domain_signal_selectors": [],
                    "decision_selectors": [],
                    "primary_flow": {
                        "selector": "#start",
                        "feedback_selector": "#feedback",
                        "terminal_selector": "#terminal",
                        "recovery_selector": "#recover",
                        "recovered_selector": "#recovered",
                    },
                    "control_scenarios": [
                        {
                            "selector": "#policy-name",
                            "action": "fill",
                            "value": "restricted-production",
                            "expected_value": "restricted-production",
                        },
                        {
                            "selector": "#approval",
                            "action": "check",
                            "expected_checked": True,
                        },
                        {
                            "selector": "#region",
                            "action": "select",
                            "value": "eu",
                            "expected_value": "eu",
                        },
                        {
                            "selector": "#terminal-action",
                            "action": "click",
                            "setup": "primary-terminal",
                            "expected_selector": "#terminal-proof",
                        },
                    ],
                },
            )
            runner = Path(__file__).resolve().with_name("live_audit.js")
            completed = subprocess.run(
                ["node", str(runner), "--config", str(config_path)],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            bundle = json.loads(completed.stdout)
            for viewport in bundle["viewports"]:
                scenarios = {item["selector"]: item for item in viewport["control_scenarios"]}
                self.assertTrue(all(item["passed"] for item in scenarios.values()))
                self.assertTrue(scenarios["#policy-name"]["value_change"])
                self.assertTrue(scenarios["#approval"]["checked_change"])
                self.assertTrue(scenarios["#region"]["value_change"])
                self.assertEqual("primary-terminal", scenarios["#terminal-action"]["setup"])
                self.assertFalse(scenarios["#terminal-action"]["expected_selector_visible_before"])
                self.assertTrue(scenarios["#terminal-action"]["expected_selector_visible_after"])

    def test_scenario_dynamic_external_resource_is_captured(self) -> None:
        with tempfile.TemporaryDirectory(prefix="genscaff-external-action-") as directory:
            root = Path(directory)
            raster = root / "proof.png"
            make_png(raster, 24, 24, 3)
            payload = raster.read_bytes()

            class Handler(http.server.BaseHTTPRequestHandler):
                def do_GET(self) -> None:
                    if self.path != "/asset":
                        self.send_error(404)
                        return
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)

                def log_message(self, format: str, *args: object) -> None:
                    return

            server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                external_url = f"http://127.0.0.1:{server.server_port}/asset"
                source = root / "index.html"
                source.write_text(
                    f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>External resource fixture</title></head>
<body><h1>Review deployment evidence</h1><button id="start">Start review</button><p id="feedback" hidden>Review started.</p>
<button id="load-proof">Load deployment proof</button><button id="schedule-late">Schedule delayed proof</button><section id="terminal" hidden>Review complete.<button id="recover">Reset review</button></section><p id="recovered" hidden>Review reset.</p>
<script>document.querySelector('#start').onclick=()=>{{document.querySelector('#feedback').hidden=false;setTimeout(()=>document.querySelector('#terminal').hidden=false,20)}};
document.querySelector('#recover').onclick=()=>{{document.querySelector('#terminal').hidden=true;document.querySelector('#recovered').hidden=false}};
document.querySelector('#load-proof').onclick=()=>{{const result=document.createElement('p');result.id='proof-loaded';result.textContent='Deployment proof queued.';document.body.append(result);setTimeout(()=>{{const image=new Image();image.src={json.dumps(external_url)};image.alt='Deployment proof';document.body.append(image)}},500)}};
document.querySelector('#schedule-late').onclick=()=>{{const result=document.createElement('p');result.id='late-queued';result.textContent='Late proof queued.';document.body.append(result);setTimeout(()=>{{document.body.dataset.late='done'}},5000)}};</script></body></html>""",
                    encoding="utf-8",
                )
                config_path = root / "config.json"
                write_json(
                    config_path,
                    {
                        "schema_version": 1,
                        "entry_url": source.resolve().as_uri(),
                        "source_fingerprint": "b" * 64,
                        "output_dir": str(root / "evidence"),
                        "viewports": [
                            {"name": "desktop", "width": 1100, "height": 760},
                            {"name": "mobile", "width": 390, "height": 760},
                        ],
                        "wait_for_selector": "#start",
                        "domain_signal_selectors": [],
                        "decision_selectors": [],
                        "primary_flow": {
                            "selector": "#start",
                            "feedback_selector": "#feedback",
                            "terminal_selector": "#terminal",
                            "recovery_selector": "#recover",
                            "recovered_selector": "#recovered",
                        },
                        "control_scenarios": [
                            {
                                "selector": "#load-proof",
                                "action": "click",
                                "expected_selector": "#proof-loaded",
                            },
                            {
                                "selector": "#schedule-late",
                                "action": "click",
                                "expected_selector": "#late-queued",
                            }
                        ],
                    },
                )
                runner = Path(__file__).resolve().with_name("live_audit.js")
                completed = subprocess.run(
                    ["node", str(runner), "--config", str(config_path)],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=120,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                bundle = json.loads(completed.stdout)
                for viewport in bundle["viewports"]:
                    scenarios = {
                        item["selector"]: item for item in viewport["control_scenarios"]
                    }
                    self.assertTrue(scenarios["#load-proof"]["passed"])
                    self.assertFalse(scenarios["#load-proof"]["pending_action_async"])
                    self.assertFalse(scenarios["#schedule-late"]["passed"])
                    self.assertIn("unsettled timer", scenarios["#schedule-late"]["error"])
                    self.assertTrue(
                        any(item["url"] == external_url for item in viewport["external_resources"]),
                        viewport["external_resources"],
                    )
                    resource = next(
                        item for item in viewport["external_resources"] if item["url"] == external_url
                    )
                    self.assertEqual("application/octet-stream", resource["content_type"])
                    self.assertEqual("image/png", resource["sniffed_type"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

    def test_http_origin_redirect_has_inspectable_redirect_evidence(self) -> None:
        page = b"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Redirect fixture</title></head><body><h1>Review deployment route</h1><button id='start'>Start route review</button><p id='feedback' hidden>Route review started.</p><section id='terminal' hidden>Route review complete.<button id='recover'>Reset route review</button></section><p id='recovered' hidden>Route review reset.</p><script>start.onclick=()=>{feedback.hidden=false;setTimeout(()=>terminal.hidden=false,20)};recover.onclick=()=>{terminal.hidden=true;feedback.hidden=true;recovered.hidden=false}</script></body></html>"""

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path == "/":
                    self.send_response(302)
                    self.send_header("Location", "/app")
                    self.end_headers()
                    return
                if self.path == "/app":
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(page)))
                    self.end_headers()
                    self.wfile.write(page)
                    return
                self.send_error(404)

            def log_message(self, format: str, *args: object) -> None:
                return

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory(prefix="genscaff-http-redirect-") as directory:
                root = Path(directory)
                config_path = root / "config.json"
                write_json(
                    config_path,
                    {
                        "schema_version": 1,
                        "entry_url": f"http://127.0.0.1:{server.server_port}/",
                        "source_fingerprint": "c" * 64,
                        "output_dir": str(root / "evidence"),
                        "viewports": [
                            {"name": "desktop", "width": 1100, "height": 760},
                            {"name": "mobile", "width": 390, "height": 760},
                        ],
                        "wait_for_selector": "#start",
                        "domain_signal_selectors": [],
                        "decision_selectors": [],
                        "primary_flow": {
                            "selector": "#start",
                            "feedback_selector": "#feedback",
                            "terminal_selector": "#terminal",
                            "recovery_selector": "#recover",
                            "recovered_selector": "#recovered",
                        },
                        "control_scenarios": [],
                    },
                )
                runner = Path(__file__).resolve().with_name("live_audit.js")
                completed = subprocess.run(
                    ["node", str(runner), "--config", str(config_path)],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=120,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                bundle = json.loads(completed.stdout)
                for viewport in bundle["viewports"]:
                    redirects = [
                        item for item in viewport["first_party_resources"] if item["status"] == 302
                    ]
                    self.assertTrue(redirects)
                    self.assertTrue(all(item["redirect"] for item in redirects))
                    self.assertTrue(all(item["body_error"] == "" for item in redirects))
                    self.assertTrue(all(item["byte_length"] == 0 for item in redirects))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_synthetic_noise_capture_fails(self) -> None:
        desktop = Path(self.report["visual_review"]["screenshots"]["desktop"])
        decoded = gate.hard_gate.decode_png(desktop, str(desktop), [])
        assert decoded is not None
        make_noise_png(desktop, decoded["width"], decoded["height"])
        path = Path(self.report["implementation_audit"]["capture_manifest"])
        manifest = read_json(path)
        record = next(item for item in manifest["captures"] if Path(item["artifact"]) == desktop)
        record["sha256"] = sha256(desktop)
        write_json(path, manifest)
        self.assert_has_error("high-frequency noise")

    def test_truncated_png_header_fails_decode(self) -> None:
        desktop = Path(self.report["visual_review"]["screenshots"]["desktop"])
        desktop.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 600)
        self.assert_has_error("PNG")

    def test_minimal_hand_authored_lighthouse_json_fails(self) -> None:
        lighthouse = Path(self.report["measurements"]["lighthouse"]["report"])
        write_json(
            lighthouse,
            {
                "categories": {
                    "performance": {"score": 0.92},
                    "accessibility": {"score": 0.96},
                    "best-practices": {"score": 0.95},
                    "seo": {"score": 0.94},
                }
            },
        )
        self.assert_has_error("full audits map")

    def test_cosmetic_substitution_phrase_variants_fail(self) -> None:
        comparison = self.report["product_specificity"]["substitution_test"]["comparisons"][0]
        comparison["breaking_signals"] = [
            "Distinctive purple accent color treatment",
            "Branded logo and custom typography style",
        ]
        self.assert_has_error("relies on cosmetic identity")

    def test_substitution_domains_must_be_unrelated(self) -> None:
        comparison = self.report["product_specificity"]["substitution_test"]["comparisons"][0]
        comparison["alternate_product"] = "LLM model catalog"
        self.assert_has_error("not semantically distant")

    def test_substitution_requires_five_axis_breakdown(self) -> None:
        comparison = self.report["product_specificity"]["substitution_test"]["comparisons"][0]
        comparison["axes"].pop("failure_recovery")
        self.assert_has_error("axes must contain exactly")

    def test_generic_cta_prefix_suffix_variant_fails(self) -> None:
        self.report["context"]["primary_cta"] = "Get started now"
        self.report["visual_target"]["primary_cta"] = "Get started now"
        self.report["action_trace"]["primary"]["label"] = "Get started now"
        self.report["action_trace"]["control_inventory"][0]["label"] = "Get started now"
        self.assert_has_error("generic prefix")

    def test_primary_cta_must_name_product_object(self) -> None:
        self.report["context"]["primary_cta"] = "Finalize now"
        self.report["visual_target"]["primary_cta"] = "Finalize now"
        self.report["action_trace"]["primary"]["label"] = "Finalize now"
        self.report["action_trace"]["control_inventory"][0]["label"] = "Finalize now"
        self.assert_has_error("must name a product object or task outcome")

    def test_context_cta_control_must_be_primary_and_functional(self) -> None:
        control = self.report["action_trace"]["control_inventory"][0]
        control["role"] = "secondary"
        control["behavior"] = "disabled"
        self.assert_has_error("must itself be primary and functional")

    def test_control_inventory_must_match_browser_dom(self) -> None:
        path = Path(self.report["implementation_audit"]["control_manifests"][0])
        manifest = read_json(path)
        manifest["controls"].append(
            {
                "label": "Unreported pricing",
                "accessible_name": "Unreported pricing",
                "role": "navigation",
                "selector": "a.pricing",
                "behavior": "navigation",
                "href": "/pricing",
                "meaningful_change": True,
                "before_state_hash": "before",
                "after_state_hash": "after",
                "before_url": "/compare",
                "after_url": "/pricing",
                "expected_result": "Navigate to a detailed pricing information surface.",
                "observed_result": "The browser opens the detailed pricing information surface.",
                "recovery": "Use browser navigation to return to the comparison surface.",
            }
        )
        write_json(path, manifest)
        self.assert_has_error("must match action_trace.control_inventory exactly")

    def test_control_manifest_behavior_must_match_report(self) -> None:
        path = Path(self.report["implementation_audit"]["control_manifests"][0])
        manifest = read_json(path)
        control = next(item for item in manifest["controls"] if item["selector"] == "#show-cost")
        control["behavior"] = "disabled"
        write_json(path, manifest)
        self.assert_has_error("must match action_trace.control_inventory exactly")

    def test_dead_browser_control_fails(self) -> None:
        path = Path(self.report["implementation_audit"]["control_manifests"][0])
        manifest = read_json(path)
        manifest["dead_controls"] = ["a[href='#']"]
        write_json(path, manifest)
        self.assert_has_error("dead_controls must be an empty list")

    def test_placeholder_href_fails(self) -> None:
        path = Path(self.report["implementation_audit"]["control_manifests"][0])
        manifest = read_json(path)
        manifest["controls"][0]["href"] = "#"
        write_json(path, manifest)
        self.assert_has_error("Dead or placeholder href")

    def test_unverified_visible_claim_fails(self) -> None:
        path = Path(self.report["implementation_audit"]["content_manifest"])
        manifest = read_json(path)
        manifest["unverified_claims"] = [
            {"text": "Trusted by 10,000 teams", "selector": ".hero-proof"}
        ]
        write_json(path, manifest)
        self.assert_has_error("unverified_claims must be an empty list")

    def test_desktop_mobile_walkthrough_evidence_must_differ(self) -> None:
        desktop_checkpoints = self.report["task_walkthroughs"][0]["checkpoints"]
        self.report["task_walkthroughs"][1]["checkpoints"] = copy.deepcopy(desktop_checkpoints)
        self.assert_has_error("must use a mobile capture")

    def test_success_and_long_content_need_state_specific_evidence(self) -> None:
        success = next(item for item in self.report["state_coverage"] if item["state"] == "success")
        long_content = next(
            item for item in self.report["state_coverage"] if item["state"] == "long-content"
        )
        long_content["evidence"] = copy.deepcopy(success["evidence"])
        self.assert_has_error("state-specific decoded pixels")

    def test_task_traits_restrict_not_applicable_states(self) -> None:
        self.report["context"]["task_traits"] = ["async"]
        self.assert_has_error("require state_coverage.error to be implemented")
        self.assert_has_error("require state_coverage.loading to be implemented")

    def test_iteration_screenshots_must_be_chronological(self) -> None:
        path = Path(self.report["implementation_audit"]["capture_manifest"])
        manifest = read_json(path)
        first = next(item for item in manifest["captures"] if item["checkpoint"] == "visual-pass-1")
        second = next(item for item in manifest["captures"] if item["checkpoint"] == "visual-pass-2")
        first["captured_at"], second["captured_at"] = second["captured_at"], first["captured_at"]
        write_json(path, manifest)
        self.assert_has_error("strict chronological order")

    def test_iteration_metadata_only_difference_fails(self) -> None:
        pass_one = Path(self.report["visual_review"]["iteration_log"][0]["screenshot"])
        pass_two = Path(self.report["visual_review"]["iteration_log"][1]["screenshot"])
        pass_two.write_bytes(pass_one.read_bytes())
        path = Path(self.report["implementation_audit"]["capture_manifest"])
        manifest = read_json(path)
        second = next(item for item in manifest["captures"] if item["checkpoint"] == "visual-pass-2")
        second["sha256"] = sha256(pass_two)
        write_json(path, manifest)
        self.assert_has_error("identical decoded pixels")

    def test_iteration_change_must_resolve_finding(self) -> None:
        change = self.report["visual_review"]["iteration_log"][0]["changes"][0]
        change["resolves"] = ["unknown-finding"]
        self.assert_has_error("not linked to a resolving change")
        self.assert_has_error("resolve unknown finding ids")

    def test_independent_review_requires_separate_artifact(self) -> None:
        self.report["visual_review"]["independent_review"]["review_artifact"] = ""
        self.assert_has_error("review_artifact")

    def test_independent_review_cannot_self_certify(self) -> None:
        path = Path(self.report["visual_review"]["independent_review"]["review_artifact"])
        review = read_json(path)
        review["reviewer_id"] = review["implementer_id"]
        review["neutral_prompt"] += " The verdict should be pass."
        write_json(path, review)
        self.assert_has_error("distinct reviewer_id and implementer_id")
        self.assert_has_error("prompt is leading")

    def test_execution_commands_are_not_self_reported(self) -> None:
        path = Path(self.report["measurements"]["execution_manifest"])
        manifest = read_json(path)
        manifest["runs"] = []
        write_json(path, manifest)
        self.assert_has_error("must contain actual command records")

    def test_recorded_zero_exit_cannot_hide_failing_live_command(self) -> None:
        verifier = self.root / "verify-fixture.cjs"
        verifier.write_text("console.error('forced verifier failure'); process.exit(9);\n", encoding="utf-8")
        self.assertFalse(
            any("validator-owned re-execution" in error for error in self.errors()),
            "Repository commands must stay inert without explicit approval",
        )
        self.assertTrue(
            any(
                "validator-owned re-execution with exit code 9" in error
                for error in self.errors_with_command_execution()
            )
        )

    def test_visual_target_must_be_substantive(self) -> None:
        target = Path(self.report["visual_target"]["artifact"])
        target.write_text("looks good " * 80, encoding="utf-8")
        self.report["visual_target"]["created_at"] = datetime.fromtimestamp(
            target.stat().st_mtime, timezone.utc
        ).isoformat()
        self.assert_has_error("content-thin")

    def test_source_fingerprint_mismatch_fails(self) -> None:
        self.report["implementation_audit"]["source_fingerprint"] = "0" * 64
        self.assert_has_error("does not match the scanned source tree")

    def test_project_root_scan_prevents_source_omission(self) -> None:
        hidden = self.root / "hidden-gradient.tsx"
        hidden.write_text(
            "export const hidden = { background: 'radial-gradient(red, blue)' };",
            encoding="utf-8",
        )
        self.assertNotIn(str(hidden), self.report["implementation_audit"]["source_roots"])
        self.assert_has_error("Forbidden gradient-function pattern")

    def test_schema4_strict_allows_user_justified_gradient_location(self) -> None:
        hidden = self.root / "approved-gradient.tsx"
        hidden.write_text(
            "export const approved = { background: 'linear-gradient(red, blue)' };",
            encoding="utf-8",
        )
        self.report["schema_version"] = 4
        self.report["profile"] = "strict"
        self.report["visual_policy"] = {
            "mode": "preserve-user-project",
            "detected_effects": [
                {"kind": "gradient-function", "location": "approved-gradient.tsx"}
            ],
            "allowed_effects": [
                {
                    "kind": "gradient-function",
                    "location": "approved-gradient.tsx",
                    "source": "user",
                    "rationale": "The locked user reference explicitly requires this gradient.",
                }
            ],
        }
        self.report["execution_policy"] = {
            "mode": "none",
            "approved_commands": [],
            "active_browser": "approved",
        }
        errors = self.errors()
        self.assertFalse(
            any(
                "Forbidden gradient-function" in error and "approved-gradient.tsx" in error
                for error in errors
            ),
            errors,
        )

    def test_schema4_strict_rejects_unjustified_visual_effect(self) -> None:
        self.report["schema_version"] = 4
        self.report["profile"] = "strict"
        self.report["visual_policy"] = {
            "mode": "preserve-user-project",
            "detected_effects": [
                {"kind": "gradient-function", "location": "unexplained.css"}
            ],
            "allowed_effects": [],
        }
        self.report["execution_policy"] = {
            "mode": "none",
            "approved_commands": [],
            "active_browser": "approved",
        }
        self.assert_has_error("Strict visual effect lacks user/project justification")

    def test_generated_output_scan_prevents_dist_omission(self) -> None:
        generated = self.root / "dist" / "assets" / "app.js"
        generated.parent.mkdir(parents=True)
        generated.write_text(
            "document.body.style.backdropFilter = 'blur(18px)';",
            encoding="utf-8",
        )
        self.assertNotIn(str(generated), self.report["implementation_audit"]["source_roots"])
        self.assert_has_error("Forbidden backdrop-filter pattern")

    def test_percent_encoded_data_uri_svg_gradient_fails(self) -> None:
        source = Path(self.report["implementation_audit"]["source_roots"][0])
        source.write_text(
            "<img alt='forbidden' src=\"data:image/svg+xml,%3Csvg%3E%3Cdefs%3E"
            "%3ClinearGradient%20id='g'/%3E%3C/defs%3E%3C/svg%3E\">",
            encoding="utf-8",
        )
        self.assert_has_error("decoded data URI")

    def test_rendered_roots_are_mandatory(self) -> None:
        self.report["implementation_audit"]["rendered_roots"] = []
        self.assert_has_error("rendered_roots must contain")

    def test_project_wide_rendered_root_excludes_gate_artifacts_from_fingerprint(self) -> None:
        self.report["implementation_audit"]["rendered_roots"] = [str(self.root)]
        self.assertEqual([], self.errors())

    def test_legacy_boolean_only_report_fails(self) -> None:
        self.report = {"checks": {key: True for key in gate.REQUIRED_CHECKS}}
        self.assert_has_error("schema_version")


if __name__ == "__main__":
    unittest.main()
