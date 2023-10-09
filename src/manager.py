import os
import json
import pathlib
import logging

# 로거
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class WorkSpaceJsonManager():
    def __init__(self) -> None:
        pass

    def create_json(self, path):
        with open(path, 'w') as f:
            json.dump({'raws': []}, f, indent=4, ensure_ascii=False)

    def fn_raws(self):
        return lambda d: d['raws']

    def fn_raw_names(self):
        def generator(d):
            for raw in self.fn_raws()(d):
                yield raw['raw_name']
        return lambda d: generator(d)

    def fn_video(self, raw_idx: int):
        return lambda d: self.fn_raws()(d)[raw_idx]

    def dump(self, json_path, d: dict, fn = None):
        """ 딕셔너리의 키가 json 파일에 존재하면 값을 덮어쓰고,
            존재하지 않으면 새로운 키-값 쌍을 json 파일의 특정 위치에 추가합니다.

        Args:
            d (dict): 덮어쓰거나 추가할 데이터가 있는 딕셔너리.
            fn (function, optional): 딕셔너리를 인자로 받아 딕셔너리를 리턴하는 함수
                이 함수를 이용하여 json 파일에서 어떤 부분을 수정할지 지정하는 일에 사용
                Defaults to None.
        """
        if fn is None:
            fn = self.fn_video(-1)
        with open(json_path, 'r') as f:
            original = json.load(f)
        assert type(fn(original)) is dict
        for k, v in d.items():
            fn(original)[k] = v
        with open(json_path, 'w') as f:
            json.dump(original, f, indent=4, ensure_ascii=False)

    def append(self, json_path, e, fn = None):
        """ 딕셔너리의 키가 json 파일에 존재하고 이에 대응하는 값이 리스트면 값을 append 하고,
            존재하지 않으면 새로운 값을 json 파일의 특정 위치에 리스트 형태로 추가합니다.

        Args:
            e: append 할 데이터
            fn (function, optional): 딕셔너리를 인자로 받아 딕셔너리를 리턴하는 함수
                이 함수를 이용하여 json 파일에서 어떤 부분을 수정할지 지정하는 일에 사용
                Defaults to None.
        """
        if fn is None:
            fn = self.fn_raws()
        with open(json_path, 'r') as f:
            original = json.load(f)
        assert type(fn(original)) is list
        fn(original).append(e)
        with open(json_path, 'w') as f:
            json.dump(original, f, indent=4, ensure_ascii=False)

    def template_newraw(self,
                        original_video_name: str,
                        new_name_with_suffix: str,
                        new_path: str,
                        clips_dir: str) -> dict:
        """ json 템플릿을 생성하고 값을 작성하여
            json 파일에 작성할 수 있는 형태로 리턴합니다.

        Args:
            original_video_name (str): 원본 동영상의 이름
            new_name (str): 워크스페이스 내부로 복사된 원본 동영상의 이름
            new_path (str): 워크스페이스 내부로 복사된 원본 동영상의 경로
            clips_dir (str): 나누어진 클립이 저장되는 디렉토리

        Returns:
            dict: 값이 작성된 json 템플릿
        """
        return {
            'original_video_name': original_video_name,
            'raw_name': new_name_with_suffix,
            'raw_path': new_path,
            'clips_dir': clips_dir
        }

class WorkSpacePathManager():
    """ 경로와 관련된 작업을 하는 클래스
        NOTE: 이 클래스는 절대 json파일의 키를 직접 읽거나 쓰지 않습니다.
        반드시 WorkSpaceJsonManager을 통해서만 상호작용합니다.
    """
    def __init__(self, parent_dir, name_ws) -> None:
        self._parent_dir = parent_dir
        self._name_ws = name_ws
        self.ws_dir = os.path.join(self._parent_dir, self._name_ws)
        self.wsjson_path = os.path.join(self.ws_dir, 'workspace.json')
        self.raw_dir = os.path.join(self.ws_dir, 'raws')

    def get_rawname(self,
                    wsjson_manager: WorkSpaceJsonManager,
                    original_video_path: os.PathLike
                    ) -> str:
        """ 이 라이브러리에서 칭하는 'raw'란 'clip'으로 쪼개질 수 있는
            비디오를 의미합니다. 한 번 쪼개진 'clip' 도 다시 'raw'가 될 수 있습니다.
            이때 모든 'raw'와 'clip'은 파일의 이름을 통해 구분됩니다.
            따라서 중복되지 않는 적절한 이름을 탐색하는 작업이 중요합니다.

        Args:
            wsjson_manager (WorkSpaceJsonManager): 생략
            original_video_path (os.PathLike): 'raw'가 될 후보 비디오의 경로.
                새롭게 워크스페이스에 등록되는 비디오의 경로가 될 수도 있고,
                이미 워크스페이스에 들어 있지만 더 쪼개고 싶은 비디오의 경로가 될 수 있습니다.

        Returns:
            str: 새로운 이름
        """
        ori = pathlib.Path(original_video_path)
        original_video_fullname = ori.stem + ori.suffix
        newname = ''
        with open(self.wsjson_path, 'r') as f:
            d = json.load(f)
        cnt = 0
        for raw_fullname in wsjson_manager.fn_raw_names()(d):
            if raw_fullname == original_video_fullname:
                newname = ori.stem
                break
            if raw_fullname == f'initial_{cnt}.{ori.suffix}':
                cnt += 1
                newname = f'initial_{cnt}'
        if not newname:
            assert cnt == 0
            newname = f'initial_{cnt}'
        return newname

    def read_rawname(self,
                     wsjson_manager: WorkSpaceJsonManager,
                     raw_idx: int = -1,
                     suffix: bool = True
                     ) -> str:
        with open(self.wsjson_path, 'r') as f:
            d = json.load(f)
        p = pathlib.Path(wsjson_manager.fn_video(raw_idx)(d).get('raw_name'))
        ret = p.stem
        if suffix:
            ret += p.suffix
        return ret

    def set_clips_dir(self,
                      wsjson_manager: WorkSpaceJsonManager,
                      original_video_path: os.PathLike):
        ori = pathlib.Path(original_video_path)
        original_video_fullname = os.path.basename(original_video_path)

        copied_video_newname = self.get_rawname(wsjson_manager, original_video_path)
        copied_video_newfullname = copied_video_newname + ori.suffix
        if original_video_fullname != copied_video_newfullname:
            logger.info(f'동영상 `{original_video_fullname}`의 이름을 '
                        f'`{copied_video_newfullname}`으로 변경합니다.')

        clips_dirname = copied_video_newname
        clips_dirpath = os.path.join(self.ws_dir, clips_dirname)

        t = wsjson_manager.template_newraw(
            original_video_fullname,
            copied_video_newfullname,
            os.path.join(self.raw_dir, copied_video_newfullname),
            clips_dirpath
        )
        wsjson_manager.append(self.wsjson_path, t, wsjson_manager.fn_raws())
        os.makedirs(clips_dirpath)
        return clips_dirpath

    def read_clips_dir(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        with open(self.wsjson_path, 'r') as f:
            d = json.load(f)
        return wsjson_manager.fn_video(raw_idx)(d).get('clips_dir')

    def get_splitlogfile_path(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        return self.read_splitlogfile_path(wsjson_manager, raw_idx)

    def read_splitlogfile_path(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        return os.path.join(self.read_clips_dir(wsjson_manager, raw_idx), 'splitlog.txt')

    def get_splitmanifestfile_path(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        return self.read_splitmanifestfile_path(wsjson_manager, raw_idx)

    def read_splitmanifestfile_path(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        return os.path.join(self.read_clips_dir(wsjson_manager, raw_idx), 'splitmanifest.json')

    def read_raw_path(self, wsjson_manager: WorkSpaceJsonManager, raw_idx: int):
        with open(self.wsjson_path, 'r') as f:
            d = json.load(f)
        return wsjson_manager.fn_video(raw_idx)(d).get('raw_path')
