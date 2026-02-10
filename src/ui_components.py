"""Streamlit UI 재사용 가능한 컴포넌트

모바일 최적화 CSS 및 공통 위젯
"""

import streamlit as st


def mobile_css():
    """모바일 최적화 CSS를 적용한다. (전문가 디자인)"""
    st.markdown("""
    <style>
        /* 글로벌 설정 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');

        * {
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        /* 메인 컨테이너 */
        .main {
            padding: 0.5rem;
            max-width: 100%;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }

        /* 표현 카드 - 그라데이션 & 애니메이션 */
        .expression-card {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-radius: 16px;
            margin: 0.8rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border: 1px solid rgba(255,255,255,0.8);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .expression-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }

        .expression-card:active {
            transform: scale(0.98);
            box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        }

        .expression-english {
            font-size: 1.25rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            line-height: 1.5;
            letter-spacing: -0.02em;
        }

        .expression-korean {
            font-size: 1.05rem;
            color: #4a5568;
            line-height: 1.6;
            font-weight: 500;
        }

        /* 비문법 경고 카드 - 개선된 디자인 */
        .broken-card {
            background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
            padding: 1.2rem;
            border-radius: 16px;
            border-left: 5px solid #fc8181;
            margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(252, 129, 129, 0.15);
            transition: all 0.3s ease;
        }

        .broken-card:hover {
            box-shadow: 0 6px 20px rgba(252, 129, 129, 0.25);
        }

        .broken-warning {
            color: #c53030;
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }

        .broken-correction {
            color: #2f855a;
            background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
            padding: 0.8rem;
            border-radius: 12px;
            margin-top: 0.8rem;
            font-weight: 600;
            border-left: 3px solid #48bb78;
        }

        /* 버튼 - 터치 최적화 */
        .stButton button {
            width: 100%;
            min-height: 54px;
            font-size: 1.1rem;
            font-weight: 700;
            border-radius: 16px;
            border: none;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            letter-spacing: -0.01em;
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
        }

        .stButton button:active {
            transform: translateY(0);
            box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
        }

        /* 프로그레스 바 - 애니메이션 */
        .progress-container {
            background-color: #e2e8f0;
            border-radius: 12px;
            height: 36px;
            margin: 1.5rem 0;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
        }

        .progress-bar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            border-radius: 12px;
            text-align: center;
            color: white;
            font-weight: 700;
            line-height: 36px;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 1rem;
        }

        /* 라디오 버튼 - 모던한 선택지 */
        .stRadio > label {
            font-size: 1.05rem;
            padding: 1rem 1.2rem;
            margin: 0.6rem 0;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-radius: 14px;
            display: block;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 2px solid transparent;
            font-weight: 500;
        }

        .stRadio > label:hover {
            background: linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%);
            border-color: #4fd1c5;
            transform: translateX(4px);
        }

        .stRadio > label:active {
            transform: scale(0.98);
        }

        /* 뱃지 - 더 세련된 디자인 */
        .badge {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            margin-right: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .badge-beginner {
            background: linear-gradient(135deg, #d1f2eb 0%, #9ae6b4 100%);
            color: #22543d;
            box-shadow: 0 2px 8px rgba(154, 230, 180, 0.4);
        }

        .badge-intermediate {
            background: linear-gradient(135deg, #feebc8 0%, #fbd38d 100%);
            color: #744210;
            box-shadow: 0 2px 8px rgba(251, 211, 141, 0.4);
        }

        .badge-advanced {
            background: linear-gradient(135deg, #fed7d7 0%, #fc8181 100%);
            color: #742a2a;
            box-shadow: 0 2px 8px rgba(252, 129, 129, 0.4);
        }

        .badge-category {
            background: linear-gradient(135deg, #bee3f8 0%, #90cdf4 100%);
            color: #2c5282;
            box-shadow: 0 2px 8px rgba(144, 205, 244, 0.4);
        }

        /* 사이드바 - 모바일 최적화 */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }

        [data-testid="stSidebar"] .stButton button {
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        [data-testid="stSidebar"] .stButton button:hover {
            background: rgba(255,255,255,0.3);
            border-color: rgba(255,255,255,0.5);
        }

        /* 타이틀 */
        h1 {
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1.5rem;
            letter-spacing: -0.03em;
        }

        h2, h3 {
            font-weight: 700;
            color: #2d3748;
            letter-spacing: -0.02em;
        }

        /* 구분선 */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, #e2e8f0 50%, transparent 100%);
            margin: 2rem 0;
        }

        /* 로딩 스피너 */
        .stSpinner > div {
            border-top-color: #667eea !important;
        }

        /* 셀렉트박스 */
        .stSelectbox > div > div {
            border-radius: 12px;
            border: 2px solid #e2e8f0;
            min-height: 48px;
        }

        /* 익스팬더 */
        .streamlit-expanderHeader {
            border-radius: 12px;
            background-color: #f7fafc;
            font-weight: 600;
            padding: 1rem;
        }

        /* 성공/에러/정보 메시지 */
        .stSuccess, .stError, .stInfo, .stWarning {
            border-radius: 14px;
            padding: 1rem 1.2rem;
            border-left-width: 5px;
        }

        /* 모바일 터치 피드백 */
        @media (hover: none) and (pointer: coarse) {
            * {
                -webkit-tap-highlight-color: rgba(102, 126, 234, 0.2);
            }
        }

        /* 작은 화면 최적화 */
        @media (max-width: 640px) {
            .block-container {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }

            .expression-card {
                padding: 1.2rem;
            }

            .expression-english {
                font-size: 1.15rem;
            }

            .expression-korean {
                font-size: 1rem;
            }

            .stButton button {
                min-height: 50px;
                font-size: 1rem;
            }
        }

        /* 다크모드 대응 */
        @media (prefers-color-scheme: dark) {
            .expression-card {
                background: linear-gradient(135deg, #667eea25 0%, #764ba225 100%);
                border-color: rgba(255,255,255,0.1);
            }

            .expression-korean {
                color: #cbd5e0;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def expression_card(english: str, korean: str, show_korean: bool = False, metadata: dict = None):
    """표현 카드를 렌더링한다.

    Args:
        english: 영어 표현
        korean: 한국어 번역
        show_korean: 한국어 표시 여부
        metadata: 추가 메타데이터 (episode, difficulty, category 등)
    """
    with st.container():
        st.markdown(f"""
        <div class="expression-card">
            <div class="expression-english">{english}</div>
            {'<div class="expression-korean">' + korean + '</div>' if show_korean else ''}
        </div>
        """, unsafe_allow_html=True)

        # 메타데이터 표시
        if metadata and show_korean:
            cols = st.columns(4)
            if 'episode' in metadata:
                cols[0].caption(f"Ep.{metadata['episode']}")
            if 'difficulty' in metadata:
                diff_badge = f"badge-{metadata['difficulty']}"
                cols[1].markdown(f'<span class="badge {diff_badge}">{metadata["difficulty"]}</span>', unsafe_allow_html=True)
            if 'category' in metadata:
                cols[2].markdown(f'<span class="badge badge-category">{metadata["category"]}</span>', unsafe_allow_html=True)


def broken_english_card(original: str, corrected: str, issues: list):
    """비문법 영어 경고 카드를 렌더링한다.

    Args:
        original: 원문
        corrected: 교정된 문장
        issues: 문법 이슈 리스트
    """
    st.markdown(f"""
    <div class="broken-card">
        <div class="broken-warning">[X] Mr. Kim's English</div>
        <div style="margin: 0.5rem 0;">{original}</div>
        <div class="broken-correction">[OK] Correct: {corrected}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("문법 포인트 보기"):
        for issue in issues:
            st.markdown(f"**{issue['matched']}** → **{issue['correction']}**")
            st.caption(issue['explanation'])


def progress_bar(current: int, total: int, label: str = "진행률"):
    """프로그레스 바를 렌더링한다.

    Args:
        current: 현재 값
        total: 전체 값
        label: 레이블
    """
    percentage = (current / total * 100) if total > 0 else 0

    st.markdown(f"""
    <div style="margin-bottom: 0.5rem;">{label}: {current}/{total}</div>
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%;">
            {percentage:.0f}%
        </div>
    </div>
    """, unsafe_allow_html=True)


def quiz_widget(quiz: dict, key: str):
    """퀴즈 문제를 렌더링한다.

    Args:
        quiz: 퀴즈 딕셔너리
        key: Streamlit 위젯 key

    Returns:
        선택한 답변 인덱스 (0-based), 미선택 시 None
    """
    st.markdown(f"### {quiz['question']}")

    if 'hint' in quiz:
        st.caption(quiz['hint'])

    # 선택지
    options = [f"{i+1}. {choice}" for i, choice in enumerate(quiz['choices'])]

    selected = st.radio(
        "답을 선택하세요:",
        options,
        key=key,
        label_visibility="collapsed"
    )

    if selected:
        # "1. xxx" 형식에서 인덱스 추출
        selected_index = int(selected.split('.')[0]) - 1
        return selected_index

    return None


def show_quiz_result(selected_index: int, correct_index: int, explanation: str):
    """퀴즈 결과를 표시한다.

    Args:
        selected_index: 선택한 답변 인덱스
        correct_index: 정답 인덱스
        explanation: 설명
    """
    is_correct = selected_index == correct_index

    if is_correct:
        st.success("[OK] 정답입니다!")
    else:
        st.error("[X] 틀렸습니다.")
        st.info(f"정답은 {correct_index + 1}번입니다.")

    with st.expander("설명 보기", expanded=True):
        st.markdown(explanation)

    return is_correct


def category_grid(categories: list, on_select):
    """카테고리 그리드를 렌더링한다.

    Args:
        categories: 카테고리 리스트 [{"id": "...", "name": "..."}, ...]
        on_select: 선택 시 호출할 함수 (category_id를 인자로 받음)
    """
    # 카테고리별 아이콘 매핑
    category_icons = {
        "greetings": "👋",
        "shopping": "🛒",
        "family": "👨‍👩‍👧‍👦",
        "emotions": "😊",
        "requests": "🙏",
        "workplace": "💼",
        "daily_life": "☀️",
        "advice": "💡"
    }

    cols = st.columns(2)

    for i, category in enumerate(categories):
        col = cols[i % 2]
        with col:
            icon = category_icons.get(category['id'], "📚")
            # 커스텀 HTML 버튼으로 더 세련되게
            button_html = f"""
            <div style="
                background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
                border: 2px solid #e2e8f0;
                border-radius: 16px;
                padding: 1.5rem 1rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                margin-bottom: 1rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(102, 126, 234, 0.15)'; this.style.borderColor='#667eea';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.05)'; this.style.borderColor='#e2e8f0';">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-size: 1rem; font-weight: 700; color: #2d3748;">{category['name']}</div>
            </div>
            """

            # Streamlit 버튼은 유지 (클릭 이벤트 처리용)
            if st.button(
                f"{icon} {category['name']}",
                key=f"cat_{category['id']}",
                use_container_width=True
            ):
                on_select(category['id'])


def episode_selector(episodes: list, current: int = 1):
    """에피소드 선택기를 렌더링한다.

    Args:
        episodes: 에피소드 번호 리스트
        current: 현재 선택된 에피소드

    Returns:
        선택된 에피소드 번호
    """
    selected = st.selectbox(
        "에피소드 선택",
        episodes,
        index=episodes.index(current) if current in episodes else 0,
        format_func=lambda x: f"Episode {x}"
    )

    return selected


def day_indicator(day: int, week: int, total: int = 30):
    """Day 표시기를 렌더링한다.

    Args:
        day: 현재 Day
        week: 현재 Week
        total: 전체 Day 수
    """
    progress_percent = (day / total) * 100
    remaining = total - day

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 24px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.35);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\"><circle cx=\"10\" cy=\"10\" r=\"1\" fill=\"white\" opacity=\"0.1\"/><circle cx=\"30\" cy=\"25\" r=\"1.5\" fill=\"white\" opacity=\"0.1\"/><circle cx=\"60\" cy=\"15\" r=\"1\" fill=\"white\" opacity=\"0.1\"/><circle cx=\"80\" cy=\"30\" r=\"1.5\" fill=\"white\" opacity=\"0.1\"/></svg>');
            opacity: 0.5;
        "></div>
        <div style="position: relative; z-index: 1;">
            <div style="font-size: 0.85rem; font-weight: 600; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
                30일 챌린지
            </div>
            <div style="font-size: 3.5rem; font-weight: 900; margin: 0.5rem 0; text-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                Day {day}
            </div>
            <div style="font-size: 1.1rem; font-weight: 600; opacity: 0.95; margin-bottom: 1rem;">
                Week {week} · {remaining}일 남음
            </div>
            <div style="background: rgba(255,255,255,0.2); height: 8px; border-radius: 10px; overflow: hidden; backdrop-filter: blur(10px);">
                <div style="
                    width: {progress_percent}%;
                    height: 100%;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(255,255,255,0.5);
                    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                "></div>
            </div>
            <div style="font-size: 0.9rem; font-weight: 600; opacity: 0.9; margin-top: 0.5rem;">
                {progress_percent:.1f}% 완료
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def stat_card(title: str, value: str, color: str = "#667eea", icon: str = "📊"):
    """통계 카드를 렌더링한다.

    Args:
        title: 제목
        value: 값
        color: 색상
        icon: 아이콘 이모지
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 1.5rem 1rem;
        background: linear-gradient(135deg, {color}15 0%, {color}25 100%);
        border-radius: 20px;
        border: 2px solid {color}30;
        box-shadow: 0 4px 15px {color}20;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 25px {color}30';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px {color}20';">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 0.85rem; color: #718096; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
            {title}
        </div>
        <div style="font-size: 2rem; font-weight: 900; color: {color}; text-shadow: 0 2px 4px {color}30;">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    # 테스트 모드 (streamlit run으로 실행)
    st.title("UI Components 테스트")

    mobile_css()

    st.header("1. Expression Card")
    expression_card(
        "How are you doing today?",
        "오늘 어떻게 지내고 있어요?",
        show_korean=True,
        metadata={"episode": 1, "difficulty": "beginner", "category": "인사/소개"}
    )

    st.header("2. Broken English Card")
    broken_english_card(
        "You is very smart.",
        "You are very smart.",
        [
            {"matched": "You is", "correction": "You are", "explanation": "주어 'You'는 항상 'are'를 사용합니다."}
        ]
    )

    st.header("3. Progress Bar")
    progress_bar(15, 30, "학습 진도")

    st.header("4. Day Indicator")
    day_indicator(5, 1, 30)

    st.header("5. Stat Cards")
    cols = st.columns(3)
    with cols[0]:
        stat_card("총 표현", "300개", "#1f77b4")
    with cols[1]:
        stat_card("정답률", "85%", "#2ca02c")
    with cols[2]:
        stat_card("연속 일수", "5일", "#ff7f0e")
