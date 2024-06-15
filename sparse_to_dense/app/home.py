import argparse
import streamlit as st

# 프로젝트
from autosink_data_elt.path.autosink import AutosinkPath


def parse_arguments():
    parser = argparse.ArgumentParser(description='레이블링 streamlit 애플리케이션 실행')
    parser.add_argument(
        '--workspace_path',
        type=str,
        default=AutosinkPath().data_lake_dir,
        help='레이블링 작업을 수행할 워크스페이스 디렉토리 경로입니다.',
    )
    return parser.parse_args()


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

args = parse_arguments()

if 'workspace_path' not in st.session_state:
    st.session_state['workspace_path'] = args.workspace_path

st.write("# Data Labeling Tool 👋")

st.info('이 페이지는 Autosink 프로젝트 싱크대 데이터 레이블링 도구 모음입니다. 좌측 메뉴에서 필요한 도구를 선택하세요.')

st.write('피드백 루프를 고려하여 제작되었습니다.')
