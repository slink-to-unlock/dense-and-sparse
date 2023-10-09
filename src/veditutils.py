import os
import json

from .timing import Timing
from .manager import WorkSpacePathManager, WorkSpaceJsonManager


def check_video():
    _ = input()
    pass


def split_video(
    wspath_manager: WorkSpacePathManager,
    wsjson_manager: WorkSpaceJsonManager,
    raw_idx: int,
):
    clips = [ # FIXME: Timing 클래스를 사용하도록 변경해야 함.
        {
            "start_time": 0,
            "length": 34,
        },
        {
            "start_time": 35,
            "length": 22,
        },
        {
            "start_time": 50,
            "end_time": "00:01:20",
        }
    ]

    # create split manifest file
    # NOTE: a manifest file is required to split a video file
    # to utilize thirdparty/video-splitter
    wspath_manager.read_raw_path(wsjson_manager, raw_idx)

    with open(wspath_manager.wsjson_path, 'r') as f:
        d = json.load(f)
    for i, clip in enumerate(clips):
        clip['rename_to'] = os.path.join( # destination path
            wspath_manager.read_clips_dir(wsjson_manager, raw_idx),
            f'{wspath_manager.read_rawname(wsjson_manager, suffix=False)}_clip_{i}'
        )
    with open(wspath_manager.get_splitmanifestfile_path(wsjson_manager, raw_idx), 'w') as f:
        json.dump(clips, f, indent=4, ensure_ascii=False)

    # run python file
    py = os.path.join('thirdparty', 'video-splitter', 'ffmpeg-split.py')
    video_path = wspath_manager.read_raw_path(wsjson_manager, raw_idx)
    splitjson_path = wspath_manager.read_splitmanifestfile_path(wsjson_manager, raw_idx)
    os.system(f'python {py} -f {video_path} -m {splitjson_path}')
