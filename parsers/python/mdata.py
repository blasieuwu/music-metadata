# Music Metadata • copyright blasieuwu, 2026
# a better way of getting track metadata.
from pathlib import Path
from typing import Any
import sys, re

REQUIRED = {
    "title",
    "artist",
    "album",
    "explicit"
}

def validate_mdata(file_name: str, silent: bool = False, yields: bool = False, track_identity=None) -> dict | None:
    directory = Path(__file__).parent.resolve()
    file_path = Path(directory / file_name).resolve()
    file_ext = Path(file_name).suffix

    if not file_path.exists():
        if not silent:
            print(f"\x1b[1;31m[1/2] [-] file wasn't located.\x1b[0m")
        return

    if file_ext != ".mdata":
        if not silent:
            print(f"\x1b[1;33m[2/2] [!] '{file_name}' is not a .mdata file...\x1b[0m")
        return

    if not silent:
        print(f"\n\x1b[1;32m--- processing {file_name} ---\x1b[0m\n")
    data = {}
    errors = []
    warnings = []
    identified = False

    lines = file_path.read_text(encoding="utf-8").splitlines()

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # discard empty lines
        if not line:
            continue

        # syntax check // square brackets
        if not (line.startswith("[") and line.endswith("]")) or ":" not in line:
            errors.append(f"[{file_name}:{line_num}] invalid syntax -> '{line}'")
            continue

        content = line[1:-1].strip()
        key, value = content.split(":", 1)
        key, value = key.strip().lower(), value.strip()

        # syntax check // key/value args
        if not key or not value:
            errors.append(f"[{file_name}:{line_num}] empty key/value in '{line}'")
            continue

        # metadata checks
        if key == "explicit":
            if value.lower() not in ("true", "false"):
                errors.append(f"[{file_name}:{line_num}] 'explicit' must be 'true' or 'false'.")
            else:
                data[key] = value.lower() == "true"

        elif key in ("search-links", "playback-links"):
            links = [url.strip() for url in value.split("|")]
            data[key] = links

        elif key in ("artist", "romanized-artist"):
            data[key] = [a.strip() for a in value.split(",")]

        elif key in ("title", "romanized-title", "album"):
            data[key] = value

        elif key == "lyrics":
            data[key] = value
            lrc_file = file_path.parent / value
            if not lrc_file.exists():
                warnings.append(f"[{file_name}] lyrics file '{value}' missing.")

        else:
            errors.append(f"[{file_name}:{line_num}] unidentified metadata found -> '{line}'")

    if track_identity and not identified:
        title = data.get("romanized-title") or data.get("title")
        artist = data.get("romanized-artist") or data.get("artist")
        if title and artist:
            track_identity(title, artist)
            identified = True
    
    missing = REQUIRED - set(data.keys())
    if missing:
        errors.append(f"[{file_name}] missing required parameter(s): {', '.join(missing)}")

    if errors:
        if not silent:
            print(f"\x1b[1;31m[-] status: FAILED\x1b[0m")
            for error in errors:
                print(f"\x1b[1;31m• [E] {error}\x1b[0m")
        return None
    if not silent:    
        print(f"\x1b[1;32m[+] status: PASSED\x1b[0m")
        for warn in warnings:
            print(f"\x1b[1;33m• [!] {warn}\x1b[0m")

        print("\n\x1b[1;36m[+] parsed metadata:\x1b[0m")
        print(data)
        
    return data

def _track_identify(file_name: str) -> Any | dict[str, str]:
    directory = Path(__file__).parent.resolve()
    file_path = Path(directory / file_name).resolve()
    file_ext = Path(file_name).suffix
    
    if not file_path.exists():
        return
    
    if file_ext != ".mdata":
        return
    
    track = {}
    
    lines = file_path.read_text(encoding="utf-8").splitlines()
    
    for line in lines:
        line = line.strip()
    
        # discard empty lines
        if not line:
            continue
    
        # syntax check // square brackets
        if not (line.startswith("[") and line.endswith("]")) or ":" not in line:
            continue
    
        content = line[1:-1].strip()
        key, value = content.split(":", 1)
        key, value = key.strip().lower(), value.strip()
    
        if key in ("artist", "romanized-artist"):
            track['artist'] = [a.strip() for a in value.split(",")]

        elif key in ("title", "romanized-title"):
            track['title'] = value

        elif key == "explicit":
            if value.lower() not in ("true", "false"):
                continue
            else:
                track['explicit'] = value.lower()
    
        else:
            continue

    return track

def multi_file_input():
    files = []
    print("\nenter file names (or hit Enter to finish)")
    while True:
        file = input("\x1b[1;38;2;12;59;5m[?] .mdata file to parse -> ")
        sys.stdout.write("\x1b[0m")
        sys.stdout.flush()

        if file == "":
            break

        files.append(file)

    for mdata_file in files:
        validate_mdata(mdata_file)

def single_file_input():
    file = input("\x1b[1;38;2;12;59;5m[?] .mdata file to parse -> ")
    sys.stdout.write("\x1b[0m")
    sys.stdout.flush()
    
    validate_mdata(file)


# for systems that have to programmically pass files without user input
def singlefile(file: str, silent: bool = False) -> dict | None:
    return validate_mdata(file, silent=silent)

def multifile(*files: str, silent: bool = False) -> list[dict | None]:
    return [validate_mdata(file, silent=silent) for file in files]

def singletrack_identity(file: str) -> None:
    identity = _track_identify(file)
    if not identity:
        return
    
    print(f"\x1b[1m[{file}] track info:\x1b[0m")
    print(f"- title: \x1b[1m{identity['title']}\x1b[0m")
    print(f"- artist(s): \x1b[1m{', '.join(identity['artist'])}\x1b[0m")
    print(f"- explicit: \x1b[1m{identity['explicit']}\x1b[0m")

def multitrack_identify(*files: str):
    for file in files:
        singletrack_identity(file)

def singlefile_autoname(file: str):
    directory = Path(__file__).parent.resolve()
    file_path = Path(directory / file).resolve()
    file_ext = Path(file).suffix
    identity = _track_identify(file)
    if not identity or 'title' not in identity or 'artist' not in identity:
        return

    title = identity['title']
    artists = ', '.join(identity['artist']) if isinstance(identity['artist'], list) else identity['artist']

    _temp = re.sub(r"[^\w\s]", "", title)
    filetitle = re.sub(r"\s+", "_", _temp.strip())

    _temp = re.sub(r"[^\w\s]", "", artists)
    fileartists = re.sub(r"\s+", "_", _temp.strip())

    fullfile = f"{filetitle.lower()}-{fileartists.lower()}.mdata"

    new_file = file_path.parent / fullfile
    file_path.replace(new_file)

def multifile_autoname(*files: str):
    for file in files:
        singlefile_autoname(file)

def directory_mdata(dir_path: str = ".", recursive: bool = False, silent: bool = False) -> list[dict | None]:
    target_dir = Path(__file__).parent.resolve() / dir_path
    
    if not target_dir.is_dir():
        if not silent:
            print(f"\x1b[1;31m[-] directory '{dir_path}' not found.\x1b[0m")
        return []

    # search recursively or just top-level
    pattern = "**/*.mdata" if recursive else "*.mdata"
    mdata_files = [f.name for f in target_dir.glob(pattern)]

    if not mdata_files and not silent:
        print(f"\x1b[1;33m[!] no .mdata files found in '{dir_path}'.\x1b[0m")
        return []

    return [validate_mdata(file, silent=silent) for file in mdata_files]


def directory_autoname(dir_path: str = ".", recursive: bool = False):
    target_dir = Path(__file__).parent.resolve() / dir_path

    if not target_dir.is_dir():
        print(f"\x1b[1;31m[-] directory '{dir_path}' not found.\x1b[0m")
        return

    pattern = "**/*.mdata" if recursive else "*.mdata"
    for file_path in target_dir.glob(pattern):
        # pass relative path from directory root
        singlefile_autoname(file_path.name)

def main():
    while True:
        print("\x1b[1mselect mode:\x1b[0m")
        print("1. single file")
        print("2. multiple files")
        print("3. entire folder")
        
        mode = input("\x1b[1;38;2;12;59;5m[?] option (1/2/3) -> \x1b[0m").strip()
        
        if mode == "1":
            single_file_input()
            break
        elif mode == "2":
            multi_file_input()
            break
        elif mode == "3":
            folder = input("\x1b[1;38;2;12;59;5m[?] folder path (leave empty for current dir) -> \x1b[0m").strip() or "."
            rec = input("\x1b[1;38;2;12;59;5m[?] include subfolders? (y/n) -> \x1b[0m").lower().startswith("y")
            directory_mdata(folder, recursive=rec)
            break
        else:
            print("\x1b[1;33m[!] invalid option.\x1b[0m\n")
    
if __name__ == "__main__":
    main()