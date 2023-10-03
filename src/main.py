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
    p = pathlib.Path(video_path)
    name, ext = p.name, p.suffix
    logger.info(f'경로 `{os.path.abspath(wspath_manager.raw_dir)}`에 '
                f'동영상 `{name}`를 복사합니다.')

    def get_new_name(extension=True):
        new_name = f'raw_{len([])}'  # FIXME
        if extension:
            new_name += ext
        logger.info(f'동영상 `{name}`의 이름을 `{new_name}`으로 변경합니다.')
        return new_name

    dst_path = os.path.join(wspath_manager.raw_dir, get_new_name())
    copyutils.copy_with_callback(video_path, dst_path)

    with open(wspath_manager.wsjson_path, 'r') as f:
        d = json.load(f)
    wsjson_manager.fn_raws()(d).append({
        'original_name': name,
        'raw_name': get_new_name(extension=False),
        'raw_path': dst_path,
        'clips_dir': wspath_manager.get_clips_dir(wsjson_manager, 0), # FIXME
    })
    with open(wspath_manager.wsjson_path, 'w') as f:
        json.dump(d, f, indent=4, ensure_ascii=False)


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
