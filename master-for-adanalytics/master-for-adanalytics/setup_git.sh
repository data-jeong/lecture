#!/bin/bash

# GitHub 리포지토리 설정 스크립트
# 사용법: ./setup_git.sh [your-github-username] [repository-name]

if [ $# -ne 2 ]; then
    echo "사용법: ./setup_git.sh [GitHub 사용자명] [리포지토리명]"
    echo "예시: ./setup_git.sh myusername master-for-adanalytics"
    exit 1
fi

USERNAME=$1
REPO_NAME=$2

echo "🚀 Git 리모트 설정 중..."

# 리모트 추가
git remote add origin "https://github.com/${USERNAME}/${REPO_NAME}.git"

echo "📝 현재 상태 확인..."
git status

echo "🔄 모든 변경사항 푸시..."
git push -u origin main

echo "✅ 완료! GitHub에서 확인하세요: https://github.com/${USERNAME}/${REPO_NAME}"