class Timing:
    def __init__(self, min_: int, sec_: int) -> None:
        assert min_ >= 0 and type(min_) is int
        assert min_ < 60
        assert sec_ >= 0 and type(sec_) is int
        assert sec_ < 60
        self.min_ = min_
        self.sec_ = sec_

    def __str__(self) -> str:
        return self.to_stamp()

    def to_sec(self):
        return self.min_ * 60 + self.sec_

    def to_stamp(self):
        return f'00:{self.min_:02}:{self.sec_:02}'


def to_dict(start: Timing, end: Timing) -> dict:
    return {
        'start_time': start.to_stamp(),
        'end_time': end.to_stamp(),
    }


if __name__ == '__main__':
    print(Timing(0, 10))
    print(Timing(10, 5))
    print(Timing(1, 45))
