# 상품 페이지 동일 브리프 비교

[English](slowdrop-comparison.md) | [한국어](slowdrop-comparison.ko.md)

이 문서는 2026년 7월 31일에 진행한 정성 A/B 실행 1회를 기록합니다. 검토 가능한 근거이며 벤치마크나 인과관계 증명은 아닙니다.

## 조건

| 통제 항목 | 값 |
|---|---|
| 모델 | 서로 독립적인 `terra-medium` 에이전트 2개 |
| 브리프 | 1~2인 가구와 작은 주방을 위한 가상의 Slowdrop Mini 콜드브루 메이커 한국어 반응형 상품 페이지 |
| 제품 정보 | 900mL 내열 유리 카라페, 6/12/18시간 밸브, 재사용 80μm 스테인리스 필터, 폭 14cm, 무료배송, 미사용 제품 30일 반품 |
| 구매 흐름 | 스타터 키트 3종, 원두·합계 즉시 갱신, 데모 장바구니 담기, 명확한 완료 요약, 제거와 복구 |
| 구현 | 외부 라이브러리·폰트·이미지·네트워크 요청이 없는 단일 HTML/CSS/JavaScript 파일 |
| 처리 조건 | 한쪽은 Genscaff Standard의 상품·커머스 경로를 사용했고, 대조군은 Genscaff를 읽거나 사용하지 않았습니다. |
| 브라우저 확인 | 데스크톱 1440×1000, 모바일 390×844에서 옵션 변경, 담기, 제거·복구, 콘솔 경고·오류, 가로 오버플로를 확인했습니다. |

## 데스크톱 초기 상태

| Genscaff Standard 적용 | Genscaff 미적용 |
|---|---|
| ![Genscaff Standard Slowdrop 데스크톱 초기 상태](assets/slowdrop-comparison/genscaff-with.png) | ![미적용 Slowdrop 데스크톱 초기 상태](assets/slowdrop-comparison/genscaff-without.png) |

## 모바일 초기 상태

| Genscaff Standard 적용 | Genscaff 미적용 |
|---|---|
| ![Genscaff Standard Slowdrop 모바일 초기 상태](assets/slowdrop-comparison/genscaff-with-mobile.png) | ![미적용 Slowdrop 모바일 초기 상태](assets/slowdrop-comparison/genscaff-without-mobile.png) |

## 장바구니 담기 완료 상태

| Genscaff Standard 적용 | Genscaff 미적용 |
|---|---|
| ![Genscaff Standard Slowdrop 장바구니 상태](assets/slowdrop-comparison/genscaff-with-terminal.png) | ![미적용 Slowdrop 장바구니 상태](assets/slowdrop-comparison/genscaff-without-terminal.png) |

## 관찰 결과

- 두 결과 모두 같은 소형 콜드브루 제품의 특성을 구체적으로 표현했고 시각적 완성도도 충분했습니다. 이번 실행만으로 Genscaff 적용 결과가 미적으로 항상 더 낫다고 말할 수는 없습니다.
- Genscaff 적용 결과는 키트를 선택하지 않은 상태에서 시작하고 선택 전에는 구매를 막았습니다. 배송·반품 조건을 구매 판단 영역에 함께 제시했으며, 담기 이후에는 제거와 구성 변경 두 가지 복구 동작을 제공했습니다.
- 미적용 결과는 클래식 키트를 기본 선택했고 더 강한 편집 디자인의 첫 화면과 즉시 사용할 수 있는 구매 버튼을 제공했습니다. 완료 상태는 더 압축적이지만 제거 동작은 유지했습니다.
- 두 결과 모두 프루티 키트를 157,000원으로 갱신했고 제거 후 선택 상태를 유지했습니다. 확인한 데스크톱·모바일 흐름을 통과했으며 콘솔 경고·오류와 가로 오버플로가 없었습니다.
- Genscaff 실행은 시각 목표와 검증 기록도 생성했고, 미적용 실행은 구현 파일만 생성했습니다.

## 검증 및 한계

같은 루트 검토자가 동일한 인앱 브라우저와 viewport 크기에서 두 페이지를 직접 실행했습니다. 두 페이지 모두 첫 시각·상호작용 검사 이후 수정이 필요하지 않았습니다. 조건별 샘플이 하나뿐이므로 스킬의 영향과 독립 에이전트 차이, 생성 무작위성, 주관적인 디자인 판단을 분리할 수 없습니다. 스크린샷은 이번 실행 결과를 보여줄 뿐이며, Genscaff가 항상 더 보기 좋은 페이지를 만들거나 관찰된 모든 차이가 스킬 때문에 발생했다는 사실을 증명하지 않습니다.
