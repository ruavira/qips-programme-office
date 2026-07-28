# W07 run 001 — adversarial verification

Verdict: **PASS WITH FINDINGS**

Verified: 2026-07-28

Blocking findings open: 0

## Checks performed

- Re-read canon, F018, Q002, Q006, the brief, benchmark, options, application prototype, both
  synthetic calibrations and council record.
- Re-fetched official Africa CDC, Commonwealth, WHO, Wellcome and Ghana College sources where
  accessible.
- Independently recalculated all eighteen synthetic cases using
  `(rating / 4) × criterion weight`.
- Recalculated the extended-set diagnostics: mean total difference 2.2917, maximum 12.50,
  exact agreement 67/72 and within-one agreement 71/72.
- Searched for title, employer, sponsorship, ability-to-pay or accommodation information entering
  the numerical score.

## Findings and disposition

### SERIOUS — the first six cases could not test the moderation trigger

No first-round case reached ten total points or a two-level criterion difference.

**Disposition:** twelve paired borderline cases were added. SYN-K triggered both parts of the rule
and the moderation sequence was tested.

### SERIOUS — synthetic agreement could be misrepresented as reliability

The cases were deliberately constructed and have no observed participant outcome.

**Disposition:** the dossier reports the diagnostics only as a process test and prohibits a
threshold or reliability claim.

### SERIOUS — project access was leaking into judgement

One reviewer reduced the improvement-challenge rating because access was conditional.

**Disposition:** the rule now rates the challenge on its own anchors and records project access as
a separate evidence gate.

### SERIOUS — Q006 and upstream dependencies remain open

Demand, W01 personas and W03 credential level are not established.

**Disposition:** the dossier requests process architecture only and leaves threshold, cap, country
allocation and forecast unapproved.

### MINOR — two-reviewer cost is unknown

Application volume and reviewer capacity cannot be costed without Q006.

**Disposition:** retained as a W07/W16 implementation input, not replaced with an invented value.

## Claim result

The calculations are correct, the proposed moderation trigger was exercised, and the architecture
keeps eligibility, evidence sufficiency, scoring and financial support separate. No threshold,
capacity or conversion claim is supported.
