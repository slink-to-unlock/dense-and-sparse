# 내장
import os
import argparse
from typing import Union

# 서드파티
from streamlit.web import cli

# 프로젝트
from sparse_to_dense import streamlit_home_py_path

DEFAULT_PORT = 8501


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run Streamlit app')
    parser.add_argument(
        '--port',
        type=int,
        default=DEFAULT_PORT,
        help='Port to run the Streamlit app on',
    )
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


def main(
    workspace_path: Union[os.PathLike, str],
    feature_store_path: Union[os.PathLike, str],
    port: int = DEFAULT_PORT,
):
    print(f'워크스페이스 경로는 `{workspace_path}` 입니다.')
    print(f'피처 스토어에 푸시하면 경로 `{feature_store_path}` 으로 이미지들을 옮깁니다.')
    print(f'포트 `{port}`번을 사용합니다.')
    cli.main_run(
        [
            streamlit_home_py_path,
            # Streamlit internal arguments
            f'--server.port={port}',
            '--',
            # Application arguments
            f'--workspace_path={workspace_path}',
            f'--feature_store_path={feature_store_path}'
        ]
    )


if __name__ == '__main__':
    args = parse_arguments()
    main(args.workspace_path, args.feature_store_path, args.port)
