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
    return parser.parse_args()


def main(workspace_path: Union[os.PathLike, str], port:int = DEFAULT_PORT):
    cli.main_run([
        streamlit_home_py_path,
        f'--server.port={port}', '--',
        # Application arguments
        f'--workspace_path={workspace_path}'
    ])


if __name__ == '__main__':
    args = parse_arguments()
    main(args.port)
