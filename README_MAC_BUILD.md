# Mac에서 Windows EXE 빌드하기

Mac 환경에서 Windows EXE 파일을 빌드하는 3가지 방법입니다.

## 방법 1: Docker 사용 (권장) ⭐

### 설치
1. [Docker Desktop](https://www.docker.com/products/docker-desktop) 설치
2. Docker 실행

### 빌드
```bash
# 실행 권한 부여
chmod +x build_mac_to_windows.sh

# 빌드 실행
./build_mac_to_windows.sh
```

## 방법 2: Wine 사용

### 설치 및 빌드
```bash
# 실행 권한 부여
chmod +x build_with_wine.sh

# 빌드 실행 (자동으로 Wine 설치)
./build_with_wine.sh
```

## 방법 3: GitHub Actions 사용 (가장 쉬움) ⭐⭐

### 설정
1. GitHub에 코드 업로드
2. Repository Settings → Actions → General → Workflow permissions → "Read and write permissions" 선택
3. 코드 푸시하면 자동 빌드

### 수동 실행
1. GitHub 페이지에서 Actions 탭 클릭
2. "Build Windows EXE" 워크플로우 선택
3. "Run workflow" 버튼 클릭
4. 빌드 완료 후 Artifacts에서 다운로드

### 릴리즈 자동 생성
```bash
# 태그 생성시 자동으로 릴리즈 생성
git tag v1.0.0
git push origin v1.0.0
```

## 방법 4: Windows VM 사용

### Parallels Desktop 또는 VMware Fusion
1. Windows 11 VM 설치
2. Python 설치
3. `build_onefile.bat` 실행

## 빠른 시작 가이드

### 가장 빠른 방법 (GitHub Actions):
1. GitHub에 푸시
2. Actions 탭에서 다운로드

### 로컬에서 빌드 (Docker):
```bash
# Docker Desktop 실행 후
./build_mac_to_windows.sh
```

## 문제 해결

### Docker 빌드 실패
- Docker Desktop이 실행 중인지 확인
- 메모리 할당 늘리기: Docker Settings → Resources → Memory

### Wine 빌드 실패
- Wine 재설치: `brew reinstall wine-stable`
- Python 경로 확인: `wine64 python --version`

### 생성된 EXE가 실행 안됨
- Windows Defender 예외 추가 필요
- 관리자 권한으로 실행

## 빌드된 파일
- `release/JapaneseTextHooker.exe` - 기본 버전
- `release/AdvancedTextHooker.exe` - 고급 버전
- `release/TextHookerOverlay.exe` - 오버레이 + 번역 버전