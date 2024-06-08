""" 파이썬 스크립트에서 현재 실행되고 있는 파일의 위치를 기준으로 서브모듈 디렉토리들을 PYTHONPATH 환경 변수에 추가
"""
import sys
import os

video_splitter_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'submodules', 'video-splitter')

if video_splitter_path not in sys.path:
    sys.path.append(video_splitter_path)
