# 상품 소개 페이지 동일 브리프 비교

[English](product-page-comparison.md) | [한국어](product-page-comparison.ko.md)

이 문서는 2026년 7월 31일에 진행한 정성 A/B 실행 1회를 기록합니다. 한 번의 실행에서 얻은 검토 가능한 근거이며 벤치마크나 인과관계 증명은 아닙니다.

## 조건

| 통제 항목 | 값 |
|---|---|
| 모델 | 서로 독립적인 `terra-medium` 에이전트 2개 |
| 브리프 | 가상의 실내 수경재배기 Mori One을 소개하고 6포드 재배 데크, 24W 높이 조절 LED, 4L 물탱크, 약 21일 첫 수확을 설명한 뒤 바질·샐러드·믹스 스타터 키트를 선택하도록 구성 |
| 핵심 흐름 | 믹스 키트 선택, 데모 장바구니 추가, 장바구니 요약 확인, 제거 후 초기 상태 복구 |
| 구현 | 조건별 단일 HTML/CSS/JavaScript 파일, 한국어 문구, 외부 의존성·자산·폰트·네트워크 요청 없음 |
| 처리 조건 | 한쪽은 Genscaff Standard를 사용하고 대조군은 Genscaff를 읽거나 사용하지 않음 |
| 브라우저 확인 | CSS viewport 1440×1000 및 390×844, 가로 오버플로, 핵심 흐름, 복구, 콘솔 오류와 경고 |

Genscaff 실행은 제품 계약, 시각 목표, 검증 기록을 생성했습니다. 첫 브라우저 캡처에서 CSS 클래스 충돌과 한국어 줄바꿈 결함이 발견됐고, 같은 에이전트가 브라우저 근거를 바탕으로 두 차례 수정했습니다. 미적용 결과는 루트 시각 검사를 수정 없이 통과했습니다.

## 데스크톱 초기 상태

| Genscaff Standard 적용 | Genscaff 미적용 |
|---|---|
| ![Genscaff Standard 데스크톱 상품 페이지](assets/product-comparison/product-with-genscaff-desktop.png) | ![미적용 데스크톱 상품 페이지](assets/product-comparison/product-without-genscaff-desktop.png) |

## 모바일 초기 상태

| Genscaff Standard 적용 | Genscaff 미적용 |
|---|---|
| ![Genscaff Standard 모바일 상품 페이지](assets/product-comparison/product-with-genscaff-mobile.png) | ![미적용 모바일 상품 페이지](assets/product-comparison/product-without-genscaff-mobile.png) |

## 장바구니 완료 상태

| Genscaff Standard 적용 | Genscaff 미적용 |
|---|---|
| ![Genscaff Standard 장바구니 완료 상태](assets/product-comparison/product-with-genscaff-terminal.png) | ![미적용 장바구니 완료 상태](assets/product-comparison/product-without-genscaff-terminal.png) |

## 관찰 결과

- Genscaff 적용 결과는 주석이 포함된 제품 구조와 스타터 키트 결정을 히어로 가까이에 배치해 상품 정보와 핵심 작업을 긴밀하게 연결했습니다.
- 미적용 결과는 더 전형적인 프리미엄 커머스 위계를 사용했으며 첫 화면 구성이 더 정돈됐고 장바구니 수량과 키트별 가격을 명확하게 표시했습니다.
- Genscaff의 근거 반복 과정은 정적 검사에서 놓친 제품 도식 라벨 겹침과 모바일 한국어 줄바꿈 결함을 발견하고 수정했습니다.
- 두 결과 모두 필수 사양 4개를 표시하고 선택·추가·제거 흐름을 완료했으며 가로 오버플로와 확인된 콘솔 오류·경고가 없었습니다.

## 한계

조건별 샘플이 하나뿐이고 가상의 상품 하나와 주관적인 시각 판단을 사용했습니다. 독립 에이전트 차이와 생성 무작위성도 결과에 영향을 줄 수 있습니다. 첫 루트 캡처에서 Genscaff 적용 결과에만 시각적 결함이 발견되어 수정 횟수가 비대칭입니다. 이 스크린샷은 이번 실행 결과를 보여줄 뿐이며, 어느 조건이 항상 더 좋은 상품 소개 페이지를 만들거나 관찰된 차이가 오직 Genscaff 때문에 발생했다는 사실을 증명하지 않습니다.
