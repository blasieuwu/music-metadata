# .mdata specification (v1.0)

`.mdata` is an open, human-readable metadata format designed for audio track search ups, local file management, and programmical querying across media.

## syntax rules
1. files **must** be UTF-8 encoded plaintext.
2. metadata fields follow the key-value syntax: `[key: value]`.
3. keys are case-insensitive and normalized to lowercase (`title`, `artist`, `album`).
4. multiple artists **must** be comma-seperated (`artist1, artist2`).
5. multiple URLs/links **must** be pipe-seperated (`url1 | url2`).
6. empty lines and trailing and leading whitespaces are ignored.

## field schema
| key | type | required | description |
| :--- | --- | --- | --- |
| `title` | string | yes | official track title |
| `romanized-title` | string | no | romanized track title (auto-naming fallback) |
| `artist` | list[string] | yes | main and featured artists |
| `romanized-artist` | list[string] | no | romanized artist name(s) |
| `album` | string | yes | album (deluxe or non-deluxe), EP, or single project name |
| `lyrics` | string | no | filename of associated synced lyrics file (e.g., `.lrc`) |
| `search-links` | list[url] | no | external references/platform links (Spotify, YouTube Music, Soundcloud, Apple Music, etc.)
| `playback-links` | list[url] | no | direct playable audio stream/source URLs |
| `explicit` | boolean | yes | whether the track contains explicit words (`true` or `false`)

## naming & file convention
to maintain cross-platform filesystem friendliness, filenames **must** follow:
`song_name-artist_name.mdata`

1. lowercase all characters.
2. replace whitespace and dashes with underscores (`_`).
3. strip special non-alphanumeric characters (excluding underscores).
4. join multiple artists with underscores (`_`).
5. if present, prefer `romanized-title` and `romanized-arist` for file naming.
