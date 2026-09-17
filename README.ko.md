<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/brand/genscaff-logo-dark.png"><source media="(prefers-color-scheme: light)" srcset="docs/assets/brand/genscaff-logo-light.png"><img src="docs/assets/brand/genscaff-logo-light.png" alt="Genscaff" width="760"></picture></p>

# Genscaff

[English](README.md) | [한국어](README.ko.md)

Genscaff는 명시적으로 호출하는 근거 기반 프런트엔드 Codex 플러그인입니다. 가벼운 `$genscaff`는 Quick·Standard 생성을 안내하고, `$genscaff-release-audit`는 비용이 큰 Strict 배포 감사를 분리해서 수행합니다. 사용자 요구와 기존 디자인 시스템은 항상 Genscaff 휴리스틱보다 우선합니다.

이 프로젝트는 독립적인 커뮤니티 프로젝트이며 OpenAI와 제휴하거나 OpenAI의 보증을 받지 않습니다.

## GitHub marketplace에서 설치

```shell
codex plugin marketplace add gloz9102/genscaff --ref main
codex plugin add genscaff@genscaff-public
```

Codex를 다시 시작하거나 새 작업을 열어 주세요. 두 스킬 모두 암묵적으로 호출되지 않습니다.

```text
$genscaff                 # Standard: 일반적인 생성·개편
$genscaff quick           # Quick: 작은 로컬 변경
$genscaff-release-audit   # Strict: 배포 중요 전체 감사
$genscaff strict          # v2.1에서 종료, $genscaff-release-audit 사용
```

## 2.1.0 전환

레거시 소스 트리·ZIP과 `$genscaff strict` 호환 경로를 제거합니다. 종료된 호출에는 이전 방법만 안내하며 감사나 Standard 작업을 자동으로 시작하지 않습니다. 기존 보고서 스키마 호환성은 유지합니다. 소스 버전 변경은 릴리스 게시를 의미하지 않습니다.

## 유지되는 v2.0.1 로딩 계약

- 사용자에게 보이는 모든 비동기 경계에는 대기 제거 우선 로딩 계약을 적용합니다. 사용할 수 있는 맥락을 보존하고, 정직한 상태와 복구 수단을 제공하며, 스피너를 완료 근거로 대신하지 않고 관찰한 경계를 기록합니다.
- Standard·Strict 보고서는 불완전한 로딩 경계 기록을 거부합니다. Strict의 `async`·`generation` 작업은 로딩 경험을 선언하고 근거를 남겨야 합니다.

## 미배포 변경: 지침 중복 제거와 감사 구현 분리

Core는 제품·디자인 계약을 한 번 기록하고 상세 요구사항을 기존 reference로 안내하도록 정리했습니다. 일반 UI 디자인 지침 파일의 내용·강제 수준·적용 조건은 유지합니다. Strict 내부 구현은 책임별로 분리하며 CLI 진입점, 보고서 스키마와 검증 규칙은 유지합니다.

Windows 패치 쓰기는 앱에 포함된 CLI 0.155.0-alpha.2.6을 사용하여 workspace-write 격리를 유지한 상태로 복구했습니다. 크레딧 복구 후 수정 후보의 PR 16회와 브라우저 없는 조건 2회를 모두 완료했습니다. 블라인드·순서 교환 비교 8쌍과 사용자의 예약·송금 선호 판정을 반영한 결과는 수정판 6승·이전판 2승입니다. 이는 지침 준수를 포함한 선호이며 시각 품질 개선의 입증은 아닙니다. 두 대시보드 쌍 모두 390px에서 가로 넘침이 남아 전체 행동 채택 판정은 보류합니다. PR 실행 시간 중앙값은 줄었지만 입력 토큰 중앙값은 증가하여 비용 절감을 주장하지 않습니다. [v2.1 평가 기록](evals/v2.1-transition.md)에 최초 실패·재실행·모델 점수·사용자 선호·잔여 결함을 구분했습니다. 120회 릴리스 평가는 실행하지 않았습니다. [이전 중단 기록과 Strict 동등성 근거](evals/instruction-refactor.md)도 보존합니다.

## 미배포 변경: 디자인 탐색과 보존 검증

아래 흐름은 2.1.0 소스 버전에서도 유지합니다. 릴리스 게시는 별도 단계입니다.

- 방향이 열려 있는 신규 화면·대규모 개편은 같은 조건의 대표 화면 두 안을 비교하고 사용자가 선택하는 방식이 기본입니다. 사용자는 단일안 진행 또는 선택 위임을 지정할 수 있습니다. Quick, 잠금 재현, 구성이 확정된 기존 시스템 확장은 비교를 생략합니다.
- 필수 정보, 접근 가능한 이름, 의미 있는 순서와 동작 결과를 보존합니다. HTML이 같다는 사실만으로 보존을 판정하지 않으며, 레퍼런스 관찰을 구현 위치와 실제 화면 증거까지 연결합니다.
- 기존 미학 규칙은 변경하지 않습니다. 후보 비교와 선택안의 미학 검토 2회를 구분하며, 정보·기능·접근성·런타임 결함 수정 후에는 필요한 재검증을 수행합니다.

```text
$genscaff 새 예약 페이지를 만들어 주세요.                 # 기본: 대표 화면 두 안 비교
$genscaff 예약 페이지를 단일안으로 진행해 주세요.           # 비교 생략 선택
$genscaff 두 방향을 비교한 뒤 적합한 안을 대신 골라 주세요. # 선택 명시적 위임
```

명시적인 위임이 없으면 사용자의 선택을 받은 뒤 선택안을 확장합니다. 브라우저를 사용할 수 없어도 비교 가능한 두 방향의 설명과 가능한 소스 작업을 유지하고 미검증임을 표시합니다. 임의로 단일안을 선택하거나 화면 검증을 완료했다고 보고하지 않습니다.

상세 기준은 [탐색 절차](plugins/genscaff/skills/genscaff/references/design-exploration.md), [보존 계약](plugins/genscaff/skills/genscaff/references/visual-target-template.md), [레퍼런스 추적](plugins/genscaff/skills/genscaff/references/reference-intent.md)에서 확인할 수 있습니다. [평가 절차와 빠른 검증 결과](evals/design-preservation.md)는 실제 관찰과 미검증 요구사항을 구분합니다.

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

## 프로필

| 호출 | 범위 | 근거 |
|---|---|---|
| `$genscaff quick` | 작은 문구·컴포넌트·로컬 스타일 변경 | 영향 코드, 필요한 경우 viewport 하나 |
| `$genscaff` | 일반적인 생성·개편 | 데스크톱/모바일 렌더·흐름·콘솔·오버플로·키보드·초점 |
| `$genscaff-release-audit` | 신뢰한 배포 중요 프런트엔드 | 4단계 캡처, 전체 컨트롤, Lighthouse, provenance, 독립 리뷰 |

Genscaff는 그라디언트, 글래스, 블러, 글로우 자체를 금지하지 않습니다. 사용자, 잠긴 참고 자료, 프로젝트 시스템이 요구한 효과는 보존합니다. 작성 주체 탐지기, 독창성 인증서, 실제 사용자 검증의 대체재가 아닙니다.

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

## 동일 브리프 샘플

공개 샘플은 v2.1 이전의 결과입니다. 과거 사례로 보존하며 현재 지침의 성능 근거로 사용하지 않습니다.

서로 독립적인 `terra-medium` 에이전트 2개에 같은 상품 페이지 브리프를 제공했습니다. 적용 조건만 Genscaff Standard를 명시적으로 호출했습니다.

| Genscaff Standard | 대조군 |
|---|---|
| <img src="docs/assets/slowdrop-comparison/genscaff-with.png" alt="Genscaff Standard로 만든 상품 페이지" width="720"> | <img src="docs/assets/slowdrop-comparison/genscaff-without.png" alt="Genscaff 없이 만든 대조군 상품 페이지" width="720"> |

두 결과 모두 사용할 수 있는 수준이었습니다. 이 정성 비교 한 쌍만으로 우월성을 주장하지 않습니다. 자세한 내용은 [전체 비교 문서](docs/slowdrop-comparison.ko.md)에서 확인하실 수 있습니다. v2.0은 첫 점수화 Release 실행을 마케팅 주장이 아닌 기준선으로 사용합니다.

## 저장소 구조

```text
.agents/plugins/marketplace.json
plugins/genscaff/{.codex-plugin,assets,skills/{genscaff,genscaff-release-audit}}
evals/                   # 과제, rubric, 평가 절차, Git에 넣는 요약
tools/                   # 검증기, 재현 패키징, 평가 하네스
```

## 검증

코어 검증은 Python을 사용합니다. Strict는 bundled manifest에 선언된 Node version과 production dependency, Chrome 또는 Chromium을 추가로 사용하며 manifest를 runtime source of truth로 봅니다.

```shell
python tools/check_skill.py
python -m unittest discover -s tools -p "test_*.py"
python -m unittest discover -s plugins/genscaff/skills/genscaff/scripts -p "test_*.py"
npm ci --omit=dev --prefix plugins/genscaff/skills/genscaff-release-audit/scripts
npm audit --omit=dev --audit-level=moderate --prefix plugins/genscaff/skills/genscaff-release-audit/scripts
python plugins/genscaff/skills/genscaff-release-audit/scripts/test_quality_gate.py
python tools/package_skill.py
```

검증기는 저장소 명령을 기본적으로 재실행하지 않습니다. 정확한 명령을 검사하고 사용자가 저장소를 명시적으로 신뢰한 경우에만 `--execute-approved-commands`를 사용해 주세요. 활성 브라우저 감사는 페이지 JavaScript를 실행하고 외부 요청을 만들 수 있습니다.

## 평가 하네스

`prepare --baseline-skill <previous-core-skill>`을 사용하면 이전 스킬의 고정 사본과 현재 스킬을 비교합니다. 양쪽에 같은 프롬프트로 Genscaff를 명시적으로 호출하며, 옵션을 생략하면 기존 스킬 미사용 대조군을 유지합니다. 비대화형 실행은 양쪽에 디자인 선택을 위임합니다. 사용자 선택 경계, 원본 입력, 품질·비용 판정, 정적 사례와 실제 실행의 차이는 [평가 절차](evals/design-preservation.md)에 설명합니다.

```shell
python tools/eval_harness.py prepare --suite pr --model gpt-5.6-terra --reasoning medium --output eval-run
python tools/eval_harness.py run --run-dir eval-run
python tools/eval_harness.py blind --run-dir eval-run
python tools/eval_harness.py score --run-dir eval-run
python tools/eval_harness.py validate --run-dir eval-run
```

여러 CLI가 설치되어 있으면 `run --codex-bin <executable>`로 실행 파일을 지정할 수 있습니다. 하네스는 실제 실행 경로와 버전을 기록합니다. `--windows-sandbox elevated|unelevated`, `--jobs 1|2|4`는 실행별 설정이며 이어서 실행할 때 기존 정책을 유지합니다.

모델 실행은 로컬 Codex 인증, 분리된 Git 작업공간, `codex exec --ephemeral --ignore-user-config --ignore-rules --sandbox workspace-write`, JSONL trace 보존을 사용합니다. 실행 원본은 Git에 넣지 않고 릴리스 artifact로 보관하며 요약만 커밋합니다.

## 배포 패키지

`python tools/package_skill.py`는 재현 가능한 `genscaff-plugin.zip`, 버전별 평가 산출물과 SHA-256 파일을 생성합니다. 평가 파일명은 플러그인 manifest 버전을 따릅니다. `--kind plugin`은 플러그인 ZIP만, 기본값인 `--kind all`은 평가 산출물까지 생성합니다. `--kind legacy`는 지원하지 않습니다. 과거 평가 요약은 원래 버전 이름으로 보존합니다.

## 라이선스

프로젝트 소유 소스와 문서는 [Apache License 2.0](LICENSE)을 적용합니다. 서드파티 조건은 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), 취약점 신고와 실행 위험은 [SECURITY.md](SECURITY.md)에서 확인해 주세요.
