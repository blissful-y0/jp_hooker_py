# Japanese Text Hooker - 빌드 가이드

## 필요 사항
- Windows 10/11
- Python 3.8 이상

## EXE 파일 만들기

### 방법 1: PyInstaller 사용 (권장)

#### 옵션 A: 여러 파일로 빌드
```batch
build.bat
```
- 실행 속도가 빠름
- 바이러스 백신 오탐 가능성 낮음

#### 옵션 B: 단일 파일로 빌드
```batch
build_onefile.bat
```
- 하나의 EXE 파일로 모든 기능 포함
- 휴대성이 좋음
- 첫 실행시 약간 느림

### 방법 2: cx_Freeze 사용 (대안)
```batch
build_cx_freeze.bat
```
- PyInstaller가 작동하지 않을 때 사용

## 빌드된 파일 위치
- `release/` 폴더에 생성됨
- `JapaneseTextHooker.exe` - 기본 버전
- `AdvancedTextHooker.exe` - 고급 버전 (관리자 권한 필요)

## 문제 해결

### "Python이 설치되지 않음" 오류
1. https://www.python.org/ 에서 Python 설치
2. 설치시 "Add Python to PATH" 체크

### 바이러스 백신 오탐
- Windows Defender에서 예외 추가
- 또는 `build.bat` 사용 (단일 파일 대신)

### 실행시 오류
- 관리자 권한으로 실행
- Windows Defender 실시간 보호 일시 중지 후 빌드

## 직접 Python으로 실행
```batch
pip install -r requirements.txt
python text_hooker.py
```