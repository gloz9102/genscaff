---
name: image-to-web-impl
description: "Use when the user wants Codex to create a gpt ima2 webpage mockup from a prompt, extract locked mockup specs such as visible text, section order, layout direction, component count, CTA labels, analyze the mockup image, implement a visually matching frontend through the frontend-quality-gate workflow, apply strict typography, color, layout, component, WebGL/Three.js, rendering performance, semantic HTML, accessibility, and UX principles, run it in a browser, capture screenshots, compare the result against the mockup, and iterate until locked spec, visual match, and quality gate are acceptable."
---

# Image To Web Impl

## 목적

사용자 프롬프트를 기준으로 `gpt ima2` 웹페이지 목업 이미지를 생성하고, 그 이미지를 웹 요소 단위로 분석한 뒤 `$frontend-quality-gate` 워크플로를 통해 실제 동작 가능한 프론트엔드 코드로 구현한다. 최종 결과물은 목업 이미지와 시각적으로 최대한 일치해야 하며, 프론트엔드 품질 검증을 통과해야 한다. 구현에 사용되는 샘플 이미지 등 시각 리소스는 WebP 또는 JPG로 생성하거나 변환하여 용량과 로드 부하를 최소화한다.

## 기본 원칙

- 사용자 프롬프트에 명시된 범위 안에서만 작업한다.
- 사용자의 의도를 임의로 확장하거나 추정하지 않는다.
- 프론트엔드 구현에 필수적인 정보가 부족한 경우에만 질문한다.
- 목업 이미지의 레이아웃, 색상, 간격, 타이포그래피, 컴포넌트 구조, 시각적 위계를 우선 기준으로 삼는다.
- 이미지 기반 웹 구현에서는 목업의 visible text, section order, layout direction, component count, CTA labels를 locked spec으로 취급한다.
- locked spec은 사용자의 명시 요청 없이 변경하지 않는다.
- 디자인 품질 개선은 locked spec을 보존한 범위 안에서만 수행한다.
- 구현에 사용되는 샘플 이미지, 목업 이미지, 배경 이미지, 카드 이미지 등 시각 리소스는 WebP 또는 JPG 형식으로 생성하거나 변환한다.
- 실제 웹 코드 구현 단계에서는 반드시 `$frontend-quality-gate` 스킬을 사용한다.
- `$frontend-quality-gate`의 브리프 확장, 시각 목표, 구현 표준, 브라우저 피드백 루프, 품질 리포트 검증 절차를 따른다.
- 결과 검증은 반드시 목업 이미지와 실제 웹페이지 스크린샷을 비교하여 수행한다.
- 웹 UI를 구현할 때는 기존 프로젝트 구조, 디자인 시스템, 컴포넌트 패턴, 스타일링 방식을 먼저 확인하고 따른다.
- 새 프로젝트가 필요한 경우에는 요청 범위에 맞는 가장 단순한 프론트엔드 구조를 만든다.
- 구현 완료 전 브라우저에서 실제 렌더링 상태를 확인한다.

## 구현 품질 원칙

실제 웹 코드 구현 시 다음 원칙을 반드시 준수한다.

### 0. 화면 구성

- 화면 표현에 필요하다면 WebGL과 Three.js를 활용한다.
- WebGL 또는 Three.js는 요청 범위, 목업의 시각 구조, 인터랙션 목적상 필요한 경우에만 적용한다.
- 3D 또는 캔버스 기반 화면을 구현하면 데스크톱과 모바일에서 캔버스가 비어 있지 않고 올바르게 프레이밍되는지 확인한다.

### 1. 타이포그래피

- 폰트 스케일은 모듈러 스케일 기준으로 설계하고, 일반적으로 `1.2`에서 `1.333` 배율을 사용한다.
- 폰트 크기는 `rem` 기반 체계를 사용한다.
- 본문 행간은 `line-height: 1.4`에서 `1.6` 범위로 설계한다.
- 자간은 폰트와 언어 특성에 맞게 조정하되 가독성을 해치지 않는다.
- 본문 텍스트 한 줄 길이는 가능한 경우 `45`에서 `75`자 범위로 제한한다.
- 웹폰트는 FOUT/FOIT 영향을 고려하고, `font-display`와 subset 전략을 적용한다.
- 한글 웹폰트는 용량과 렌더링 부하가 크므로 subset, fallback, preload 여부를 더 엄격히 검토한다.

### 2. 색상

- 팔레트는 HSL 또는 OKLCH 기반으로 설계한다.
- 색상은 `primary`, `surface`, `on-surface`, `border`, `muted`, `danger`, `success` 같은 시맨틱 컬러 토큰으로 정의한다.
- 텍스트 명도 대비는 WCAG AA 기준을 따른다: 일반 텍스트 `4.5:1` 이상, 큰 텍스트 `3:1` 이상.
- 다크모드는 단순 색상 반전으로 처리하지 않고 elevation, 채도, 표면 대비를 조정해 설계한다.

### 3. 레이아웃과 공간

- 8pt 그리드 시스템을 기본으로 사용한다.
- spacing 토큰은 `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64` 같은 4px 또는 8px 계열을 사용한다.
- 시각적 위계는 크기, 굵기, 색, 여백으로 우선순위를 표현한다.
- 정렬, 근접성, 반복, 대비 원칙을 적용한다.
- 반응형 브레이크포인트를 명시하고, 컴포넌트 단위 적응이 필요한 영역은 컨테이너 쿼리를 검토한다.
- `position: absolute`로 목업을 그림처럼 억지 배치하지 않는다.
- 실제 구현에 사용할 방식과 동일하게 grid, flex, container query, semantic flow를 기준으로 레이아웃을 설계한다.
- 목업 자체가 레이아웃 검증 자료가 되도록 실제 코드 구조와 목업 구조를 맞춘다.

### 4. 컴포넌트와 디자인 시스템

- 디자인 토큰을 Figma Variables와 CSS Custom Properties가 대응될 수 있는 구조로 설계한다.
- 컴포넌트 상태를 구현한다: hover, focus, active, disabled, loading, empty, error.
- 로딩 상태는 필요한 경우 스켈레톤으로 표현한다.
- 디자이너가 그리지 않은 hover, focus, active, disabled, loading, empty, error 상태도 개발 단계에서 누락하지 않는다.
- Atomic Design 또는 프로젝트의 기존 컴포넌트 계층을 따른다.
- Figma variant에 해당하는 차이는 React props 또는 프로젝트 컴포넌트 variant 구조로 대응한다.

### 5. 인터랙션과 모션

- 진입 애니메이션은 ease-out, 퇴장 애니메이션은 ease-in 계열 이징을 우선 사용한다.
- 지속시간은 일반적으로 `150ms`에서 `300ms` 범위로 제한한다.
- 애니메이션은 `transform`과 `opacity`만 사용한다.
- `width`, `top`, `margin` 애니메이션은 매 프레임 layout을 유발하므로 금지한다.
- 한 프레임 안에서 `offsetHeight` 같은 layout 읽기와 `style` 변경 같은 쓰기를 교차 반복하지 않는다.
- layout thrashing을 유발하는 DOM 읽기/쓰기 패턴을 분리한다.
- `box-shadow`, `filter: blur()`, 대면적 `backdrop-filter` 애니메이션은 비용이 크므로 피한다.
- 오프스크린 영역은 필요한 경우 `content-visibility: auto`를 사용해 렌더링 비용을 줄인다.
- `prefers-reduced-motion`을 반영한다.
- 피드백, 스켈레톤, 낙관적 UI 같은 마이크로 인터랙션은 사용자 상태 인지를 돕는 경우에만 적용한다.

### 6. 접근성

- 키보드 내비게이션이 가능해야 한다.
- `focus-visible` 스타일을 명확히 제공한다.
- 시맨틱 마크업을 우선 사용하고, ARIA는 필요한 경우에만 사용한다.
- 터치 타깃은 최소 `44px` by `44px`를 확보한다.
- 색만으로 정보를 전달하지 않는다.
- 이미지에는 의미에 맞는 `alt`를 제공한다.
- 클릭 가능한 요소는 `<button>` 또는 적절한 네이티브 인터랙티브 요소를 사용한다.
- 클릭 가능한 `div`를 만들지 않는다.
- 폼 컨트롤은 `<label>`과 명확히 연결한다.

### 7. 시맨틱 구조

- `div`를 남발하지 말고 `header`, `nav`, `main`, `section`, `footer` 같은 landmark 구조를 우선 사용한다.
- 제목 위계는 `h1`에서 `h3` 중심으로 순서와 의미를 지킨다.
- 목업의 구조가 실제 구현으로 전파되므로 목업 분석 단계부터 시맨틱 구조를 바로잡는다.
- 섹션, 네비게이션, 폼, 카드, 버튼, 목록은 실제 HTML 의미와 맞게 분리한다.

### 8. UX 기본 원칙

- 히크의 법칙을 고려해 선택지 수를 불필요하게 늘리지 않는다.
- 피츠의 법칙을 고려해 주요 타깃의 크기와 거리를 설계한다.
- 게슈탈트 원리를 적용해 그룹, 흐름, 관계가 명확하게 보이도록 한다.
- 플랫폼 관례와 일관성을 유지한다.
- 인지 부하를 최소화한다.
- 에러 메시지 작성보다 에러 방지를 우선한다.

## 작업 절차

### 1. 목업 샘플 이미지 생성

사용자 프롬프트를 기반으로 `gpt ima2` 또는 사용 가능한 이미지 생성 도구를 사용해 웹페이지 목업 샘플 이미지를 생성한다. 생성된 목업 이미지와 구현에 사용할 샘플 이미지 리소스는 WebP 또는 JPG 형식으로 저장한다.

목업에는 다음 요소가 명확히 드러나야 한다.

- 전체 페이지 레이아웃
- 주요 섹션 구조
- 헤더, 내비게이션, 본문, 카드, 버튼, 폼 등 UI 요소
- 색상 팔레트
- 타이포그래피 위계
- 여백과 정렬
- 반응형 고려가 필요한 구조
- 필요한 경우 WebGL 또는 Three.js 기반 영역
- 실제 구현과 동일한 grid/flex 기반 레이아웃 구조
- 시맨틱 landmark와 제목 위계
- hover, focus, active, disabled, loading, empty, error 상태
- 이미지 alt, 버튼, label 같은 접근성 요소

### 2. 목업 고정 요소 추출

이미지 분석과 디자인 품질 개선을 시작하기 전에 목업의 고정 요소를 먼저 추출하고 `locked spec`으로 선언한다.

다음 항목을 반드시 추출한다.

- 상단 copy
- H1 문구
- CTA 문구
- nav 문구
- 섹션 순서
- flow 방향
- 카드 개수
- form 위치
- 후기 및 사진 배치
- visible text
- section order
- layout direction
- component count
- CTA labels

locked spec은 다음 규칙을 따른다.

- 문구를 더 자연스럽게 바꾸지 않는다.
- 구조를 더 좋아 보이게 재설계하지 않는다.
- 가로 flow를 세로 panel로 바꾸지 않는다.
- 섹션을 추가하거나 끼워 넣지 않는다.
- 사용자의 명시 요청 없이 locked spec을 변경하지 않는다.
- 디자인 품질 개선은 locked spec을 보존한 범위 안에서만 수행한다.

다음 경우에는 locked spec을 임의 변경하지 말고 사용자에게 질문한다.

- 반응형 대응을 위해 구조 변경이 필요한 경우
- 접근성 보완을 위해 문구, 구조, 순서 변경이 필요한 경우
- 텍스트가 너무 작거나 깨지는 경우
- 목업 자체가 구현 불가능한 경우

### 3. 이미지 분석 및 요소 분리

생성된 목업 이미지를 분석하여 웹 개념 단위로 요소를 분리한다.

분리 기준은 다음과 같다.

- locked spec
- 페이지 전체 구조
- 레이아웃 그리드
- 실제 구현에 사용할 grid/flex/container query 구조
- 시맨틱 landmark와 제목 위계
- 섹션 단위
- 컴포넌트 단위
- 컴포넌트 상태: hover, focus, active, disabled, loading, empty, error
- 텍스트 계층
- 이미지 및 아이콘 영역
- 버튼과 인터랙션 요소
- WebGL 또는 Three.js가 필요한 화면 영역
- 색상, 그림자, 테두리, 배경
- 반응형 변화가 필요한 영역

분석 결과는 구현 순서에 맞게 정리한다.

### 4. `$frontend-quality-gate` 적용 준비

실제 웹 코드 구현을 시작하기 전에 `$frontend-quality-gate` 스킬을 로드하고 해당 스킬의 지침을 따른다.

다음 항목을 목업 분석 결과와 연결한다.

- locked spec을 `$frontend-quality-gate`의 확장 디자인 브리프와 시각 목표의 변경 금지 조건으로 사용한다.
- 목업 분석 결과를 확장 디자인 브리프의 입력으로 사용한다.
- 목업의 시각 구조를 시각 목표의 기준으로 사용한다.
- 목업의 색상, 간격, 타이포그래피, 컴포넌트 구조를 구현 표준의 구체 값으로 사용한다.
- 목업 분석 결과를 `구현 품질 원칙`의 타이포그래피, 색상, 레이아웃, 컴포넌트, 모션, 접근성, UX 기준에 맞춰 보정한다.
- 목업 분석 결과에서 WebGL 또는 Three.js가 필요한 화면 영역이 있는지 판단한다.
- 목업 분석 결과에서 시맨틱 구조, 실제 레이아웃 방식, 필수 컴포넌트 상태, 접근성 요소를 확정한다.
- 목업과 실제 브라우저 스크린샷 비교를 브라우저 피드백 루프의 핵심 검증 증거로 사용한다.
- `$frontend-quality-gate`의 품질 리포트 JSON에 locked spec 일치 결과, 목업 비교 결과, 데스크톱 및 모바일 스크린샷 경로를 포함한다.

### 5. 요소별 순차 코드화

분리된 요소를 바탕으로 `$frontend-quality-gate` 워크플로 안에서 프론트엔드 코드를 순차적으로 작성한다.

구현 순서는 다음을 따른다.

1. 프로젝트 기본 구조 작성
2. 전역 스타일 작성
3. 레이아웃 구조 작성
4. 공통 컴포넌트 작성
5. 섹션별 UI 작성
6. WebP 또는 JPG 형식의 이미지, 아이콘, 시각 요소 적용
7. 필요한 경우 WebGL 또는 Three.js 화면 요소 적용
8. 반응형 스타일 적용
9. 인터랙션과 상태 구현

각 단계는 이전 단계의 구조를 유지하면서 누적 구현한다.

구현 중에는 다음 `$frontend-quality-gate` 기준을 반드시 적용한다.

- locked spec을 변경하지 않는다.
- 문구, 섹션 순서, layout direction, component count, CTA labels를 목업과 동일하게 유지한다.
- 기존 프로젝트의 프레임워크, 라우팅, 스타일 시스템, 컴포넌트 규칙을 따른다.
- 기존 토큰이 있으면 색상, 간격, 타이포그래피, radius, shadow에 기존 토큰을 사용한다.
- 토큰 시스템이 없으면 최소한의 로컬 토큰 레이어를 먼저 정의한다.
- 타이포그래피, 색상, 레이아웃, 컴포넌트, WebGL/Three.js, 렌더링 성능, 시맨틱 구조, 접근성, UX는 `구현 품질 원칙`을 기준으로 구현한다.
- 구현에 포함되는 샘플 이미지 등 시각 리소스는 WebP 또는 JPG를 사용하여 번들 크기와 로드 부하를 최소화한다.
- 관련 UI 상태를 구현한다: hover, focus, active, disabled, loading, empty, error, long-content, responsive.
- 레이아웃은 실제 서비스 코드와 동일한 grid/flex/container query 구조로 구현한다.
- `position: absolute`는 장식 또는 겹침이 의미상 필요한 경우에만 제한적으로 사용한다.
- 애니메이션은 `transform`과 `opacity`만 사용하고 layout을 유발하는 속성 애니메이션을 금지한다.
- 시맨틱 HTML, 이미지 alt, 네이티브 버튼, label 연결을 구현한다.
- 데스크톱과 모바일에서 텍스트 줄바꿈, 오버플로, 겹침, 수평 스크롤을 확인한다.

### 6. 최종 조립

모든 요소가 작성되면 전체 페이지를 하나의 완성된 화면으로 조립한다.

조립 단계에서 다음 항목을 확인한다.

- locked spec 보존 여부
- 섹션 순서
- 컴포넌트 배치
- 전체 너비와 높이
- 시각적 균형
- 텍스트 줄바꿈
- 버튼과 입력 요소의 크기
- 이미지 비율
- 이미지 리소스 형식과 용량
- WebGL 또는 Three.js 영역의 렌더링 상태
- grid/flex 기반 레이아웃 안정성
- 시맨틱 landmark와 제목 위계
- hover, focus, active, disabled, loading, empty, error 상태
- 이미지 alt, 버튼, 폼 label 연결
- 데스크톱 및 모바일 화면 대응
- `$frontend-quality-gate`의 시각 목표와 구현 결과의 일치 여부

### 7. 목업 이미지와 결과물 비교

완성된 웹페이지를 브라우저에서 실행하고 스크린샷을 캡처한다.

캡처한 결과물을 최초 목업 샘플 이미지와 비교한다.

비교 기준은 다음과 같다.

- locked spec과 실제 구현의 일치 여부
- H1이 목업과 같은지 여부
- flow 카드가 같은 개수인지 여부
- flow 방향이 같은지 여부
- CTA 문구가 같은지 여부
- 후기 섹션 위치가 같은지 여부
- form 구조가 같은지 여부
- 레이아웃 일치도
- 색상 일치도
- 폰트 크기와 굵기
- 여백과 간격
- 컴포넌트 크기
- 정렬 상태
- 이미지와 아이콘 위치
- WebGL 또는 Three.js 요소 위치와 렌더링 상태
- 시각적 밀도
- 반응형 화면에서의 안정성
- `$frontend-quality-gate` 품질 기준 충족 여부
- `구현 품질 원칙` 충족 여부

불일치가 발견되면 즉시 임의 수정하지 말고 `2. 목업 고정 요소 추출` 단계부터 다시 수행한다.

재분석 후 다음 순서로 반복한다.

1. locked spec 재추출
2. 이미지 재분석
3. 요소 재분리
4. `$frontend-quality-gate` 시각 목표 갱신
5. 코드 재작성 또는 수정
6. 최종 조립
7. 스크린샷 재비교
8. locked spec 일치 여부 재검증
9. `$frontend-quality-gate` 품질 리포트 재검증

목업과 결과물이 충분히 일치하고 `$frontend-quality-gate` 검증이 통과될 때까지 반복한다.

### 8. 품질 검증

`$frontend-quality-gate`의 품질 검증 절차를 따른다.

필수 검증 항목은 다음과 같다.

- 데스크톱 브라우저 스크린샷 확인
- 모바일 브라우저 스크린샷 확인
- 콘솔 오류 확인
- 레이아웃 깨짐, 텍스트 겹침, 오버플로, 수평 스크롤 확인
- locked spec과 실제 구현의 일치 여부 확인
- H1, CTA 문구, nav 문구, 섹션 순서, flow 방향, 카드 개수, form 위치, 후기 및 사진 배치 확인
- 목업 이미지와 실제 결과물 비교
- 타이포그래피, 색상 대비, grid/flex 레이아웃, 시맨틱 구조, 컴포넌트 상태, 모션, 렌더링 성능, 접근성, UX 원칙 준수 여부 확인
- WebGL 또는 Three.js를 사용한 경우 캔버스가 비어 있지 않고 데스크톱 및 모바일에서 올바르게 렌더링되는지 확인
- `width`, `top`, `margin`, `box-shadow`, `filter: blur()`, 대면적 `backdrop-filter` 애니메이션이 없는지 확인
- layout thrashing을 유발하는 DOM 읽기/쓰기 교차 패턴이 없는지 확인
- 오프스크린 비용이 큰 영역에 `content-visibility: auto` 적용이 필요한지 확인
- 이미지 alt, 네이티브 버튼, 폼 label 연결, 키보드 내비게이션, `focus-visible` 확인
- 관련 lint, typecheck, test, build 명령 실행
- 구현에 사용된 이미지 리소스가 WebP 또는 JPG 형식인지 확인
- 가능하면 Lighthouse 측정 실행
- `$frontend-quality-gate` 품질 리포트 JSON 작성
- `$frontend-quality-gate`의 `scripts/quality_gate.py` 검증 통과

품질 게이트 통과 조건은 다음을 따른다.

- 보기 좋음만으로 통과 처리하지 않는다.
- 목업 고정 요소가 다르면 실패 처리한다.
- Lighthouse 점수가 좋아도 목업과 다르면 실패 처리한다.
- locked spec과 실제 구현이 일치하지 않으면 실패 처리한다.

### 9. 최종 보고

모든 작업이 완료되면 사용자에게 마크다운 형식으로 보고한다.

보고에는 다음 항목만 포함한다.

- 구현 완료 여부
- 최종 웹페이지 실행 URL 또는 파일 경로
- 최종 웹페이지 스크린샷
- 목업 이미지와의 비교 결과
- locked spec과 실제 구현의 일치 여부
- `$frontend-quality-gate` 검증 결과
- 주요 구현 요소 요약

## 완료 기준

다음 조건을 모두 만족하면 작업을 완료한다.

- 사용자 프롬프트 기반 목업 이미지가 생성되어 있다.
- 목업의 locked spec이 구현 전에 추출되어 있다.
- locked spec이 사용자의 명시 요청 없이 변경되지 않았다.
- 목업 이미지가 웹 요소 단위로 분석되어 있다.
- 분석 결과를 기반으로 `$frontend-quality-gate` 시각 목표가 작성되어 있다.
- `$frontend-quality-gate` 워크플로를 통해 프론트엔드 코드가 작성되어 있다.
- 구현에 사용된 샘플 이미지 등 시각 리소스가 WebP 또는 JPG 형식으로 준비되어 있다.
- 타이포그래피, 색상, 레이아웃, 컴포넌트, WebGL/Three.js 필요 여부, 렌더링 성능, 시맨틱 구조, 접근성, UX 기본 원칙이 구현에 반영되어 있다.
- hover, focus, active, disabled, loading, empty, error 상태가 필요한 컴포넌트에 반영되어 있다.
- 실제 구현과 동일한 grid/flex/container query 기반 레이아웃으로 구성되어 있다.
- 이미지 alt, 네이티브 버튼, 폼 label 연결, 키보드 내비게이션이 확인되어 있다.
- 실제 브라우저에서 결과물이 정상 렌더링된다.
- H1, CTA 문구, nav 문구, 섹션 순서, flow 방향, 카드 개수, form 위치, 후기 및 사진 배치가 목업과 일치한다.
- 결과물 스크린샷이 목업 이미지와 정교하게 비교되었다.
- 불일치 항목이 해결되었다.
- `$frontend-quality-gate` 품질 리포트 검증이 통과되었다.
- 사용자에게 최종 스크린샷과 함께 결과가 보고되었다.
