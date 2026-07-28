# Security and information handling

The QIPS Programme Office repository stores governance and programme-development records. It must not become a repository for patient data, participant personal data, private contact lists, credentials or signed agreements.

## Never commit

- `.env` files, passwords, access tokens, API keys or service-account material
- patient-level or case-level clinical data
- participant personal data or application records
- private mailing lists or faculty contact details
- signed contracts, insurance documents or identity documents

Store restricted material in an access-controlled Drive folder and record only its document ID, owner, status and approved audience in `documents/register.yaml`.

Report accidental exposure to the repository owner immediately. Rotate any exposed credential before continuing work.
