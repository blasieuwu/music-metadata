"""
# Music Metadata
the python script for Music Metadata
currently this script is version 2.0

## contents
classes:
- `MusicMetadata`
  - accepts a `Path` or a `str` object
- `MusicMetadataBuilder`
  - builder (uses method chaining)
"""

# Music Metadata (v2.0) • copyright blasieuwu, 2026
# a better way of getting track metadata.
from typing import Self, TextIO
from pathlib import Path
from types import SimpleNamespace
import warnings
import re


def warnings_formatter(
    message: Warning | str,
    category: type[Warning],
    filename: str,
    lineno: int,
    line: str | None = None,
) -> str:
    return f"\x1b[1;33m[warn] {message}\x1b[0m"


warnings.formatwarning = warnings_formatter  # type: ignore | reason: i hate fucking type signatures


class FileSyntaxError(Exception):  # used by MusicMetadata
    """invalid file format syntax"""

    def __init__(self, message: str, /) -> None:
        super().__init__(message)


class MissingParameters(Exception):  # used by MusicMetadataBuildwe
    """missing required parameters"""

    def __init__(self, message: str, /) -> None:
        super().__init__(message)


class AmbiguousData(Exception):  # used by MusicMetadata
    """unexpected extra data / trailing data"""

    def __init__(self, message: str, /) -> None:
        super().__init__(message)


class MusicMetadata:  # brand new v2.0 feature
    """
    ## new in version 2.0
    represents a music .mdata file with direct metadata lookups

    ### parameters
    - `file`: a Path (pathlib) to the exact .mdata file, or string, representing the name of said file
      - turned into a Path object if a string is passed
            - resolved by default

    ### info
    you can access the track metadata directly via dot notation

    ```python
    # example:
    mdata_file = MusicMetadata("song.mdata").track.title

    # querying links
    mdata_file = MusicMetadata("song.mdata").links.playback
    ```
    """

    def __init__(self, file: Path | str, /, *, suppress: bool = True) -> None:
        self.requiredtags = {
            # format: [tag]: [boolean; true if missing]
            # everything is missing by default cuz, well, we haven't processed
            # the file yet :P
            "title": True,
            "artist": True,
            "album": True,
            "explicit": True,
        }
        working_dir: Path = Path(__file__).resolve().parent
        self.file: Path = Path(working_dir / file).resolve()

        if not self.file.exists():
            raise FileNotFoundError(
                f"{self.file.name} doesn't exist in your current directory."
            )

        if self.file.suffix != ".mdata" and not suppress:
            warnings.warn("file isn't a .mdata file format...")

        self.track = SimpleNamespace(
            title=None,
            artists=None,
            album=None,
            explicit=None,
            romanized=SimpleNamespace(title=None, artists=None),
            lyrics_file=None,
        )
        self.links = SimpleNamespace(search=None, playback=None)

        lines = self.file.read_text(encoding="utf-8").splitlines()

        for line_num, line in enumerate(lines, 1):
            # skip empty lines
            if not line:
                continue

            # syntax check // brackets | tested by blasieuwu
            if not (line.startswith("[") and line.endswith("]")) or ":" not in line:
                raise FileSyntaxError(f"invalid syntax at line {line_num}\n└ {line}")

            # key/value separation process (uses re instead of .split())
            match = re.search(r"\[([\w\-]+):\s*(.*)\]", line)
            if match:
                tag, value = match.groups()
                tag = tag.strip().lower()
                value = value.strip()

            # syntax check // empty key/value pairs | tested by blasieuwu
            if not tag or not value:
                raise FileSyntaxError(
                    f"empty key/value pair in line {line_num}\n└ {line}"
                )

            # metadata parsing
            if tag == "explicit":
                if value.lower() not in ("true", "false"):
                    raise FileSyntaxError(
                        f"explicit must be 'true' or 'false' (line {line_num})\n└ {line}"
                    )
                self.track.explicit = value.lower() == "true"
                self.requiredtags["explicit"] = False

            elif tag in ("search-links", "playback-links"):
                links = [url.strip() for url in value.split(" | ")]

                if tag == "search-links":
                    self.links.search = links
                else:
                    self.links.playback = links

            elif tag in ("artist", "romanized-artist"):
                artists = [artist for artist in value.split(", ")]

                if tag == "artist":
                    self.track.artists = artists
                    self.requiredtags["artist"] = False
                else:
                    self.track.romanized.artists = artists

            elif tag in ("title", "romanized-title", "album"):
                if tag == "title":
                    self.track.title = value
                    self.requiredtags["title"] = False
                elif tag == "album":
                    self.track.album = value
                    self.requiredtags["album"] = False
                else:
                    self.track.romanized.title = value

            elif tag == "lyrics":
                self.track.lyrics_file = working_dir / value

                if not self.track.lyrics_file.exists() and not suppress:
                    warnings.warn(
                        f"no .lrc file named '{value}' found in current directory."
                    )

            else:
                raise AmbiguousData(
                    f"unexpected trailing data found at line {line_num}\n└ {line}"
                )

        # tested by blasie
        missingtags = []
        if True in self.requiredtags.values():  # check if any tag is missing
            for tag, missing in self.requiredtags.items():
                if missing:
                    missingtags.append(tag)
            raise MissingParameters(
                f"the following tags are missing:\n└ {', '.join(missingtags)}"
            )

        self.info = f"metadata info ({self.file.__str__()}):\n├ title: {self.track.title}\n├ artist: {', '.join(self.track.artists)}\n├ album: {self.track.album}\n└ explicit: {self.track.explicit.__str__().lower()}"


class MusicMetadataBuilder:
    """
    ## new in version 2.0
    create a music metadata class

    ## parameters
    takes no parameters, instead uses methods to build it

    demonstration:
    ```python
    from mdata import MusicMetadataBuilder

    track = (
            MusicMetadataBuilder()
            .title("my-song")
            .artist("myself")
            .album("my-song")
            .explicit(False)
    )
    ```
    """

    def __init__(self) -> None:
        self._data: dict[str, bool | None | str | list[str] | Path] = {
            # the following 4 items are required
            "title": None,
            "artists": None,
            "album": None,
            "explicit": True,
            # the rest aren't required
            "romanized_title": None,
            "romanized_artists": None,
            "search_links": [],
            "playback_links": [],
            "lyrics_file": None,
        }

    def title(self, title: str) -> Self:
        self._data["title"] = title
        return self

    def artists(self, artists: list[str] | str) -> Self:
        self._data["artists"] = artists
        return self

    def album(self, album: str) -> Self:
        self._data["album"] = album
        return self

    def explicit(self, explicit: bool) -> Self:
        self._data["explicit"] = explicit
        return self

    def romanized_title(self, title: str) -> Self:
        self._data["romanized_title"] = title
        return self

    def romanized_artists(self, artists: list[str] | str) -> Self:
        self._data["romanized_artists"] = artists
        return self

    def links_search(self, links: list[str] | str) -> Self:
        self._data["search_links"] = links
        return self

    def links_playback(self, links: list[str] | str) -> Self:
        self._data["playback_links"] = links
        return self

    def lyric_file(self, file: str | Path) -> Self:
        self._data["lyrics_file"] = Path(file).resolve()

        if not self._data["lyrics_file"].exists():
            warnings.warn(
                f"\x1b[1;33m[warn] MusicMetadataBuilder: lyric file '{self._data['lyrics_file'].__str__()}' not found.\x1b[0m"
            )
        return self

    def create(self) -> SimpleNamespace:
        missing = set()

        if self._data["title"] == None:
            missing.add("title")

        if self._data["artists"] == None:
            missing.add("artists")

        if self._data["album"] == None:
            missing.add("album")

        if self._data["explicit"] == None:
            missing.add("explicit")

        if missing:
            raise MissingParameters(
                f"MusicMetadataBuilder lacks the following required parameters:\n|-----> {', '.join(missing)}"
            )

        return SimpleNamespace(**self._data)
