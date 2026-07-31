<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/brand/genscaff-logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/brand/genscaff-logo-light.png">
    <img src="docs/assets/brand/genscaff-logo-light.png" alt="Genscaff" width="760">
  </picture>
</p>

# Genscaff

[English](README.md) | [한국어](README.ko.md)

Genscaff는 브라우저에서 렌더링되는 프런트엔드를 만들고 검토하기 위한 근거 기반 Codex 스킬입니다. 사용자와 프로젝트의 디자인 의도를 보존하면서 작업 규모에 맞는 수준으로 제품 고유성, 동작 연속성, 반응형 동작, 접근성 기본 사항, 런타임 무결성을 확인합니다.

이 프로젝트는 독립적인 커뮤니티 프로젝트이며 OpenAI와 제휴하거나 OpenAI의 보증을 받지 않습니다.

## 동일 브리프 비교

서로 독립적인 `terra-medium` 에이전트 2개에 같은 한국어 물류 대시보드 브리프와 구현 제약을 제공했습니다. 한쪽은 Genscaff Standard를 사용했고, 다른 쪽은 Genscaff를 읽거나 사용하지 않도록 분리했습니다.

| Genscaff Standard 적용 | Genscaff 미적용 |
|---|---|
| <img src="docs/assets/comparison/genscaff-with.png" alt="Genscaff Standard로 만든 작업 중심 물류 대시보드" width="720"> | <img src="docs/assets/comparison/genscaff-without.png" alt="Genscaff 없이 만든 일반적인 물류 대시보드" width="720"> |

이 샘플에서 Genscaff 적용 결과는 위험 건 선택부터 조치까지의 흐름이 더 직접적이었고 별도 검증 산출물을 생성했습니다. 미적용 결과는 KPI와 사이드바 중심의 완성도 높은 일반 대시보드를 만들었습니다. 두 결과 모두 반응형이었고 요청·취소 상호작용이 동작했으며 확인한 흐름에서 콘솔 오류와 경고가 없었습니다.

단일 정성 A/B 샘플이므로 모든 미적용 실행보다 우수하다는 증거는 아닙니다. 브리프, 통제 조건, 데스크톱·모바일·완료 상태 캡처, 관찰 결과와 한계는 [상세 비교 문서](docs/comparison.ko.md)에서 확인하실 수 있습니다.

## 검증 프로필

| 프로필 | 용도 | 필수 검증 |
|---|---|---|
| **Quick** | 사용자가 명시한 작은 문구·컴포넌트·로컬 스타일 변경 | 영향 코드와 필요한 경우 대표 viewport 하나 |
| **Standard** | 일반적인 생성·개편 작업의 기본값 | 데스크톱/모바일 주요 흐름, 콘솔, 오버플로, 초점, 접근성 기본 사항 |
| **Strict** | 사용자가 명시한 배포 중요·전체 검증 | 전체 브라우저·컨트롤·콘텐츠·Lighthouse·캡처·독립 리뷰 근거 |

Standard의 광범위한 UI 작업에서는 craft 지침을 읽기 전에 페이지 유형 하나를 선택합니다. 상품·커머스 페이지에는 구성, 제품 스토리텔링, 위계, 브랜드 일관성, 상호작용 완성도를 스크린샷으로 판정하는 결과 게이트를 적용하며 필요한 경우에만 최대 두 번 수정합니다.

Standard 보고서는 `IMPLEMENTED_UNVERIFIED`와 `VERIFIED_STANDARD`를 구분합니다. 검증 완료 상태를 사용하려면 서로 다른 데스크톱·모바일 시작 및 완료 스크린샷, 콘솔 오류·경고 0건, 가로 오버플로 없음, 두 viewport에서 확인된 핵심 동작과 복구가 필요합니다.

Genscaff는 그라디언트, 글래스, 블러 기술 자체를 금지하지 않습니다. 사용자 요구와 기존 프로젝트 디자인이 우선합니다. Standard는 근거 없는 장식 상투 표현을 경고하고, Strict는 발견된 효과를 제거하거나 사용자·프로젝트 근거로 정당화하도록 요구합니다.

Genscaff는 AI 작성 여부 탐지기나 독창성 인증서가 아니며, 실제 사용자를 대상으로 한 테스트를 대체하지 않습니다.

## 저장소 구조

```text
.
├── skill/genscaff/        # 설치 가능한 Codex 스킬
├── tools/                 # 저장소 검증 및 패키징 도구
├── docs/                  # 평가 기록 및 비교 근거
├── .github/workflows/     # CI
├── LICENSE                # Apache License 2.0
├── NOTICE
└── THIRD_PARTY_NOTICES.md
```

저장소용 문서는 설치 가능한 스킬 외부에 둡니다. 따라서 배포되는 스킬에는 실행 지침, 번들 리소스, 법적으로 필요한 고지만 포함됩니다.

## 요구 사항

- Python 3.10 이상
- Node.js 22.19 이상
- Chrome 또는 Chromium
- 브라우저 감사 의존성을 설치하기 위한 npm 접근 권한

## 설치

기존 `genscaff`가 설치돼 있다면 교체 전에 백업해 주세요.

### Windows PowerShell

```powershell
Copy-Item -Recurse .\skill\genscaff "$env:USERPROFILE\.codex\skills\genscaff"
npm ci --omit=dev --prefix "$env:USERPROFILE\.codex\skills\genscaff\scripts"
```

### macOS 또는 Linux

```shell
cp -R skill/genscaff "$HOME/.codex/skills/genscaff"
npm ci --omit=dev --prefix "$HOME/.codex/skills/genscaff/scripts"
```

Codex를 다시 시작하거나 새 작업을 연 뒤 `$genscaff`를 호출하실 수 있습니다.

## 검증 및 테스트

```shell
python tools/check_skill.py
npm ci --omit=dev --prefix skill/genscaff/scripts
npm audit --omit=dev --audit-level=moderate --prefix skill/genscaff/scripts
python skill/genscaff/scripts/test_quality_gate.py
```

전체 회귀 테스트는 실제 브라우저와 Lighthouse 프로세스를 실행합니다. Chrome을 자동으로 찾지 못하면 `CHROME_PATH`를 설정해 주세요.

## 안전한 검증

`test`, `lint`, `build`라는 이름이 붙어도 저장소 스크립트는 임의 코드입니다. 검증기는 기본적으로 이를 재실행하지 않습니다. 정확한 명령과 연결된 스크립트를 검사하고 저장소를 신뢰한 뒤에만 `--execute-approved-commands`를 사용해 주세요.

Strict 브라우저 검증은 대상 페이지의 JavaScript를 실행하고 네트워크 요청을 만들 수 있습니다. `--allow-active-browser-audit`가 필요하며 schema v4 보고서에서는 `execution_policy.active_browser=approved`도 설정해야 합니다. 신뢰하지 않는 대상에 자격 증명이나 비밀 값을 노출하지 마세요.

```shell
python skill/genscaff/scripts/quality_gate.py --init report.json --profile standard
python skill/genscaff/scripts/quality_gate.py --init strict-report.json --profile strict
python skill/genscaff/scripts/quality_gate.py --report strict-report.json --allow-active-browser-audit
```

기존 schema v3 보고서는 `legacy-strict`로 계속 지원합니다.

## 설치용 압축 파일 빌드

```shell
python tools/package_skill.py
```

명령을 실행하면 `dist/genscaff.zip`과 `dist/genscaff.zip.sha256`이 생성됩니다. 압축 파일에는 Codex 스킬 디렉터리에 바로 복사할 수 있는 최상위 `genscaff/` 디렉터리가 들어 있습니다.

## 저장소 배포

`NOTICE`를 검토하고 필요하면 공동 저작권 표기를 법적 이름이나 GitHub 핸들로 교체해 주세요. 이후 저장소 루트에서 다음 명령을 실행하실 수 있습니다.

```shell
git init
git add .
git commit -m "feat: publish genscaff skill"
git branch -M main
gh repo create genscaff --public --source=. --remote=origin --push
```

마지막 명령은 공개 외부 상태를 생성합니다. 실행 전 스테이징된 파일과 저장소 공개 범위를 확인해 주세요.

## 기여

[CONTRIBUTING.md](CONTRIBUTING.md)를 확인해 주세요. 모든 기여는 저장소와 동일한 Apache-2.0 조건으로 받습니다.

## 라이선스

프로젝트가 소유한 소스 코드와 문서는 [Apache License 2.0](LICENSE)에 따라 배포됩니다. 서드파티 구성 요소와 인용된 외부 자료에는 각각의 조건이 적용됩니다. 자세한 내용은 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)를 확인해 주세요.
