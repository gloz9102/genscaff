# 동일 브리프 비교

[English](comparison.md) | [한국어](comparison.ko.md)

이 문서는 2026년 7월 30일에 진행한 정성 A/B 실행 1회를 기록한다. 검토 가능한 근거이며 벤치마크나 인과관계 증명은 아니다.

## 조건

| 통제 항목 | 값 |
|---|---|
| 모델 | 서로 독립적인 `terra-medium` 에이전트 2개 |
| 브리프 | 물류센터 입고 지연 위험 건을 찾고, 원인을 확인한 뒤 담당자에게 조치를 요청하는 반응형 운영 대시보드 |
| 구현 | 외부 의존성·자산 없는 단일 HTML/CSS/JavaScript, 한국어 문구 |
| 처리 조건 | 한쪽은 Genscaff Standard 사용, 대조군은 Genscaff를 읽거나 사용하지 않음 |
| 브라우저 확인 | 데스크톱·모바일 레이아웃, 요청·취소 흐름, 콘솔 오류와 경고 |

## 데스크톱 초기 상태

| Genscaff Standard 적용 | Genscaff 미적용 |
|---|---|
| ![Genscaff Standard 데스크톱 결과](assets/comparison/genscaff-with.png) | ![미적용 데스크톱 결과](assets/comparison/genscaff-without.png) |

## 모바일 초기 상태

| Genscaff Standard 적용 | Genscaff 미적용 |
|---|---|
| ![Genscaff Standard 모바일 결과](assets/comparison/genscaff-with-mobile.png) | ![미적용 모바일 결과](assets/comparison/genscaff-without-mobile.png) |

## 조치 요청 완료 상태

| Genscaff Standard 적용 | Genscaff 미적용 |
|---|---|
| ![Genscaff Standard 요청 완료 상태](assets/comparison/genscaff-with-terminal.png) | ![미적용 요청 완료 상태](assets/comparison/genscaff-without-terminal.png) |

## 관찰 결과

- Genscaff 적용 결과는 위험 건 선택, 원인 확인, 담당자·SLA 지정, 요청 전송, 취소 복구로 이어지는 단일 작업 흐름을 강조했다.
- 미적용 결과는 일반적인 대시보드 탐색, KPI 요약, 더 넓은 운영 화면 구성을 강조했다.
- 두 결과 모두 반응형이며 상호작용이 동작했다. 확인한 흐름에서 브라우저 콘솔 오류와 경고는 없었다.
- Genscaff 실행은 시각 목표와 검증 기록도 생성했고, 미적용 실행은 구현 파일만 생성했다.

## 한계

조건별 샘플이 하나뿐이다. 독립 에이전트 차이, 생성 무작위성, 주관적인 디자인 판단이 결과에 영향을 줄 수 있다. 스크린샷은 이번 실행 결과를 보여줄 뿐 Genscaff가 항상 더 보기 좋은 인터페이스를 만들거나 관찰된 차이가 오직 스킬 때문에 발생했다는 사실을 증명하지 않는다.
