# Algorithmic

This project is a placeholder for a future algorithmic composition scaffold.

The current scaffold exists so the project has a package, CLI, score builder, and CI/release hooks before any musical material is added.

## Current State

- package stub only
- placeholder score output
- no compositional material yet

## Rendering the Placeholder Score

Install the project in editable mode:

```bash
pip install -e .
```

Then generate output with the package CLI:

```bash
python -m algorithmic -o build
# or
algorithmic -o build
```

By default this produces:

- `build/algorithmic.ly`
- `build/algorithmic.pdf`
- `build/algorithmic.midi`

You can also request specific outputs:

```bash
python -m algorithmic -o build --ly
python -m algorithmic -o build --pdf
python -m algorithmic -o build --midi
```

## Next Steps

Likely future additions include:

- pitch-class and row utilities
- transformation helpers (prime, inversion, retrograde, retrograde inversion)
- registral / rhythmic mapping strategies
- score-building logic for one or more movements
