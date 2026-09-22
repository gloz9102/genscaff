# Genscaff Standard 제작 계약

## 분류

- `project_mode`: `new`
- `reference_mode`: `no-reference`
- `primary_archetype`: `product-editorial`
- `secondary_archetype`: `transaction`에 가까운 방문 계획 계산 흐름을 보조로 사용하지만 예약이나 결제는 제공하지 않음
- `surface_type`: `landing`
- `change_scope`: `route`
- 근거: 새 폴더에 프레임워크와 기존 디자인 시스템이 없고, 사용자는 공간과 좌석을 이해한 뒤 좌석 종류와 시간을 골라 방문 계획을 계산함. 제공된 이미지는 브리프가 고정한 콘셉트 미디어이며 외부 사이트 레퍼런스로 취급하지 않음.

## Product

- Target user / primary job / success outcome: LEVEL PC 라운지를 처음 방문하려는 개인 또는 2인 방문자가 좌석 성격과 시간별 비용을 빠르게 비교하고, 선택한 방문 계획의 금액을 확인함.
- Domain objects and vocabulary: 스탠다드석, 와이드석, 듀오석, 이용 시간, 1시간 단가, 총액, 24시간 운영, 방문 계획.
- Primary CTA / secondary actions: `방문 계획 확인`이 선택 결과를 확정해 화면에 보여주는 주 CTA. `공간 보기`, `요금 보기`, 좌석 선택, 이용 시간 선택, `수정하기`, 모바일 메뉴가 보조 행동임.
- Required decisions / actions to success / safe defaults: 좌석 기본값은 스탠다드석, 시간 기본값은 1시간. 사용자가 좌석과 시간을 선택하면 총액이 즉시 바뀌고, 주 CTA를 누르면 선택한 좌석과 시간과 총액이 확인 상태가 됨. 확인 뒤 `수정하기`로 같은 흐름에 돌아갈 수 있음.
- Failure or recovery when applicable: 실제 외부 예약이나 결제가 없으므로 네트워크 실패 상태는 해당 없음. 잘못 고른 계획은 선택 컨트롤 또는 `수정하기`로 되돌릴 수 있음.
- Evidence labels: 브리프에 명시된 사실은 `user`. 새 시각 시스템과 문구는 `assumption`이며 기능은 정적 페이지의 실제 동작으로 검증함.

## Reference

- Mode / primary archetype / optional secondary / surfaces: `no-reference` / `product-editorial` / 방문 계획 계산 흐름 / `landing`.
- Adopted principles and product-fit rationale: 제공된 콘셉트 이미지를 공간을 설명하는 큰 미디어로 사용함. 어두운 매장과 따뜻한 조명을 기반으로 화면의 집중과 휴식을 표현함. 좌석 선택과 요금 계산을 같은 시선 흐름에 배치해 공간 이해가 방문 계획으로 이어지게 함.
- Deliberate differences: 외부 브랜드나 사이트의 로고, 카피, 고유 색상, 고유 레이아웃을 차용하지 않음. 이미지 위 중앙 영웅 레이아웃 대신 좌측 메시지와 우측 공간 이미지를 분리함. 기능 선택은 별도 계산 패널로 구성하고 24시간 운영과 비예약 안내를 자체 정보로 제시함.
- Locked requirements and allowed changes: `../assets/cafe-hero.png`만 미디어로 사용하며 좌석 가격, 좌석 설명, 1/2/3시간, 24시간 운영, 예약·결제 아님 안내를 보존함. 실제 주소와 연락처, 임의 장비 성능, 후기, 이용자 수는 추가하지 않음. 색상, 조합, 여백, 순서는 브리프를 해치지 않는 범위에서 선택함.
- Reference trace: 외부 레퍼런스 없음. 브리프의 제공 이미지 / 좌석이 보이는 매장 콘셉트 / 공간을 직접 보여주는 미디어 원칙 / 방문 전 공간 파악에 적합 / 히어로 이미지 영역과 공간 섹션 / 브라우저에서 이미지 로딩 및 캡션 관찰 / 추가 사진과 실제 매장 주장 제외.

## Content

- Hierarchy / expected item count: 상단 네비게이션과 히어로, 공간 좌석 3종, 요금표 3행, 방문 계획 계산기 1개, 24시간 운영과 비예약 안내.
- Long-content and missing-data behavior: 길게 늘어나는 한국어 문구는 고정 높이 없이 자연스럽게 줄바꿈함. 필수 데이터는 정적 객체로 제공하며 이미지 실패 시 배경색과 대체 문구가 남도록 처리함.
- Localization and writing-direction needs: 한국어 존댓말 UI. 좌우 쓰기 방향은 한국어 기본값인 `ltr`.

## Preservation

- Required information / values / accessible names and their source: 브리프의 세 좌석 이름과 시간당 가격, 듀오석 1시간 2인 합계 5,000원, 1/2/3시간 선택, 24시간 운영, 예약·결제 아님 안내를 그대로 노출함. 라디오에는 좌석과 시간의 명확한 접근성 이름을 부여함.
- User actions / terminal outcomes / data and API contracts to preserve: 좌석 또는 시간 선택 시 즉시 총액이 바뀜. `방문 계획 확인`은 선택 결과와 총액을 확인 영역과 라이브 상태로 표시함. `수정하기`는 선택 폼으로 포커스를 반환함. 외부 API 없음.
- Meaningful reading and focus order: 헤더와 히어로 메시지, 공간 설명, 요금, 방문 계획 순서. DOM 순서와 모바일 시각 순서를 동일하게 유지함.
- Permitted presentation or content changes / justified DOM changes: 브리프에 없는 장비 사양, 주소, 전화번호, 후기와 사진은 추가하지 않음. 카드와 요금표는 스캔 가능한 자체 표현으로 구성함.
- Affected invariant -> brief baseline -> implementing region -> observed result and evidence / unresolved limitations: 가격과 좌석 설명 -> 브리프 고정값 -> `#space`, `#rates`, `#planner` -> 브라우저 검증 뒤 실제 텍스트와 선택 결과를 기록함. 브라우저 기반 보조기기 검증은 범위 밖임.

## Exploration

- Two-candidate comparison: 동일한 좌석 정보, 가격, 콘셉트 이미지, 1440×1000 및 390×844를 대상으로 두 방향을 비교함. 사용자 요청이 선택을 위임했으므로 제작자가 선택함.
- Candidate A: 장면 중심 editorial. 히어로를 크게 두고 이미지 위에 공간 설명을 겹친 뒤, 아래에 좌석 소개와 계산기를 배치함. 미디어 이해는 빠르지만 핵심 결정이 첫 화면 아래로 밀림.
- Candidate B: 계획 계산기 우선. 히어로에서 공간 이미지와 24시간 운영 정보를 보여주고, 바로 아래에서 좌석 선택, 시간 선택, 금액 결과를 한 덩어리로 연결함. 방문 전 비용 결정을 먼저 해결하며 공간 정보는 별도 좌석 섹션에서 보완함.
- Differences beyond color: B는 선택 컨트롤을 첫 주요 구간으로 당겨 정보 밀도를 높이고, 가격과 총액의 숫자 계층을 크게 둠. A는 이미지와 설명의 세로 내러티브가 먼저이며 계산기가 후순위임. 두 방향 모두 동일한 3좌석, 3시간, 동일 이미지를 사용함.
- Explicit delegation / selected direction and rationale: 사용자가 디자인 방향 선택을 제작자에게 위임함. B를 선택함. 핵심 방문 계획을 한 번의 선택 흐름으로 확인할 수 있고, 공간 이미지가 기능을 압도하지 않으면서도 좌석 성격을 설명하기 때문임.
- Candidate evidence status: 비교용 대표 히어로를 `candidate-a.html`, `candidate-b.html`로 저장하고 데스크톱·모바일 캡처를 남김. 이 캡처는 실제 최종 페이지 구현 이후 보완된 비교 증거라 선택 전 렌더 순서를 증명하지 않음. 최종 선택 구현은 아래 구현과 별도 브라우저 캡처로 검증함.

## Visual system

- Surface mode / dominant idea / focal point / information density: 야간 라운지의 따뜻한 조명과 모니터 블루를 사용하는 어두운 editorial surface. 첫 초점은 `원하는 좌석과 시간을 골라 보세요`와 총액 계산기임. 정보는 히어로에서 낮게, 계획 섹션에서 중간 밀도로 배치함.
- Product-specific visual signature: 실제 매장 사진 대신 제공된 콘셉트 이미지, 좌석 종류별 공간 역할, 원/시간 기반 금액 계산, 24시간 운영과 비예약 안내의 조합.
- Deliberate non-default composition choice and product rationale: 반복적인 feature card 그리드 대신 좌석 소개를 수평 비교 목록과 선택 가능한 계획 패널로 연결함. 사용자의 선택 결과가 바로 금액으로 바뀌어야 하기 때문임.
- Typography / spacing / color roles: 시스템 sans-serif와 숫자용 `font-variant-numeric: tabular-nums`, 4px 배수 간격. 배경 `#10100f`, 표면 `#171715`, 본문 `#f3efe7`, 보조 `#b9b1a5`, 액센트 `#e0a14a`, 액센트 대비색 `#1b140c`, 포커스 `#8dc5ff`.
- Radius / elevation strategy: 패널은 20px, 선택 컨트롤은 12px, 버튼은 10px. 이미지와 고정 요약 패널에만 얕은 그림자를 사용하고 일반 정보는 선과 여백으로 분리함.
- Image or media strategy: `../assets/cafe-hero.png` 한 장만 사용. 큰 화면에서는 우측 히어로 미디어로, 좁은 화면에서는 메시지 아래로 재배치하며 `aspect-ratio`와 `object-fit`으로 안정성을 유지함.
- Motion intent / reduced-motion behavior: 선택 변화와 메뉴는 짧은 opacity 및 transform 피드백만 사용하며 `prefers-reduced-motion: reduce`에서는 즉시 상태로 전환함.

## Engineering

- Framework / router / rendering model / styling system: 의존성 없는 정적 `index.html`, `styles.css`, `script.js`, 브라우저 네이티브 DOM과 CSS.
- Token source / reusable components: `:root`의 의미 기반 CSS 토큰과 좌석 옵션, 버튼, 요금표, 메뉴 패턴.
- State ownership / data boundary: `script.js`의 `seatPrices`와 `state`가 선택 상태를 소유함. 서버와 네트워크 없음.
- Browser support / performance risks / verification plan: 모던 Chromium 기준. 이미지 한 장의 로딩과 모바일 크롭, 콘솔 오류, 수평 넘침, 좌석 3종 × 시간 3종 계산, 확인·수정, 키보드, hover/pointerleave, 터치 에뮬레이션, reduced-motion을 Playwright로 검증함.

## First-render findings and correction

실제 첫 렌더는 `evidence-desktop.png`, `evidence-mobile.png`로 확인함. 이미지가 필요한 공간 설명을 담당하며 계획 패널이 방문 전 결정을 이어받음. 반복 카드와 과도한 장식이 핵심 선택을 가리는 클러스터는 관찰되지 않아 선택 컨트롤과 요금 결과를 유지함. 모바일에서 한국어 단어가 중간 분리되지 않도록 `word-break: keep-all`과 안전한 긴 문자열 줄바꿈을 전역에 적용함. 모바일 메뉴는 닫힘 상태에서 `visibility`와 `aria-hidden`으로 탭 순서에서 제외하고, Escape로 닫은 뒤 메뉴 버튼에 포커스를 돌려줌.

- Composition: pass. 1440×1000에서 좌측 메시지, 우측 공간 미디어, 아래 계획 흐름으로 시선이 연결되고 390×844에서 같은 DOM 순서를 유지함.
- Product storytelling: pass. `cafe-hero.png`가 공간을 설명하고 세 좌석의 역할과 요금이 텍스트로 이어짐.
- Hierarchy: pass. 좌석 선택, 시간 선택, 총액, `방문 계획 확인`의 순서가 계획 패널에서 명확함.
- Brand coherence: pass. 어두운 표면과 따뜻한 조명 색을 토큰으로 묶고 액센트의 hover, focus, 선택 상태를 공유함. 측정한 대비는 `--quiet`와 패널 배경 6.40:1, 주황 액센트와 어두운 글자 8.15:1, 본문과 어두운 배경 16.48:1임.
- Interaction polish: pass. 좌석 3종 × 시간 3종의 총액, 확인과 수정, 메뉴 열기·닫기, hover·pointer-out, 터치 탭, reduced-motion을 실제 브라우저에서 확인함.
- Generic-default cluster response: keep. 카드와 라운딩은 실제 좌석 선택과 계획 결과를 묶는 제품 역할이 있어 유지함. 가짜 후기, 지표, 주소와 추가 사진은 넣지 않음.

## Verification record

실제 실행 명령: `node candidate-evidence.mjs`, `node verify.mjs`.

- 후보 비교 캡처: `candidate-a-desktop.png`, `candidate-a-mobile.png`, `candidate-b-desktop.png`, `candidate-b-mobile.png`.
- 선택된 구현 캡처: `evidence-desktop.png`, `evidence-mobile.png`.
- 브라우저 범위: Playwright Chromium, 1440×1000 및 390×844 viewport, 터치 에뮬레이션, `prefers-reduced-motion: reduce`.
- 관찰 결과: 이미지 로딩, 콘솔 및 페이지 오류 없음, 두 viewport 수평 넘침 없음, 세 좌석 × 세 시간 계산 9개 통과, 확인과 수정 통과, Tab 및 visible focus 확인, 모바일 메뉴와 Escape focus return 통과, hover·pointer-out과 touch 메뉴 통과, reduced-motion 미디어 쿼리 통과. 최종 수정 뒤 `node verify.mjs` 전체 항목이 PASS임.
- 상태: `VERIFIED_KEYBOARD_FLOW`. 테스트 상태 범위의 자동 접근성 스캐너, 실제 모바일 기기, 보조기기, 대표 사용자 검증은 수행하지 않음.
- 제한: 후보 캡처는 대표 히어로와 계획 모듈 비교용이며 전체 제품 품질을 증명하지 않음. 한 번의 비교는 일반적인 우열이나 통계적 유효성을 입증하지 않음.
