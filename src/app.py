import os
import json
import time

import streamlit as st

clips_directory = os.path.join('volume', 'test-ws', 'sparse-label')
label_json = os.path.join(clips_directory, 'result.json')


@st.cache_data
def get_video_paths():
    with open(label_json, 'r') as f:
        li = json.load(f)
    # st.write(li)
    video_paths = []
    for e in li:
        video_path = os.path.join(clips_directory, e['clip_name'])
        assert os.path.exists(video_path)
        video_paths.append(video_path)
    return video_paths


video_paths = get_video_paths()
selected_video_path = st.selectbox('레이블링할 비디오', video_paths)
col1, col2 = st.columns([1, 1])
with col1:
    video_file = open(selected_video_path, 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)
with col2:
    레이블_규약_버전 = st.selectbox('레이블 규약 버전', [1])
    단계 = st.selectbox('설거지 단계', [
        '애벌', '세제', '수세미 헹굼', '헹굼'
    ])
    수세미를_든_손 = st.radio('수세미를 든 손 (수세미, 손 모두 보여야 함)', [
        '보임', '안보임'
    ])
    식기를_든_손 = st.radio('식기를 든 손 (식기, 손 모두 보여야 함)', [
        '보임', '안보임'
    ])
    지정한_위치_내에_식기 = st.radio('수전 아래 영역 내에 식기가 들어옴', [
        '예', '아니오'
    ], disabled=(식기를_든_손 != '보임'))
    물이_틀어져_있음 = st.radio('물이 틀어져 있음', [
        '예', '아니오'
    ])
    label = None
    if 레이블_규약_버전 == 1:
        if (단계 == '세제'):
            if 수세미를_든_손 == '안보임':
                st.warning('고려하지 않음')
                label = -1
            else:
                st.info('물 끄기', icon='🏷️')
                label = 0
        elif (단계 == '헹굼'):
            if 수세미를_든_손 == '보임':
                st.error('아웃라이어')
                label = -1
            else:
                if 식기를_든_손 == '보임':
                    if 지정한_위치_내에_식기 == '예':
                        st.info('물 틀기', icon='🏷️')
                        label = 1
                    else:
                        st.info('물 끄기', icon='🏷️')
                        label = 0
                else:
                    st.info('물 끄기', icon='🏷️')
                    label = 0
        else:
            st.warning('고려하지 않음')
            label = -1

with open(label_json, 'r') as f:
    videos = json.load(f)
for video in videos:
    if 'meta_info' in video:
        labeler = video['meta_info'].get('labeler', [])
    else:
        labeler = []
    if 'TODO' not in labeler:
        labeler.append('TODO')
    if video.get('clip_name') == os.path.basename(selected_video_path):
        video['sparse_label'] = [label]
        video['meta_info'] = {
            "step": 단계,
            "scrubber_holding_hand": 수세미를_든_손 == '보임',
            "dishes_holding_hand": 식기를_든_손 == '보임',
            "dishes_in_roi": 지정한_위치_내에_식기 == '예',
            "is_water_falling": 물이_틀어져_있음 == '예',
            "labeler": labeler,
            "last_labeled_time": time.strftime("%Y%m%d-%H:%M:%S")
        }
        break

if st.button('저장', use_container_width=True):
    import pprint
    pprint.pprint(videos)
    with open(label_json, 'w') as f:
        json.dump(videos, f, ensure_ascii=False, indent=4)

st.write(video)
