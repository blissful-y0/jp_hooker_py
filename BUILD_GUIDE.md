# 빌드 가이드

## GitHub Actions로 Windows EXE 빌드하기

### 1. GitHub 저장소 설정

#### 새 저장소 생성
1. [GitHub](https://github.com)에 로그인
2. "New repository" 클릭
3. Repository name 입력
4. "Create repository" 클릭

#### 로컬 코드 연결
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 2. 자동 빌드 실행

#### 방법 1: 스크립트 사용
```bash
./push_to_github.sh
```

#### 방법 2: 수동 실행
1. GitHub 저장소 페이지 → Actions 탭
2. "Build Windows EXE" 워크플로우 선택
3. "Run workflow" 버튼 클릭
4. "Run workflow" 확인

### 3. EXE 파일 다운로드

빌드 완료 후 (약 2-3분):
1. Actions 탭 → 최신 워크플로우 클릭
2. "Artifacts" 섹션에서 `windows-executables` 다운로드
3. ZIP 파일 압축 해제

### 4. 릴리즈 생성 (선택사항)

태그를 푸시하면 자동으로 릴리즈 생성:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 생성되는 파일

- `JapaneseTextHooker.exe` - 기본 텍스트 후킹
- `AdvancedTextHooker.exe` - 고급 메모리 스캔 (관리자 권한)
- `TextHookerOverlay.exe` - 오버레이 + Gemini 번역

## 문제 해결

### Actions가 실행되지 않음
- Settings → Actions → General → "Allow all actions" 선택
- Workflow permissions → "Read and write permissions" 선택

### 빌드 실패
- requirements.txt 파일 확인
- Python 코드 문법 오류 확인

### EXE가 실행되지 않음
- Windows Defender 실시간 보호 일시 중지
- 관리자 권한으로 실행