# changelog
below is the changelogs for the python parser

> all past versions are in a [versions/](/parsers/python/versions) folder.

## [2.0.0] - 10/25/26
the great code rewrite
> (yes i know the version jumps are drastic its cuz i literally decided to randomly rewrite it)

### added
- dedicated classes (`MusicMetadata`, `MusicMetadataBuilder`) to represent a .mdata file
  - automatically runs the parse checker on construction
- the file supports docstrings! from the dedicated classes to the actual script itself.

### changed
- syntax errors and missing parameters **WILL** now throw an error (`FileSyntaxError`, `MissingParameters`)
- replaced `.split()` chaining with a regex expression instead.
- direct access to metadata (via `SimpleNamespace` for dot notation)
- the class will now try to parse the file EVEN if the file extension isn't an `.mdata` file.

### removed
- **the original cli system and most stuff are removed entirely. scripts depending on the old functions will have to leverage with the new version until then.**

### planned
- possibly add methods for automatic renaming (v1.0 revamp)
- rework the python api

---

## [0.1.0] - 9/20/26
initial release
