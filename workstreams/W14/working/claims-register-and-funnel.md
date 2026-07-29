# W14 claims register and demand funnel

Status: working instrument; no public launch authorised

## Claim states

| State | Meaning | Public treatment |
|---|---|---|
| APPROVED | Exact statement is supported by canon | May publish verbatim or through an approved faithful rendering |
| APPROVED_WITH_SOURCE | Canon fact plus a live source record is required | Publish only with the named citation or proof link |
| PENDING_DECISION | A dossier or council recommends it | Omit; do not publish a plausible placeholder |
| PENDING_EVIDENCE | Human, legal or external proof is missing | Show a visible `[TO CONFIRM: …]` only in restricted review material |
| PROHIBITED | Claim conflicts with canon or exceeds authority | Never publish |

## Current market-facing claims register

| Claim family | State | Controlled statement or treatment | Authority |
|---|---|---|---|
| Duration and format | APPROVED | 12-month hybrid professional programme | F001 |
| Monthly rhythm | APPROVED | One eLearning release, one live faculty session, one small-group coaching call and one artefact each month | F003, F005 |
| Submission rhythm | APPROVED | Artefact submitted four days before the coaching call | F004 |
| Observership | APPROVED | 40 hours from month 3 to week 2 of month 4 at a qualified host site in the participant's country | F006–F008 |
| Travel | APPROVED | Travel and accommodation are met by the participant or sponsoring organisation | F007 |
| Applications | APPROVED | Open October 2026 and close 31 December 2026 | F012 |
| Cohort period | APPROVED | January to December 2027 | F013 |
| Sponsor | APPROVED | SQHN is lead sponsor and contracting entity | F014 |
| Partner architecture | APPROVED | Other organisations are Partners, led by RCI, QAI and TAC | F015; descriptions and marks remain gated |
| Time commitment | APPROVED | About four hours a week in an ordinary week and about 228 hours in total | F019 |
| Countries | APPROVED | Nigeria, Ghana and Pakistan | F020 |
| Programme name | PENDING_DECISION | Omit from public release; use restricted working candidate only | Q010 / W13 |
| Completion award | PENDING_DECISION | Omit exact title, issuer and recognition | Q002 / W03 |
| Faculty | PENDING_EVIDENCE | No name, image, biography, title or affiliation before review, appointment and consent | Q003 / W05 |
| Price, deposit and cap | PENDING_DECISION | No amount, discount, scarcity or capacity claim | F024–F026 proposed; W16 |
| Shifa/ISQua programme affiliation | PENDING_EVIDENCE | Omit; individual faculty affiliation only after consent | F022, Q008 |
| Host-site names | PENDING_EVIDENCE | Omit until qualification, agreement and permission | W04/W15/W17 |
| Employment or income outcome | PROHIBITED | No guarantee or implication | canon/glossary.md |
| Nigerian validation or international recognition | PROHIBITED until independently established | Do not use | R002, F021 |

## Two-track journey

1. **Discover.** Approved proof page, SQHN owned channels, partner channels only after permission,
   and direct institutional outreach.
2. **Understand.** Public summary provides duration, rhythm, workload, countries, application
   window and the honest list of what is still to be confirmed.
3. **Express interest.** Minimum data: name, email, country, role, individual/institutional route,
   consent version and source. No health or patient data.
4. **Readiness conversation.** Confirm workplace setting, access to a suitable improvement problem,
   time and sponsor context without making an admissions promise.
5. **Apply.** Open only after Q009, approved name, award, price/policies and application form
   controls. W07 owns selection.
6. **Offer.** Conditional offer states the exact approved commitments, expiry and required evidence.
7. **Deposit and enrolment.** Activate only after W16 payment, refund, FX and reconciliation rules
   pass and SQHN's merchant account is ready.

## Q006 demand-denominator request

SQHN should provide a de-identified aggregate extract for each relevant 2024–2026 promotion:

| Field | Definition |
|---|---|
| Contactable records | Unique records with a lawful current contact basis |
| Delivered invitations | Messages accepted by the channel, excluding hard bounces |
| Unique landing visits | Deduplicated sessions attributable to the promotion |
| Started registrations | Unique people who began the form |
| Completed registrations | Unique people who submitted the form |
| Paid registrations | Unique people whose payment reconciled |
| Attended | Unique people recorded as attending |
| Source and date | Channel/campaign and promotion window |
| Price and offer | Exact amount and any discount for that promotion |

No names, phone numbers or email addresses belong in GitHub or Base44. The source extract remains in
a restricted Drive location; only aggregate counts and the data definition enter the dossier.

## Measurement rules

- Every stage has one event name, timestamp, consent version and source code.
- A person is counted once per stage per campaign.
- Conversion is reported as numerator and denominator, never a percentage alone.
- Channel performance is separated by country and individual/institutional route.
- A lead is not an applicant, an applicant is not an offer, and an offer is not a paid enrolment.
