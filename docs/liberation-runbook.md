# Liberation runbook — GitHub as the single control plane

**Goal:** code on GitHub, the walkthrough deployed from GitHub on every merge to `main`,
reviewer answers in the owner's own Netlify account, and every AI tool or human an
interchangeable driver through the three lanes AGENTS.md already defines. Prepared
8 August 2026; owner actions verified from the agent side where a retry can prove them.

## Lock-in audit — 8 August 2026

| Layer | Where it lives today | Captive? | Destination |
|---|---|---|---|
| Code | `ruavira/qips-programme-office`, owner's GitHub, public. In-flight work reaches it as proved bundles the owner pushes. | **Free.** | Unchanged. |
| Hosting/runtime | `qips-walkthrough.netlify.app`, owner's own Netlify account. | **Free at the account layer.** | Unchanged. |
| Data | Reviewer answers land in Netlify Forms (`qips-walkthrough-responses`), owner's account; the page also offers "Save my responses to a file" as a reviewer-side copy. Canon and every register are plain files in git. No participant personal data exists in any system, by decision. | **Free.** Export path documented below. | Unchanged. |
| Identity/auth | None — the walkthrough deliberately has no login. GitHub and Netlify identities are the owner's. | **Free.** | Unchanged. |
| Deploy path | **One Mac.** Build with `walkthrough.py` into `~/qips-site` (not a git repo), then `netlify-cli` using a login that lives on that machine. No CI. Found on audit day: the live page was built from `0dd9c5e`, four commits behind the branch, still carrying vocabulary canon had since banned. | **CAPTIVE — the only captive layer.** | `deploy-walkthrough.yml`: push to `main` → section-8 gates → build → deploy → verified at the live URL. |

The one decision this asked of the owner: none about providers — everything already
runs in his accounts. Only the two secrets below.

## Already done (verified, not assumed)

- `.github/workflows/deploy-walkthrough.yml` added: gates (all eleven checks) → build →
  deploy → **post-deploy verification that the live page carries the deploying commit's
  stamp and none of the banned vocabulary**. Refuses loudly if secrets are missing.
- The exact gate-and-build sequence was run in a clean environment against this branch:
  all checks green, page built, commit stamp present in the artifact.
- Deploys fire only from `main`. Only the owner merges to `main` (CODEOWNERS), so the
  merge that makes something true is the same act that publishes it.
- Rollback preserved: the manual path (HANDOFF.md §5 rebuild command from `~/qips-programme-office`,
  then `npx netlify-cli deploy --dir ~/qips-site --prod`) still works and is unchanged.

## One-time owner actions

1. **Create a Netlify personal access token.**
   https://app.netlify.com/user/applications → *Personal access tokens* → *New access token*
   → name it `qips-deploy-ci` → copy the token once. (No billing prompt; tokens are free.)
2. **Add the two repository secrets.**
   https://github.com/ruavira/qips-programme-office/settings/secrets/actions → *New repository secret*:
   - `NETLIFY_AUTH_TOKEN` — the token from step 1.
   - `NETLIFY_SITE_ID` — `f0a0030c-d45b-4f94-884e-dae84332e2e9` (from `~/qips-site/.netlify/state.json`;
     a site id alone cannot deploy, which is why it may be written here in a public repo).
3. **First run, manually.**
   https://github.com/ruavira/qips-programme-office/actions/workflows/deploy-walkthrough.yml
   → *Run workflow* on `main`. (Merges performed by GitHub Apps do not fire push
   workflows — the manual trigger is the standing escape hatch, and the first run is
   also the secrets check.) The log ends with the live-page verification.
4. **Keep Netlify form detection enabled** (Site configuration → Forms). The workflow's
   deploys carry the same form markup; if detection is ever off, the page reports sends
   honestly as unacknowledged, and the live send test in HANDOFF §8 stands.

No token, cookie or credential transits chat at any point: step 1's token goes from the
Netlify page straight into the GitHub secrets page, both in the owner's browser.

## Reviewer-answer export (the data layer, for the record)

Netlify → the site → *Forms* → `qips-walkthrough-responses` → export CSV. The reviewer's
own browser additionally holds "Save my responses to a file" at every part boundary, so
a copy independent of Netlify always exists at the source.

## Multi-agent access — the part that makes agents interchangeable

Reading needs nothing: the repo is public and `HANDOFF.md` is item 0 in `AGENTS.md`.
Writing has two lanes, both already defined in AGENTS.md; this runbook only says how to
grant them:

- **Lane 1 (agent can push).** Grant per-tool, owner-side, so the credential lives in the
  platform and never in a conversation: Codex/ChatGPT via its GitHub connector on the
  owner's account; a Claude session by attaching the repo with push access when the
  session asks; a human collaborator via
  https://github.com/ruavira/qips-programme-office/settings/access. Pushing a
  `proposal/**` branch makes `proposal.yml` open the pull request. Branch protection on
  `main` plus CODEOWNERS on `canon/**` keeps every verdict with the owner regardless of
  how many agents can push.
- **Lane 2 (agent cannot push).** Unchanged: proved bundle + apply script, owner runs one
  command. This lane is why an agent with no credential at all can still contribute.

**Post-liberation operating rule:** the walkthrough goes live by merging to `main` — from
any tool, any account, through the lanes. Nothing else publishes. If the live page ever
disagrees with `main`, that is an incident, not a mystery.

## Explicitly not migrated, and why

- **Base44 and Google Drive mirrors** — governed mirrors by design (AGENTS.md); they must
  not override GitHub and are synchronised with recorded source commits. Mirrors are not
  captivity when the source of truth is the repo.
- **Netlify as host** — it is the owner's account, the site is one static page, and the
  form inbox is exportable. Moving hosts would be motion without liberation. The day that
  changes, this workflow is the only thing to edit.
