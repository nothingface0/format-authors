# format-authors
Python script that tries to parse a .tex file for authors and affiliations and reformats it, discarding duplicates

## Requirements
Python >= 3.6

## Usage
`python3 format_authors <file in> <file out>`

`file in` is the file to extract the authors and affiliations from,
`file out` is the new file to write to

For debug messages, pass a `--debug` argument.

## Behavior
- If no affiliation is found for an author, an error message is issued.

## Known limitations
- Multiline `\author{}` and `\affiliation{}` control sequences are discarded.
- Lines containing multiple `\author{}` and/or `\affiliation{}` control sequences will not behave as expected.
