# 외장
import os
import logging
import sys
import time

# 서드파티
import pick

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
    time.sleep(3)
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


def cli_selector(
    wspath_manager: WorkSpaceJsonManager,
    wsjson_manager: WorkSpaceJsonManager
) -> (int, os.PathLike):
    li = wspath_manager.atomic_videos(wsjson_manager)
    ret, idx = pick.pick([e.name for e in li] + ['exit'])
    if ret == 'exit':
        return -1, None
    video_path = li[idx].video_path
    logger.info(f'{video_path} 가 선택되었습니다.')
    return idx, video_path


def vis_tree(
    wspath_manager: WorkSpacePathManager,
    wsjson_manager: WorkSpaceJsonManager
) -> None:
    tree = wspath_manager.get_videos_relationtree(wsjson_manager)
    clear = lambda: os.system('clear')
    clear()
    from anytree import RenderTree
    for pre, fill, node in RenderTree(tree):
        print("%s%s" % (pre, node.name))


if __name__ == '__main__':
    wsjson_manager = WorkSpaceJsonManager()
    wspath_manager = WorkSpacePathManager('.', 'test-ws')
    try:
        create_workspace(wsjson_manager, '.', name_ws='test-ws')
    except FileExistsError:
        logger.error('워크스페이스를 새로 만들 수 없습니다. '
                     f'워크스페이스 `{wspath_manager.ws_dir}`가 이미 존재합니다.')
        raise NotImplementedError()

    first = True
    while True:
        if first:
            copy_video(wspath_manager, wsjson_manager, '연호설거지_1.MOV.mov')
            first = False
        else:
            _, video_path = cli_selector(wspath_manager, wsjson_manager)
            if video_path is None:
                vis_tree(wspath_manager, wsjson_manager)
                break
            copy_video(wspath_manager, wsjson_manager, video_path)
        veditutils.split_video(wspath_manager, wsjson_manager, -1)
        vis_tree(wspath_manager, wsjson_manager)
        logger.info('5초 뒤 다음 동영상을 선택합니다.')
        time.sleep(5)
