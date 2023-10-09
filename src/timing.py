import cv2
class Timing:
    def __init__(self, misec_: int) -> None:
        assert misec_ >= 0 and type(misec_) is int
        self.misec_ = misec_
        self.totalsec_ = round(self.misec_/1000)

    def __str__(self) -> str:
        return self.to_stamp()

    def split_min_sec(self):
        return self.totalsec_//60, self.totalsec_%60

    def to_stamp(self):
        self.min_,self.sec_ = self.split_min_sec()
        return f'00:{self.min_:02}:{self.sec_:02}'


def videoplayer(video_path):
    capture = cv2.VideoCapture(video_path)
    times = [0]
    while capture.isOpened():
        run, frame = capture.read()
        key = cv2.waitKeyEx(30)
        # print(capture.get(cv2.CAP_PROP_POS_MSEC))
        if not run:
            print("[프레임 수신 불가] - 종료합니다")
            break
        prev_time = capture.get(cv2.CAP_PROP_POS_MSEC)
        img = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (520, 520))

        cv2.imshow('video', img)
        # cv2.waitKey(30)
        if key == ord('s'):
            cv2.waitKeyEx()
        if key == ord('p'):
            cv2.waitKeyEx(30)
        if key == ord('q'):
            # 프로그램 종료
            break
        if key == ord('t'):
            t = capture.get(cv2.CAP_PROP_POS_MSEC)
            times.append(int(t))

        if key == 0x250000:
            current_time = capture.get(cv2.CAP_PROP_POS_MSEC)
            capture.set(cv2.CAP_PROP_POS_MSEC, current_time - 1000)
        if key == 0x270000:
            current_time = capture.get(cv2.CAP_PROP_POS_MSEC)
            capture.set(cv2.CAP_PROP_POS_MSEC, current_time + 1000)

    capture.release()
    cv2.destroyAllWindows()
    times.append(int(prev_time))
    print('times:',times)
    return times

def to_dict(start: Timing, end: Timing) -> dict:
    return {
        'start_time': start.to_stamp(),
        'end_time': end.to_stamp(),
    }


if __name__ == '__main__':
    # print(Timing(0, 10))
    # print(Timing(10, 5))
    print(123456)
    print(Timing(123456))
    print(to_dict(Timing(0),Timing(123456)))

