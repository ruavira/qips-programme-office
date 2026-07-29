# W10 global calendar and monthly operations v0.9

Status: verified operating skeleton; exact dates are not approved except existing canon

## Calendar data contract

Every event record must contain:

- stable event ID and programme month;
- event type and required/optional status;
- UTC start/end in ISO 8601;
- organising IANA zone and generated participant-local display;
- release, submission and feedback deadlines where relevant;
- host, alternate, delivery link and support contact;
- caption, recording and transcript state;
- change history, approval state and last tzdb check;
- make-up or equivalent route.

Never store only a time-zone abbreviation or a local clock time. Calendar invitations are issued in participants' local time and repeat UTC in the description.

## Protected monthly rhythm

| Point | Governed activity | Minimum operating control |
|---|---|---|
| Month open | eLearning release and orientation note | Content, links, accessibility and download check complete |
| Live faculty session | Synchronous interpretation and application | Host/alternate, captions, audio fallback and incident channel tested |
| Four days before coaching | Artefact submission cutoff | Time-zone-safe deadline, exception route and coach access confirmed |
| Coaching | Small-group feedback on submitted work | Coach has reviewed work; no patient-identifiable material displayed |
| Month close | Feedback, recovery and next release readiness | Missing evidence reconciled; support and quality issues logged |

The 40-hour observership from month 3 to week 2 of month 4 runs as a separately scheduled block or approved split schedule without erasing the ordinary monthly controls.

## Time-zone fairness

1. Do not optimise for the programme-office location.
2. Collect each participant's IANA zone and access constraints during onboarding.
3. Publish the full calendar at least eight weeks before the first required live event; publish changes immediately with acknowledgement tracking.
4. Use one primary live window only after testing the actual cohort distribution. If a single window creates unreasonable local hours, rotate windows or offer an equivalent route.
5. A make-up route must preserve the intended evidence, not merely provide a recording.
6. Recheck tzdb and national/religious conflicts at 90, 30 and 7 days before each event.

## Change control

- Minor: link, room or named alternate; operator may change with logged notice.
- Material: date, time, deadline, required status or assessment consequence; programme director approves and affected participants acknowledge.
- Emergency: safety, platform outage or force majeure; incident lead invokes fallback, records impact and starts recovery within the published service window.

## Monthly runbook

| When | Owner action | Evidence |
|---|---|---|
| T-21 days | Confirm content, faculty, coaches, host links and accessibility needs | Readiness record |
| T-14 | Release participant preview and test accounts/permissions | Test log |
| T-7 | Run live-session technical rehearsal and support drill | Rehearsal result |
| T-1 | Confirm captions, host/alternate, attendance minimisation and incident channel | Go/no-go checklist |
| Event day | Operate session, accessibility and incident roles separately | Event log |
| T+1 | Reconcile attendance, exceptions and incidents; remove unnecessary raw exports | Reconciliation record |
| T+5 | Review feedback and operational defects | Improvement actions |
| Month close | Confirm artefact status, recovery actions and next-month readiness | Monthly close record |

## Calendar lock blockers

- W02 content and assessment dependencies are working drafts, not approved.
- F023 (9 January 2027 first live session) remains PROPOSED.
- Faculty, coach, host-site and actual participant availability are unknown.
- Verified 2027 country and religious calendars have not been recorded.
- Attendance/make-up consequences await the W03/W07 decisions.
