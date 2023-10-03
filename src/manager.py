import os
import json


class WorkSpaceJsonManager():
    def __init__(self) -> None:
        pass

    def create_json(self, path):
        with open(path, 'w') as f:
            json.dump({'raws': []}, f, indent=4, ensure_ascii=False)

    def fn_raws(self):
        return lambda x: x['raws']

    def fn_video(self, raw_idx: int):
        return lambda x: self.fn_raws()(x)[raw_idx]

    def _dump(self, wspath_manager, d: dict, fn = None):
        """ 이 함수를 클래스 외부에서 직접적으로 호출하지 마세요.
        아직 불안정한 함수입니다. 딕셔너리의 키가 json 파일에 존재하면 값을 덮어쓰고,
        존재하지 않으면 새로운 키-값 쌍을 json 파일의 특정 위치에 추가합니다.

        Args:
            d (dict): 덮어쓰거나 추가할 데이터가 있는 딕셔너리.
            fn (function, optional): 딕셔너리를 인자로 받아 딕셔너리를 리턴하는 함수
                이 함수를 이용하여 json 파일에서 어떤 부분을 수정할지 지정하는 일에 사용
                Defaults to None.
        """
        if fn is None:
            fn = self.fn_video(-1)
        with open(wspath_manager.wsjson_path, 'r') as f:
            original = json.load(f)
        assert type(fn(original)) is dict
        for k, v in d.items():
            fn(original)[k] = v
        with open(wspath_manager.wsjson_path, 'w') as f:
            json.dump(original, f, indent=4, ensure_ascii=False)


class WorkSpacePathManager():
    def __init__(self, parent_dir, name_ws) -> None:
        self._parent_dir = parent_dir
        self._name_ws = name_ws
        self.ws_dir = os.path.join(self._parent_dir, self._name_ws)
        self.wsjson_path = os.path.join(self.ws_dir, 'workspace.json')
        self.raw_dir = os.path.join(self.ws_dir, 'raws')

    def get_clips_dir(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        dirname = f'clips_{raw_idx}'
        p = os.path.join(self.ws_dir, dirname)
        os.makedirs(p)
        # TODO: JsonManager 에 값을 추가하는 기능 추가
        return p

    def read_clips_dir(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        with open(self.wsjson_path, 'r') as f:
            d = json.load(f)
        return wsjson_manager.fn_video(raw_idx)(d).get('clips_dir')

    def get_splitmanifestfile_path(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        # NOTE: pathmanager 이 처리 가능한 부분으로, JSON 파일에 등록할 필요가 없음.
        # TODO: 하지만 추후 일관성을 위해서라도 read 와 분리해볼 것.
        return self.read_splitmanifestfile_path(wsjson_manager, raw_idx)

    def read_splitmanifestfile_path(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        return os.path.join(self.read_clips_dir(wsjson_manager, raw_idx), 'splitmanifest.json')

    def read_raw_path(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        with open(self.wsjson_path, 'r') as f:
            d = json.load(f)
        return wsjson_manager.fn_video(raw_idx)(d).get('raw_path')
