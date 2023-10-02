import argparse
from io import TextIOWrapper
import os
import pathlib
import re
import shutil
import typing as t

import music_tag

import tqdm


DictKeys: t.TypeAlias = (
    t.Literal["AudioFilename"] |
    t.Literal["TitleUnicode"] |
    t.Literal["ArtistUnicode"] |
    t.Literal["Title"]
)

def load_osu(file: TextIOWrapper) -> dict[DictKeys, str]:
    cur_object = {}
    for line in file:
        for field in [
            "AudioFilename",
            "TitleUnicode",
            "ArtistUnicode",
            "Title",
            "Artist",
        ]:
            if line.startswith(field):
                cur_object[field] = line.split(":")[-1].strip()

    return cur_object


def extract_audio(path: pathlib.Path):
    pattern = re.compile(r"[<>:\"/\\|?*]")
    songs_dir = path / "Songs"
    os.makedirs("out", exist_ok=True)
    for folder_name in tqdm.tqdm(os.listdir(songs_dir)):
        audio_files: dict[str, dict[DictKeys, str]] = {}
        for osus in (songs_dir / folder_name).glob("*.osu"):
            with open(osus, encoding="utf-8") as f:
                data = load_osu(f)
                filename = data["AudioFilename"]
                audio_files[filename] = data
        for k, v in audio_files.items():
            if "TitleUnicode" in v:
                title = v["TitleUnicode"]
            else:
                title = v["Title"]

            if "ArtistUnicode" in v:
                artist = v["ArtistUnicode"]
            else:
                artist = v["Artist"]

            copied_filename = f'{title}.{v["AudioFilename"].split(".")[-1]}'
            copied_filename = re.sub(pattern, "", copied_filename)
            # for x in invalid_chars:
            try:
                shutil.copy2(
                    songs_dir / folder_name / k,
                    pathlib.Path("out") / copied_filename
                )
                f = music_tag.load_file(pathlib.Path("out") / copied_filename)
                f["title"] = title
                f["artist"] = artist
            except Exception as e:
                print("Warning, ", e)
                pass


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
