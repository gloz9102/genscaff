# 상세 사용 및 검증 기준

[English](workflow-details.md) | [한국어](workflow-details.ko.md) | [README](../README.ko.md)

디자인 선택, 보존, 작업 분류, 검증 근거와 실행 환경의 상세 기준을 설명합니다.

## 유지되는 흐름: 디자인 탐색과 보존 검증

아래 흐름은 v2.2.5에 포함됩니다.

- 방향이 열려 있는 신규 화면·대규모 개편은 같은 조건의 대표 화면 두 안을 비교하고 사용자가 선택하는 방식이 기본입니다. 사용자는 단일안 진행 또는 선택 위임을 지정할 수 있습니다. Quick, 잠금 재현, 구성이 확정된 기존 시스템 확장은 비교를 생략합니다.
- 필수 정보, 접근 가능한 이름, 의미 있는 순서와 동작 결과를 보존합니다. HTML이 같다는 사실만으로 보존을 판정하지 않으며, 레퍼런스 관찰을 구현 위치와 실제 화면 증거까지 연결합니다.
- 기존 미학 규칙은 변경하지 않습니다. 후보 비교와 선택안의 미학 검토 2회를 구분하며, 정보·기능·접근성·런타임 결함 수정 후에는 필요한 재검증을 수행합니다.

```text
$genscaff 새 예약 페이지를 만들어 주세요.                 # 기본: 대표 화면 두 안 비교
$genscaff 예약 페이지를 단일안으로 진행해 주세요.           # 비교 생략 선택
$genscaff 두 방향을 비교한 뒤 적합한 안을 대신 골라 주세요. # 선택 명시적 위임
```

명시적인 위임이 없으면 사용자의 선택을 받은 뒤 선택안을 확장합니다. 브라우저를 사용할 수 없어도 비교 가능한 두 방향의 설명과 가능한 소스 작업을 유지하고 미검증임을 표시합니다. 임의로 단일안을 선택하거나 화면 검증을 완료했다고 보고하지 않습니다.

상세 기준은 [탐색 절차](../plugins/genscaff/skills/genscaff/references/design-exploration.md), [보존 계약](../plugins/genscaff/skills/genscaff/references/visual-target-template.md), [레퍼런스 추적](../plugins/genscaff/skills/genscaff/references/reference-intent.md)에서 확인할 수 있습니다. [평가 절차와 빠른 검증 결과](../evals/design-preservation.md)는 실제 관찰과 미검증 요구사항을 구분합니다.

## 현재 프런트엔드 워크플로

- schema v6는 검증 `result`, `method`, `coverage`, 근거, 문제, 제한사항을 분리합니다.
- 새 보고서는 `IMPLEMENTED_UNVERIFIED`, `VERIFIED_RENDER`, `VERIFIED_PRIMARY_FLOW`, `VERIFIED_KEYBOARD_FLOW`, `VERIFIED_STANDARD_BASELINE`을 사용합니다. 근거 없는 boolean이나 `pass` 문자열로 상태를 올릴 수 없습니다.
- Standard는 broad 작업 전에 `project_mode`, 네 가지 reference mode, primary experience archetype 하나, 관련 surface type, change scope를 분류합니다.
- Product/Design contract가 제품, reference, content, visual system, engineering, 보존 결정을 다루며 해당되는 경우 탐색 기록을 포함합니다. 실패·취소·되돌리기·미완료·네트워크·transaction이 실제 의미가 있을 때만 recovery를 요구합니다.
- product editorial, marketplace discovery, media discovery, workflow application, content editorial, transaction용 craft 모듈 6개를 제공합니다.
- 유명 사이트 참고는 원리와 deliberate difference를 추출하며 logo, copy, asset, composition, navigation, geometry, interaction을 복제하지 않습니다.
- 상품·트랜잭션 craft는 검증용으로 지어낸 선택 단계와 비활성 CTA를 `FABRICATED_FRICTION`으로 거부합니다.
- Strict는 구형 AI-slop·브랜드 연구 문서를 연쇄 로드하지 않고 공통 workflow rubric을 사용합니다.
- 결정적 A/B 하네스는 PR 8개 과제의 쌍별 비교(16회) 또는 Release 120회 실행 계약을 유지합니다. 정적 행동 사례 30개에는 보존, 디자인 선택, 레퍼런스 추적, 결함 재검증이 포함되며 사례 정의 자체는 실행 결과가 아닙니다. 이전 스킬의 고정 사본을 대조군으로 지정해 변경 전후를 비교할 수 있습니다.
- 코어 스킬에는 Node, Playwright, Lighthouse 의존성이 없으며 해당 도구는 release-audit에만 포함됩니다.

release-audit는 schema v3·v4 Strict 보고서를 계속 지원합니다. 코어는 schema v5 Standard 보고서를 계속 읽습니다. legacy `VERIFIED_FLOW`는 최대 `VERIFIED_PRIMARY_FLOW`, `VERIFIED_STANDARD`는 근거 재검사 후 최대 `VERIFIED_KEYBOARD_FLOW`로 변환하며 새 보고서는 legacy 상태명을 내보내지 않습니다.

## 분류와 reference

Reference mode는 `locked-reproduction`, `structural-reference`, `aesthetic-inspiration`, `no-reference`입니다. 스크린샷을 제공했다는 이유만으로 자동 잠금하지 않습니다. 정확한 재현은 명시적인 lock 범위와 제공 asset 사용 권리가 필요합니다.

Experience archetype은 제품 과제를 설명합니다: `product-editorial`, `marketplace-discovery`, `media-discovery`, `workflow-application`, `content-editorial`, `transaction`. Surface type은 변경 화면을 설명하며 `landing`, `search`, `listing`, `detail`, `dashboard`, `form`, `checkout` 등이 있습니다.

```text
"Apple 제품 페이지의 명료함과 pacing 원리를 사용하되 layout, asset,
navigation, copy, typography, interaction은 복제하지 않는다."
→ aesthetic-inspiration / product-editorial / landing

"Airbnb 같은 성숙한 search, comparison, availability, trust 원리를
사용하되 branding과 component geometry는 복제하지 않는다."
→ aesthetic-inspiration / marketplace-discovery / search, listing

"Netflix 같은 content discovery 원리를 progress, missing media,
complete keyboard navigation에 적용하되 실제 제품은 복제하지 않는다."
→ aesthetic-inspiration / media-discovery / landing, listing
```

이 분류는 craft 방향을 잡을 뿐 사용자 요구나 기존 정보구조를 대체하지 않습니다.

## Runtime과 승인 모델

Chrome이 없으면 Standard의 browser evidence만 막히며 안전한 source 구현은 계속합니다. Lighthouse 부재는 해당 감사만 막습니다. Strict 전용 의존성이나 reviewer가 없으면 Strict는 incomplete입니다.

Read-only inspection, project command 실행, dependency 설치, active browser, network command, destructive operation은 별도 권한입니다. Workspace 수정·테스트 요청은 검사한 비파괴 lint/test/build를 허용할 수 있지만 install, deploy, migration, credential, network, cleanup까지 허용하지 않습니다. 검증 출력은 범위가 제한된 근거이며 WCAG 준수나 법적·독창성 인증이 아닙니다.
