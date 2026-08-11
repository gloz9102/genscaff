## Visual Target

Artifact:
- Saved local path: `examples/pccafe-franchise-product-editorial/index.html`
- Created at with timezone: `2026-08-05T09:42:09+09:00`
- Baseline repository or source context: 새 standalone 예시. 기존 두 예시와 구현 파일을 공유하지 않음.

Product:
- What is being built: 가상 PC방 프랜차이즈 `NOON PC`의 예비 점주용 웹사이트.
- Primary user: PC방 창업을 검토하며 상가 면적과 상권에 맞는 좌석 구성이 필요한 예비 점주.
- User need: "내 점포 크기에서 좌석 수, 좌석 등급, 동선이 어떻게 구성되는지 먼저 보고 싶다."
- Primary task: 45/60/80평 모델을 비교하고 하나를 선택해 상권 검토 요청서를 만든다.
- Observable success outcome: 선택 평형, 예상 좌석, GPU 존 구성, 입력 상권이 완료 패널에 유지되고 수정할 수 있다.
- Primary action: 선택 모델로 상권 검토 요청서 만들기.
- Single primary CTA: `60평 상권 검토 요청서 만들기`.
- Recovery path: 완료 패널의 `내용 수정`으로 기존 선택과 입력을 유지한 채 폼으로 돌아간다.
- Domain objects and vocabulary: 평형, 좌석 수, GPU 존, 프리미엄석, 팀룸, 흡배기 동선, 전력 여유, 상권, 상가 보유 상태.
- Non-cosmetic differentiators: 평형 선택이 좌석 수·좌석 믹스·필요 전력·CTA를 동시에 바꾼다. 상권과 상가 상태가 요청서에 보존된다.
- User-provided facts: PC방 프랜차이즈 웹사이트 제작, 아키타입 자율 선택.
- Repository evidence: Genscaff에 `product-editorial`과 `transaction` craft가 존재함.
- External research: 없음. 번들 Apple의 단일 제품 집중, Linear의 실제 작업면 우선 원칙만 사용함.
- Explicit assumptions: 브랜드, 수치, 공간 구성, 장비 등급은 전부 가상 데모 데이터이며 실제 수익·가맹 조건을 주장하지 않음.

Direction Decision:
- Direction A and product/task fit: 어두운 운영 설계도 중심. 실제 좌석 배치·존·전력 수치를 첫 화면에서 조작하고 판단함.
- Direction B and product/task fit: 감성 매장 사진 중심. 분위기는 강하지만 허구 사진과 추상 카피가 창업 결정을 대신할 위험이 큼.
- Selected direction: Direction A.
- Selection rationale: 예비 점주의 다음 결정은 브랜드 분위기보다 면적당 좌석, 좌석 등급, 전력과 동선의 구체적 결과에 달려 있음.

Expanded Brief:
- Brief created before coding: yes.
- Preserved user constraints: PC방 프랜차이즈 사이트, 적절한 아키타입 자율 선택.
- Added domain-specific sections: 실시간 좌석 평면, 모델 선택, 장비·동선 설명, 상권 검토 폼, 완료·수정 상태.
- Shared components: 모델 세그먼트, 평면도 셀, 사양 행, 대화상자, 폼, 상태 메시지.
- Layout board or page structure: 첫 화면에서 브랜드 설명과 좌석 설계도를 함께 보여주고, 아래에 운영 설계 근거와 요청 흐름을 둠.
- Requirement trace: 프랜차이즈 상품 이해는 평면도와 운영 데이터, 상담 전환은 선택 모델 기반 요청서로 증명함.

Benchmark Direction:
- Reference site(s) inspected or research fallback used: 번들 Apple·Linear 관찰 원칙.
- Reference signals: 한 제품 표면이 지배하는 집중도, 실제 워크플로 데이터를 첫 화면에서 보여주는 방식.
- Same-domain or same-interaction-model relevance: 복잡한 B2B 상품을 구체적 도구와 수치로 이해시키는 상호작용 모델.
- Why these references fit: 예비 점주가 브랜드 카피보다 실제 구성 결과를 먼저 판단해야 함.
- What not to copy: 브랜드, 로고, 카피, 색 조합, 내비게이션, 제품 이미지, 구도, 전환 효과를 복제하지 않음.

Composition:
- Desktop: 12열 그리드. 왼쪽 서사 5열, 오른쪽 좌석 설계도 7열. 아래 운영 근거는 평면 구획형 섹션.
- Mobile: 제목→모델 선택→좌석 설계도→핵심 수치→CTA 순서. 모달은 전체 폭 시트처럼 동작함.
- First viewport must show: PC방 가맹 상품, 선택 평형, 예상 좌석, GPU 존, 전력 여유, 상권 검토 CTA.
- Main visual anchor: 선택 모델에 따라 다시 그려지는 좌석 평면도.
- Information density limit: 첫 화면은 모델 선택에 필요한 4개 결과만 노출. 세부 공사·계약·수익 내용은 제외.
- Deferred or removed details: 실제 가맹비, 매출, 수익률, 가맹점 수, 고객 후기, 인증, 지도, 결제.
- Product-specific decision shown: 어느 평형 모델을 상권 검토 대상으로 삼을지.
- Inputs needed for that decision: 전용 면적, 좌석 수, GPU 존 비중, 팀룸, 전력 여유.
- Consequence of the decision: 평면도, 운영 수치, CTA와 요청서 요약이 바뀜.

System:
- Existing tokens/components to reuse: standalone 예시에 공용 디자인 시스템 없음.
- Local token fallback if no theme exists: CSS custom properties로 배경·표면·텍스트·경계·액센트·포커스·성공·오류를 정의함.
- Typography: 시스템 산세리프. 12/14/16/18/20/24/32px, 3개 weight.
- Spacing and density: 4/8/12/16/24/32/48/64px.
- Color and contrast: 흰 페이지, 검은 첫 제품 표면, 산뜻한 라임 단일 액센트, 상태색은 의미가 있을 때만 사용.
- Background policy: 페이지 기본은 white. 첫 제품 설계도 구역만 기능적 black inverse surface.
- Background variation confirmation: inverse surface는 좌석 설계도와 전력 경로를 명료하게 보여주는 제품 표면임.
- Color token map: `--bg`, `--surface`, `--surface-inverse`, `--text`, `--text-inverse`, `--muted`, `--border`, `--accent`, `--focus`, `--success`, `--danger`.
- Accent/status color limits: 라임은 선택·CTA·전력 경로만, 빨강은 입력 오류만.
- Von Restorff emphasis target: 현재 선택 모델과 상권 검토 CTA.
- Radius and shadow levels: 8px/16px, 모달 그림자 1개.
- Border minimization: 입력과 평면 셀, 데이터 행 구분에만 사용.
- Border-radius minimization: 모델 세그먼트와 모달에만 사용. 평면도 셀은 4px 고정.
- Box-shadow usage: 모달 외 금지.
- List item border/shadow treatment: 운영 사양 행은 구분선만 사용.
- Necessary badges/titles only: `가상 설계 데이터`와 좌석 존 라벨만 유지.
- Word-break and wrapping: 한국어 어절 단위, 긴 상권명은 overflow-wrap.
- Components: semantic buttons, fieldset, dialog-like modal, labeled inputs, live status.
- Imagery or media: 외부 이미지 없이 CSS 좌석 평면도와 전력 라인으로 상품 구조를 설명함.
- Motion: 선택과 모달 전환 180ms. reduced-motion에서 제거.

Copy:
- Primary message: `좌석 수보다 먼저, 좌석의 이유를 설계함.`
- Domain terms that must appear: 60평, 82석, RTX 존, 팀룸, 흡배기, 전력 여유, 상권 검토.
- Generic terms or claims to remove: 혁신, 프리미엄 경험, 압도적 수익, 성공 창업.
- Sentence density rule: 한 문장에 한 주장.
- Copy length rule: 본문 45자 안팎, 버튼은 결과를 명시함.
- Redundant copy to avoid: 제목을 반복하는 섹션 설명과 근거 없는 브랜드 찬사.

States:
- Loading: 원격 경계가 없는 로컬 데모라 not applicable.
- Empty: not applicable. 안전 기본값 60평이 항상 존재함.
- Error: 상권명 미입력 시 필드 근처 오류와 포커스 이동.
- Disabled: 제출 중복 방지 상태는 동기 처리라 not applicable.
- Hover/focus/active: 모든 버튼·입력에 명확한 상태와 3px focus ring.
- Long content and extreme values: 긴 상권명 입력과 80평 112석 모델을 검증함.

Action Continuity:
- CTA cue and information scent: 선택 평형, 예상 좌석, 전력, 팀룸이 CTA 바로 위에 있음.
- Start state and preconditions: 안전 기본값 60평 선택. 상권명만 필수 입력.
- Immediate feedback: CTA 클릭 시 선택 모델이 유지된 요청 폼이 열림. 유효성 오류는 필드 아래 표시됨.
- Result or destination: 요청서 준비 완료 패널에 모델·좌석·상권·상가 상태가 표시됨.
- Terminal state: `상권 검토 요청서가 준비됨`.
- Recovery: `내용 수정`으로 입력을 유지한 폼에 복귀, `닫기`로 선택 화면 복귀.
- Functional, disabled, and prototype-only controls: 모든 버튼은 기능함. 실제 접수가 아닌 로컬 기능 데모임을 모달과 완료 패널에 고지함.

Product Specificity:
- Domain signal 1: 평형별 좌석 수·GPU 존·팀룸·전력 여유가 바뀌는 평면도.
- Domain signal 2: 좌석 구역과 흡배기·전력 동선을 설명하는 운영 설계 행.
- Domain signal 3: 선택 모델과 상권·상가 상태를 보존하는 검토 요청서.
- Unrelated substitution domain 1 and breaking signals: 피부과 사이트는 좌석 존, GPU 등급, 전력 여유, 팀룸 평면을 재사용할 수 없음.
- Unrelated substitution domain 2 and breaking signals: 식품 구독 사이트는 평형·흡배기·좌석 수·상권 검토 요청 흐름을 재사용할 수 없음.
- Why name, logo, and color are not the only specific signals: 데이터 모델, 평면도, 결정 입력, 결과 문서가 PC방 창업에 종속됨.

Anti-Slop Risks:
- Visual slop risk: 네온 그라디언트와 유리 카드로 게임 분위기를 대신하는 것.
- Content slop risk: 실제 근거 없는 매출·가맹점 수·성공률을 수치로 제시하는 것.
- Interaction slop risk: 모델 버튼·상담 CTA·폼이 보이지만 상태를 바꾸지 않는 것.
- Verification slop risk: 초기 화면 한 장만 보고 제출 흐름을 통과했다고 주장하는 것.
- UI craft risk: 검은 화면에서 라임과 흰 텍스트가 과다 경쟁하거나 모바일 평면도가 잘리는 것.

Verification Preflight:
- Dev-server or direct-open command: `python -m http.server 4175 --directory examples/pccafe-franchise-product-editorial`.
- Desktop/mobile browser and capture method: Codex in-app browser 1440x1000, 390x844.
- Interaction walkthrough method: 모델 선택, 모달 열기, 필수 오류, 유효 제출, 내용 수정, 닫기.
- Lighthouse JSON command: 기존 로컬 Lighthouse CLI와 Chromium 사용, `artifacts/lighthouse.json` 저장.
- Repository lint/typecheck/test/build commands: standalone HTML 정적 점검과 브라우저 실행. 별도 빌드 없음.
- Required dependencies confirmed: 이전 예시 검증에서 Python 서버, 브라우저, Chromium, Lighthouse 확인됨.
- Quality report path: `examples/pccafe-franchise-product-editorial/quality-report.json`.
- Evidence catalog ID convention: `pccafe-{viewport}-{state}`.

Visual Comparison Plan:
- Brand reference principle to compare: Apple의 단일 제품 집중과 Linear의 실제 작업면 우선.
- UI craft guideline to compare: 한 액센트, 최소 경계·그림자, 첫 뷰포트 제품 가시성.
- AI slop counterexample to reject: 네온 그라디언트, 가짜 매출 지표, generic hero+3 cards.
- Desktop screenshot evidence: 시작·오류·완료.
- Mobile screenshot evidence: 시작·오류·완료.
- Expected iteration count: 최소 2회, 실제 수정 1회 이상.
- Primary-task desktop walkthrough evidence: 80평 선택→요청 폼→오류→유효 제출→수정.
- Primary-task mobile walkthrough evidence: 45평 선택→요청 폼→유효 제출→닫기.
- Lighthouse JSON artifact: `artifacts/lighthouse.json`.
- Independent reviewer and blinded questions: 제품·대상·과업 식별, 제품 신호, 행동 연속성, generic/오도 요소.

Acceptance:
- Screenshot should prove: 첫 화면에서 PC방 프랜차이즈와 평형별 좌석 설계 결정이 보임.
- Task walkthrough should prove: 모델 선택 결과가 요청서에 유지되고 오류와 수정 복구가 동작함.
- Substitution test should prove: 피부과와 식품 구독으로 이름만 바꿀 수 없음.
- Requirement trace should prove: 사용자 요청, 아키타입 선택, 프랜차이즈 상품 이해와 상담 전환이 UI·행동 증거로 연결됨.
- Lighthouse target: performance 80+, accessibility 90+, best practices 90+, SEO 90+.
- Commands to run: 서버, 브라우저 데스크톱·모바일 흐름, Lighthouse, 품질 리포트 validator.
