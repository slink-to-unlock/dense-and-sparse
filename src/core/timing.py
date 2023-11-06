# 빌트인
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

    def __add__(self, timing):
        return Timing(self.misec + timing.misec)

    def __sub__(self, timing):
        return Timing(self.misec - timing.misec)

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
            'start_time': self.sec,
            'length': (end - self).sec,
            # NOTE: 이유는 정확히 모르겠으나,
            # 일부 컴퓨터에서 ffmpeg의 'end_time' 옵션이
            # 정상적으로 인식되지 않는 문제가 있으므로
            # 되도록이면 `length` 옵션을 사용할 것
        }
