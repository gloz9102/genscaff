# Genscaff

[English](README.md) | [한국어](README.ko.md)

Genscaff는 브라우저에서 렌더링되는 프런트엔드를 만들고 검토하기 위한 증거 기반 Codex 스킬이다. 제품 고유성, 동작 연속성, 반응형 디자인, 접근성, 런타임 무결성, AI 특유의 획일적인 결과를 걸러내는 품질 기준을 브라우저 및 Lighthouse 자동 검증과 결합한다.

이 프로젝트는 독립적인 커뮤니티 프로젝트이며 OpenAI와 제휴하거나 OpenAI의 보증을 받지 않았다.

## 적용하는 품질 기준

- 구현 전 제품 계약과 시각적 목표 정의
- 제품 도메인 고유 신호와 2개 도메인 치환 테스트
- 피드백, 완료 상태, 복구 상태까지 포함한 주요 동작의 전체 흐름
- 화면에 보이는 모든 컨트롤과 사실 주장 목록화
- 데스크톱 및 모바일 브라우저 증거 수집
- 검증기가 직접 실행하는 DOM, 계산된 스타일, 리소스, Lighthouse 재검사
- 그라디언트, 글래스모피즘, 글로 효과, 장식용 오브를 금지하는 엄격한 프로젝트 정책
- 기계 검증과 분리해 관리하는 독립 리뷰 출처

Genscaff는 AI 작성 여부 탐지기나 독창성 인증서가 아니며, 실제 사용자를 대상으로 한 테스트를 대체하지 않는다.

## 저장소 구조

```text
.
├── skill/genscaff/        # 설치 가능한 Codex 스킬
├── tools/                 # 저장소 검증 및 패키징 도구
├── .github/workflows/     # CI
├── LICENSE                # Apache License 2.0
├── NOTICE
└── THIRD_PARTY_NOTICES.md
```

저장소용 문서는 설치 가능한 스킬 외부에 둔다. 따라서 배포되는 스킬에는 실행 지침, 번들 리소스, 법적으로 필요한 고지만 포함된다.

## 요구 사항

- Python 3.10 이상
- Node.js 22.19 이상
- Chrome 또는 Chromium
- 브라우저 감사 의존성을 설치하기 위한 npm 접근 권한

## 설치

기존 `genscaff`가 설치돼 있다면 교체 전에 백업하라.

### Windows PowerShell

```powershell
Copy-Item -Recurse .\skill\genscaff "$env:USERPROFILE\.codex\skills\genscaff"
npm install --omit=dev --prefix "$env:USERPROFILE\.codex\skills\genscaff\scripts"
```

### macOS 또는 Linux

```shell
cp -R skill/genscaff "$HOME/.codex/skills/genscaff"
npm install --omit=dev --prefix "$HOME/.codex/skills/genscaff/scripts"
```

Codex를 다시 시작하거나 새 작업을 연 뒤 `$genscaff`를 호출하면 된다.

## 검증 및 테스트

```shell
python tools/check_skill.py
npm install --omit=dev --prefix skill/genscaff/scripts
python skill/genscaff/scripts/test_quality_gate.py
```

전체 회귀 테스트는 실제 브라우저와 Lighthouse 프로세스를 실행한다. Chrome을 자동으로 찾지 못하면 `CHROME_PATH`를 설정하라.

## 설치용 압축 파일 빌드

```shell
python tools/package_skill.py
```

명령을 실행하면 `dist/genscaff.zip`과 `dist/genscaff.zip.sha256`이 생성된다. 압축 파일에는 Codex 스킬 디렉터리에 바로 복사할 수 있는 최상위 `genscaff/` 디렉터리가 들어 있다.

## 저장소 배포

`NOTICE`를 검토하고 필요하면 공동 저작권 표기를 법적 이름이나 GitHub 핸들로 교체하라. 이후 저장소 루트에서 다음 명령을 실행한다.

```shell
git init
git add .
git commit -m "feat: publish genscaff skill"
git branch -M main
gh repo create genscaff --public --source=. --remote=origin --push
```

마지막 명령은 공개 외부 상태를 생성한다. 실행 전 스테이징된 파일과 저장소 공개 범위를 확인하라.

## 기여

[CONTRIBUTING.md](CONTRIBUTING.md)를 확인하라. 모든 기여는 저장소와 동일한 Apache-2.0 조건으로 받는다.

## 라이선스

프로젝트가 소유한 소스 코드와 문서는 [Apache License 2.0](LICENSE)에 따라 배포된다. 서드파티 구성 요소와 인용된 외부 자료에는 각각의 조건이 적용된다. 자세한 내용은 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)를 확인하라.
