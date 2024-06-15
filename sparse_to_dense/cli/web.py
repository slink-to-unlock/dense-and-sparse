# 내장
import argparse

# 서드파티
from streamlit.web import cli

# 프로젝트
from sparse_to_dense import streamlit_home_py_path


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run Streamlit app')
    parser.add_argument(
        '--port',
        type=int,
        default=8501,
        help='Port to run the Streamlit app on',
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    cli.main_run([streamlit_home_py_path, f'--server.port={args.port}'])
