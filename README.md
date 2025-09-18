# Japanese Text Hooker 🎮

Windows 게임에서 일본어 텍스트를 실시간으로 추출하고 번역하는 프로그램

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 주요 기능 ✨

- 🔍 **실시간 텍스트 캡처** - Windows 게임/프로그램에서 일본어 텍스트 자동 추출
- 🌐 **자동 번역** - Gemini API를 통한 실시간 번역
- 🖼️ **오버레이 디스플레이** - 게임 위에 떠있는 반투명 창
- 📝 **다양한 캡처 방법** - Window Text, Memory Scan, Clipboard 모니터링
- 💾 **텍스트 저장** - 캡처된 텍스트 파일로 저장

## 다운로드 📥

### Windows 사용자
[Releases](https://github.com/YOUR_USERNAME/YOUR_REPO/releases)에서 최신 버전 다운로드:
- `JapaneseTextHooker.exe` - 기본 버전
- `TextHookerOverlay.exe` - 오버레이 + 번역 버전 ⭐
- `AdvancedTextHooker.exe` - 고급 메모리 스캔 버전

## 설치 및 실행 🚀

### 방법 1: EXE 파일 실행 (가장 쉬움)
1. EXE 파일 다운로드
2. 실행 (Windows Defender 경고시 "추가 정보" → "실행")

### 방법 2: Python으로 실행
```bash
# 필요 패키지 설치
pip install -r requirements.txt

# 실행
python overlay_hooker.py
```

## 사용법 📖

### 기본 사용법
1. 프로그램 실행
2. 게임/프로그램 창 선택
3. **Start** 버튼 클릭
4. 텍스트가 자동으로 캡처됨

### Gemini API 설정 (번역 기능)
1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 무료 API 키 발급
2. Settings 탭에서 API 키 입력
3. **Test API** 버튼으로 확인
4. Auto-translate 체크박스 활성화

### 오버레이 사용법
- 드래그로 위치 이동
- 투명도 슬라이더로 조절
- 최소화/복원 버튼
- 자동 번역 기능

## 빌드 방법 🔨

### Windows에서 빌드
```batch
build_onefile.bat
```

### Mac에서 Windows EXE 빌드
```bash
# Apple Silicon (M1/M2/M3)
./build_arm64_mac.sh

# Intel Mac
./build_mac_to_windows.sh
```

### GitHub Actions 자동 빌드
1. 코드를 GitHub에 푸시
2. Actions 탭에서 자동 빌드
3. Artifacts에서 다운로드

## 기능 비교 📊

| 기능 | Basic | Advanced | Overlay |
|------|-------|----------|---------|
| Window Text 캡처 | ✅ | ✅ | ✅ |
| 메모리 스캔 | ❌ | ✅ | ❌ |
| 클립보드 모니터링 | ✅ | ✅ | ✅ |
| 오버레이 표시 | ❌ | ❌ | ✅ |
| Gemini 번역 | ❌ | ❌ | ✅ |
| 관리자 권한 필요 | ❌ | ✅ | ❌ |

## 시스템 요구사항 💻

- Windows 10/11
- Python 3.8+ (소스 실행시)
- 인터넷 연결 (번역 기능 사용시)

## 문제 해결 🔧

### Windows Defender 차단
- Windows 보안 → 바이러스 및 위협 방지 → 제외 추가

### 텍스트가 캡처되지 않음
1. 다른 캡처 방법 시도 (Settings에서 변경)
2. 관리자 권한으로 실행
3. Advanced 버전 사용

### API 키 오류
- API 키 확인
- [할당량 확인](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas)

## 라이선스 📄

MIT License

## 기여 🤝

Pull Request 환영합니다!

## 주의사항 ⚠️

- 개인 사용 목적으로만 사용
- 게임 EULA 확인 필요
- API 키는 안전하게 보관