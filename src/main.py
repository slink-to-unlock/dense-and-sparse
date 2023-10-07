# 외장
import os
import json
import pathlib
import logging
import sys

logging.basicConfig(
    format=f'(%(asctime)s)[%(levelname)s]:%(module)s: %(message)s',
    datefmt='%Y/%m/%d-%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    level=logging.INFO)

# main.py 로거
logger = logging.getLogger(__name__)

# 프로젝트
from .manager import WorkSpacePathManager, WorkSpaceJsonManager
from . import copyutils
from . import veditutils


def create_workspace(
    wsjson_manager: WorkSpaceJsonManager,
    parent_dir: os.PathLike,
    name_ws: str = 'anonymous-ws'
) -> WorkSpacePathManager:
    wspath_manager = WorkSpacePathManager(parent_dir, name_ws)
    os.mkdir(wspath_manager.ws_dir)
    logger.info(
        f'경로 `{os.path.abspath(parent_dir)}`에 워크스페이스 `{name_ws}`를 생성합니다.')
    os.mkdir(wspath_manager.raw_dir)
    wsjson_manager.create_json(wspath_manager.wsjson_path)
    return wspath_manager


def copy_video(
    wspath_manager: WorkSpacePathManager,
    wsjson_manager: WorkSpaceJsonManager,
    video_path: os.PathLike,
) -> None:
    """ 비디오를 워크스페이스의 raws디렉토리로 복사하고
    메타정보를 json파일에 기록합니다.

    Args:
        wspath_manager (WorkSpacePathManager): 알잘딱
        video_path (os.PathLike): 비디오의 경로
    """
    wspath_manager.set_clips_dir(wsjson_manager, video_path)
    logger.info(f'동영상 `{os.path.basename(video_path)}`를 복사합니다.')
    copyutils.copy_with_callback(
        video_path,
        wspath_manager.read_raw_path(wsjson_manager, -1)
    )


if __name__ == '__main__':
    wsjson_manager = WorkSpaceJsonManager()
    wspath_manager = create_workspace(wsjson_manager, '.')
    wspath_manager = WorkSpacePathManager('.', 'anonymous-ws')
    copy_video(wspath_manager, wsjson_manager, '연호설거지_1.MOV.mov')
    veditutils.split_video(wspath_manager, wsjson_manager, 0)

# TODO: 구현 목표
# 처음 올라간 것의 이름은 initial_{i} 로 한다.
# 클립을 나누면 initial_{i} 폴더 내에 initial_{i}_clip_{i} 로 한다.
# initial_{i}_clip_{i} 는 또다시 raws 폴더 안에 들어갈 수 있다.
# 이것들은 또다시 클립들로 나누어질 수 있다.
