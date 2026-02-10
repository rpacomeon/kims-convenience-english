"""김씨네 편의점 영어학습 앱 - 메인 Streamlit 앱

6개 페이지: 오늘의 학습, 에피소드별, 상황별, 구동사, 퀴즈, 학습기록
"""

import sys
from pathlib import Path

# 현재 디렉토리를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd

# 로컬 모듈 임포트
from data_loader import load_subtitle_data, add_episode_column, add_clean_subtitle_column, add_speaker_column
from expression_extractor import extract_key_expressions, add_difficulty_column
from categorizer import Categorizer, add_category_column
from vocabulary_builder import analyze_phrasal_verbs, extract_vocabulary, get_word_examples
from broken_english import BrokenEnglishDetector
from quiz_engine import QuizEngine
from spaced_repetition import LearningDataManager
from curriculum import Curriculum
from ui_components import (
    mobile_css, expression_card, broken_english_card, progress_bar,
    quiz_widget, show_quiz_result, category_grid, episode_selector,
    day_indicator, stat_card
)


# 페이지 설정
st.set_page_config(
    page_title="김씨네 편의점 영어학습",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)


@st.cache_data
def load_data():
    """데이터를 로드하고 캐싱한다."""
    # 프로젝트 루트 디렉토리 찾기
    project_root = Path(__file__).parent.parent
    data_file = project_root / "김씨네 편의점.txt"

    df = load_subtitle_data(str(data_file))
    df = add_episode_column(df)
    df = add_clean_subtitle_column(df)
    df = add_speaker_column(df)
    return df


@st.cache_resource
def load_resources():
    """리소스를 로드하고 캐싱한다."""
    # 프로젝트 루트 디렉토리 찾기
    project_root = Path(__file__).parent.parent

    categorizer = Categorizer(str(project_root / "config" / "categories.json"))
    broken_detector = BrokenEnglishDetector(str(project_root / "config" / "broken_patterns.json"))
    return categorizer, broken_detector


def initialize_session_state():
    """세션 상태를 초기화한다."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "오늘의 학습"

    if 'quiz_state' not in st.session_state:
        st.session_state.quiz_state = {
            'current_quiz': None,
            'answered': False,
            'score': 0,
            'total': 0
        }

    if 'learning_manager' not in st.session_state:
        project_root = Path(__file__).parent.parent
        st.session_state.learning_manager = LearningDataManager(str(project_root / "learning_data.json"))

    if 'curriculum' not in st.session_state:
        df = load_data()
        st.session_state.curriculum = Curriculum(df)


def page_today_learning():
    """페이지 1: 오늘의 학습"""
    mobile_css()

    # 페이지 헤더
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">📚</div>
        <h1 style="margin: 0;">오늘의 학습</h1>
        <p style="color: #718096; font-size: 1rem; margin-top: 0.5rem;">매일 조금씩, 꾸준하게</p>
    </div>
    """, unsafe_allow_html=True)

    # 커리큘럼 가져오기
    curriculum = st.session_state.curriculum
    today = curriculum.get_today_plan()

    # Day 표시기
    day_indicator(today['day'], today['week'])

    # 학습 초점
    st.subheader(f"🎯 {today['focus']}")

    # 진행률
    progress = curriculum.get_progress()
    progress_bar(progress['current_day'], 30, "30일 챌린지")

    # 구동사 포커스
    if today['phrasal_verbs']:
        st.subheader("💡 오늘의 구동사")
        for pv in today['phrasal_verbs']:
            st.markdown(f"- **{pv}**")

    # 오늘의 표현
    st.subheader(f"📖 오늘의 표현 ({today['new_count']}개)")

    expressions = today['expressions']

    if len(expressions) > 0:
        # 표현 카드
        for idx, row in expressions.head(10).iterrows():
            show_korean = st.session_state.get(f"show_korean_{idx}", False)

            col1, col2 = st.columns([4, 1])

            with col1:
                expression_card(
                    row['clean_subtitle'],
                    row.get('Machine Translation', ''),
                    show_korean=show_korean,
                    metadata={
                        'episode': row.get('episode'),
                        'difficulty': row.get('difficulty', 'beginner')
                    }
                )

            with col2:
                if st.button("👁️", key=f"toggle_{idx}"):
                    st.session_state[f"show_korean_{idx}"] = not show_korean
                    st.rerun()
    else:
        st.info("오늘의 표현을 로드하는 중...")

    # 복습 대상
    due = st.session_state.learning_manager.get_due_expressions()

    if len(due) > 0:
        st.subheader(f"🔄 복습 대기 ({len(due)}개)")
        for item in due[:5]:
            st.markdown(f"- {item['text']} (연체 {item['days_overdue']}일)")

    # 퀴즈 바로가기
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 오늘의 퀴즈", use_container_width=True):
            st.session_state.current_page = "퀴즈"
            st.rerun()
    with col2:
        if st.button("📊 학습 기록", use_container_width=True):
            st.session_state.current_page = "학습 기록"
            st.rerun()


def page_episode_learning():
    """페이지 2: 에피소드별 학습"""
    mobile_css()

    # 페이지 헤더
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎬</div>
        <h1 style="margin: 0;">에피소드별 학습</h1>
        <p style="color: #718096; font-size: 1rem; margin-top: 0.5rem;">Kim's Convenience 시즌 1</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()

    # 에피소드 선택
    selected_episode = episode_selector(list(range(1, 14)), 1)

    # 에피소드 정보
    episode_df = df[df['episode'] == selected_episode]
    st.info(f"Episode {selected_episode}: {len(episode_df)}개 라인")

    # 핵심 표현
    st.subheader("💎 핵심 표현")
    key_expressions = extract_key_expressions(df, selected_episode, top_n=20)
    key_expressions = add_difficulty_column(key_expressions)

    for idx, row in key_expressions.iterrows():
        show = st.session_state.get(f"ep_show_{idx}", False)

        col1, col2 = st.columns([4, 1])

        with col1:
            expression_card(
                row['clean_subtitle'],
                row.get('Machine Translation', ''),
                show_korean=show,
                metadata={'difficulty': row['difficulty']}
            )

        with col2:
            if st.button("👁️", key=f"ep_toggle_{idx}"):
                st.session_state[f"ep_show_{idx}"] = not show
                st.rerun()

    # 비문법 표현 (Mr. Kim)
    st.subheader("🔧 Mr. Kim's English")
    broken_detector = load_resources()[1]

    mr_kim_lines = episode_df[episode_df['speaker'].isin(['MR. KIM', 'MR KIM', 'APPA'])]

    broken_found = []
    for _, row in mr_kim_lines.iterrows():
        text = row['clean_subtitle']
        result = broken_detector.suggest_correction(text)
        if result['has_errors']:
            broken_found.append((text, result))

    if broken_found:
        for original, result in broken_found[:5]:
            broken_english_card(original, result['corrected'], result['issues'])
    else:
        st.caption("비문법 표현이 발견되지 않았습니다.")


def page_category_learning():
    """페이지 3: 상황별 표현"""
    mobile_css()

    # 페이지 헤더
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">📑</div>
        <h1 style="margin: 0;">상황별 표현</h1>
        <p style="color: #718096; font-size: 1rem; margin-top: 0.5rem;">8가지 일상 상황</p>
    </div>
    """, unsafe_allow_html=True)

    categorizer, _ = load_resources()
    df = load_data()

    # 카테고리 선택
    categories = categorizer.get_all_categories()

    st.subheader("카테고리 선택")

    selected_category = st.session_state.get('selected_category', None)

    if selected_category is None:
        # 카테고리 그리드
        def on_category_select(cat_id):
            st.session_state.selected_category = cat_id
            st.rerun()

        category_grid(categories, on_category_select)

    else:
        # 선택된 카테고리 표현
        cat_name = categorizer.get_category_name(selected_category)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"📌 {cat_name}")
        with col2:
            if st.button("← 뒤로"):
                st.session_state.selected_category = None
                st.rerun()

        # 카테고리별 표현 추출
        df_with_cat = add_category_column(df, categorizer)
        cat_df = categorizer.filter_by_category(df_with_cat, selected_category)

        st.info(f"{len(cat_df)}개 표현")

        # 표현 표시
        for idx, row in cat_df.head(20).iterrows():
            show = st.session_state.get(f"cat_show_{idx}", False)

            col1, col2 = st.columns([4, 1])

            with col1:
                expression_card(
                    row['clean_subtitle'],
                    row.get('Machine Translation', ''),
                    show_korean=show,
                    metadata={'episode': row.get('episode')}
                )

            with col2:
                if st.button("👁️", key=f"cat_toggle_{idx}"):
                    st.session_state[f"cat_show_{idx}"] = not show
                    st.rerun()


def page_phrasal_verbs():
    """페이지 4: 구동사 마스터"""
    mobile_css()

    # 페이지 헤더
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🚀</div>
        <h1 style="margin: 0;">구동사 마스터</h1>
        <p style="color: #718096; font-size: 1rem; margin-top: 0.5rem;">Phrasal Verbs 완전정복</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()

    st.info("드라마에서 실제 사용된 구동사를 학습합니다!")

    # 구동사 분석
    project_root = Path(__file__).parent.parent
    phrasal_analysis = analyze_phrasal_verbs(df, str(project_root / "config" / "phrasal_verbs.json"))

    if len(phrasal_analysis) > 0:
        st.subheader(f"📚 사용된 구동사 ({len(phrasal_analysis)}개)")

        for idx, row in phrasal_analysis.iterrows():
            with st.expander(f"**{row['verb']}** - {row['meaning']} ({row['frequency']}회)"):
                st.markdown(f"**의미:** {row['meaning']}")
                st.markdown(f"**빈도:** {row['frequency']}회")

                st.markdown("**드라마 속 예문:**")
                for ex in row['examples']:
                    st.markdown(f"- {ex['english']}")
                    st.caption(f"  ({ex['korean']})")
    else:
        st.warning("구동사 데이터를 로드할 수 없습니다.")


def page_quiz():
    """페이지 5: 퀴즈"""
    mobile_css()

    # 페이지 헤더
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">📝</div>
        <h1 style="margin: 0;">퀴즈</h1>
        <p style="color: #718096; font-size: 1rem; margin-top: 0.5rem;">능동적 회상으로 실력 UP!</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    _, broken_detector = load_resources()

    quiz_engine = QuizEngine(df)

    # 퀴즈 설정
    if st.session_state.quiz_state['current_quiz'] is None:
        st.subheader("퀴즈 설정")

        quiz_type = st.selectbox(
            "퀴즈 유형",
            ["random", "kr_to_en", "en_to_kr", "fill_blank", "grammar_correction"],
            format_func=lambda x: {
                "random": "랜덤",
                "kr_to_en": "한국어 → 영어",
                "en_to_kr": "영어 → 한국어",
                "fill_blank": "빈칸 채우기",
                "grammar_correction": "문법 교정"
            }[x]
        )

        if st.button("퀴즈 시작", use_container_width=True):
            quiz = quiz_engine.generate_quiz(quiz_type, broken_detector=broken_detector)
            if quiz:
                st.session_state.quiz_state['current_quiz'] = quiz
                st.session_state.quiz_state['answered'] = False
                st.rerun()
            else:
                st.error("퀴즈를 생성할 수 없습니다.")

    else:
        # 퀴즈 표시
        quiz = st.session_state.quiz_state['current_quiz']

        # 통계
        col1, col2, col3 = st.columns(3)
        with col1:
            stat_card("총 문제", str(st.session_state.quiz_state['total']), "#667eea", "📝")
        with col2:
            stat_card("정답", str(st.session_state.quiz_state['score']), "#48bb78", "✅")
        with col3:
            rate = (st.session_state.quiz_state['score'] / st.session_state.quiz_state['total'] * 100) if st.session_state.quiz_state['total'] > 0 else 0
            stat_card("정답률", f"{rate:.0f}%", "#f6ad55", "🎯")

        st.divider()

        if not st.session_state.quiz_state['answered']:
            # 문제 풀기
            selected = quiz_widget(quiz, "quiz_answer")

            if selected is not None:
                if st.button("제출", use_container_width=True):
                    is_correct = show_quiz_result(selected, quiz['correct_index'], quiz['explanation'])

                    st.session_state.quiz_state['answered'] = True
                    st.session_state.quiz_state['total'] += 1
                    if is_correct:
                        st.session_state.quiz_state['score'] += 1

                    st.rerun()

        else:
            # 결과 표시됨
            show_quiz_result(
                st.session_state.quiz_state.get('last_answer', 0),
                quiz['correct_index'],
                quiz['explanation']
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("다음 문제", use_container_width=True):
                    next_quiz = quiz_engine.generate_quiz("random", broken_detector=broken_detector)
                    if next_quiz:
                        st.session_state.quiz_state['current_quiz'] = next_quiz
                        st.session_state.quiz_state['answered'] = False
                        st.rerun()

            with col2:
                if st.button("종료", use_container_width=True):
                    st.session_state.quiz_state['current_quiz'] = None
                    st.session_state.quiz_state['answered'] = False
                    st.rerun()


def page_learning_record():
    """페이지 6: 학습 기록"""
    mobile_css()

    # 페이지 헤더
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">📊</div>
        <h1 style="margin: 0;">학습 기록</h1>
        <p style="color: #718096; font-size: 1rem; margin-top: 0.5rem;">나의 학습 여정</p>
    </div>
    """, unsafe_allow_html=True)

    curriculum = st.session_state.curriculum
    learning_manager = st.session_state.learning_manager

    # 진행률
    progress = curriculum.get_progress()

    st.subheader("🎯 30일 챌린지 진행률")
    progress_bar(progress['current_day'], 30, "진행 중")

    st.caption(f"Day {progress['current_day']}/30 | {progress['progress_percent']:.1f}% 완료")

    # 에피소드별 진행률
    st.subheader("📺 에피소드별 진행률")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**완료 에피소드**")
        if progress['completed_episodes']:
            for ep in progress['completed_episodes']:
                st.markdown(f"- Episode {ep}")
        else:
            st.caption("아직 없습니다.")

    with col2:
        st.markdown("**남은 에피소드**")
        for ep in progress['remaining_episodes'][:5]:
            st.markdown(f"- Episode {ep}")

    # 통계
    st.subheader("📈 학습 통계")

    stats = learning_manager.get_statistics()

    col1, col2, col3 = st.columns(3)

    with col1:
        stat_card("총 복습", str(stats['total_reviews']), "#667eea", "🔄")

    with col2:
        stat_card("학습 표현", str(stats['total_expressions']), "#48bb78", "📚")

    with col3:
        rate = stats['correct_rate'] * 100
        stat_card("평균 정확도", f"{rate:.0f}%", "#f6ad55", "⭐")

    # 퀴즈 통계
    st.subheader("📝 퀴즈 통계")

    quiz_total = st.session_state.quiz_state['total']
    quiz_score = st.session_state.quiz_state['score']

    if quiz_total > 0:
        progress_bar(quiz_score, quiz_total, "정답률")
        st.caption(f"{quiz_score}/{quiz_total} 문제 정답")
    else:
        st.caption("아직 퀴즈를 풀지 않았습니다.")


def main():
    """메인 앱"""
    initialize_session_state()

    # 사이드바 네비게이션
    with st.sidebar:
        # 로고 & 타이틀
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem 1rem 1rem;">
            <div style="font-size: 3.5rem; margin-bottom: 0.8rem;">🏪</div>
            <h2 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 900; text-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                김씨네 편의점
            </h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 0.9rem; margin-top: 0.5rem; font-weight: 600;">
                영어학습 30일 챌린지
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # 페이지 네비게이션 (아이콘 포함)
        pages = [
            ("오늘의 학습", "📚"),
            ("에피소드별 학습", "🎬"),
            ("상황별 표현", "📑"),
            ("구동사 마스터", "🚀"),
            ("퀴즈", "📝"),
            ("학습 기록", "📊")
        ]

        for page_name, icon in pages:
            if st.button(f"{icon}  {page_name}", use_container_width=True, key=f"nav_{page_name}"):
                st.session_state.current_page = page_name
                st.rerun()

        # 푸터
        st.divider()
        st.markdown("""
        <div style="text-align: center; padding: 1rem; color: rgba(255,255,255,0.7); font-size: 0.75rem;">
            <p style="margin: 0;">Made with ❤️</p>
            <p style="margin: 0.2rem 0 0 0;">by Claude Code</p>
        </div>
        """, unsafe_allow_html=True)

    # 현재 페이지 렌더링
    current_page = st.session_state.current_page

    if current_page == "오늘의 학습":
        page_today_learning()
    elif current_page == "에피소드별 학습":
        page_episode_learning()
    elif current_page == "상황별 표현":
        page_category_learning()
    elif current_page == "구동사 마스터":
        page_phrasal_verbs()
    elif current_page == "퀴즈":
        page_quiz()
    elif current_page == "학습 기록":
        page_learning_record()


if __name__ == "__main__":
    main()
