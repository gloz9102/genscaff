# Genscaff 공격적 하드 게이트

이 문서는 Genscaff Strict 프로필의 증거 계약이다. 이 게이트는 AI 제작 여부를 감별하지 않는다. 제품과 행동의 근거가 빈약한데도 형식만 채워 `PASS`하는 일을 막는다.

## 판정 원칙

다음 게이트는 서로 보상할 수 없다. 하나라도 `FAIL` 또는 `NOT TESTED`이면 전체 결과는 실패다.

| 게이트 | 필수 근거 |
|---|---|
| 요구 충실도 | 사용자·저장소·외부 근거·가정을 구분한 requirement trace |
| 제품 특이성 | 제품 계약, 도메인 객체, 결정과 결과, 5축 두 도메인 치환 테스트 |
| 행동 연속성 | DOM 컨트롤 전수 목록, 시작·피드백·종료·복구 캡처, 데스크톱·모바일 실행 기록 |
| 콘텐츠 무결성 | 사실형 주장·수치·로고·추천사·인증의 출처 또는 명확한 데모 표시 |
| Anti-slop 시각 정책 | 소스 정적 스캔, computed-style 스캔, SVG·canvas·래스터 사람 검토 |
| 접근성 | 자동 감사와 키보드·초점·상태 변화 수동 검증을 분리한 기록 |
| 반응형 행동 | 여러 폭의 배치뿐 아니라 같은 핵심 과업의 실제 실행 기록 |
| 시각 충실도 | 잠긴 목업 또는 pre-code visual target과의 구체적 차이 기록 |
| 런타임 무결성 | 콘솔·오버플로·실패 상태·명령 실행 원문 |

Lighthouse, 빌드, 반응형 스크린샷, 자동 접근성 점수는 기술 바닥선이다. 다른 게이트의 실패를 상쇄하지 못한다. `checks.* = true`는 판정 근거가 아니라 작성자 주장일 뿐이다.

판정 상태는 다음처럼 해석한다.

- `VERIFIED`: 직접 실행하고 관찰한 로컬 증거가 있다.
- `SUPPORTED`: 명시적 제품 자료는 있으나 실제 사용자 검증은 없다.
- `NOT TESTED`: 필요한 검증을 하지 않았다. `PASS`로 합치지 않는다.
- `FAIL`: 직접 실패했거나 필수 근거가 없다.

## 시각 효과 정책

사용자 요구와 기존 프로젝트 디자인 시스템이 Genscaff 취향보다 우선한다. 다음 효과는 무조건 결함이 아니지만, Strict에서는 소스, computed style, SVG, canvas, WebGL, 래스터 이미지, 데스크톱 또는 모바일 캡처에서 발견된 위치를 전부 기록한다.

- `linear-gradient`, `radial-gradient`, `conic-gradient`, repeating 변형, canvas gradient API
- 그라디언트 텍스트, Tailwind `bg-gradient-*`, `from-*`, `via-*`, `to-*`
- `backdrop-filter`, `-webkit-backdrop-filter`, `backdrop-blur-*`
- 반투명 surface와 blur·밝은 border·확산 shadow를 결합한 glass surface
- 컬러 orb, blob, 광원, bokeh, mesh, neon glow, 큰 확산형 shadow
- SVG `linearGradient`, `radialGradient`, `feGaussianBlur`
- 이미지 안에 구워 넣은 그라디언트 텍스트·빛 번짐·유리 카드

각 효과는 `visual_policy.detected_effects`에 `kind`와 `location`을 기록한다. 사용자 요구, 기존 프로젝트 토큰, 잠긴 reference 중 하나가 근거라면 `visual_policy.allowed_effects`에 동일한 `kind`·`location`과 `source`, 구체적 `rationale`을 기록한다. 일치하는 근거가 없는 장식 효과만 실패한다. 이는 WCAG가 금지한 기술이라는 주장이 아니며 AI 저작 여부도 증명하지 않는다.

Schema v3 `legacy-strict`는 하위 호환성을 위해 기존의 절대 금지 판정을 유지한다.

검사는 네 층을 모두 통과해야 한다.

1. `implementation_audit.project_root` 전체와 `source_roots`를 validator가 직접 재귀 스캔한다. 위반 파일을 source list에서 빼는 방식은 통하지 않는다.
2. `implementation_audit.rendered_roots`에 실제 서비스·배포되는 모든 결과 root를 별도로 기록한다. `dist`, `build`, `out` 자체가 rendered root이거나 그 아래에 있으면 generated/vendor ignore 규칙을 적용하지 않고 HTML·CSS·JS·SVG·shader·인코딩된 data URI까지 검사한다.
3. validator가 새 브라우저 세션을 소유하고 데스크톱·모바일 기본 route를 다시 연다. report가 제공한 결과를 신뢰하지 않고 실제 DOM·pseudo-element 포함 computed style·SVG·canvas 계측·보이는 control 활성화·visible claim·로드된 first-party와 external 리소스를 다시 수집한다.
4. 독립 reviewer가 SVG·canvas·WebGL·래스터와 전체 스크린샷을 사람 눈으로 확인하고, 허용 근거와 실제 사용 위치가 일치하는지 판단한다.

사전에 만든 `runtime_probe.js` 결과와 manifest는 live-browser 재실행의 입력 또는 대체 증거가 아니다. validator의 새 실행 결과와 일치하는지 확인하는 교차검사 대상이다. CSSOM이나 source 문자열에 나타나지 않는 런타임 스타일, 빌드 결과에만 남은 금지 표현, 퍼센트·base64 인코딩된 SVG/data URI, 동적으로 로드된 first-party CSS·JS·SVG도 loaded-resource 검사에 포함한다.

## 제품 특이성 반증

제품명, 로고, 색, 폰트, 아이콘, 분위기는 제품 특이성 신호로 세지 않는다. 각 주요 UI 요소는 다음 연결을 가져야 한다.

`UI 요소 → 사용자 요구 → 도메인 데이터 또는 상태 → 가능한 행동 → 결과 → 근거 출처`

두 도메인 치환 테스트는 표준화된 학술 척도가 아니라 재현 가능한 내부 반증 휴리스틱이다. 목표 제품 및 서로와 의미적으로 먼 두 도메인을 고르고, 각 도메인에 다음 5축을 모두 기록한다.

1. `information_architecture`
2. `data_schema`
3. `state_transitions`
4. `action_sequence`
5. `failure_recovery`

각 축은 `breaks`와 구체적 `reason`을 가진다. 각 대체 도메인에서 최소 4축이 구조적으로 깨져야 한다. 한 도메인에서 3축 이상이 그대로 자연스럽거나 두 도메인 모두에서 2축 이상이 통하면 실패다. `purple`, `logo`, `branding`, `font` 같은 미용 근거는 실패다.

제품 신호와 결정 지점 selector는 DOM에 존재하는 것만으로 부족하다. selector는 각 목록과 두 목록 전체에서 중복될 수 없고 `body`, `main`, `#app`, `#root` 같은 application container를 증거로 쓸 수 없다. 서로 다른 selector가 같은 실제 DOM node로 resolve되어도 실패다. viewport와 실제 교차하고, 부모 opacity까지 반영한 effective opacity, text range의 실제 pixel area, text color alpha, content-visibility, `aria-hidden`, `elementFromPoint` 기반 가림 비율을 통과해야 한다. 화면 밖 배치, 투명 글자, 0에 가까운 크기, 실제 clip, overlay 뒤 은닉으로 semantic token만 심으면 실패다. 단, `clip-path: inset(0)`처럼 실제 text를 자르지 않는 선언만으로 오탐시키지 않는다.

## 행동과 컨트롤 전수 검사

다음을 렌더된 DOM에서 전부 수집한다.

- `a[href]`, `button`, submit input, select, textarea
- `[role=button|link|tab|checkbox|radio|switch]`
- 키보드 접근 가능한 custom control

각 컨트롤은 표시 이름, accessible name, selector, role, disabled 상태, 기대 결과, 실제 URL 또는 상태 hash 변화, 피드백, 복구를 기록한다. `href="#"`, `javascript:void`, 콘솔 출력뿐인 동작, action 전후 URL·DOM·보이는 text·입력값·checked 상태 중 의미 있는 변화가 없는 컨트롤, inventory에서 빠진 보이는 컨트롤은 실패다. 포커스 outline 때문에 screenshot만 달라진 것은 동작 증거가 아니다. `disabled`는 report와 실제 DOM이 양방향으로 정확히 일치해야 하며 primary와 recovery control은 비활성일 수 없다.

주요 행동은 데스크톱과 모바일에서 각각 다음 네 캡처를 가져야 한다.

`primary-start → primary-feedback → primary-terminal → primary-recovery`

네 캡처는 서로 다른 PNG decoded pixels와 시간 순서를 가져야 한다. 초기 화면 한 장을 여러 상태에 돌려쓰거나 1픽셀·metadata만 바꿔 다른 증거처럼 꾸미면 실패다. `success`와 `long-content`도 서로 다른 상태 증거를 사용한다.

## Schema v3 증거 파일

모든 JSON은 로컬 파일이어야 한다. 임의로 결과를 적지 말고 브라우저 실행과 명령 원문에서 만든다. 다만 로컬 파일이라는 사실은 작성 주체나 실행 출처를 증명하지 않는다. manifest는 validator-owned live audit와 교차검사되기 전까지 자기신고 증거다.

### 소스 지문

```bash
python <skill-dir>/scripts/quality_gate.py --fingerprint <source-root> [<source-root> ...]
```

출력된 `SOURCE_FINGERPRINT`를 report와 모든 manifest에 동일하게 기록한다. 구현이 바뀌면 지문과 이후 증거를 다시 생성한다. `source_roots` 지문과 별개로 `rendered_roots` 및 브라우저가 실제로 로드한 first-party·external resource hash를 보존하며, report가 가리키지 않은 배포 산출물이나 외부 visual payload도 숨길 수 없어야 한다.

### Validator-owned live browser audit

`implementation_audit.live_audit_config`는 validator가 직접 새 브라우저 세션을 시작할 수 있는 기본 URL, desktop/mobile viewport, primary control, feedback·terminal·recovery 관찰 조건, 제품 신호와 결정 지점 selector를 제공한다. 파일 URL은 선언된 `rendered_root` 바로 아래이면서 canonical project `index.html`/`index.htm`이어야 한다. `project_root` 직속 index가 있으면 어떤 하위 index보다 우선하며, 직속 index가 없으면 가장 얕은 index가 정확히 하나여야 한다. 캡처된 start URL과 top frame도 계속 canonical file이어야 하므로 meta/JS redirect로 하위 audit 전용 화면을 열 수 없다. HTTP(S)는 credential·query·fragment 없는 origin root 요청이어야 하며 정상 3xx는 status·location·빈 body 증거로 보존한다. primary와 recovery 및 report·DOM 양쪽에서 확인된 semantic disabled control 외의 모든 control은 `control_scenarios`에서 fresh context로 실행한다. scenario는 `click|fill|select|check|press`, `default|primary-feedback|primary-terminal` setup, 기대 selector·URL·value·checked 중 하나 이상을 선언한다. selector·URL·값·checked 상태는 action 전에는 기대값이 아니고 action 후에 기대값이 되어야 한다. 기대 상태 직후에도 최소 관찰 시간, network idle, response drain을 거치며 action이 만든 timeout·interval·animation task가 남으면 실패한다. 기존 live-audit 결과 JSON 경로를 “검증 완료” 입력으로 받지 않는다.

validator는 한 실행에서 최소 다음 원시 사실을 직접 수집하고 report·manifest와 교차검사한다.

- browser version, 기본 URL, viewport, source fingerprint, DOM hash, visible-text hash, screenshot decoded-pixel hash
- 실제 DOM과 `::before`·`::after`의 computed `background-image`, `mask-image`, `border-image-source`, `list-style-image`, `content`, `filter`, `backdrop-filter`, opacity·border·shadow 조합
- SVG gradient·blur와 페이지 초기화 전에 계측한 canvas gradient API 호출
- 렌더된 모든 보이는 interactive control의 안정 selector·accessible name·role·disabled 상태
- 각 non-disabled control을 깨끗한 상태 또는 명시한 primary feedback/terminal setup에서 활성화한 뒤의 URL, DOM·visible-text hash, form value·checked 상태, status/feedback, terminal state, recovery, console/page/network error. screenshot hash 단독 변화는 인과적 행동 증거로 인정하지 않는다.
- 실제 보이는 수치·고객·추천사·인증·integration·성능·사실형 데이터 claim 후보
- 로드된 first-party와 external HTML·CSS·JS·SVG·이미지·data URI의 URL, origin 분류, browser resource type, declared content type, decoded body, byte hash와 금지 패턴 검사 결과. MIME과 확장자를 믿지 않고 PNG/JPEG/GIF/WebP/AVIF/BMP magic bytes와 SVG payload를 다시 판별한다. 외부의 변경 가능하거나 판별 불가능한 raster 이미지는 로컬 고정·검토하지 않으면 실패한다.

실행 중 발견한 control이나 claim이 report inventory에 없거나, report 항목이 실제 DOM에 없거나, primary flow의 상태 순서가 재현되지 않으면 실패다. live audit 자체가 생성한 run ID·runner hash·config hash·browser version·resource hash 없이 수동 JSON만 추가해 통과시킬 수 없다.

### Capture manifest

`implementation_audit.capture_manifest`는 다음 top-level 필드를 가진다.

```json
{
  "schema_version": 1,
  "generated_by": "genscaff-browser-capture-v1",
  "source_fingerprint": "sha256",
  "captures": []
}
```

각 capture는 `artifact`, `sha256`, `width`, `height`, `viewport`, `route`, `state`, `checkpoint`, `captured_at`을 가진다. report의 모든 PNG는 manifest에 있어야 한다. PNG는 전체 chunk CRC와 IDAT decode를 통과해야 하며, 고주파 노이즈·빈 이미지·동일 decoded pixels는 거부된다.

### Runtime style manifest

데스크톱과 모바일 JSON을 각각 저장한다.

```json
{
  "schema_version": 1,
  "generated_by": "genscaff-computed-style-audit-v1",
  "source_fingerprint": "sha256",
  "viewport": "desktop",
  "captured_at": "ISO-8601",
  "url": "http://...",
  "scanned_elements": 1,
  "pseudo_elements_checked": true,
  "canvas_and_svg_checked": true,
  "canvas_elements_reviewed": true,
  "gradient_matches": [],
  "backdrop_blur_matches": [],
  "glass_surface_matches": [],
  "blur_or_glow_matches": [],
  "svg_gradient_or_blur_matches": [],
  "raster_visual_findings": []
}
```

`runtime_probe.js`가 `canvas_elements_reviewed: false`를 반환하면 canvas 결과를 독립적으로 시각 검토한다. 발견 항목을 지우지 말고 제거하거나 `visual_policy`의 근거 있는 허용 항목과 연결한 뒤 probe를 다시 실행한다.

### Control manifest

데스크톱과 모바일 JSON을 각각 저장한다. top level은 `generated_by: genscaff-control-audit-v1`, 소스 지문, viewport, capture time, `all_visible_controls_tested`, `dead_controls`, `unreported_controls`, `controls`를 가진다.

각 control은 최소 `label`, `accessible_name`, `role`, `selector`, `behavior`, `href`, `meaningful_change`, `before_state_hash`, `after_state_hash`, `before_url`, `after_url`, `expected_result`, `observed_result`, `recovery`를 가진다. report의 `control_inventory`와 정확히 일치해야 한다.

### Content manifest

`implementation_audit.content_manifest`는 `generated_by: genscaff-content-audit-v1`, 소스 지문, capture time, `inventory_complete`, `visible_claims`, `unverified_claims`를 가진다. `runtime_probe.js`와 validator-owned live audit의 claim candidate부터 시작해 수치, 고객, 추천사, 인증, 수상, integration, 성능 주장, 실제처럼 보이는 도메인 데이터를 전수 분류한다.

각 claim은 text, selector, claim type, source type, source, capture hash를 기록한다. 저장소 근거는 실제 로컬 파일, 외부 근거는 URL, fixture는 화면에 보이는 데모 표시를 가져야 한다. `unverified_claims`는 0개여야 한다.

### Independent review artifact

screen, flow, site, design-board의 독립 review는 fresh subagent가 수행한다. 슬롯이 없으면 완료를 선언하지 않는다. reviewer에게 의도한 verdict를 알려주지 않는다.

원문 JSON은 `generated_by: genscaff-independent-review-v1`, 서로 다른 `reviewer_id`와 `implementer_id`, blind prompt 원문, 소스 지문, 최소 네 capture hash, 완료 시간, `identity_probe`, `action_probe`, `anti_slop_probe`를 가진다. 구현자 자기평가, 판정을 유도하는 prompt, report 안의 `reviewer: subagent` 문자열만으로는 통과하지 못한다. 이 review는 사람 대상 사용성 테스트가 아니다.

validator는 JSON shape, capture hash, source fingerprint, 응답 내용과 report의 일치만 검사할 수 있다. 로컬 JSON은 누구나 작성·복사할 수 있으므로 fresh subagent가 실제로 수행했다는 provenance를 증명하지 못한다. machine gate 성공 후 root agent가 실제 협업 mailbox에서 task 식별자, 구현자와 다른 agent, blind 요청 원문, 전달한 capture hash, raw 응답, 완료 상태를 직접 대조한다. mailbox 접근이나 대조가 불가능하면 `REVIEW_PROVENANCE_UNVERIFIED`로 남기며 전체 완료로 합치지 않는다.

### Lighthouse와 명령 실행

Lighthouse artifact는 score 네 개만 손으로 적은 JSON이 아니라 `lighthouseVersion`, `fetchTime`, `finalUrl`, `userAgent`, `environment`, `configSettings`, 100개 이상의 전체 audit map, 표준 audit ID, category `auditRefs`, `timing`, `runWarnings`, gate-owned runner/config hash를 포함해야 한다. validator는 `scripts/lighthouse_audit.js`로 같은 `live_audit_config` URL을 새 Chrome에서 다시 측정하고 저장 artifact와 점수·구조·provenance를 대조한다.

`measurements.execution_manifest`는 `generated_by: genscaff-command-runner-v1`, 소스 지문, 실제 command별 `cwd`, 시작·종료 시간, exit code, log path, log SHA-256을 가진다. report에 적은 command와 정확히 일치해야 하며 validator가 shell metacharacter 없는 allowlist 명령을 프로젝트 root 안의 cwd에서 직접 다시 실행한다. 저장된 `exit_code: 0`은 재실행 성공을 대신하지 못한다.

## 독립 reviewer 질문

구현 의도와 정답을 숨기고 다음을 묻는다.

1. 이름·로고·accent를 무시했을 때 무슨 제품이며 사용자는 어떤 일을 끝낼 수 있는가?
2. 미용 요소가 아닌 도메인 신호 세 개는 무엇인가?
3. 주요 CTA의 결과를 누르기 전에 예측할 수 있는가?
4. 시작부터 피드백, 종료, 복구까지 실제로 이어지는가?
5. 두 먼 도메인으로 치환했을 때 5축 중 무엇이 구조적으로 깨지는가?
6. gradient, glass, orb, glow, generic hero, 동일 카드 반복 중 사용자·프로젝트 근거 없이 남은 것이 있는가?

## 판정 문구의 한계

판정은 의도적으로 둘로 분리한다.

1. `STRUCTURAL_EVIDENCE_INVARIANTS_VERIFIED`: validator-owned live browser 재실행을 포함한 로컬 구조 증거와 불변식이 재현됐다. 이 상태명에는 무제한적 `PASS` 의미가 없다.
2. `REVIEW_PROVENANCE_VERIFIED_BY_ROOT_AGENT` 또는 `REVIEW_PROVENANCE_UNVERIFIED`: root agent가 실제 협업 mailbox에서 독립 review 출처를 확인했는지 나타낸다. validator는 첫 상태만 판정하며 두 번째 상태를 스스로 `VERIFIED`로 만들 수 없다.

첫 상태만으로 전체 완료나 품질 인증을 선언하지 않는다. 두 상태가 모두 충족돼도 AI 비사용, 인간 저작, 보편적 독창성, 실제 타깃 사용자의 성공, 공인된 “non-slop 인증”을 뜻하지 않는다. 허용되는 표현은 “정의된 Genscaff 구조·live-browser 불변식을 통과했고 root agent가 독립 review 출처를 확인했다”처럼 검사 범위를 정확히 한정한 문장이다.

## 웹 근거와 한계

- [Microsoft Research의 web vibe coding 획일화 연구](https://www.microsoft.com/en-us/research/publication/interrogating-design-homogenization-in-web-vibe-coding/)는 모호한 의도를 확률적 기본값으로 채울 때 평균적 미학으로 수렴할 위험과 구현 전 의도 확인의 필요성을 설명한다. 위험 분석이지 universal detector는 아니다.
- [CHI 2024 디자인 고착 연구](https://doi.org/10.1145/3613904.3642919)와 [C&C 2024 아이디어 획일화 연구](https://doi.org/10.1145/3635636.3656204)는 생성 도구가 초기 예시 고착과 아이디어 유사성을 키울 수 있음을 보고한다. 웹 UI 완성도를 직접 판정하는 연구는 아니다.
- [W3C 접근성 평가 도구 선택 지침](https://www.w3.org/WAI/test-evaluate/tools/selecting/)은 자동 도구만으로 접근성을 판정할 수 없고 오류나 오해 가능성이 있음을 명시한다.
- [Chrome Lighthouse 접근성 점수 설명](https://developer.chrome.com/docs/lighthouse/accessibility/scoring)은 수동 audit가 점수에 포함되지 않음을 설명한다.
- [GOV.UK 사용자 요구](https://www.gov.uk/service-manual/service-standard/point-1-understand-user-needs), [전체 문제 해결](https://www.gov.uk/service-manual/service-standard/point-2-solve-a-whole-problem), [단순한 서비스](https://www.gov.uk/service-manual/service-standard/point-4-make-the-service-simple-to-use)는 기술이 아니라 사용자 과업과 전체 여정을 기준으로 설계·검증할 것을 요구한다.
- [W3C link purpose](https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html), [GOV.UK button](https://design-system.service.gov.uk/components/button/), [confirmation page](https://design-system.service.gov.uk/patterns/confirmation-pages/)는 label, 목적, 결과, 완료 상태의 연속성을 뒷받침한다.
- [Apple Materials](https://developer.apple.com/design/human-interface-guidelines/materials)와 [Microsoft Acrylic](https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic)은 glass 계열 효과의 제한적 플랫폼 용도와 대비 위험을 함께 설명한다. glass가 본질적으로 나쁘다는 근거는 아니다.
- [Slopless](https://www.slopless.design/)와 [Impeccable Slop Catalog](https://impeccable.style/slop/)는 gradient, glass card, glow, 동일 카드 그리드를 생성 UI 상투 표현으로 분류하는 실무자 자료다. 동료심사된 타당도 연구가 아니므로 Genscaff는 이를 감별기가 아니라 명시적 금지 정책의 실무 배경으로만 사용한다.
