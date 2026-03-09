# Jazz Rhythmic Patterns

This module provides a collection of reusable jazz comping rhythms generated programmatically using [Abjad](https://abjad.github.io/).

## Available Patterns

The rhythms are defined in `src/jazz_rhythm/rhythms.py`. Each function returns a one-measure rhythmic cell.

| Pattern | Description |
|---------|-------------|
| `charleston` | Classic Charleston rhythm: Dotted quarter (1) + Eighth (2&) |
| `charleston_extended` | Charleston rhythm plus a "push" on the "and" of 4 |
| `anticipation` | Rest on 1-3, Eighth note on "and" of 4 (anticipating the next bar) |
| `two_beat` | Straight quarter notes on beats 2 and 4 |
| `syncopated` | Off-beat accents on the "and" of 1 and "and" of 2 |

## Rendering the Score

You can generate a PDF score showing these patterns by running the included script:

```bash
python3 render_rhythms.py
```

This will produce `build/jazz-rhythms.pdf`.

## Usage in Code

You can import these rhythms to build larger structures:

```python
from src.jazz_rhythm import rhythms
import abjad

# Create a staff with 4 measures of Charleston rhythm
staff = abjad.Staff()
for _ in range(4):
    staff.extend(rhythms.charleston())

abjad.show(staff)
```
