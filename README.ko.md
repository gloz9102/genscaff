<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/assets/brand/genscaff-logo-dark.png"><source media="(prefers-color-scheme: light)" srcset="docs/assets/brand/genscaff-logo-light.png"><img src="docs/assets/brand/genscaff-logo-light.png" alt="Genscaff" width="760"></picture></p>

# Genscaff

[English](README.md) | [한국어](README.ko.md)

Genscaff는 브라우저 프런트엔드를 만들고 개선하며 검증하는 Codex 플러그인입니다. 명시적으로 호출하면 요구사항을 반응형 UI와 실제 작동하는 상호작용으로 구현합니다.

## 주요 원칙

- 사용자 요구와 기존 디자인 시스템을 우선합니다.
- 한 화면에 정보를 몰아넣지 않고 여백을 허용합니다. 대시보드, 백오피스와 명시적인 요청은 높은 정보 밀도를 허용합니다.
- 주제가 바뀌는 문구는 실제 화면에서 줄이나 문단으로 분리합니다.
- 모바일은 메시지와 액션 우선순위에 맞게 재구성하고, 자연스러운 줄바꿈과 의미 있는 이미지 크롭을 유지합니다.
- 호버, 누름, 키보드 초점과 터치 반응을 제공하고 모션 감소 설정을 지원합니다.
- 포인트 색상과 상태별 색상을 공통 토큰으로 관리하여 일관되게 변경할 수 있게 합니다.

## GitHub marketplace에서 설치

```shell
codex plugin marketplace add gloz9102/genscaff --ref main
codex plugin add genscaff@genscaff-public
```

Codex를 다시 시작하거나 새 작업을 열어 주세요. 두 스킬 모두 암묵적으로 호출되지 않습니다.

## 사용법

두 스킬 모두 명시적으로 호출합니다. 작업 범위에 맞춰 선택합니다.

| 호출 | 적합한 작업 | 검증 범위 |
|---|---|---|
| `$genscaff quick` | 작은 문구, 컴포넌트, 로컬 스타일 변경 | 영향받는 동작과 필요한 대표 화면 |
| `$genscaff` | Standard로 새 페이지 제작 또는 넓은 범위의 개편 | 데스크톱과 모바일, 주요 흐름, 키보드, 초점, 런타임 오류 |
| `$genscaff-release-audit` | 명시적인 배포 감사(Strict) | 확장 브라우저 검사, Lighthouse, 독립 검토 |

```text
$genscaff PC방 랜딩페이지를 만들어 주세요. 두 방향을 비교하고 대신 골라 주세요.
$genscaff quick 이 버튼의 호버와 키보드 초점 표시를 개선해 주세요.
$genscaff-release-audit 이 프런트엔드를 배포 전에 감사해 주세요.
```

Standard는 기본적으로 디자인 두 방향을 비교하고 사용자의 선택을 받습니다. 단일안 진행이나 선택 위임도 요청할 수 있습니다. 종료된 `$genscaff strict` 대신 `$genscaff-release-audit`를 사용합니다.

## Genscaff 2.2.5 Standard 비교: PC방

가상의 **LEVEL PC 라운지**를 두 독립 에이전트가 같은 제작 브리프, 생성 이미지, 모델(`gpt-5.6-luna`), 추론 수준(`xhigh`)으로 제작했습니다. 한쪽에는 Genscaff Standard를 적용하고 다른 쪽은 프런트엔드 디자인 스킬 없이 제작했습니다. 디자인 방향 선택은 제작자에게 위임했습니다.

| Standard 적용 | Genscaff 미적용 |
|---|---|
| <img src="examples/v2.2.5-pccafe-comparison/artifacts/standard-desktop.png" alt="Genscaff Standard를 적용한 LEVEL PC 랜딩페이지" width="560"> | <img src="examples/v2.2.5-pccafe-comparison/artifacts/control-desktop.png" alt="Genscaff를 적용하지 않은 LEVEL PC 랜딩페이지" width="560"> |
| [소스](examples/v2.2.5-pccafe-comparison/standard/index.html) | [소스](examples/v2.2.5-pccafe-comparison/control/index.html) |

| 확인한 차이 | Standard 적용 | Genscaff 미적용 |
|---|---|---|
| 시각 구성 | 호박색 포인트, 절제된 표면 구분 | 라임 포인트, 큰 기울임 강조, 공간별 색면 |
| 방문 계획 확인 | 계산기 아래 인라인 표시 | 별도 모달 표시 |
| 검토 후 보정 | 한국어 단어 경계, 모바일 메뉴의 키보드 접근, 보조 문구 대비 | 밝은 배경의 강조 문구 대비, 모션 감소 시 스크롤 |
| 공통 기능 검증 | 데스크톱 및 모바일 요금 계산, 확인과 수정, 키보드, 호버, 터치 메뉴 통과 | 동일 검사 통과 |

두 결과 모두 검토 후 보정되었습니다. 색상과 구성은 이번 샘플의 선택이며 스킬이 강제하는 스타일이나 일반적인 우열의 근거가 아닙니다.

공통 이미지는 imagegen으로 생성했습니다. 실제 예약이나 결제는 전송하지 않습니다.

[샘플 실행 방법, 모바일 스크린샷과 검증 한계](docs/v2.2.5-pccafe-comparison.ko.md)

## 주요 제한사항

검증 보고서는 실제 확인한 범위의 근거이며 전체 접근성 적합성이나 실제 사용자 성과를 보증하지 않습니다. 필요한 실행 환경이 없으면 브라우저 의존 검사는 미검증으로 남습니다. PC방 비교도 보정된 한 쌍의 예시이며 통계적 효과 검증이 아닙니다.

이 프로젝트는 독립적인 커뮤니티 프로젝트이며 OpenAI와 제휴하거나 OpenAI의 보증을 받지 않습니다.

## 문서 안내

| 문서 | 내용 |
|---|---|
| [상세 사용 및 검증 기준](docs/workflow-details.ko.md) | 디자인 선택, 보존, 분류, 검증 근거, 실행 환경과 권한 |
| [개발 및 검증 안내](docs/development.ko.md) | 저장소 구조, 테스트, 평가 하네스, 배포 패키지 |
| [버전 변경과 평가 이력](docs/version-history.ko.md) | 버전별 변경, 내부 구조 개편, 과거 평가 한계 |
| [이전 Quick 예시](docs/v2.2-quick-examples.ko.md) | 대시보드와 랜딩페이지 샘플 |
| [릴리스](https://github.com/gloz9102/genscaff/releases) | 게시된 버전과 다운로드 패키지 |

프로젝트 소유 소스와 문서는 [Apache License 2.0](LICENSE)을 적용합니다. [서드파티 조건](THIRD_PARTY_NOTICES.md)과 [보안 정책](SECURITY.md)을 함께 확인할 수 있습니다.
