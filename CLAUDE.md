# 프로젝트 가이드

## 프로젝트 개요

`json_lib`를 데이터 저장소로 사용하는 **JSON 파일 기반 CRUD 콘솔 애플리케이션**입니다.

### 완료된 구성 요소

`json_lib`는 구현이 완료된 자체 JSON 라이브러리입니다. 외부 `json` 모듈 없이 파싱과 직렬화를 직접 처리합니다.

```
json_lib/
├── __init__.py     # 공개 API: load(file_path), dump(data, file_path, indent)
├── lexer.py        # 문자열 → 토큰 스트림
├── parser.py       # 토큰 스트림 → Python 객체
└── serializer.py   # Python 객체 → JSON 문자열
```

### 개발할 구성 요소

JSON 파일을 데이터베이스로 사용하는 콘솔 애플리케이션을 Phase 단위로 개발합니다.

```
app/                # 애플리케이션 소스
tests/              # 전체 테스트 (json_lib + app)
```

---

### CRUD 기능 요구사항
- Create: 새로운 데이터를 입력 받아JSON 파일에 저장.
- Read: 전체 목록 보기및특정ID/키값으로검색기능.
- Update: 기존 데이터를 선택하여특정필드수정.
- Delete: 특정 데이터를 안전하게삭제.


## 개발 원칙

### 1. Phase 단위 진행

구현은 Phase 단위로 순서대로 진행합니다. Phase는 프로젝트 진행에 따라 추가될 수 있습니다.

**각 Phase가 완료된 시점에 해당 기능이 독립적으로 동작해야 합니다.** 사용자가 직접 실행하거나 테스트를 통해 검증할 수 있는 상태여야 하며, 미완성 상태로 다음 Phase로 넘어가지 않습니다.

### 2. TDD (Test-Driven Development)

각 Phase는 반드시 다음 순서로 진행합니다.

```
① 테스트 작성  →  ② 테스트 실행 (실패 확인)  →  ③ 구현  →  ④ 회귀 검증
```

- 구현 코드보다 **테스트를 먼저** 작성합니다.
- 테스트가 실패하는 상태(Red)에서 시작하여, 통과(Green)하는 최소한의 코드를 작성합니다.
- 테스트 파일은 `tests/test_<모듈명>.py` 형식으로 작성합니다.
- 테스트 프레임워크는 `unittest`를 사용합니다.

### 3. 회귀 검증 (Phase 완료 시 자동 수행)

**각 Phase 구현이 완료되면 사용자에게 보고하기 전에 반드시 스스로 회귀 검증을 수행합니다.**

#### 검증 절차

```
Step 1. 현재 Phase 테스트 실행  →  전체 통과 확인
Step 2. 전체 테스트 스위트 실행  →  이전 Phase 테스트가 깨지지 않았는지 확인
Step 3. 실패한 테스트가 있으면   →  원인을 파악하고 수정 후 Step 1부터 재시작
Step 4. 모두 통과한 경우에만     →  사용자에게 완료 보고
```

#### 검증 명령

```bash
# Step 1: 현재 Phase 테스트 (Phase가 추가될 때마다 목록에 추가)
.venv/Scripts/python -m pytest tests/test_<모듈명>.py -v

# Step 2: 전체 회귀 검증 (항상 실행 — json_lib 테스트 포함)
.venv/Scripts/python -m pytest tests/ -v
```

- 회귀 검증 결과(통과 수, 실패 수)를 완료 보고 시 함께 사용자에게 전달합니다.

---

## 작업 지침

- 새로운 Phase를 시작하기 전에 이전 Phase의 모든 테스트가 통과했는지 확인합니다.
- 데이터 저장/로드는 반드시 `json_lib.load()` / `json_lib.dump()`를 사용합니다. 표준 라이브러리의 `json` 모듈은 사용하지 않습니다.
- 콘솔 입출력은 표준 `input()` / `print()`를 사용합니다. 외부 UI 라이브러리는 사용하지 않습니다.

### json_lib 수정 금지

`json_lib/` 디렉터리 하위 파일(`__init__.py`, `lexer.py`, `parser.py`, `serializer.py`)은 구현이 완료된 코드입니다. **어떠한 경우에도 수정하지 않습니다.**

- 기능이 부족하거나 동작이 예상과 다르더라도 `json_lib`를 직접 수정하는 대신 애플리케이션 레이어에서 해결합니다.
- `json_lib`의 테스트(`tests/test_lexer.py`, `tests/test_parser.py`, `tests/test_serializer.py`, `tests/test_integration.py`)도 수정하지 않습니다.
