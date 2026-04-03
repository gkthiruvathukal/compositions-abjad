"""Generate a modular ensemble piece from curated bird-song phrases."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable

from bird_im_migration.analysis import (
    CURATED_BIRD_REGIONS,
    DEFAULT_PARTIALS_PATH,
    parse_spear_partials,
    quantize_region_pitches,
)


PITCH_CLASS_NAME_TO_INT = {
    "c": 0,
    "cs": 1,
    "d": 2,
    "ds": 3,
    "e": 4,
    "f": 5,
    "fs": 6,
    "g": 7,
    "gs": 8,
    "a": 9,
    "as": 10,
    "b": 11,
}


@dataclass(frozen=True)
class BirdSource:
    sample_id: str
    partials_path: str
    curated_regions: tuple[tuple[str, object], ...]


@dataclass(frozen=True)
class Phrase:
    phrase_id: str
    sample_id: str
    region_name: str
    note_bins: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class PhraseVariant:
    phrase: Phrase
    transform_name: str
    note_bins: tuple[tuple[str, ...], ...]
    span_measures: int


@dataclass(frozen=True)
class MovementConfig:
    number: int
    title: str
    subtitle: str
    time_signature: tuple[int, int]
    tempo_bpm: int
    key_literal: str
    center_midi: int
    total_measures: int
    phrase_pairs: int
    intro_measures: int
    closing_measures: int
    phrase_measures: int
    call_transforms: tuple[str, ...]
    response_transforms: tuple[str, ...]
    call_response_probability: float
    percussion_density: float
    percussion_pattern: str
    piano_pattern: str
    seed_offset: int


@dataclass(frozen=True)
class InstrumentPart:
    staff_id: str
    name: str
    short_name: str
    clef: str
    midi_instrument: str
    events: tuple["EnsembleEvent", ...]


@dataclass(frozen=True)
class EnsembleEvent:
    start_unit: int
    duration_units: int
    pitches: tuple[int, ...] | None


@dataclass(frozen=True)
class MovementMaterial:
    config: MovementConfig
    measure_units: int
    measures: int
    parts: tuple[InstrumentPart, ...]


@dataclass(frozen=True)
class EnsemblePiece:
    title: str
    composer: str
    subtitle: str
    movements: tuple[MovementMaterial, ...]
    generation_note_lines: tuple[str, ...]


DEFAULT_SOURCE = BirdSource(
    sample_id="parkbirds",
    partials_path=str(DEFAULT_PARTIALS_PATH),
    curated_regions=CURATED_BIRD_REGIONS,
)


DEFAULT_MOVEMENTS: tuple[MovementConfig, ...] = (
    MovementConfig(
        number=1,
        title="I. Opening Call",
        subtitle="Bird-call fragments introduced in measured exchange",
        time_signature=(4, 4),
        tempo_bpm=88,
        key_literal=r"\key d \dorian",
        center_midi=50,
        total_measures=32,
        phrase_pairs=6,
        intro_measures=2,
        closing_measures=3,
        phrase_measures=1,
        call_transforms=("identity", "repeat"),
        response_transforms=("identity", "retrograde"),
        call_response_probability=0.95,
        percussion_density=0.18,
        percussion_pattern="son-clave",
        piano_pattern="two-beat",
        seed_offset=0,
    ),
    MovementConfig(
        number=2,
        title="II. Echo / Nocturne",
        subtitle="Slower transformation and expanded time",
        time_signature=(3, 4),
        tempo_bpm=57,
        key_literal=r"\key b \minor",
        center_midi=47,
        total_measures=32,
        phrase_pairs=6,
        intro_measures=1,
        closing_measures=3,
        phrase_measures=1,
        call_transforms=("augment", "identity"),
        response_transforms=("retrograde", "augment"),
        call_response_probability=0.9,
        percussion_density=0.12,
        percussion_pattern="habanera-wave",
        piano_pattern="charleston",
        seed_offset=29,
    ),
    MovementConfig(
        number=3,
        title="III. Last Calls",
        subtitle="Layered returns and controlled closure",
        time_signature=(5, 4),
        tempo_bpm=108,
        key_literal=r"\key d \minor",
        center_midi=50,
        total_measures=32,
        phrase_pairs=7,
        intro_measures=2,
        closing_measures=3,
        phrase_measures=1,
        call_transforms=("identity", "retrograde", "repeat"),
        response_transforms=("identity", "retrograde", "augment"),
        call_response_probability=1.0,
        percussion_density=0.28,
        percussion_pattern="cascara-light",
        piano_pattern="syncopated",
        seed_offset=71,
    ),
)


PERCUSSION_PATTERNS: dict[str, tuple[int, ...]] = {
    "son-clave": (0, 3, 6, 10, 12, 19, 22, 26),
    "habanera-wave": (0, 3, 4, 6, 8, 12, 15, 16, 18, 20, 24, 27, 28, 30),
    "cascara-light": (0, 2, 5, 7, 8, 11, 12, 14, 17, 19, 20, 23, 24, 26, 29, 31),
}


PIANO_PATTERNS: dict[str, tuple[int, ...]] = {
    "two-beat": (4, 12),
    "charleston": (0, 6),
    "anticipation": (14,),
    "syncopated": (2, 6),
}


def _measure_units(time_signature: tuple[int, int]) -> int:
    numerator, denominator = time_signature
    return numerator * (16 // denominator)


def _note_name_to_midi(note_name: str) -> int:
    index = len(note_name)
    while index > 0 and (
        note_name[index - 1].isdigit() or note_name[index - 1] == "-"
    ):
        index -= 1
    pitch_class_name = note_name[:index]
    octave = int(note_name[index:])
    return (octave + 1) * 12 + PITCH_CLASS_NAME_TO_INT[pitch_class_name]


def _resample_bins(
    note_bins: tuple[tuple[str, ...], ...],
    *,
    target_units: int,
) -> tuple[tuple[str, ...], ...]:
    if not note_bins:
        return tuple(() for _ in range(target_units))
    result: list[tuple[str, ...]] = []
    source_length = len(note_bins)
    for target_index in range(target_units):
        source_index = min(source_length - 1, (target_index * source_length) // target_units)
        result.append(note_bins[source_index])
    return tuple(result)


def _retrograde_bins(note_bins: tuple[tuple[str, ...], ...]) -> tuple[tuple[str, ...], ...]:
    return tuple(reversed(note_bins))


def _repeat_bins(
    note_bins: tuple[tuple[str, ...], ...],
    *,
    target_units: int,
) -> tuple[tuple[str, ...], ...]:
    repeated = note_bins + note_bins
    return _resample_bins(repeated, target_units=target_units)


def _make_variant(
    phrase: Phrase,
    transform_name: str,
    *,
    measure_units: int,
    phrase_measures: int,
) -> PhraseVariant:
    if transform_name == "identity":
        span_measures = phrase_measures
        bins = _resample_bins(phrase.note_bins, target_units=measure_units * span_measures)
    elif transform_name == "retrograde":
        span_measures = phrase_measures
        bins = _resample_bins(
            _retrograde_bins(phrase.note_bins),
            target_units=measure_units * span_measures,
        )
    elif transform_name == "augment":
        span_measures = phrase_measures * 2
        bins = _resample_bins(phrase.note_bins, target_units=measure_units * span_measures)
    elif transform_name == "repeat":
        span_measures = phrase_measures * 2
        bins = _repeat_bins(phrase.note_bins, target_units=measure_units * span_measures)
    else:
        raise ValueError(f"Unknown transform: {transform_name}")
    return PhraseVariant(
        phrase=phrase,
        transform_name=transform_name,
        note_bins=bins,
        span_measures=span_measures,
    )


def build_phrase_library(
    *,
    sources: Iterable[BirdSource] = (DEFAULT_SOURCE,),
    bins_per_phrase: int = 16,
) -> tuple[Phrase, ...]:
    phrases: list[Phrase] = []
    for source in sources:
        partials = parse_spear_partials(source.partials_path)
        for region_name, region in source.curated_regions:
            note_bins = tuple(
                quantize_region_pitches(partials, region, bins_per_measure=bins_per_phrase)
            )
            phrase_id = f"{source.sample_id}:{region_name.lower().replace(' ', '-')}"
            phrases.append(
                Phrase(
                    phrase_id=phrase_id,
                    sample_id=source.sample_id,
                    region_name=region_name,
                    note_bins=note_bins,
                )
            )
    return tuple(phrases)


def _fit_pitch_to_range(midi_pitch: int, low: int, high: int) -> int:
    while midi_pitch < low:
        midi_pitch += 12
    while midi_pitch > high:
        midi_pitch -= 12
    return min(high, max(low, midi_pitch))


def _map_bin_to_instrument(
    note_bin: tuple[str, ...],
    *,
    center_midi: int,
    low: int,
    high: int,
    max_notes: int,
    prefer_highest: bool,
) -> tuple[int, ...]:
    if not note_bin:
        return tuple()
    midi_pitches = sorted(_note_name_to_midi(note) for note in note_bin)
    if prefer_highest:
        midi_pitches = list(reversed(midi_pitches))
    selected = midi_pitches[:max_notes]
    mapped: list[int] = []
    for midi_pitch in selected:
        shifted = midi_pitch - 72 + center_midi
        mapped.append(_fit_pitch_to_range(shifted, low, high))
    return tuple(sorted(mapped))


def _phrase_bins_to_events(
    note_bins: list[tuple[int, ...] | None],
) -> list[EnsembleEvent]:
    events: list[EnsembleEvent] = []
    if not note_bins:
        return events
    current = note_bins[0]
    duration = 1
    start = 0
    for index, note_bin in enumerate(note_bins[1:], start=1):
        if note_bin == current:
            duration += 1
            continue
        events.append(EnsembleEvent(start_unit=start, duration_units=duration, pitches=current))
        start = index
        current = note_bin
        duration = 1
    events.append(EnsembleEvent(start_unit=start, duration_units=duration, pitches=current))
    return events


def _merge_pitch_sets(
    current: tuple[int, ...] | None,
    incoming: tuple[int, ...] | None,
) -> tuple[int, ...] | None:
    if current is None:
        return incoming
    if incoming is None:
        return current
    return tuple(sorted(set(current + incoming)))


def _apply_span(
    bins: list[tuple[int, ...] | None],
    *,
    start: int,
    duration: int,
    pitches: tuple[int, ...],
) -> None:
    stop = min(len(bins), start + duration)
    for index in range(start, stop):
        bins[index] = _merge_pitch_sets(bins[index], pitches)


def _build_piano_bins(
    config: MovementConfig,
    *,
    measures: int,
    measure_units: int,
) -> tuple[list[tuple[int, ...] | None], list[tuple[int, ...] | None]]:
    root = config.center_midi - 14
    fifth = root + 7
    octave = root + 12
    shimmer_root = config.center_midi + 10
    shimmer_fifth = shimmer_root + 7
    shimmer_ninth = shimmer_root + 14
    shimmer_upper = shimmer_root + 12
    total_units = measures * measure_units
    left_bins: list[tuple[int, ...] | None] = [None] * total_units
    right_bins: list[tuple[int, ...] | None] = [None] * total_units
    eighth_units = 2
    half_measure = max(eighth_units, measure_units // 2)

    if config.piano_pattern == "two-beat":
        right_entries = (
            (max(eighth_units, measure_units // 4), (shimmer_root, shimmer_fifth), 2),
            (max(eighth_units, (measure_units * 3) // 4), (shimmer_root,), 2),
        )
    elif config.piano_pattern == "charleston":
        right_entries = (
            (0, (shimmer_root, shimmer_fifth), 3),
            (max(eighth_units, (measure_units * 3) // 8), (shimmer_root,), 1),
        )
    elif config.piano_pattern == "anticipation":
        right_entries = (
            (max(eighth_units, measure_units - 2), (shimmer_fifth, shimmer_ninth), 2),
        )
    elif config.piano_pattern == "syncopated":
        right_entries = (
            (max(eighth_units, measure_units // 8), (shimmer_root,), 2),
            (max(eighth_units, (measure_units * 3) // 8), (shimmer_fifth, shimmer_ninth), 2),
        )
    else:
        raise ValueError(f"Unknown piano pattern: {config.piano_pattern}")

    for measure_index in range(measures):
        measure_start = measure_index * measure_units
        in_closing = measure_index >= measures - config.closing_measures
        if in_closing:
            _apply_span(
                left_bins,
                start=measure_start,
                duration=measure_units,
                pitches=(root, fifth, octave),
            )
            _apply_span(
                right_bins,
                start=measure_start,
                duration=half_measure,
                pitches=(shimmer_root, shimmer_fifth),
            )
            _apply_span(
                right_bins,
                start=measure_start + half_measure,
                duration=half_measure,
                pitches=(shimmer_root,),
            )
            continue

        if config.number == 2:
            two_measure_phase = measure_index % 2
            arpeggio_cycle = (
                (0, (root,)),
                (2, (fifth,)),
                (4, (octave,)),
                (6, (fifth,)),
                (8, (root + 12,)),
                (10, (fifth,)),
            )
            shifted_cycle = (
                (0, (root, fifth)),
                (2, (octave,)),
                (4, (fifth,)),
                (6, (root,)),
                (8, (fifth, octave)),
                (10, (fifth,)),
            )
            cycle = arpeggio_cycle if two_measure_phase == 0 else shifted_cycle
            for offset, chord in cycle:
                _apply_span(
                    left_bins,
                    start=measure_start + min(offset, max(0, measure_units - eighth_units)),
                    duration=eighth_units,
                    pitches=chord,
                )
        else:
            if measure_index % 3 == 0:
                left_chord = (root, fifth)
            elif measure_index % 3 == 1:
                left_chord = (root, octave)
            else:
                left_chord = (root, fifth, octave)
            _apply_span(
                left_bins,
                start=measure_start,
                duration=measure_units,
                pitches=left_chord,
            )
            if measure_index % 2 == 1:
                _apply_span(
                    left_bins,
                    start=measure_start + half_measure,
                    duration=half_measure,
                    pitches=(root, fifth),
                )

        shifted_entries = [
            (
                min(measure_units - eighth_units, start + (eighth_units if measure_index % 2 == 1 else 0)),
                chord,
                duration_eighths,
            )
            for start, chord, duration_eighths in right_entries
        ]
        for start, chord, duration_eighths in shifted_entries:
            _apply_span(
                right_bins,
                start=measure_start + start,
                duration=max(eighth_units, duration_eighths * eighth_units),
                pitches=chord,
            )
    return left_bins, right_bins


def _build_closing_phrase_bins(
    variant: PhraseVariant,
    *,
    measures: int,
    measure_units: int,
) -> tuple[list[tuple[int, ...] | None], list[tuple[int, ...] | None]]:
    target_units = measures * measure_units
    whistle: list[tuple[int, ...] | None] = [None] * target_units
    trumpet: list[tuple[int, ...] | None] = [None] * target_units
    tail = variant.note_bins[-measure_units:]
    whistle_tail = [
        _map_bin_to_instrument(
            note_bin,
            center_midi=74,
            low=72,
            high=91,
            max_notes=1,
            prefer_highest=True,
        )
        or None
        for note_bin in tail
    ]
    trumpet_tail = [
        _map_bin_to_instrument(
            note_bin,
            center_midi=67,
            low=55,
            high=79,
            max_notes=1,
            prefer_highest=False,
        )
        or None
        for note_bin in tail
    ]
    whistle[: len(whistle_tail)] = whistle_tail
    response_start = max(0, measure_units // 2)
    trumpet[response_start : response_start + len(trumpet_tail[: target_units - response_start])] = trumpet_tail[
        : target_units - response_start
    ]
    whistle[-measure_units:] = [whistle_tail[-1] if whistle_tail and whistle_tail[-1] else (74,)] * measure_units
    trumpet[-measure_units:] = [None] * (measure_units // 2) + [(62,)] * (measure_units - (measure_units // 2))
    return whistle, trumpet


def _scaled_pattern_hits(pattern_name: str, cycle_units: int) -> tuple[int, ...]:
    pattern = PERCUSSION_PATTERNS.get(pattern_name)
    if pattern is None:
        raise ValueError(f"Unknown percussion pattern: {pattern_name}")
    base_cycle = 32
    scaled = {
        min(cycle_units - 1, round(index * cycle_units / base_cycle))
        for index in pattern
    }
    return tuple(sorted(scaled))


def _build_percussion_bins_from_pattern(
    *,
    whistle_bins: list[tuple[int, ...] | None],
    trumpet_bins: list[tuple[int, ...] | None],
    measures: int,
    measure_units: int,
    closing_measures: int,
    pattern_name: str,
    density: float,
    rng: random.Random,
) -> list[tuple[int, ...] | None]:
    bins: list[tuple[int, ...] | None] = []
    cycle_units = measure_units * 2
    pattern_hits = _scaled_pattern_hits(pattern_name, cycle_units)
    previous_active = False
    for index, (whistle_bin, trumpet_bin) in enumerate(zip(whistle_bins, trumpet_bins)):
        measure_index = index // measure_units
        unit_index = index % measure_units
        cycle_index = index % cycle_units
        active = whistle_bin is not None or trumpet_bin is not None
        in_closing = measure_index >= measures - closing_measures
        pattern_hit = cycle_index in pattern_hits and unit_index % 2 == 0
        answer_hit = measure_index % 2 == 1 and unit_index == max(2, measure_units // 2)
        entry_accent = active and not previous_active and rng.random() <= min(1.0, density + 0.15)
        if in_closing:
            bins.append((60,) if unit_index in (0, max(1, measure_units // 2)) else None)
        elif pattern_hit and rng.random() <= min(1.0, density + 0.25):
            bins.append((60,))
        elif answer_hit and active and rng.random() <= density + 0.1:
            bins.append((60,))
        elif entry_accent:
            bins.append((60,))
        else:
            bins.append(None)
        previous_active = active
    return bins


def _build_movement_material(
    phrases: tuple[Phrase, ...],
    config: MovementConfig,
    *,
    seed: int,
) -> MovementMaterial:
    measure_units = _measure_units(config.time_signature)
    target_phrase_measures = max(config.total_measures - config.closing_measures, config.intro_measures)
    total_measures = config.intro_measures
    whistle_bins: list[tuple[int, ...] | None] = []
    trumpet_bins: list[tuple[int, ...] | None] = []

    whistle_bins.extend([None] * (config.intro_measures * measure_units))
    trumpet_bins.extend([None] * (config.intro_measures * measure_units))

    rng = random.Random(seed + config.seed_offset)
    last_variant: PhraseVariant | None = None
    while total_measures < target_phrase_measures:
        call_phrase = rng.choice(phrases)
        remaining_before_closing = target_phrase_measures - total_measures
        call_transform = rng.choice(config.call_transforms)
        call_variant = _make_variant(
            call_phrase,
            call_transform,
            measure_units=measure_units,
            phrase_measures=config.phrase_measures,
        )
        if call_variant.span_measures > remaining_before_closing:
            call_variant = _make_variant(
                call_phrase,
                "identity",
                measure_units=measure_units,
                phrase_measures=min(config.phrase_measures, remaining_before_closing),
            )
        last_variant = call_variant
        call_bins = [
            _map_bin_to_instrument(
                note_bin,
                center_midi=74,
                low=72,
                high=91,
                max_notes=1,
                prefer_highest=True,
            )
            or None
            for note_bin in call_variant.note_bins
        ]
        whistle_bins.extend(call_bins)
        trumpet_bins.extend([None] * len(call_bins))
        total_measures += call_variant.span_measures

        remaining_before_closing = target_phrase_measures - total_measures
        if remaining_before_closing <= 0:
            break

        if rng.random() <= config.call_response_probability:
            response_phrase = rng.choice(phrases)
            response_variant = _make_variant(
                response_phrase,
                rng.choice(config.response_transforms),
                measure_units=measure_units,
                phrase_measures=config.phrase_measures,
            )
            if response_variant.span_measures > remaining_before_closing:
                response_variant = _make_variant(
                    response_phrase,
                    "identity",
                    measure_units=measure_units,
                    phrase_measures=min(config.phrase_measures, remaining_before_closing),
                )
            last_variant = response_variant
            response_bins = [
                _map_bin_to_instrument(
                    note_bin,
                    center_midi=67,
                    low=55,
                    high=79,
                    max_notes=1,
                    prefer_highest=False,
                )
                or None
                for note_bin in response_variant.note_bins
            ]
            whistle_bins.extend([None] * len(response_bins))
            trumpet_bins.extend(response_bins)
            total_measures += response_variant.span_measures

    if last_variant is None:
        last_variant = _make_variant(
            phrases[0],
            "identity",
            measure_units=measure_units,
            phrase_measures=config.phrase_measures,
        )

    closing_whistle, closing_trumpet = _build_closing_phrase_bins(
        last_variant,
        measures=config.closing_measures,
        measure_units=measure_units,
    )
    whistle_bins.extend(closing_whistle)
    trumpet_bins.extend(closing_trumpet)
    total_measures += config.closing_measures

    piano_lh_bins, piano_rh_bins = _build_piano_bins(
        config,
        measures=total_measures,
        measure_units=measure_units,
    )
    percussion_bins = _build_percussion_bins_from_pattern(
        whistle_bins=whistle_bins,
        trumpet_bins=trumpet_bins,
        measures=total_measures,
        measure_units=measure_units,
        closing_measures=config.closing_measures,
        pattern_name=config.percussion_pattern,
        density=config.percussion_density,
        rng=rng,
    )

    max_units = max(
        len(whistle_bins),
        len(trumpet_bins),
        len(percussion_bins),
        len(piano_lh_bins),
        len(piano_rh_bins),
    )
    for bins in (whistle_bins, trumpet_bins, percussion_bins, piano_lh_bins, piano_rh_bins):
        bins.extend([None] * (max_units - len(bins)))

    desired_units = config.total_measures * measure_units
    for bins in (whistle_bins, trumpet_bins, percussion_bins, piano_lh_bins, piano_rh_bins):
        if len(bins) < desired_units:
            bins.extend([None] * (desired_units - len(bins)))
        elif len(bins) > desired_units:
            del bins[desired_units:]

    measures = config.total_measures
    parts = (
        InstrumentPart(
            staff_id="violin",
            name="Violin",
            short_name="Vln.",
            clef="treble",
            midi_instrument="violin",
            events=tuple(_phrase_bins_to_events(whistle_bins)),
        ),
        InstrumentPart(
            staff_id="trumpet",
            name="Trumpet in C",
            short_name="Tpt.",
            clef="treble",
            midi_instrument="trumpet",
            events=tuple(_phrase_bins_to_events(trumpet_bins)),
        ),
        InstrumentPart(
            staff_id="percussion",
            name="Percussion",
            short_name="Perc.",
            clef="percussion",
            midi_instrument="woodblock",
            events=tuple(_phrase_bins_to_events(percussion_bins)),
        ),
        InstrumentPart(
            staff_id="piano_rh",
            name="Piano",
            short_name="Pno.",
            clef="treble",
            midi_instrument="acoustic grand",
            events=tuple(_phrase_bins_to_events(piano_rh_bins)),
        ),
        InstrumentPart(
            staff_id="piano_lh",
            name="Piano",
            short_name="Pno.",
            clef="bass",
            midi_instrument="acoustic grand",
            events=tuple(_phrase_bins_to_events(piano_lh_bins)),
        ),
    )
    return MovementMaterial(
        config=config,
        measure_units=measure_units,
        measures=measures,
        parts=parts,
    )


def build_ensemble_piece(
    *,
    sources: Iterable[BirdSource] = (DEFAULT_SOURCE,),
    movements: tuple[MovementConfig, ...] = DEFAULT_MOVEMENTS,
    seed: int = 7,
) -> EnsemblePiece:
    phrases = build_phrase_library(sources=sources)
    materials = tuple(
        _build_movement_material(phrases, movement, seed=seed)
        for movement in movements
    )
    generation_note_lines = (
        "Bird Im-Migration Ensemble",
        "Source treatment: curated bird fragments -> modular phrase variants",
        "Transforms: identity, retrograde, augment, repeat",
        "Ensemble: violin, trumpet, percussion, piano drone (legato LH + jazz comp RH)",
        f"Phrase sources: {', '.join(sorted({phrase.region_name for phrase in phrases}))}",
        f"Seed: {seed}",
    )
    return EnsemblePiece(
        title="Bird Im-Migration Ensemble",
        composer="George K. Thiruvathukal",
        subtitle="A modular chamber sketch built from curated bird-song fragments",
        movements=materials,
        generation_note_lines=generation_note_lines,
    )
