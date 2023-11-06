# 빌트인
import os
import json
import logging
import subprocess

# 서드파티
import cv2

# 프로젝트
from src.core.timing import Timing
from src.core.manager import (
    WorkSpacePathManager,
    WorkSpaceJsonManager
)

# 로거
logger = logging.getLogger(__name__)


def timing_collecter(
    video_path: os.PathLike
):
    capture = cv2.VideoCapture(video_path)
    timings = [Timing(0)]
    while capture.isOpened():
        run, frame = capture.read()
        key = cv2.waitKeyEx(30)

        if not run:
            print("[프레임 수신 불가] - 종료합니다")
            break

        img = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (520, 520))
        cv2.imshow('video', img)
        if (_t:=int(capture.get(cv2.CAP_PROP_POS_MSEC))) >= 0:
            prev_timing = Timing(_t)

        if key == ord('s'):
            cv2.waitKeyEx()
        if key == ord('p'):
            cv2.waitKeyEx(30)
        if key == ord('q'):
            # 프로그램 종료
            break
        if key == ord('t'):
            timing = Timing(int(capture.get(cv2.CAP_PROP_POS_MSEC)))
            logger.info(f'`{timing}`을 절단합니다.')
            timings.append(timing)

        if key == 0x250000:
            current_time = capture.get(cv2.CAP_PROP_POS_MSEC)
            capture.set(cv2.CAP_PROP_POS_MSEC, current_time - 1000)
        if key == 0x270000:
            current_time = capture.get(cv2.CAP_PROP_POS_MSEC)
            capture.set(cv2.CAP_PROP_POS_MSEC, current_time + 1000)

    capture.release()
    cv2.destroyAllWindows()
    timings.append(prev_timing)
    return timings


def get_split_specs(
    video_path: os.PathLike
) -> list:
    split_specs = []
    times = timing_collecter(video_path)
    for i, time in enumerate(times):
        if i == 0:
            prevtime = time
            continue
        else:
            split_specs.append(prevtime.until(time))
        if i == len(times) - 1:
            break
        prevtime = time

    return split_specs


def split_video(
    wspath_manager: WorkSpacePathManager,
    wsjson_manager: WorkSpaceJsonManager,
    raw_idx: int,
):
    """비디오 클립의 목록에서 비디오를 선택해 분할합니다.
    비디오를 분할하여 워크스페이스에 적절히 저장합니다.

    Args:
        raw_idx (int): `raw` 비디오 클립의 인덱스.
            `-1`은 가장 최근에 추가된 비디오를 의미합니다.
    """
    video_path = wspath_manager.read_raw_path(wsjson_manager, raw_idx)
    split_specs = get_split_specs(video_path)

    # create split manifest file
    # NOTE: a manifest file is required to split a video file
    # to utilize thirdparty/video-splitter
    for i, spec in enumerate(split_specs):
        stem, suffix = wspath_manager.read_raw_name(wsjson_manager)
        spec['rename_to'] = os.path.join(
            wspath_manager.read_clips_dir(wsjson_manager, raw_idx),
            f'{stem}_clip_{i}{suffix}'
        )
    with open(wspath_manager.get_splitmanifestfile_path(wsjson_manager, raw_idx), 'w') as f:
        json.dump(split_specs, f, indent=4, ensure_ascii=False)

    # run python file
    script = os.path.join('thirdparty', 'video-splitter', 'ffmpeg-split.py')
    splitjson_path = wspath_manager.read_splitmanifestfile_path(wsjson_manager, raw_idx)
    with open(wspath_manager.get_splitlogfile_path(wsjson_manager, -1), 'w') as f:
        subprocess.Popen([
            'python', f'{script}',
            '-f', f'{video_path}',
            '-m', f'{splitjson_path}'
        ], stdout=f, stderr=f)

    logger.info('동영상을 클립으로 분해하는 작업이 완료되었습니다.')
