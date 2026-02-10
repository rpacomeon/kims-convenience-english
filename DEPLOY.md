# Streamlit Cloud 배포 가이드 🚀

## 1. GitHub에 업로드

```bash
# Git 초기화 (처음 한 번만)
cd "C:\Users\dhaud\Downloads\김씨네편의점"
git init
git add .
git commit -m "Initial commit: 김씨네 편의점 영어학습 앱"

# GitHub 리포지토리 생성 후
git remote add origin https://github.com/YOUR_USERNAME/kims-convenience-english.git
git branch -M main
git push -u origin main
```

## 2. Streamlit Cloud 배포

### 2.1 계정 생성
1. https://share.streamlit.io/ 접속
2. GitHub 계정으로 로그인

### 2.2 앱 배포
1. "New app" 클릭
2. 리포지토리 선택: `YOUR_USERNAME/kims-convenience-english`
3. Branch: `main`
4. Main file path: `src/app.py`
5. "Deploy!" 클릭

### 2.3 배포 완료
- URL: `https://YOUR_USERNAME-kims-convenience-english.streamlit.app`
- 배포 시간: 약 2-3분
- 자동 HTTPS 지원

## 3. 모바일 최적화 확인

### 3.1 Chrome DevTools로 테스트
1. Chrome에서 앱 열기
2. F12 → DevTools 열기
3. 상단 "Toggle device toolbar" (Ctrl+Shift+M)
4. 기기 선택: iPhone 12 Pro, Galaxy S21 등

### 3.2 실제 기기에서 테스트
1. 스마트폰 브라우저에서 앱 URL 접속
2. 홈 화면에 추가 (PWA처럼 사용 가능)
   - **iOS Safari**: 공유 → 홈 화면에 추가
   - **Android Chrome**: 메뉴 → 홈 화면에 추가

## 4. 성능 최적화 팁

### 4.1 데이터 캐싱
- `@st.cache_data`: 데이터 로딩 함수에 이미 적용됨
- `@st.cache_resource`: 모델/커넥션에 적용됨

### 4.2 로딩 속도 개선
```python
# 이미 적용된 최적화
- 데이터 미리 로드 (load_data())
- 리소스 캐싱 (load_resources())
- 불필요한 재렌더링 방지 (session_state 활용)
```

### 4.3 모바일 데이터 절약
- 이미지 최적화 (현재는 이모지만 사용)
- 불필요한 API 호출 제거
- 페이지 단위 로딩

## 5. 업데이트 방법

```bash
# 코드 수정 후
git add .
git commit -m "Update: 설명"
git push

# Streamlit Cloud에서 자동 재배포됨 (약 1-2분 소요)
```

## 6. 환경 변수 설정 (필요시)

Streamlit Cloud 대시보드에서:
1. 앱 선택 → Settings
2. Secrets 탭
3. TOML 형식으로 환경 변수 추가

```toml
# .streamlit/secrets.toml 예시
API_KEY = "your_api_key_here"
DB_PASSWORD = "your_password"
```

## 7. 커스텀 도메인 (선택)

Streamlit Cloud Pro 플랜:
- 커스텀 도메인 연결 가능
- 예: `english.yourdomain.com`

무료 플랜:
- `*.streamlit.app` 도메인만 사용 가능

## 8. 문제 해결

### 배포 실패 시
1. 로그 확인 (Streamlit Cloud 대시보드)
2. requirements.txt 확인
3. Python 버전 확인 (3.8-3.11 권장)

### 앱이 느릴 때
1. 데이터 크기 확인 (GitHub 100MB 제한)
2. 캐싱 적용 확인
3. 불필요한 연산 제거

### 모바일에서 안 보일 때
1. 브라우저 캐시 삭제
2. 시크릿 모드로 테스트
3. 다른 브라우저 시도

## 9. 모니터링

### Streamlit Cloud 대시보드
- 앱 상태 (Running/Stopped)
- 리소스 사용량 (CPU, RAM)
- 방문자 통계 (Pro 플랜)
- 에러 로그

### Google Analytics (선택)
```python
# app.py에 추가
st.components.v1.html("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_ID');
</script>
""", height=0)
```

## 10. 백업

중요 데이터는 정기적으로 백업:
- `learning_data.json` (사용자 진도)
- 설정 파일들
- GitHub에 자동 백업됨

---

**배포 완료 후**: 친구들에게 링크 공유하고 피드백 받기! 📱✨
