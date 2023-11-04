import json
import os

clips_directory = os.path.join('test-ws', 'sparse-label')
label_json = os.path.join(clips_directory, 'result.json')
def main():
    with open(label_json, "r") as f:
        datas = json.load(f, strict=False)



if __name__ == "__main__":
    main()
