# 빌트인
import os
import json
import logging

# 서드파티
import cv2
import pick

# 프로젝트
from .manager import WorkSpacePathManager, WorkSpaceJsonManager
from .manager import ResultJsonManager

# 로거
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def video_player(
    video_path: os.PathLike
) -> list:
    assert os.path.isfile(video_path)
    label = []
    running = True
    video = cv2.VideoCapture(video_path)
    w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    while running:
        logger.debug(
            f'비디오 `{os.path.basename(video_path)}`를 '
            '처음부터 다시 재생합니다.'
        )
        while video.isOpened():
            _valid, img = video.read()
            current_frame = int(video.get(cv2.CAP_PROP_POS_FRAMES))
            if not _valid:
                logger.error(
                    f'비디오 `{os.path.basename(video_path)}`'
                    f'의 총 {total_frames}프레임 중, '
                    f'{current_frame + 1}번째 프레임 '
                    '을 정상적으로 열 수 없습니다.'
                )
                video.set(cv2.CAP_PROP_POS_MSEC, 0)
                break
            img = cv2.resize(img, (w//4, h//4))
            img = cv2.cvtColor(img, cv2.IMREAD_COLOR)
            img = cv2.putText(
                img,
                text=f'{current_frame}/{total_frames}',
                org=(10, 30),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1,
                color=(255, 255, 255),
                thickness=2
            )
            cv2.imshow(os.path.basename(video_path), img)
            key = cv2.waitKey(1)
            if key == ord('q'):
                running = False
                break
            elif key == ord('0'):
                running = False
                label.append(0)
                break
            elif key == ord('1'):
                running = False
                label.append(1)
                break
    video.release()
    cv2.destroyAllWindows()
    return label


def do_labeling(
    wspath_manager: WorkSpacePathManager,
    resjson_manager: ResultJsonManager
):
    with open(wspath_manager.resjson_path, 'r') as f:
        d = json.load(f)
    for i, video in enumerate(videos:=resjson_manager.fn_videos()(d)):
        clip_name = resjson_manager.get_clip_name(video)
        video_path = os.path.join(
            wspath_manager.result_dir,
            clip_name
        )
        logger.info(
            f'총 {len(videos)}개의 비디오 중 '
            f'{i}번째 비디오 `{clip_name}`를 엽니다.'
        )
        new_label = video_player(video_path)
        logger.info(
            '동영상의 레이블을 '
            f'`{resjson_manager.get_label(video)}`에서 '
            f'`{new_label}`(으)로 변경합니다.'
        )
        resjson_manager.change_label(video, new_label)
    with open(wspath_manager.resjson_path, 'w') as f:
        json.dump(d, f, indent=4, ensure_ascii=True)
