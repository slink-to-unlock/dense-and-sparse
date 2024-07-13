# 내장
import os
import json
import shutil
import datetime
from typing import Optional, Union

# 서드파티
from PIL import Image
import streamlit as st
import pandas as pd


def list_directories(path):
    """ 지정된 경로에 있는 모든 디렉토리를 리스트로 반환 """
    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return directories


def get_files(directory):
    """ 디렉토리 내의 모든 파일들을 JSON 파일로 분류하여 반환 """
    files = os.listdir(directory)
    json_file = [f for f in files if f.endswith('.json')]
    return json_file[0] if json_file else None


def load_json(directory, file_name):
    """ JSON 파일을 로드하고 내용을 반환. 파일은 다음과 같은 형태.
    {
        "interactions": [
            {
                "image": "105.png",
                "auto_label": 0,
                "user_label": 1,
                "validation": true
            },
            {
                "image": "106.png",
                "auto_label": 0,
                "user_label": 1,
                "validation": true
            },
            ...
        ],
        "pushed_to_feature_store": true,
        "last_pushed_to_feature_store": "2024-06-08 18:43:46.479181"
    }
    """
    with open(os.path.join(directory, file_name), 'r') as file:
        return json.load(file)


def save_json(directory, file_name, data):
    """ JSON 데이터를 파일로 저장 """
    with open(os.path.join(directory, file_name), 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def label_to_int(label):
    """ 레이블을 내부 정수로 변환 """
    return 1 if label == "Turn on" else 0


def int_to_label(value):
    """ 내부 정수를 사용자 레이블로 변환 """
    return "Turn on" if value == 1 else "Turn off"


def copy_and_organize_images(directory, interactions, feature_store_path):
    """ Validated 이미지를 각각의 폴더로 복사 """
    copy_cnt = 0
    for i, interaction in enumerate(interactions):
        if interaction.get('validation', False):  # Only copy validated images
            image_path = os.path.join(directory, interaction['image'])
            label = interaction['user_label']
            target_folder = os.path.join(feature_store_path, str(label))
            os.makedirs(target_folder, exist_ok=True)
            new_name = f"{os.path.basename(directory)}-{i}.{image_path.split('.')[-1]}"
            shutil.copy(image_path, os.path.join(target_folder, new_name))

            copy_cnt += 1
    # NOTE: DEBUG
    st.info(f'{copy_cnt} files copied into {feature_store_path}')
    if copy_cnt:
        assert os.listdir(
            feature_store_path
        ), f'file not exists in {feature_store_path} even though {copy_cnt} files copied.'
    # Mark directory as pushed
    return True


def app(
    workspace_path: Optional[Union[os.PathLike, str]] = None,
    feature_store_path: Optional[Union[os.PathLike, str]] = None
):
    """ Streamlit 애플리케이션의 진입점입니다.

    Args:
      workspace_path: Directory where your application will store and access files
    related to its operation. 지정되지 않는 경우 streamlit session state 으로부터 값을 가져옵니다.
      feature_store_path: 정제가 완료된 데이터셋을 쓰는 경로입니다. 지정되지 않는 경우
    streamlit session state 으로부터 값을 가져옵니다.
    NOTE: 이 함수는 버전을 관리하지 않습니다. 최종 디렉토리 경로를 지정해 주어야 합니다. (e.g. feature-store/train/v7)
    """
    if workspace_path is None:
        workspace_path = st.session_state.get('workspace_path')
    assert isinstance(
        workspace_path, (str, os.PathLike)
    ), f'타입 `{type(workspace_path)}` 은 경로가 아닙니다.'
    if feature_store_path is None:
        feature_store_path = st.session_state.get('feature_store_path')
    assert isinstance(
        feature_store_path, (str, os.PathLike)
    ), f'타입 `{type(feature_store_path)}` 은 경로가 아닙니다.'

    st.title('Continuous Labeling')
    directories = list_directories(workspace_path)

    directory_info = []
    for directory in directories:
        full_path = os.path.join(workspace_path, directory)
        json_file = get_files(full_path)
        if json_file:
            data = load_json(full_path, json_file)
            last_pushed = data.get('last_pushed_to_feature_store', 'Not yet pushed')
            last_updated = data.get('last_updated', 'Not yet updated')
        else:
            last_pushed = 'Not yet pushed'
            last_updated = 'Not yet updated'
        directory_info.append(
            {
                'Directory Name': directory,
                'Last Pushed to Feature Store': last_pushed,
                'Last Updated in Data Lake': last_updated
            }
        )

    df = pd.DataFrame(directory_info)
    st.table(df)

    selected_directory = st.selectbox('Select a directory:', directories)
    if selected_directory:
        full_path = os.path.join(workspace_path, selected_directory)
        json_file = get_files(full_path)

        if json_file:
            data = load_json(full_path, json_file)
            interactions = data.get('interactions', [])
            feature_store_pushed = data.get('pushed_to_feature_store', False)

            total_images = len(interactions)
            unvalidated_images = sum(
                1 for interaction in interactions if not interaction.get('validation', False)
            )

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Images", total_images)
            with col2:
                st.metric("Unvalidated Images", unvalidated_images)

            image_index = st.slider('Select an image', 0, len(interactions) - 1, 0)
            interaction = interactions[image_index]
            image_path = interaction.get('image')
            auto_label = interaction.get('auto_label', 'No label')
            user_label = int_to_label(interaction.get('user_label', 0))
            is_validated = interaction.get('validation', False)

            if feature_store_pushed:
                st.info("This directory has already been pushed to the feature-store.")

            if is_validated:
                st.info("This image has already been validated and can still be edited.")

            if image_path:
                image = Image.open(os.path.join(full_path, image_path))
                st.image(image, caption=f'Autolabel: {int_to_label(auto_label)}')

            new_user_label = st.radio(
                f'Label for {image_path}:', ['Turn on', 'Turn off'],
                index=['Turn on', 'Turn off'].index(user_label)
            )
            if st.button(f'Validate Label for {image_path}'):
                interactions[image_index]['user_label'] = label_to_int(new_user_label)
                interactions[image_index]['validation'] = True
                save_json(full_path, json_file, data)
                st.success(f'Label for {image_path} validated successfully.')

            all_validated = unvalidated_images == 0
            if all_validated:
                if st.button("Push to feature-store"):
                    feature_store_pushed = copy_and_organize_images(
                        full_path,
                        interactions,
                        feature_store_path,
                    )
                    data['pushed_to_feature_store'] = feature_store_pushed
                    data['last_pushed_to_feature_store'] = str(datetime.datetime.now())
                    save_json(full_path, json_file, data)
                    st.success("Images have been successfully pushed to feature-store.")

        else:
            st.error('No JSON file found in the selected directory.')


if __name__ == '__main__':
    app()
