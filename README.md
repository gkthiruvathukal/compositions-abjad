# Music Composition with Abjad

This repository contains programmatic music composition experiments and finished works using [Abjad](https://abjad.github.io/) and [LilyPond](https://lilypond.org/).

## Projects

### 1. [Modus Operandi for Piano](README-ModusOperandi.md)

A monody for solo piano in three movements (F Dorian, F Phrygian, F Lydian). This is a complete composition with a CI/CD pipeline for generating PDF scores and MIDI/WAV audio.

- **Source:** `src/modus_operandi_abjad/`
- **Build:** `make abjad`

### 2. [Jazz Rhythmic Patterns](README-JazzRhythms.md)

A collection of generated jazz comping rhythms (Charleston, anticipation, syncopated figures) rendered as rhythmic notation.

- **Source:** `src/jazz_rhythm/`
- **Render:** `python3 render_rhythms.py`

## Setup

Both projects require Python 3.10+ and LilyPond 2.24+.

1.  **Install dependencies:**

    ```bash
    pip install -e .
    ```

2.  **Install LilyPond:**
    -   macOS: `brew install lilypond`
    -   Ubuntu: `sudo apt install lilypond`

3.  **Install FluidSynth (optional, for audio rendering):**
    -   macOS: `brew install fluidsynth`
    -   Ubuntu: `sudo apt install fluidsynth`
