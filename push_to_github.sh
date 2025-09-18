#!/bin/bash

echo "========================================="
echo "GitHub Actions 자동 빌드"
echo "========================================="
echo ""

# Git 초기화 확인
if [ ! -d ".git" ]; then
    echo "Git 저장소 초기화..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# 원격 저장소 확인
if ! git remote | grep -q origin; then
    echo ""
    echo "⚠️  GitHub 저장소를 먼저 연결하세요:"
    echo ""
    echo "1. GitHub에서 새 저장소 생성"
    echo "2. 아래 명령어 실행:"
    echo ""
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo ""
    exit 1
fi

# 변경사항 커밋
echo "변경사항 커밋 중..."
git add .
git commit -m "Update $(date +%Y-%m-%d' '%H:%M:%S)" || echo "변경사항 없음"

# main 브랜치로 푸시
echo "GitHub에 푸시 중..."
git push -u origin main

# 릴리즈용 태그 생성
read -p "릴리즈 버전 태그를 생성하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    VERSION="v$(date +%Y%m%d.%H%M%S)"
    git tag $VERSION
    git push origin $VERSION
    echo "✅ 릴리즈 태그 생성: $VERSION"
fi

echo ""
echo "========================================="
echo "✅ GitHub에 푸시 완료!"
echo "========================================="
echo ""
echo "이제 아래 링크에서 빌드 진행 상황을 확인하세요:"
echo "👉 https://github.com/YOUR_USERNAME/YOUR_REPO/actions"
echo ""
echo "빌드가 완료되면:"
echo "1. Actions 탭 → 최신 워크플로우 → Artifacts에서 다운로드"
echo "2. Releases 탭에서 다운로드 (태그 생성한 경우)"
echo ""