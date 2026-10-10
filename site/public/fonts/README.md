# Bundled fonts for the finding cards' renders (session 170)

The render frame (`site/app/analysis/card/render.css`) sets the card's title and subtitle in Source Serif 4 and the rest in Inter, both under the SIL Open Font License 1.1, from the files named here. The renderer (`site/scripts/render-cards.mjs`) refuses to make a render when any of these files is missing or when the browser laid the card out in a fallback face.

| File | Font | License |
|---|---|---|
| `SourceSerif4-Variable.ttf` | Source Serif 4, variable, upright (Adobe, github.com/adobe-fonts/source-serif) | `OFL-SourceSerif4.txt` |
| `SourceSerif4-Italic-Variable.ttf` | Source Serif 4, variable, italic | `OFL-SourceSerif4.txt` |
| `Inter-Variable.ttf` | Inter, variable (Rasmus Andersson, github.com/rsms/inter) | `OFL-Inter.txt` |

Session 170 ran with no pull allowed beyond one public source for a statistic, so the font files are not in this commit: the three files and the two license texts, exactly as the fonts' own releases ship them, are placed here by a person (the session report's "To finish" gives the releases). Until they are, `render-cards.mjs` exits 1 and names what is missing, and no render goes out in a fallback font.

## The files, as placed by session 172's chain (session 173, 10 October 2026)

The owner approved the pull (the chain prompt of 9 October 2026: "Source Serif 4 and Inter from their official GitHub releases or Google Fonts, open license, at most 10 requests and 15 MB; record the license files"). The files are Google Fonts' copies in the `google/fonts` repository (`ofl/sourceserif4/`, `ofl/inter/`), read through GitHub's API (which GitHub's robots file points programs to) and the raw file host, with the contact string "ERW research project, github.com/SamuelEnrique/erw" as the User-Agent. Nine requests, 3,949,893 bytes in all: two robots files (github.com, 200; raw.githubusercontent.com, 404, no robots file), two folder listings, five files. The listing's git blob ids and each file's sha256 are in `runs/session173/pull/` (not in git); the sha256 of what is here:

| File here | Source file | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|---|
| `SourceSerif4-Variable.ttf` | `ofl/sourceserif4/SourceSerif4[opsz,wght].ttf` | 1,209,508 | `97b2d4da6e3cb494b5a1e66ae176914d852ccabef49e0c02c0df25f3e39aca0b` | 2026-10-10 02:15:14 |
| `SourceSerif4-Italic-Variable.ttf` | `ofl/sourceserif4/SourceSerif4-Italic[opsz,wght].ttf` | 855,432 | `15fbc7e4679489a501998c3669272637a6646388ef7e4bd77eebb5bf967a1f42` | 02:15:16 |
| `Inter-Variable.ttf` | `ofl/inter/Inter[opsz,wght].ttf` | 876,576 | `29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031` | 02:15:18 |
| `OFL-SourceSerif4.txt` | `ofl/sourceserif4/OFL.txt` ("Copyright 2014 The Source Serif 4 Project Authors") | 4,400 | `5f94c3fd3a23131a417ab5a0c8452de57e70c3cfb9f604d88241f7065ebf9fd9` | 02:15:20 |
| `OFL-Inter.txt` | `ofl/inter/OFL.txt` ("Copyright 2020 The Inter Project Authors") | 4,377 | `5b9321a4298cfeb6b34354164a1c3afc3db114569984c502b9b35d988fd58c57` | 02:15:22 |

Both licenses are the SIL Open Font License 1.1, as the two texts say. The files are byte for byte the repository's; nothing was converted or subset. Google Fonts' copies carry an optical size axis (`opsz`) beside weight; the render frame asks for weights only, which both faces answer.
