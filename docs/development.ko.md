# 개발 및 검증 안내

[English](development.md) | [한국어](development.ko.md) | [README](../README.ko.md)

아래 명령은 저장소 루트에서 실행합니다. 기여자를 위한 검증, 평가 실행, 패키징 절차를 설명합니다.

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

`prepare --baseline-skill <previous-core-skill>`을 사용하면 이전 스킬의 고정 사본과 현재 스킬을 비교합니다. 양쪽에 같은 프롬프트로 Genscaff를 명시적으로 호출하며, 옵션을 생략하면 기존 스킬 미사용 대조군을 유지합니다. 비대화형 실행은 양쪽에 디자인 선택을 위임합니다. 사용자 선택 경계, 원본 입력, 품질·비용 판정, 정적 사례와 실제 실행의 차이는 [평가 절차](../evals/design-preservation.md)에 설명합니다.

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
