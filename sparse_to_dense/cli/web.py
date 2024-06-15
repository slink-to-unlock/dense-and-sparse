# 서드파티
from streamlit.web import cli

# 프로젝트
from sparse_to_dense import streamlit_home_py_path

if __name__ == '__main__':
    cli.main_run([streamlit_home_py_path])
