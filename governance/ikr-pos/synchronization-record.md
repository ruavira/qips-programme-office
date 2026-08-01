# IKR-POS Installation Synchronization Record

**Control owner:** Programme Office / W09  
**Installation source:** `ruavira/qips-programme-office`  
**Installation revision:** `0c6334d8a48ee5552f155fa92f277f5ba9321f72`  
**Installation PR:** #11  
**Synchronized:** 2026-07-31 20:55 America/Edmonton  
**Overall status:** `IN_SYNC`  
**CCC ratification:** `PENDING` (`IKR-D001`)

## GitHub

The QIPS-native IKR-POS profile, repository charter, system-of-record map, installation manifest,
portable-export manifest, governance registers, agent contract, pull-request controls, validator and
mandatory repository workflow were squash-merged in PR #11.

Validation completed successfully in GitHub Actions run `30680835572`, job `91317371425`:

- CCC agenda generation: PASS;
- control-room generation: PASS;
- Python compilation of `engine/validate_ikr_pos.py`: PASS;
- IKR-POS governance validation: PASS;
- generated-file consistency: PASS;
- secret and environment-file scan: PASS.

## Base44

**Application ID:** `6a68b8381ea8ff36dd473cd2`

The following programme-document records were created and read back:

- Operating Profile: `6a6d5fa0b7e20cd4a419626e`;
- Repository Charter: `6a6d5fa0b7e20cd4a419626f`;
- Installation Handover: `6a6d5fa0b7e20cd4a4196270`;
- Governance Registers: `6a6d5fa0b7e20cd4a4196271`;
- Installation and Ratification Pack: `6a6d60349bba2f9b8ec3d4c2`.

Decision dossier `IKR-D001` was created as `ready_for_ccc`, verification `pass`, with record ID
`6a6d5fadb7bc3f06457213fb`. It points to installation revision
`0c6334d8a48ee5552f155fa92f277f5ba9321f72`. No approval is implied.

## Google Drive

The native Google Doc **QIPS IKR-POS Installation and Ratification Pack** was created, populated,
moved into the QIPS Programme Office folder and read back.

- QIPS Programme Office folder ID: `1e2hs6yuN27dbZPCVcnQzKfE6ezssXdIc`;
- document ID: `1bIkR9rAbtWVJWuKLSjeYllUQPKgxpgFKHUqGQgZVJwM`;
- review URL: `https://docs.google.com/document/d/1bIkR9rAbtWVJWuKLSjeYllUQPKgxpgFKHUqGQgZVJwM`.

The pack explicitly states that GitHub remains authoritative, identifies PR #11 and the exact source
revision, distinguishes the installed operating baseline from CCC ratification, and preserves
Supabase, Netlify and Vercel as unregistered surfaces.

## Unregistered surfaces

- **Supabase:** no governed QIPS project identifier, approved schema or access policy; no activation performed.
- **Netlify:** no governed QIPS deployment identifier; no deployment performed.
- **Vercel:** no governed QIPS deployment identifier; no deployment performed.

## Governance conclusion

The installation content and its Base44 and Drive mirrors are reconciled against the exact GitHub
installation revision. The profile is the current installed repository operating baseline. Formal
policy ratification, publication, any change to authority, database activation and deployment remain
subject to their explicit human gates. Decision `IKR-D001` remains pending.
