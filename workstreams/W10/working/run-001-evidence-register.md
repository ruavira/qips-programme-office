# W10 run 001 — evidence register

Status: working evidence; accessed 29 July 2026

| Source | Finding used | Operating implication |
|---|---|---|
| [IANA Time Zone Database](https://www.iana.org/time-zones) | Civil-time rules can change and tzdb is updated to reflect government changes. | Store UTC plus an IANA zone identifier; regenerate local views from a current tzdb release. |
| [ISO 8601-1:2019](https://www.iso.org/standard/70907.html) | ISO 8601 provides unambiguous date/time strings and UTC offsets for interchange. | Machine records use ISO 8601; invitations also show readable local times. |
| [WHO Learning on TAP delivery guide](https://www.who.int/publications/i/item/9789240118348) | Blended health-workforce delivery requires explicit planning, delivery and adaptable supporting resources. | Publish the monthly rhythm and give operators reusable preparation/checklist records. |
| [Zoom attendance reporting](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0073594) | Reports can provide join, leave and duration data after a session. | Attendance is an operational signal, not a proxy for participation or competence, and must be minimised. |
| [Zoom captions](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0059762) | Manual and automated captions can be made available and participant display can be customised. | Caption availability and a captioner contingency belong in every live-session checklist. |

## Evidence limits

- This run does not claim exact 2027 national or religious holiday dates beyond approved canon.
- Target-country calendars and faculty availability must be primary-verified before calendar lock.
- No validated cohort time-zone distribution exists yet; the rule must support locations beyond the three recruitment countries.
