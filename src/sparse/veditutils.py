import os
import json
import logging
import subprocess

from .timing import videoplayer
from .manager import WorkSpacePathManager, WorkSpaceJsonManager

# 로거
logger = logging.getLogger(__name__)


def check_video(
    video_path: os.PathLike
) -> list:
    clips = []
    times = videoplayer(video_path)
    for i, time in enumerate(times):
        if i == 0:
            prevtime = time
            continue
        else:
            clips.append(prevtime.until(time))
        if i == len(times) - 1:
            break
        prevtime = time

    return clips


def split_video(
    wspath_manager: WorkSpacePathManager,
    wsjson_manager: WorkSpaceJsonManager,
    raw_idx: int,
):
    video_path = wspath_manager.read_raw_path(wsjson_manager, raw_idx)
    clips = check_video(video_path)
    # create split manifest file
    # NOTE: a manifest file is required to split a video file
    # to utilize thirdparty/video-splitter
    with open(wspath_manager.wsjson_path, 'r') as f:
        d = json.load(f)
    for i, clip in enumerate(clips):
        stem, suffix = wspath_manager.read_raw_name(wsjson_manager)
        clip['rename_to'] = os.path.join(
            wspath_manager.read_clips_dir(wsjson_manager, raw_idx),
            f'{stem}_clip_{i}{suffix}'
        )
    with open(wspath_manager.get_splitmanifestfile_path(wsjson_manager, raw_idx), 'w') as f:
        json.dump(clips, f, indent=4, ensure_ascii=False)

    # run python file
    py = os.path.join('thirdparty', 'video-splitter', 'ffmpeg-split.py')
    splitjson_path = wspath_manager.read_splitmanifestfile_path(wsjson_manager, raw_idx)
    with open(wspath_manager.get_splitlogfile_path(wsjson_manager, -1), 'w') as f:
        subprocess.Popen([
            'python', f'{py}',
            '-f', f'{video_path}',
            '-m', f'{splitjson_path}'
        ], stdout=f, stderr=f)
    logger.info('동영상을 클립으로 분해하는 작업이 완료되었습니다.')
