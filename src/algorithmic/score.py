"""Score construction for the Algorithmic scaffold."""

import abjad

TITLE = "Algorithmic"
COMPOSER = "George K. Thiruvathukal"
SUBTITLE = "Algorithmic composition scaffold"


def build_lilypond_file():
    """Build a placeholder LilyPond file for future development."""
    staff = abjad.Staff(name="Placeholder Staff")
    staff.append(abjad.Rest("r1"))

    first_leaf = abjad.select.leaf(staff, 0)
    abjad.attach(abjad.Clef("treble"), first_leaf)
    abjad.attach(abjad.TimeSignature((4, 4)), first_leaf)
    abjad.attach(
        abjad.Markup(
            r'\markup \italic "Stub only: compositional material to be added."'
        ),
        first_leaf,
        direction=abjad.UP,
    )

    score = abjad.Score([staff], name="Score")

    header_block = abjad.Block(name="header")
    header_block.items.append(rf'title = "{TITLE}"')
    header_block.items.append(rf'subtitle = "{SUBTITLE}"')
    header_block.items.append(rf'composer = "{COMPOSER}"')
    header_block.items.append(r"tagline = ##f")

    layout_block = abjad.Block(name="layout")
    midi_block = abjad.Block(name="midi")

    score_block = abjad.Block(name="score")
    score_block.items.append(score)
    score_block.items.append(layout_block)
    score_block.items.append(midi_block)

    return abjad.LilyPondFile(items=[header_block, score_block])
