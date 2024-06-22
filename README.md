# sparse-to-dense

labeling tool

## 실행 준비

### 저장소 클론

```bash
# 서드파티 서브모듈들이 포함된 저장소이므로 모두 함께 다운로드
git clone --recursive https://github.com/slink-to-unlock/sparse-to-dense
# 프로젝트 루트로 디렉토리 이동
cd sparse-to-dense
```

### 파일 준비

- `source.mov` 파일을 프로젝트 루트에 준비
- 다른 이름의 파일을 실행하고 싶다면 `sparse_to_dense/sparse/main.py` 파일을 수정할 것.

### 파이썬 의존성 설치

#### 실행 스크립트

```bash
{프로젝트_루트}$ python -m pip install -r requirements.txt
```
### 시스템 의존성 설치

- 서드파티 라이브러리의 의존성인 [ffmpeg](https://www.ffmpeg.org/) 설치
- 서드파티 디렉토리에 `video-splitter` 설치

## 실행

### 레이블러 실행

#### 동영상을 클립으로 분해

- T를 눌러서 클립으로 분절할 타이밍 명시
- Q를 눌러서 종료 (하나의 타이밍으로 계산됨)
- **NOTE**: MacOS환경에서 동영상이 되감기되지 않으므로 주의
- **NOTE**: 동영상이 맨 마지막까지 실행되면 자동으로 하나의 클립으로 인식함

#### 분해된 클립들을 0, 1 태깅

- 0을 눌러서 0으로 태깅, 1을 눌러서 1로 태깅
- **NOTE**: 메타데이터 태깅 과정에서 동일한 작업을 GUI로 실행할 수 있으므로 이 과정을 생략해도 됨.

#### 실행 스크립트

```bash
{프로젝트_루트}$ python -m sparse_to_dense.sparse.main
```

### 메타데이터 태깅 실행

#### 실행 스크립트

```bash
{프로젝트_루트}$ streamlit run sparse_to_dense/app/home.py
```

## 가보자가보자

- 여기에 나와 있는 하드코딩적 요소들을 제거
- dense 모드에서 같은 기능이 CLI와 GUI로 모두 제공되는 사용성 해결
  - index 기반으로 json에서 파싱하지 말고 경로를 바탕으로 선택하는 것이 나은 설계
- sparse 모드와 dense 모드가 잘 어우러지도록 변경
- Manager 객체들에 함수들이 제멋대로 값을 쓰는 캡슐화 문제 수정
- Manager 클래스가 너무 많은 권한을 가지고 만능 키처럼 쓰이고 있음
  - 객체의 정보가 파일에 동시에 동기화되는 방식이 너무 원시적임
    - 이 문제가 해결되어야 다음과 같은 상황에 대응 가능
      - 처음에 불러올 비디오가 n개가 되는 경우
      - 레이블링 도중에 다른 `raw`비디오가 추가되는 경우
  - 이것을 어떻게 수정할 수 있을지에 대한 중장기적인 고민이 필요
- 환경 이슈를 줄이기 위해 도커로 패킹하여 제공
