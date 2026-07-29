# W12 data assets, consent and research standard v0.9

Status: verified working draft; legal review required

## Purpose boundary

Classify every field before collection:

1. **Programme operations:** needed to apply, contract, provide access, deliver, support, assess, issue the approved credential and meet legal duties.
2. **Programme evaluation:** proportionate evidence used to improve and account for the programme.
3. **Optional research/publication:** systematic secondary use intended for generalisable dissemination; separately reviewed and never bundled as a condition of participation unless counsel/ethics review establishes otherwise.
4. **Prohibited:** patient-identifiable data, copied clinical records, unnecessary special-category data, secrets or unrestricted legal/insurance evidence in ordinary platforms.

Changing purpose requires a fresh review; an available field is not an authorised field.

## Data inventory v0.9

| Domain | Minimum field groups | Sensitivity/control | System of record |
|---|---|---|---|
| Applicant/contact | Identity, contact, country/zone, application state, access needs where volunteered | Personal; access-limited; separate adjustments from selection where possible | Approved admissions system |
| Contract/payment | Sponsor, agreement, invoice/payment status and finance references | Restricted; no payment-card data in QIPS systems | Contract/finance system |
| Account/access | Stable person ID, role, authentication state and access history | Security-sensitive | Approved identity provider |
| Delivery | Enrolment, release/completion events, exceptions and minimal attendance | Personal behavioural trace | Learning/operations systems |
| Assessment | Submission metadata, rubric outcomes, moderation and appeals | Confidential/high consequence | Approved assessment store |
| Artefacts/projects | Version, workplace/sponsor, measures, change records and review state | Potentially sensitive service information | Restricted artefact store |
| Observership | Qualification, schedule, induction, attendance, incident and completion | Restricted; no patient/record content | Restricted observership register |
| Support/accessibility | Request, agreed adjustment, fulfilment and closure | Potential health/sensitive data | Restricted case system |
| Feedback/evaluation | Instrument/version, response, linkage state and consent/purpose | Personal or de-identified depending design | Evaluation store |
| Research/publication | Ethics/classification, consent where required, extract version, disclosure review and outputs | Restricted until approved/de-identified | Research environment |
| Governance | Decision, data dictionary, access, retention, incident, disclosure and deletion evidence | Controlled audit evidence | GitHub metadata plus restricted evidence links |

## Artefact and project controls

- Participants receive a mandatory de-identification checklist before submission.
- Direct patient identifiers, copied records, screenshots and unredacted local system exports are prohibited.
- Measures use aggregate or appropriately de-identified values; small-cell and re-identification risk are reviewed.
- Workplace/sponsor permission, contribution, ownership and publication authority are recorded separately.
- The programme may assess submitted work only under agreed terms; research/publication reuse requires the classification and authority recorded for that use.
- Every extract receives an ID, data-dictionary version, query/date, population, exclusions, transformations, disclosure check, owner and checksum.

## Consent/information architecture

Participant-facing information must distinguish:

- what is necessary to administer and assess the programme;
- what evaluation is undertaken, why, by whom and with what linkage;
- what optional research/publication uses are proposed;
- withdrawal/objection limits once data are irreversibly de-identified or results are published;
- workplace, sponsor, colleague and patient data the participant is not authorised to disclose;
- controller/contact, recipients/processors, locations/transfers, retention, rights, complaints and incidents.

Consent is not used as a decorative cure for unnecessary collection or an unsuitable legal basis. W17/counsel must select and document the lawful basis per purpose and jurisdiction.

## Retention matrix template

No duration is approved. W17 completes each row with legal/contractual reason and a deletion method.

| Record class | Purpose | Trigger | Duration | Hold/exception | Disposal evidence | Owner |
|---|---|---|---|---|---|---|
| Application/non-enrollee | TBD | Application closure | TBD | Complaint/legal hold | Deletion log | W07/W17 |
| Participant contract/finance | TBD | Contract close | TBD | Legal/tax requirement | Disposal certificate | W16/W17 |
| Account/access log | TBD | Account closure | TBD | Security investigation | Log attestation | W09/W17 |
| Assessment/appeal | TBD | Credential/appeal close | TBD | Recognition/legal need | Deletion/archive record | W03/W17 |
| Artefact/project | TBD | Programme close | TBD | Optional authorised archive | Disposal/transfer record | W02/W12 |
| Observership | TBD | Placement close | TBD | Incident/legal hold | Disposal record | W04/W17 |
| Evaluation/research | TBD | Analysis/publication close | TBD | Ethics/replication requirement | Archive/deletion record | W11/W12/W17 |

## Access and disclosure

- least privilege by role and purpose;
- named owner and quarterly access review for restricted stores;
- multi-factor authentication for privileged roles;
- no raw personal data in GitHub, Base44 status fields, public analytics or AI prompts;
- approved de-identification and disclosure review before partner/funder reporting;
- incident route linked to W17 with containment, evidence preservation, assessment, notification and corrective action.

## Research/publication gate

Before a dataset or output becomes a research asset, record:

1. question and intended use;
2. operational evaluation versus research classification and authority;
3. ethics/legal review required and outcome;
4. data minimisation, sample/population and analysis plan;
5. participant/workplace/sponsor permissions;
6. de-identification and disclosure-risk review;
7. authorship/contribution and conflict terms;
8. publication review, SQUIRE mapping and limitations;
9. repository/retention/access location;
10. decision owner and release approval.

Fifty projects do not become a research dataset merely because they exist.
