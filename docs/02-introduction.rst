Introduction
============

Most music software assumes that composition begins in a notation editor or a digital audio workstation. This project starts from a different assumption. It treats code as a first-class compositional medium. That choice changes both the workflow and the kinds of musical questions that can be asked. When a score is built in code, the same source can define pitch material, rhythm, instrumentation, notation details, rendering choices, and release artifacts. It also becomes much easier to reproduce a result, rerun it with controlled changes, or compare two closely related systems.

This repository was built around that idea. It uses Python, Abjad, and LilyPond to move from compositional logic to engraved score. It also uses shell scripts and GitHub Actions so that the same scores can be built locally and in continuous integration. The result is a repository that functions as both a set of compositions and a software system.

The artistic motivation is clearest in the quartet work. ``Algo Rhythms Quartet No. 1`` is a tonal proof of concept for a larger planned system. ``Algorithmic Piano Quartet No. 2`` begins from the same base but is allowed to change more aggressively so that new musical ideas can be tested without rewriting the original piece. This makes the repository useful in two ways at once. It preserves completed work, and it gives a controlled place for technical and musical experiments.

The goal of this report is to describe that combined system in a form closer to a technical paper than to a project README. The report focuses on architecture, generation methods, rendering, and release workflow. It also discusses each current score in enough detail to show how the musical ideas and the code design fit together.
