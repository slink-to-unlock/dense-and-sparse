import cv2
import os
import argparse
import json
import natsort


def video2imgs(path, fps):  # clips/clip1.mp4 -> clip_frames/clip1
    id = path.split("/")[-1][:-4]  # clip1
    save_dir = os.path.join("clip_frames/", id)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)  # 해당 경로 폴더 생성
    vidcap = cv2.VideoCapture(path)  # 비디오 읽어오기
    vid_fps = vidcap.get(cv2.CAP_PROP_FPS)
    rate = vid_fps // fps
    count = 0

    if rate == 0:
        while True:
            success, image = vidcap.read()
            if success is False:
                break  # 읽어 올 영상이 없으면 끝내기
            if success is True:
                cv2.imwrite(
                    save_dir + "/%06d.jpg" % count, image
                )  # save frame as JPEG file
                # print('Read a new frame: ', success)
                count += 1
    else:
        while True:
            success, image = vidcap.read()
            if success is False:
                break  # 읽어 올 영상이 없으면 끝내기

            if (success is True) and (
                vidcap.get(cv2.CAP_PROP_POS_FRAMES) % (rate) == 0
            ):  # 원하는 fps로 frame을 저장하기 위한 조건
                cv2.imwrite(
                    save_dir + "/%06d.jpg" % count, image
                )  # save frame as JPEG file
                # print('Read a new frame: ', success)
                count += 1
    print("finish! convert video to frame (%d count)" % count)
    return save_dir


def DenseModule(frame_dir, image_names, label, sampling, size):
    cv2.namedWindow("image")

    for idx, image_name in enumerate(image_names):
        image_path = os.path.join(frame_dir, image_name)  # frame_dir + image_name
        image = cv2.imread(image_path)
        image = cv2.resize(image, (size, size), interpolation=cv2.INTER_LINEAR)

        if (
            idx < sampling or idx > len(image_names) - sampling
        ):  # 비디오의 앞,뒤 구간에 해당하는 이미지일 경우
            flag = False

            while True:
                cv2.imshow("image", image)  # show image in window
                key = cv2.waitKey(0)

                if key == ord("0"):
                    new_dir = "./0/" + frame_dir.split("/")[-1] + "_" + image_name
                    cv2.imwrite(new_dir, image)
                    break

                if key == ord("1"):
                    new_dir = "./1/" + frame_dir.split("/")[-1] + "_" + image_name
                    cv2.imwrite(new_dir, image)
                    break

                if key == ord("r"):
                    break

                if key == ord("q"):
                    # 프로그램 종료
                    flag = True
                    break

        else:  # do not dense mode(just move image with video label)
            cv2.destroyAllWindows()
            flag = False
            if label == 0:
                new_dir = "./0/" + frame_dir.split("/")[-1] + "_" + image_name
                print(new_dir)
                cv2.imwrite(new_dir, image)
            elif label == 1:
                new_dir = "./1/" + frame_dir.split("/")[-1] + "_" + image_name
                print(new_dir)
                cv2.imwrite(new_dir, image)

        if flag:
            break

    # 모든 window를 종료합니다.
    cv2.destroyAllWindows()


def GetArgument():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True, help="Enter the clip folder")
    ap.add_argument(
        "--fps", default=15, help="Enter the fps to convert image.(default = 15)"
    )
    ap.add_argument(
        "--sampling", default=30, help="Enter the frame number to check.(default = 20)"
    )
    ap.add_argument("--label_file", required=True, help="Enter the label file of clip.")
    ap.add_argument(
        "--size", default=520, help="Enter the resize size of image.(default = 520)"
    )
    args = vars(ap.parse_args())
    folder = args["folder"]
    label_file = args["label_file"]
    fps = int(args["fps"])
    sampling = int(args["sampling"])
    size = int(args["size"])
    return folder, label_file, fps, sampling, size


def main():
    # 이미지 디렉토리 경로를 입력 받는다.
    folder, label_file, fps, sampling, size = GetArgument()

    if not os.path.exists("./0"):
        os.makedirs("./0")  # 해당 경로 폴더 생성
    if not os.path.exists("./1"):
        os.makedirs("./1")  # 해당 경로 폴더 생성
    if not os.path.exists("./clip_frames"):
        os.makedirs("./clip_frames")  # 해당 경로 폴더 생성

    with open("result.json", "r") as f:
        datas = json.load(f, strict=False)
    # print(json_data[0]['name'])
    root_path = "clips/"

    for data in datas:
        print("\n")
        print("1. 입력한 파라미터인 clip 경로(--path)에서 이미지들을 차례대로 읽어옵니다.")
        print("2. 키보드에서 '0'을 누르면(물x) 해당폴더로 이동합니다.")
        print("3. 키보드에서 '1'를 누르면(물o) 해당폴더로 이동합니다.")
        print("4. 키보드에서 'r'를 누르면 버리는 이미지에 해당합니다.")
        print("5. 이미지 경로에 존재하는 모든 이미지에 작업을 마친 경우 또는 'q'를 누르면(quit 약자) 프로그램이 종료됩니다.")

        path = os.path.join(root_path, data["name"])  # clips/clip1.mp4
        label = data["sparselabel"][0]
        frame_dir = video2imgs(path, fps)

        # 이미지로 저장된 폴더명을 받는다.
        image_names = os.listdir(frame_dir)  # images list
        image_names = natsort.natsorted(image_names)  # sort images list
        # print(image_names)

        DenseModule(frame_dir, image_names, label, sampling, size)

        # create new window


if __name__ == "__main__":
    main()
