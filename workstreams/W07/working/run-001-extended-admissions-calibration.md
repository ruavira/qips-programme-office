# W07 run 001 — extended synthetic admissions calibration

Status: synthetic process test; no real applicant data, approved entry threshold or cohort cap

Date: 2026-07-28

## Purpose and method

This second calibration adds twelve fictional borderline cases to the first six. It tests one
evidence variable at a time, the proposed moderation trigger and the separation of eligibility,
evidence sufficiency and numerical ranking.

The six criterion weights remain: relevance 15; improvement challenge 25;
initiative/follow-through 20; protected time and completion plan 15; reflection/learning
readiness 15; contribution/equity impact 10. Criterion points equal
`(rating from 0–4 / 4) × weight`.

The cases are fictional and contain no personal data. Reviewers A and B scored independently.

## Twelve-case set

| Case | Single variable tested | Reviewer A | Reviewer B | A total | B total | Result |
|---|---|---|---|---:|---:|---|
| SYN-G | Project access verified | 3/3/3/3/3/3 | 3/3/3/3/3/3 | 75.00 | 75.00 | Eligible evidence complete |
| SYN-H | Same profile; project access conditional | 3/3/3/3/3/3 | 3/3/3/3/3/3 | 75.00 | 75.00 | Score unchanged; evidence gate becomes conditional |
| SYN-I | Protected-time plan specific and calendar-backed | 3/3/3/4/3/2 | 3/3/3/3/3/2 | 76.25 | 72.50 | One-level anchor difference |
| SYN-J | Same profile; protected-time plan vague | 3/3/3/1/3/2 | 3/3/3/1/3/2 | 65.00 | 65.00 | Lower score follows the changed evidence |
| SYN-K | Improvement challenge specific; reviewer interpretation differs | 2/4/2/3/3/3 | 2/2/2/3/3/3 | 72.50 | 60.00 | Moderation trigger fires: 12.50 points and two levels |
| SYN-L | Same profile; challenge only partly bounded | 2/2/2/3/3/3 | 2/2/2/3/3/3 | 60.00 | 60.00 | Consistent lower score |
| SYN-M | Past follow-through verified with artefact evidence | 3/3/4/2/3/2 | 3/3/3/2/3/2 | 73.75 | 68.75 | One-level initiative-anchor difference |
| SYN-N | Same profile; follow-through merely asserted | 3/3/1/2/3/2 | 3/3/1/2/3/2 | 58.75 | 58.75 | Unsupported assertion does not score as evidence |
| SYN-O | Reflection uses a concrete failure and changed practice | 3/2/3/3/4/3 | 3/2/3/3/3/3 | 72.50 | 68.75 | One-level reflection-anchor difference |
| SYN-P | Same profile; reflection remains generic | 3/2/3/3/1/3 | 3/2/3/3/1/3 | 61.25 | 61.25 | Generic aspiration does not substitute for reflection |
| SYN-Q | Contribution case identifies an underserved setting and transfer route | 2/3/3/3/3/4 | 2/3/3/3/3/3 | 73.75 | 71.25 | One-level contribution-anchor difference |
| SYN-R | Same profile; contribution claim has no transfer mechanism | 2/3/3/3/3/1 | 2/3/3/3/3/1 | 66.25 | 66.25 | Lower score follows the changed evidence |

Ratings appear in criterion order.

## Agreement diagnostics

- Mean absolute total-score difference: **2.29 points**.
- Largest difference: **12.50 points**, on SYN-K.
- Exact criterion agreement: **67 of 72 ratings (93.06%)**.
- Agreement within one rating level: **71 of 72 ratings (98.61%)**.
- Exact agreement by criterion: relevance 100%; each other criterion 91.67%.
- One case triggered the proposed rule of ten total points or a two-level criterion difference.

These figures describe a deliberately constructed fictional set. They do not estimate reliability
on real applications, validate the rubric or establish an entry threshold.

## Moderation test

SYN-K was returned to both reviewers with the improvement-challenge anchors and evidence location.
Reviewer A had treated specificity alone as level 4; reviewer B had treated unverified access as a
reason to reduce the challenge rating. The corrected rule is:

1. rate the challenge on importance, specificity and feasible scope;
2. record project access separately as verified, conditional or not established;
3. do not convert an evidence-gate concern into an unlabelled score penalty.

On that rule, both reviewers selected level 3 for the challenge, producing a moderated total of
66.25. Moderation changed the record transparently; it did not average away the disagreement.

## Findings

1. The score and evidence gate must remain separate. SYN-G and SYN-H correctly have the same
   numerical score but different offer conditions.
2. Paired cases move in the intended direction when one evidence element changes.
3. The proposed trigger successfully identified the deliberately material disagreement.
4. The improvement-challenge anchor still needs the clearest reviewer examples because it carries
   the largest weight.
5. A score threshold remains unjustified. The test set was designed around borderline values and
   has no observed completion outcome.

## Operating recommendation

Advance the selection architecture, formula, two-reviewer record and moderation rule for CCC
approval. Keep the entry threshold, cohort cap and any country allocation unapproved until W01,
W03 and Q006 supply the missing evidence and a live pilot can relate scores to observed outcomes.
