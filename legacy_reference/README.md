# legacy_reference

This directory is reference-only.

Files here are NOT source of truth.
Current implementation MUST follow the current spec files, not legacy files.

These files MUST NOT be copied directly into the current implementation.

Allowed reference scope:
- deterministic RNG ideas
- roll-level board progression
- clear / gravity / refill order
- other predefined deterministic behavior that does not conflict with current specs

Forbidden legacy concepts:
- pool
- waterline
- control_level
- protect
- reroll
- odds_range gating
- player/state-dependent adjustment
- runtime probability adjustment
- outcome steering

Also forbidden:
- inheriting legacy naming directly
- inheriting legacy config keys directly
- inheriting legacy interfaces directly

Use legacy files only to understand old behavior, then remap valid parts into the current architecture and naming.