# 빌트인
import os
import logging

# 서드파티
import cv2

# 로거
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Timing:
    def __init__(self, misec: int) -> None:
        assert type(misec) is int, f'type(misec) is {type(misec)}, not int'
        assert misec >= 0, f'misec is {misec}, not >= 0'
        self._misec = None
        self._sec = None
        self.misec = misec # call setter

    def __str__(self) -> str:
        return self.to_stamp()

    @property
    def misec(self) -> int:
        return self._misec

    @misec.setter
    def misec(self, v):
        self._misec = v
        self._sec = round(self.misec / 1000)

    @property
    def sec(self) -> float:
        return self._sec

    @sec.setter
    def sec(self, v):
        self._sec = v
        self._misec = 1000 * v

    def to_stamp(self):
        h = 0
        m = self.sec // 60
        if m >= 60:
            h = m // 60
            m = m % 60
        s = self.sec % 60
        return f'{h:02}:{m:02}:{s:02}'

    def until(self, end, pad: bool = False) -> dict:
        if pad:
            raise NotImplementedError()
        return {
            'start_time': self.to_stamp(),
            'end_time': end.to_stamp(),
        }


def videoplayer(
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
