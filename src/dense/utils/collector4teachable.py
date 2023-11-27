""" 이 스크립트는 `./volume` 의 하위디렉토리를 순회하며 google teachable machine 이 요구하는 디렉토리 구조에 맞도록
`./form_teachable` 디렉토리로 파일들을 복사한다. google teachable machine 이 요구하는 학습 데이터셋 디렉토리는
`./form_teachable/0/*`, `./form_teachable/1/*` 과 같다.
디렉토리 0과 1 내에는 다른 디렉토리가 네스팅되어 있으면 안된다.

`./volume` 디렉토리에는 다양한 사람들의 설거지 영상들이 저장된 디렉토리가 보관되어 있다.
예를 들어, `./volume/다현설거지/0`, `./volume/다현설거지/1`, `./volume/석우설거지/0`, `./volume/석우설거지/1` ... 과 같다.
각각의 경우 디렉토리 0에는 레이블이 0인 영상들이 저장되어 있고, 1에는 레이블이 1인 영상들이 저장되어 있다.
디렉토리 0에 들어 있던 모든 영상들은 `./form_teachable/0/` 으로 복사되어야 하고
디렉토리 1에 들어 있던 모든 영상들은 `./form_teachable/1/` 으로 복사되어어야 한다.

하지만 이때 디렉토리에 들어 있는 영상들의 이름은 전역적으로 고유하지 않으므로 이름을 변경한다.
`./다현설거지/0/` 디렉토리의 `file_0.png` 를 `./form_teachable/0/` 디렉토리로 옮긴다고 하면
volume 디렉토리의 하위 디렉토리 이름을 파일명에 반영하여 `다현설거지_file_0.png` 로 이름이 변경되어 복사된다.
"""

import os
import shutil
import argparse


def create_directory_structure(target_dir):
    # Create the target directory structure if it does not exist
    for i in range(2): # Assuming 0 and 1 are the only directories
        dir_path = os.path.join(target_dir, str(i))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

def copy_and_rename_files(base_dir, target_dir):
    for subdir in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir)
        if os.path.isdir(subdir_path):
            for label_dir in ["0", "1"]:
                label_dir_path = os.path.join(subdir_path, label_dir)
                if os.path.exists(label_dir_path):
                    for file in os.listdir(label_dir_path):
                        # Renaming and copying the file
                        new_filename = f"{subdir}_{file}"
                        source_file_path = os.path.join(label_dir_path, file)
                        target_file_path = os.path.join(target_dir, label_dir, new_filename)
                        shutil.copy2(source_file_path, target_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy and rename files for teachable machine')
    parser.add_argument('--base_dir', type=str, help='Base directory path', default='volume', required=False)
    parser.add_argument('--target_dir', type=str, help='Target directory path', default='form_teachable', required=False)
    args = parser.parse_args()

    base_dir = args.base_dir
    target_dir = args.target_dir

    if os.path.realpath(target_dir).startswith(os.path.realpath(base_dir)):
        raise ValueError("target_dir should not be a subdirectory of base_dir")
    create_directory_structure(target_dir)
    copy_and_rename_files(base_dir, target_dir)
