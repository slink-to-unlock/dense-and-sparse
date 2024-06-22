# 내장
import argparse

# 서드파티
import streamlit as st


def parse_arguments():
    parser = argparse.ArgumentParser(description='레이블링 streamlit 애플리케이션 실행')
    parser.add_argument(
        '--workspace_path',
        type=str,
        required=True,
        help='레이블링 작업을 수행할 워크스페이스 디렉토리 경로입니다.',
    )
    parser.add_argument(
        '--feature_store_path',
        type=str,
        required=True,
        help=(
            '정제가 완료된 데이터셋을 저장하는 경로입니다. '
            '버전을 포함한 최종 디렉토리 경로를 지정해 주어야 합니다. (e.g. feature-store/train/v7)'
        ),
    )
    return parser.parse_args()


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

args = parse_arguments()

if 'workspace_path' not in st.session_state:
    st.session_state['workspace_path'] = args.workspace_path
if 'feature_store_path' not in st.session_state:
    st.session_state['feature_store_path'] = args.feature_store_path

st.write("# Data Labeling Tool 👋")

st.info('이 페이지는 Autosink 프로젝트 싱크대 데이터 레이블링 도구 모음입니다. 좌측 메뉴에서 필요한 도구를 선택하세요.')

st.write('피드백 루프를 고려하여 제작되었습니다.')
