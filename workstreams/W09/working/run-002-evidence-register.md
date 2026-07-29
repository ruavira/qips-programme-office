# W09 run 002 — evidence register

Status: working evidence; accessed 29 July 2026

| Source | Finding used | Control implication |
|---|---|---|
| [WHO health-workforce education technology assessment](https://www.who.int/publications/i/item/9789240070929) | Technology selection must consider interacting learner, organisational and system factors; there is no single universal assessment method. | Score the actual QIPS use case and pilot it; do not choose from feature lists alone. |
| [Moodle accessibility](https://docs.moodle.org/dev/Accessibility) | Current Moodle products are audited against WCAG 2.2 Level AA, with version-specific conformance. | Treat RCI Moodle as a candidate baseline, subject to version, theme, plug-in and content testing. |
| [Moodle app offline features](https://docs.moodle.org/502/en/Moodle_app_offline_features) | The official app supports offline activity, with limits and download behaviour. | Prototype every required monthly participant journey offline or on constrained data. |
| [Moodle security recommendations](https://docs.moodle.org/405/en/Security_recommendations) | Moodle recommends current releases, HTTPS, least privilege, security checks, backups and tested restoration. | Make patching, role review, backup and restore evidence launch gates. |
| [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | WCAG 2.2 is the current W3C Recommendation and includes testable A/AA success criteria. | Target AA for the full participant journey, not merely the theme or landing page. |
| [Zoom meeting history reports](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0073594) | Licensed reporting can expose names, email, join/leave times and duration. | Minimise attendance exports and place them under the W12 retention/access matrix. |
| [Zoom captions/transcript update](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0085668) | Live captions and retained transcripts are now separate controls; transcripts require explicit settings and retention choices. | Keep live captions on; keep transcripts off until purpose, access and retention are approved. |
| [1EdTech specifications](https://www.1edtech.org/specifications) | LTI Advantage, OneRoster and Caliper define portable integration and event-data patterns. | Prefer standards-compatible interfaces; do not make proprietary event logs the only evidence. |
| [Base44 privacy and security](https://docs.base44.com/Community-and-support/Privacy-and-security) | Region moves require clone/export/import and application users are not copied or exportable. | Base44 must remain a replaceable operational projection, not the durable identity directory. |

## Evidence limits

- No inspection of the current RCI Moodle version, theme, plug-ins, hosting, backup or identity configuration has occurred.
- No real participant bandwidth/device testing has occurred in Nigeria, Ghana or Pakistan.
- Vendor documentation establishes capability, not QIPS configuration compliance.
- Q009 still blocks final storage, transcript and retention settings.
