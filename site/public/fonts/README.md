# Bundled fonts for the finding cards' renders (session 170)

The render frame (`site/app/analysis/card/render.css`) sets the card's title and subtitle in Source Serif 4 and the rest in Inter, both under the SIL Open Font License 1.1, from the files named here. The renderer (`site/scripts/render-cards.mjs`) refuses to make a render when any of these files is missing or when the browser laid the card out in a fallback face.

| File | Font | License |
|---|---|---|
| `SourceSerif4-Variable.ttf` | Source Serif 4, variable, upright (Adobe, github.com/adobe-fonts/source-serif) | `OFL-SourceSerif4.txt` |
| `SourceSerif4-Italic-Variable.ttf` | Source Serif 4, variable, italic | `OFL-SourceSerif4.txt` |
| `Inter-Variable.ttf` | Inter, variable (Rasmus Andersson, github.com/rsms/inter) | `OFL-Inter.txt` |

Session 170 ran with no pull allowed beyond one public source for a statistic, so the font files are not in this commit: the three files and the two license texts, exactly as the fonts' own releases ship them, are placed here by a person (the session report's "To finish" gives the releases). Until they are, `render-cards.mjs` exits 1 and names what is missing, and no render goes out in a fallback font.
