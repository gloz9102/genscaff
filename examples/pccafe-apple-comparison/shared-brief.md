# NOON PC Apple-principle comparison brief

- Created: 2026-08-05T10:35:00+09:00
- Comparison variable: Genscaff Standard workflow applied vs not applied
- Shared asset: `assets/noon-pc-hero-v1.jpg` (각 결과에서는 `../assets/noon-pc-hero-v1.jpg`로 참조)

## Identical implementation prompt

아래 요구사항을 만족하는 standalone 단일 페이지 웹사이트를 구현한다.

1. 가상 브랜드 `NOON PC`의 PC방 프랜차이즈 상품 웹사이트다.
2. Apple 웹사이트의 원칙인 한 제품 중심의 첫 화면, 짧고 직접적인 카피, 넓은 여백, 소수의 명확한 액션, 고품질 이미지 중심 전개를 참고한다. Apple 상표·카피·에셋·정확한 레이아웃은 복제하지 않는다.
3. 제공된 동일 이미지 `../assets/noon-pc-hero-v1.jpg`를 히어로의 핵심 시각 자료로 사용한다.
4. 첫 화면에서 PC방 프랜차이즈, 매장 공간, 45·60·80평 모델 선택, 선택 결과, 상담 CTA를 이해할 수 있어야 한다.
5. 기본 선택은 60평이다. 모델을 바꾸면 예상 좌석, RTX 존, 팀룸, 설계 전력과 상담 CTA가 함께 바뀐다.
6. CTA는 상담 요약 dialog를 열고, 상권 입력 검증, 완료 결과, 내용 수정과 닫기 복구를 실제로 제공한다. 외부 전송은 하지 않으며 가상 데모임을 고지한다.
7. 사용자 노출 한국어는 존댓말을 기본으로 한다. 반말과 `~함`, `~음`, `~됨` 형태의 음슴체를 사용하지 않는다. 짧은 제목은 명사형 단답을 사용할 수 있다.
8. 1440px 데스크톱과 390px 모바일에서 가로 넘침 없이 동작하고 키보드 포커스가 보여야 한다.
9. 외부 패키지나 프레임워크 없이 `index.html` 하나로 구현한다.

## Shared visual target

- Target user: 상가 면적에 맞는 PC방 좌석·전력 구성을 검토하는 예비 점주
- Primary task: 45·60·80평 중 하나를 선택하고 상권 상담 요약을 완료한 뒤 수정하거나 닫는다.
- Success outcome: 선택 평형과 운영 수치, 입력 상권이 완료 화면에 보이고 복구할 수 있다.
- Primary CTA: `60평 상담 구성 확인하기`
- Domain objects: 전용 평형, 예상 좌석, RTX 존, 팀룸, 설계 전력, 상권, 상담 구성
- Direction A: 흰 배경과 대형 매장 이미지 중심의 고요한 제품 편집형
- Direction B: 검은 배경과 좌석 데이터 중심의 운영 대시보드형
- Selected direction: Direction A. Apple의 참고 원칙과 공간 이미지의 품질을 비교하기에 적합하다.
- Desktop: 얇은 내비게이션, 중앙 카피와 소수 액션, 대형 매장 이미지, 모델 선택과 수치 결과
- Mobile: 카피, CTA, 이미지, 모델 선택을 한 열로 재배치하고 16px 측면 여백 유지
- Palette: 흰색·검정·회색 중심, 라임은 선택과 핵심 CTA에만 제한
- Typography: 시스템 산세리프, 굵기 세 단계 이하, 짧은 문장
- Radius: 두 단계 이하. 그림자는 dialog에만 사용
- Forbidden: 무지개 RGB, 유리 카드, 네온 그라디언트, 가짜 수익·점포 수·후기, Apple 로고나 제품 카피 복제
- Evidence: 동일한 1440×1000 및 390×844 시작 화면, 상담 완료 화면, 오버플로·콘솔·키보드 확인
