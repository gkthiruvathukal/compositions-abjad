# Modus Operandi for Piano

**Composer:** George K. Thiruvathukal

A monody for solo piano in three movements, each built on a different mode rooted on F. The piece explores the melodic character of the Dorian, Phrygian, and Lydian modes through contrasting tempi and textures while maintaining a single-voice (monophonic) melodic line in the right hand over simple intervallic accompaniment in the left hand.

| Movement | Mode | Meter | Tempo |
|----------|------|-------|-------|
| I | F Dorian | 4/4 | Lento (quarter = 46) |
| II | F Phrygian | 6/8 | Presto agitato (dotted quarter = 80) |
| III | F Lydian | 4/4 | Andante tranquillo (quarter = 76) |

Each movement is 16 bars long. The right hand carries the melodic line in quarter notes (I), eighth notes with ottava (II), and quarter notes with ottava (III). The left hand provides a slower-moving accompaniment in half notes (I, III) or dotted quarters (II), outlining intervals of fourths and fifths rooted on F.

## Building

The score is generated programmatically using [Abjad](https://abjad.github.io/), a Python library for formalized score control, and compiled to PDF and MIDI with [LilyPond](https://lilypond.org/).

### Requirements

- Python >= 3.10
- LilyPond >= 2.24

### Install and build

```bash
pip install -e .
make abjad
```

This produces three files in `build/`:

| File | Description |
|------|-------------|
| `modus-operandi-abjad.ly` | Generated LilyPond source |
| `modus-operandi-abjad.pdf` | Engraved score |
| `modus-operandi-abjad.midi` | Combined MIDI (all three movements) |

You can also build individual outputs:

```bash
make abjad-ly    # .ly only
make abjad-pdf   # .ly + PDF
make abjad-midi  # .ly + MIDI
```

### Building from the LilyPond source directly

If you have LilyPond installed but not Python/Abjad, you can compile the hand-written source or a released `.ly` file directly:

```bash
lilypond -o build src/modus-operandi.ly
```

Or download `modus-operandi-abjad.ly` from the [latest release](../../releases/latest) and run:

```bash
lilypond modus-operandi-abjad.ly
```

## CI/CD

Every push to `main` and every pull request builds the score via GitHub Actions. When a version tag (`v*`) is pushed, a GitHub Release is created automatically with the PDF, MIDI, and LilyPond source attached.

```bash
git tag v0.2
git push --tags
```
