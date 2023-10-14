import os
import json

from .timing import Timing,videoplayer,to_dict
from .manager import WorkSpacePathManager, WorkSpaceJsonManager


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
            clips.append(to_dict(Timing(prevtime), Timing(time)))
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
        clip['rename_to'] = os.path.join( # destination path
            wspath_manager.read_clips_dir(wsjson_manager, raw_idx),
            f'clip_{i}'
        )
    with open(wspath_manager.get_splitmanifestfile_path(wsjson_manager, raw_idx), 'w') as f:
        json.dump(clips, f, indent=4, ensure_ascii=False)

    # run python file
    py = os.path.join('thirdparty', 'video-splitter', 'ffmpeg-split.py')
    splitjson_path = wspath_manager.read_splitmanifestfile_path(wsjson_manager, raw_idx)
    os.system(f'python {py} -f {video_path} -m {splitjson_path}')
