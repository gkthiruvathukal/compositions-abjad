# Algorithmic Piano Quartet No. 2

**Composer:** George K. Thiruvathukal

This package starts from the current `algorithmic_piano_quartet` implementation, but it is intended to develop independently. The goal is to preserve **Algo Rhythms Quartet No. 1** as it is while giving No. 2 a separate place for new musical ideas, parameter choices, and future structural changes.

## Starting Point

The initial config for No. 2 is based on the same quartet setup used for No. 1:

- piano
- violin
- viola
- cello

It uses its own config file:

- `configs/algorithmic-piano-quartet-no2.toml`

and its own module entry point:

- `python -m algorithmic_piano_quartet_no2`
- `algorithmic-piano-quartet-no2`

## Purpose

This package exists so that new ideas can be explored without changing the existing No. 1 composition. In practice, that means No. 2 can diverge in any of these areas:

- pitch materials
- rhythmic behavior
- texture and density
- form
- dynamics
- instrumentation rules
- rendering and notation choices

## How No. 2 Differs From No. 1

No. 2 begins from the same general quartet setup as **Algo Rhythms Quartet No. 1**, but it is already moving in a different direction.

Musically, No. 2 currently differs in these ways:

- the piano is allowed to generate chords instead of only single-note lines
- piano chords are shaped to prefer wider spacing, especially thirds, fourths, and larger intervals
- left-hand and right-hand chord sizes are controlled separately
- left-hand chords can open out more widely than right-hand chords
- crushed intervals smaller than a minor third are avoided in the piano voicings
- the practical top of the piano range has been lowered for No. 2

Technically, No. 2 also differs from No. 1 in these ways:

- it has its own module: `algorithmic_piano_quartet_no2`
- it has its own config: `configs/algorithmic-piano-quartet-no2.toml`
- it has its own output basename and artifact names
- it is part of the local `build.sh` workflow
- it is still excluded from GitHub Actions while the musical design is in flux

What is still shared with No. 1:

- the same basic instrumentation: piano, violin, viola, cello
- the same general generation architecture
- the same current soundfont/render pipeline

That means No. 2 is not a completely new system yet. It is a controlled fork of No. 1 for exploring new musical behavior without rewriting the original piece.

## Typical Commands

Build notation, MIDI, and LilyPond source:

```bash
python -m algorithmic_piano_quartet_no2 -c configs/algorithmic-piano-quartet-no2.toml -o build
```

Build PDF and WAV as well:

```bash
python -m algorithmic_piano_quartet_no2 -c configs/algorithmic-piano-quartet-no2.toml -o build --pdf --wav
```

## Current Build Scope

No. 2 is part of the local `build.sh` workflow, so a normal local build will generate its outputs alongside the other compositions.

It is not part of the GitHub Actions workflow yet. That is still intentional while No. 2 remains in an exploratory stage.
