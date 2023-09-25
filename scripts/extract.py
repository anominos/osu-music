import argparse
import os
import pathlib

def extract_audio(path: pathlib.Path):
    songs_dir = path / "Songs"
    c = 0
    for path in songs_dir.rglob("*.osu"):
        c += 1
    print(c)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--folder-path", "-f", type=str)
    group.add_argument("--windows-username", "-w", type=str)

    args = parser.parse_args()
    path: pathlib.Path
    if args.windows_username is not None:
        assert os.name == "nt", "-w should only be used on Windows"
        path = pathlib.Path(r"C:\Users") / args.windows_username / "AppData" / "Local" / "osu!"
    elif args.folder_path is not None:
        path = pathlib.Path(args.folder_path)
    extract_audio(path)
