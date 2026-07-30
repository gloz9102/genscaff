---
name: genscaff
description: "Full-source-compatible frontend generation and scaffolding with aggressive non-compensating product-specificity, action-continuity, evidence-provenance, accessibility, responsive, and anti-slop gates. Use to generate or analyze a webpage mockup, scaffold or polish browser UI, preserve locked specs, verify desktop/mobile behavior, reject generic or dead product surfaces, remove all gradients and glassmorphism, and run the bundled schema-v3 structural/live-browser evidence gate without treating it as authorship or originality proof."
---

# Genscaff

## 실행 기준과 우선순위

`genscaff`는 `image-to-web-impl`와 `frontend-quality-gate`의 축약본이 아니다. 두 원본의 전체 기능을 보존하고 더 엄격한 Genscaff 하드 게이트를 추가한다.

작업 전에 다음 원문을 처음부터 끝까지 읽는다.

1. `references/original-image-to-web-impl-skill.md`
2. `references/original-frontend-quality-gate-skill.md`
3. `references/aggressive-hard-gate.md`

원문 agent metadata도 보존한다.

- `references/original-image-to-web-impl-openai.yaml`
- `references/original-frontend-quality-gate-openai.yaml`

지침 우선순위는 다음과 같다.

1. 현재 사용자의 명시적 요구
2. 이 문서와 `references/aggressive-hard-gate.md`의 Genscaff 하드 게이트
3. 번들 원본 스킬과 나머지 reference

원본과 Genscaff 규칙이 충돌하면 더 엄격한 Genscaff 규칙을 따른다. 기술 점수, 시각 점수, 체크박스 평균으로 제품 특이성·행동 연속성·콘텐츠 무결성 실패를 상쇄하지 않는다.

## 필수 reference와 도구

`frontend-quality-gate` 실행 전 다음 파일을 모두 읽는다.

- `references/design-brief-expansion.md`
- `references/ui-craft-guidelines.md`
- `references/brand-visual-research.md`
- `references/design-signals.md`
- `references/ai-slop-research.md`
- `references/no-slop-checklist.md`
- `references/product-specificity-and-action-gate.md`
- `references/visual-target-template.md`
- `references/visual-comparison-protocol.md`
- `references/quality-report-schema.md`
- `references/aggressive-hard-gate.md`

검증 도구는 다음과 같다.

- `scripts/quality_gate.py`: schema v3 report를 검증하고, validator 소유 브라우저 실행을 새로 시작해 실제 구현과 자기신고 증거를 교차검사한다.
- `scripts/hard_gate.py`: 소스·PNG·manifest·제품·행동·독립 review 하드 게이트다.
- `scripts/runtime_probe.js`: 렌더된 DOM의 computed style, pseudo-element, SVG, canvas, 보이는 control을 수집한다.
- `scripts/live_audit.js`: validator가 직접 실행하는 브라우저 재검증기다. 실제 DOM, computed style, 제품 신호의 실질 가시성, control 활성화 전후 상태, 보이는 사실형 주장, 로드된 first-party·external 리소스와 decoded body type을 한 실행에서 수집한다.
- `scripts/lighthouse_audit.js`: validator가 저장된 점수를 믿지 않고 동일 `live_audit_config` URL을 새 Chrome에서 직접 측정하는 Lighthouse 실행기다. `file://` 입력은 loopback 임시 서버로만 노출한다.
- `scripts/test_quality_gate.py`: 정상 fixture와 적대적 PASS 우회를 검증하는 회귀 테스트다.

원문 지침의 `$frontend-quality-gate`, `references/...`, `scripts/...` 경로는 이 스킬 내부 리소스로 해석한다.

## 런타임 전제

- Python 3.10 이상이 필요하다. Python 스크립트는 표준 라이브러리만 사용한다.
- 브라우저 감사에는 Node.js 22.19 이상과 `scripts/package.json`의 고정 의존성이 필요하다. 설치되지 않았으면 preflight에서 중단하고 `npm install --omit=dev --prefix <skill-dir>/scripts`가 필요하다고 보고한다.
- Chrome 또는 Chromium이 필요하다. `live_audit_config.chrome_path`로 명시하거나 시스템 설치본 또는 Playwright Chromium을 사용한다.
- 중앙 관리형 Node 의존성을 사용할 때는 해당 `node_modules` 디렉터리를 `GENSCAFF_NODE_MODULES`로 지정할 수 있다. 사용자별 절대경로를 소스에 박지 않는다.
- 의존성이나 브라우저가 없으면 검증 완료를 선언하지 않는다.

## 입력 모드

- **목업 생성 모드**: 사용자가 이미지 생성을 명시하면 `original-image-to-web-impl-skill.md`의 목업 생성부터 실행한다.
- **첨부 이미지 모드**: 사용자가 이미지나 경로를 제공하면 제공 이미지를 잠긴 목업으로 보고 고정 요소 추출부터 실행한다.
- **이미지 없음 모드**: 사용자 프롬프트, 저장소 조사, 확장 디자인 브리프로 locked spec과 pre-code visual target을 만든다.

입력 방식이 결과 기준을 결정하는 데 필수인데 알 수 없을 때만 목업 생성, 첨부 이미지, 이미지 없음 중 하나를 질문한다.

## 절대 금지 시각 정책

최종 결과에서 다음을 전부 제거한다.

- CSS·SVG·canvas·WebGL·이미지의 linear/radial/conic gradient와 변형
- 그라디언트 텍스트, mesh, orb, blob, bokeh, light beam, neon glow
- `backdrop-filter`, backdrop blur, 반투명 glass surface, glass card
- SVG gradient와 Gaussian blur, Tailwind gradient·backdrop utility

기존 원본이 이를 허용하거나 잠긴 목업에 포함해도 Genscaff에서는 결함으로 기록하고 제거한다. 단색 surface, 단계형 색 구간, 패턴, 라벨, 선 종류, 명시적 scroll affordance로 대체한다. 이 정책을 WCAG나 AI 저작 여부 감별 기준으로 설명하지 않는다. Genscaff가 상투적 AI 장식을 억제하기 위해 채택한 하드 정책이라고 명시한다.

## 구현 전 계약

코딩 전에 다음을 작성하고 visual target에 봉인한다.

- 타깃 사용자, 근거가 있거나 가정으로 표시한 사용자 요구
- primary task, 시작 조건, observable success outcome, recovery
- 도메인 객체, 실제 데이터 형식과 단위, 상태 전이, 예외
- 최소 두 개의 비미용 differentiator
- 명확한 동사와 객체를 포함한 primary CTA
- 주요 UI 요소별 `요구 → 데이터/상태 → 행동 → 결과 → 출처` trace
- 두 개의 먼 대체 도메인과 5축 치환 실패 예상
- 데스크톱·모바일 행동 증거, computed style, control inventory, Lighthouse, 명령 실행 계획
- 실제 서비스되는 `rendered_roots`와 validator 소유 live-browser 재실행 설정. `dist`, `build`, `out` 같은 생성 결과를 숨기거나 source scan 제외 규칙에 기대지 않는다.
- gradient·glass·generic hero·동형 카드·가짜 지표 등 제거할 slop risk

새 작업이나 방향이 열린 작업은 구조적으로 다른 최소 두 방향을 비교한다. 색과 radius만 다른 변형은 다른 방향이 아니다. 첫 AI 시안을 그대로 다듬는 데 고착되지 않았는지 기록한다.

## 필수 실행 순서

1. 입력 모드를 결정한다.
2. 두 원본과 모든 필수 reference를 완전히 읽는다.
3. 기존 프로젝트의 연관 코드, 디자인 시스템, content model, route, 상태, control, token, 검증 명령을 조사한다.
4. dev server, browser capture, interaction walkthrough, validator-owned live audit, Lighthouse JSON, repo command, fresh reviewer 경로를 preflight한다. 필수 증거를 만들 수 없으면 완료를 약속하지 않는다.
5. 제품 계약과 requirement trace를 작성한다.
6. schema v3 report를 즉시 초기화한다.

```bash
python <skill-dir>/scripts/quality_gate.py --init <report.json>
```

7. 목업을 생성·분석하거나 pre-code visual target을 저장한다. 구현 전 생성 시간과 artifact를 기록한다.
8. materially different direction을 비교하고 제품 적합성으로 선택한다.
9. locked spec, 제품 계약, 기존 시스템에 맞춰 순차 구현한다. 모든 보이는 control은 functional, semantic disabled, 또는 명확히 disclosed prototype 중 하나여야 한다.
10. loading, empty, error, disabled, success, long-content와 responsive state를 구현한다. task trait가 요구하는 상태를 편하게 `not-applicable`로 빼지 않는다.
11. gradient·glass 정적 소스 패턴을 제거하고 소스 지문을 만든다. `source_roots`와 별도로 실제 브라우저가 받는 `rendered_roots`를 모두 기록한다. 생성물 root 내부의 `dist`, `build`, `out`, 번들 CSS·JS·SVG와 인코딩된 data URI도 검사 대상이다.

```bash
python <skill-dir>/scripts/quality_gate.py --fingerprint <source-root> [<source-root> ...]
```

12. 데스크톱과 모바일에서 primary task를 실제 실행한다. 각각 start, feedback, terminal, recovery PNG를 순서대로 캡처한다.
13. 두 viewport에서 `scripts/runtime_probe.js`를 실행한다. 모든 gradient, blur, glass, SVG 금지 항목을 구현에서 제거한 뒤 다시 probe한다. canvas·WebGL·래스터는 사람 눈으로 별도 검토한다.
14. DOM의 보이는 interactive control을 전수 테스트하고 report inventory와 일치시키며 dead control을 0개로 만든다. `click|fill|select|check|press`와 필요한 primary feedback/terminal setup을 선언하고, action이 URL·DOM·보이는 text·value·checked 상태를 실제로 바꿨는지 확인한다. screenshot만 달라진 것은 인정하지 않는다. disabled는 report와 semantic DOM이 양방향 일치해야 한다. 수치·고객·추천사·인증·integration·성능·사실형 데이터 후보도 전수 수집해 content manifest에서 출처 또는 데모 표시를 연결한다. 이 manifest들은 validator-owned live audit의 대체물이 아니라 교차검사 입력이다.
15. 렌더 결과로 두 도메인 5축 치환 테스트를 실행한다. 각 대체 도메인에서 최소 4축이 구조적으로 깨지지 않으면 재설계한다. 제품 신호와 결정 지점 selector는 서로 고유하고 실제 DOM node도 달라야 하며 `body`·`main`·`#app` 같은 container를 증거로 쓰지 않는다. viewport 교차, effective opacity, 실제 text pixel area·alpha, content visibility·`aria-hidden`, 실제 가림 비율까지 검사해 화면 밖이나 투명 layer에 token만 숨긴 증거를 거부한다.
16. 최소 두 번의 visual pass를 수행한다. 각 finding에 ID를 부여하고 change의 `resolves`로 연결하며, 서로 다른 실제 before/after 캡처를 남긴다.
17. fresh subagent에게 의도한 verdict를 숨기고 제품 식별, 비미용 신호, CTA 예측, 행동 연속성, 치환, 금지 패턴을 독립 검토시킨다. screen, flow, site, design-board에서 자기 review로 대체하지 않는다. raw review JSON을 보존한다. 로컬 JSON은 review 내용과 capture 교차검사 자료일 뿐 실제 fresh subagent 출처를 증명하지 못한다.
18. repository lint, typecheck, test, build와 실제 Lighthouse를 실행하고 원문 log·시간·hash를 execution manifest에 기록한다. 최종 validator가 allowlist 안의 repository 명령과 Lighthouse를 다시 실행하므로, 성공 값을 손으로 적거나 실행 불가능한 명령을 넣지 않는다.
19. quality report와 모든 schema v3 manifest를 완성한다.
20. validator를 실행한다. validator가 기존 manifest를 신뢰해 재사용하지 않고 새 브라우저 세션에서 배포 기본 route를 열어 데스크톱·모바일 실제 DOM, computed style와 pseudo-element, SVG·canvas 계측, 모든 보이는 control의 활성화 전후 URL·DOM·visible text·value·checked·피드백·복구, 보이는 claim 후보, 로드된 first-party와 external CSS·JS·SVG·data URI를 다시 수집한다. response MIME·확장자를 믿지 않고 body를 decode해 금지 패턴과 image magic bytes를 재검사한다. 숨긴 audit 전용 route와 외부 변경 가능 raster는 실패한다. 같은 config로 Lighthouse를 새로 측정하고, execution manifest의 allowlist 명령도 선언된 cwd에서 다시 실행한다. report·source fingerprint·capture/control/content manifest와 불일치하거나 `rendered_roots`가 빠지면 실패한다. `ERROR_COUNT=0`이 될 때까지 원인을 수정하고 증거를 다시 만든다.

```bash
python <skill-dir>/scripts/quality_gate.py --report <report.json> --max-errors 50
```

21. machine gate 성공 뒤 root agent가 실제 협업 mailbox에서 reviewer task 식별자, 구현자와 다른 agent, blind 요청 원문, 전달된 capture hash, raw 응답과 완료 상태를 직접 대조한다. report의 `reviewer_id`, 별도 JSON, `performed: true`만 보고 출처를 확인했다고 쓰지 않는다. mailbox 검증을 할 수 없으면 독립 review provenance는 `UNVERIFIED`이며 작업 전체를 완료로 보고하지 않는다.

## 공격적 실패 조건

다음 중 하나라도 해당하면 완료하지 않는다.

- 화면이 제품명·로고·색을 빼면 다른 SaaS에 그대로 들어맞는다.
- 두 대체 도메인 중 하나라도 5축의 3개 이상이 그대로 자연스럽다.
- primary CTA가 결과를 예측시키지 못하거나 start→feedback→terminal→recovery가 끊긴다.
- 보이는 control이 DOM inventory에서 빠졌거나, disabled 상태가 report와 실제 DOM에서 다르거나, action 전후 URL·DOM·visible text·value·checked 변화가 없다.
- project canonical index보다 하위의 검사용 별도 route가 config 또는 meta/JS redirect로 기본 화면을 대신하거나 외부 변경 가능 raster가 로컬 검토를 우회한다.
- action이 기대 상태만 먼저 표시하고 늦은 timer·network load를 남겨 실제 부작용 검사를 피하거나, 여러 제품 신호 selector가 같은 broad DOM node로 뭉개진다.
- validator가 새 브라우저 세션에서 구현을 직접 재실행하지 않았거나, 실제 DOM·computed style·control 활성화·visible claim·loaded resource 결과가 자기신고 manifest와 다르다.
- 실제 서비스되는 `rendered_roots`가 누락됐거나 generated/vendor ignore 규칙으로 `dist`, `build`, `out` 안의 배포 산출물을 건너뛴다.
- 같은 이미지가 상충하는 viewport, state, checkpoint를 증명한다.
- screenshot이 decode되지 않거나 고주파 노이즈·빈 이미지·metadata-only 복제다.
- gradient, glass, backdrop blur, glow, orb가 source 또는 runtime·raster review에서 발견된다.
- 사실형 수치, 고객, 추천사, 로고, 인증, 성과에 출처나 데모 표시가 없다.
- Lighthouse가 categories score만 손으로 적은 stub이거나 실행 log가 report 자기신고뿐이다.
- independent review 원문, reviewer 분리, blind prompt, capture hash가 없거나 root agent가 실제 협업 mailbox에서 출처를 확인하지 못했다.
- 기술 점수나 `checks=true`를 제품 품질 또는 “AI Slop 아님”의 증거로 사용한다.

## 완료 기준

- 두 원본 기능과 입력 모드별 locked-spec 절차가 누락 없이 실행됐다.
- 사용자 요구와 제품 계약이 구현·상태·행동·증거에 추적된다.
- 제품 특이성, 행동 연속성, 콘텐츠 무결성, anti-slop, 접근성, 반응형, visual fidelity, runtime integrity가 각각 검증됐다.
- 데스크톱·모바일 primary task와 recovery가 실제로 이어진다.
- gradient와 glassmorphism이 source, computed style, SVG·canvas·WebGL·래스터에서 0개다.
- validator-owned live audit가 데스크톱·모바일 실제 구현을 다시 실행했고 report·manifest·`rendered_roots`와 교차 일치한다.
- fresh subagent 독립 review가 raw artifact로 남아 있고 root agent가 실제 협업 mailbox에서 그 출처를 별도로 확인했다.
- schema v3 quality report가 machine gate 성공을 출력한다. 이 출력만으로 전체 완료나 독립 review provenance가 성립하지 않는다.
- 최종 보고는 실행한 명령, 주요 artifact, machine gate 결과, root-agent mailbox 검증 결과, 독립 review 내용, 알려진 검증 한계를 마크다운으로 전달한다.

`STRUCTURAL_EVIDENCE_INVARIANTS_VERIFIED`는 validator가 로컬 구조 증거와 live-browser 불변식을 재현했다는 뜻일 뿐이다. 로컬 review JSON의 작성 주체는 증명하지 못하므로 root-agent mailbox 검증 전에는 `REVIEW_PROVENANCE_UNVERIFIED`다. 두 상태를 합쳐 “AI Slop 아님”, AI 비사용, 인간 저작, 보편적 독창성, 실제 타깃 사용자의 성공, 공인된 품질 인증으로 과장하지 않는다.
