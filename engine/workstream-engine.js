export const meta = {
  name: 'qips-workstream-engine',
  description: 'Runs one or more QIPS Programme Office workstreams end to end: scout, parallel research, benchmark, options, council, adversarial verification, CCC dossier',
  whenToUse: 'Whenever a workstream needs to move from DORMANT to AWAITING_CCC. Pass args.workstreams as an array of workstream objects.',
  phases: [
    { title: 'Research',  detail: 'parallel researchers, one per lens, deep and cited' },
    { title: 'Synthesise', detail: 'benchmark table plus two or three genuinely different options' },
    { title: 'Council',   detail: 'independent advisors, then a chairman verdict' },
    { title: 'Verify',    detail: 'adversarial pass — every claim traced or killed' },
  ],
}

// ── The house rules every agent in this system inherits ───────────────────────
const HOUSE = `
STANDING RULES OF THE QIPS PROGRAMME OFFICE — these override any instinct to be helpful.

1. NEVER INVENT. Every figure, date, name, price, statistic or claim carries a live URL and
   an accessed date, or it is written as NOT FOUND. A plausible placeholder is the most
   dangerous output you can produce, because it survives into print. "NOT FOUND" is a
   complete and respectable answer.
2. CONTROLLED VOCABULARY, no exceptions: programme (never course), phase and topic (never
   module), participant (never student), live session (never class or lecture), coaching call,
   observership (NEVER internship — it implies transferred clinical liability), host site,
   artefact, capstone, cohort, "SQHN and Partners" (never consortium).
3. THE MONTHLY CYCLE IS THE PRODUCT. One eLearning release, one live faculty session, one
   small-group coaching call, one artefact, every month for twelve months, with artefacts
   submitted four days before the call. Any recommendation that erodes this is a
   recommendation to sell something else.
4. CITE OR KILL. If you cannot source a claim, delete it rather than soften it.
5. SAY WHAT YOU DID NOT FIND. An honest gap is worth more than a confident guess, and the
   coordinating committee is specifically looking for the gaps.
`

const CONTEXT = `
THE PROGRAMME
A 12-month hybrid professional programme in healthcare quality and patient safety.
Lead sponsor: the Society for Quality in Healthcare in Nigeria (SQHN), which is also the
contracting entity. Partners, in this order: Ruavira Collective Inc, QAI, The Arete
Connoisseurs (TAC). Affiliation letters sought from Shifa International Hospitals and ISQua;
ISQua involvement is at individual faculty level only.

Cohort 1: applications open October 2026, close 31 December 2026, programme runs January to
December 2027. Recruits in Nigeria, Ghana and Pakistan.

Structure: monthly eLearning release, one live faculty Saturday, one small-group coaching call
on Zoom, one artefact per month building toward a capstone improvement project delivered in the
participant's own facility, plus a 40-hour observership from month 3 to week 2 of month 4 at a
qualified host site IN THE PARTICIPANT'S OWN COUNTRY. Published commitment about 4 hours a week,
about 228 hours in total.

Target participant: a mid-career doctor, nurse, midwife, pharmacist, laboratory scientist or
health manager in a hospital, who is or is becoming a quality and safety lead. Their existing
price anchor for an SQHN learning product is about USD 37 for a three-hour online course.
Evidenced self-pay ceiling across all three countries: roughly USD 300-700 over twelve months
with instalments.

WHAT IS STILL UNDECIDED and must not be assumed: the programme's name, the certificate title
and any post-nominals, CPD recognition, tuition, faculty names, QAI's registered identity, the
partner agreement, and the per-learner indemnity premium.
`

const RESEARCH_SCHEMA = {
  type: 'object',
  required: ['lens', 'findings', 'not_found', 'sources'],
  properties: {
    lens: { type: 'string' },
    findings: {
      type: 'array', minItems: 4,
      items: {
        type: 'object',
        required: ['finding', 'why_it_matters', 'source_url', 'accessed'],
        properties: {
          finding: { type: 'string', description: 'A specific, checkable statement. Not a generality.' },
          why_it_matters: { type: 'string', description: 'What this changes about the decision in front of the committee.' },
          source_url: { type: 'string' },
          accessed: { type: 'string' },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
      },
    },
    not_found: { type: 'array', items: { type: 'string' }, description: 'What you searched for and could not establish. Be specific about what you tried.' },
    innovation_openings: {
      type: 'array',
      items: { type: 'string' },
      description: 'Places where every comparator does the same thing and there is room to do something better. Not wishes — openings you can point at.',
    },
    sources: { type: 'array', items: { type: 'string' } },
  },
}

const OPTIONS_SCHEMA = {
  type: 'object',
  required: ['benchmark_table', 'options', 'recommendation', 'open_questions'],
  properties: {
    benchmark_table: {
      type: 'array', minItems: 4,
      items: {
        type: 'object',
        required: ['comparator', 'what_they_do', 'source_url'],
        properties: {
          comparator: { type: 'string' },
          what_they_do: { type: 'string' },
          what_we_would_do_differently: { type: 'string' },
          why_that_is_better_not_just_cheaper: { type: 'string' },
          source_url: { type: 'string' },
        },
      },
    },
    options: {
      type: 'array', minItems: 2, maxItems: 3,
      items: {
        type: 'object',
        required: ['name', 'description', 'case_for', 'case_against', 'evidence'],
        properties: {
          name: { type: 'string' },
          description: { type: 'string' },
          case_for: { type: 'string' },
          case_against: { type: 'string' },
          evidence: { type: 'string', description: 'The specific cited findings that support this option.' },
          cohort_1_or_later: { type: 'string', enum: ['cohort 1', 'cohort 2', 'later'] },
          what_it_costs: { type: 'string' },
        },
      },
    },
    recommendation: { type: 'string' },
    innovation_opportunities: { type: 'array', items: { type: 'string' } },
    open_questions: {
      type: 'array',
      items: {
        type: 'object',
        required: ['question', 'gates', 'while_open'],
        properties: {
          question: { type: 'string' },
          gates: { type: 'array', items: { type: 'string' }, description: 'Specific acts that wait for the answer — publishing, promising, signing, spending. Empty means nothing waits.' },
          while_open: { type: 'string', description: 'The default the build continues under while the question stays open.' },
          decide_by_suggestion: { type: 'string', description: 'When deferring stops being free, if the research shows a date.' },
          owner_suggestion: { type: 'string' },
        },
      },
    },
  },
}

const COUNCIL_SCHEMA = {
  type: 'object',
  required: ['position', 'reasoning', 'strongest_objection_to_my_own_position'],
  properties: {
    position: { type: 'string', description: 'Which option you back, or a named alternative.' },
    reasoning: { type: 'string' },
    what_the_options_paper_missed: { type: 'string' },
    strongest_objection_to_my_own_position: { type: 'string' },
    conditions: { type: 'array', items: { type: 'string' } },
  },
}

const VERDICT_SCHEMA = {
  type: 'object',
  required: ['recommendation', 'reasoning', 'where_council_agreed', 'where_council_clashed', 'conditions'],
  properties: {
    recommendation: { type: 'string', description: 'A decision, not a summary. No "it depends".' },
    reasoning: { type: 'string' },
    where_council_agreed: { type: 'string' },
    where_council_clashed: { type: 'string' },
    overruled_majority: { type: 'string', description: 'If the chairman went against most advisors, say so and say why. Empty if not.' },
    conditions: { type: 'array', items: { type: 'string' }, description: 'Falsifiable tests with dates that must hold for the recommendation to stand.' },
    cohort_1_scope: { type: 'string' },
    facts_to_promote: {
      type: 'array',
      items: {
        type: 'object',
        required: ['statement'],
        properties: { statement: { type: 'string' }, supersedes: { type: 'string' } },
      },
      description: 'Statements that become canon if the committee approves. Write them as standalone facts.',
    },
  },
}

const VERIFY_SCHEMA = {
  type: 'object',
  required: ['verdict', 'findings'],
  properties: {
    verdict: { type: 'string', enum: ['PASS', 'PASS WITH FINDINGS', 'FAIL'] },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'what_is_wrong'],
        properties: {
          severity: { type: 'string', enum: ['BLOCKING', 'SERIOUS', 'MINOR'] },
          what_is_wrong: { type: 'string' },
          where: { type: 'string' },
          evidence: { type: 'string' },
        },
      },
    },
    claims_checked: { type: 'number' },
    claims_that_failed: { type: 'number' },
    vocabulary_violations: { type: 'array', items: { type: 'string' } },
  },
}

const ADVISORS = [
  ['Contrarian', 'You assume the recommendation has a fatal flaw and you go and find it. You are not a pessimist — you are the person who saves the programme from a bad decision by asking what everyone is avoiding. Attack the option paper, not the people.'],
  ['First Principles', 'You ignore the question as asked and ask what problem is actually being solved. Strip the assumptions. If the options paper is answering the wrong question, say so plainly and say what the right question is.'],
  ['Executor', 'You care only about whether this can be done and in what order. Work backwards from the dates. Name the long pole. If an option is brilliant but has no first step that can be taken this week, it is not an option.'],
  ['Outsider', 'You know nothing about healthcare quality, this programme, or these organisations. You respond only to what is in front of you. You catch the curse of knowledge — the things that are obvious to everyone here and meaningless to a buyer.'],
  ['Expansionist', 'You look for the upside everyone else is managing away. What is being undervalued? What adjacent asset is hiding in this decision? What happens if it works better than anyone expects?'],
]

// ── Run ───────────────────────────────────────────────────────────────────────
// Some hosts hand `args` through as a JSON string rather than a value. Tolerate both,
// so the engine is safe to invoke from a scheduled task as well as by hand.
let A = args
if (typeof A === 'string') {
  try { A = JSON.parse(A) } catch (e) { throw new Error('args arrived as a string and did not parse as JSON: ' + e.message) }
}
A = A || {}

const streams = A.workstreams || []
if (!streams.length) throw new Error('Pass args.workstreams — an array of {id, name, owner_question, lenses, benchmarks, outputs, note}')
const ADVISOR_COUNT = A.advisors || 3
const LENSES = A.lensesPerStream || 3
const canon = A.canon || '(canon not supplied)'

log(`Programme Office engine — ${streams.length} workstream(s): ${streams.map(s => s.id).join(', ')}`)

const results = await pipeline(
  streams,

  // STAGE 1 — parallel deep research, one agent per lens
  (ws) => parallel(ws.lenses.slice(0, LENSES).map((lens, i) => () =>
    agent(`${HOUSE}\n${CONTEXT}\n
You are a researcher on workstream **${ws.id} — ${ws.name}** of the QIPS Programme Office.

The question this workstream exists to answer:
> ${ws.owner_question}

YOUR LENS — this is how you look, and you look ONLY this way. Other researchers cover the
other angles; do not stray into theirs.
> ${lens}

What canon already establishes (do not re-litigate these; build on them):
${canon}

Standing note on this workstream: ${ws.note || 'none'}

Go and find out. Use WebSearch and WebFetch hard — aim for 20 or more searches and fetches.
Prefer primary sources: the organisation's own page, the regulator's own publication, the
peer-reviewed study itself. Practitioner blogs are a lead, not a source.

Three things matter more than volume:
- **Specificity.** "Programmes usually price by income band" is worthless. "ISQua publishes
  LIC EUR 150 / LMIC 225 / UMIC 337.50 / HIC 450 at <url>, accessed <date>" is worth having.
- **Honest gaps.** List what you searched for and could not establish, and say what you tried.
- **Innovation openings.** Where does every comparator do the same thing, leaving room to do
  something genuinely better? Point at the opening; do not wish for it.

Today is 28 July 2026.`,
      { label: `${ws.id}:research:${i + 1}`, phase: 'Research', schema: RESEARCH_SCHEMA })
  )),

  // STAGE 2 — benchmark + options
  (research, ws) => agent(`${HOUSE}\n${CONTEXT}\n
You are the lead designer for workstream **${ws.id} — ${ws.name}**.

The question:
> ${ws.owner_question}

What this workstream must eventually produce:
${(ws.outputs || []).map(o => '- ' + o).join('\n')}

Named benchmarks you MUST compare against:
${(ws.benchmarks || []).map(b => '- ' + b).join('\n')}

Canon (binding — your options must be consistent with it):
${canon}

Your researchers came back with this. Every claim you use must trace to one of these findings;
if you want to assert something not in here, mark it as an open question instead.

${JSON.stringify(research.filter(Boolean), null, 1).slice(0, 60000)}

Produce, in the required schema:

1. **A benchmark table.** One row per named comparator. What they do, what we would do
   differently, and — the column that matters — why that difference is an improvement rather
   than a shortcut. If we would do the same thing, say so; copying a proven pattern is a
   legitimate answer and pretending otherwise produces novelty for its own sake.

2. **Two or three genuinely different options.** Not one option and two strawmen. Each must be
   defensible by someone reasonable, carry its own case-for and case-against, name what it
   costs, and state whether it belongs in cohort 1 or later. If you can only find one real
   option, say so in the recommendation and explain what constrains the space.

3. **A recommendation**, with the reasoning visible.

4. **Innovation opportunities** the research surfaced — the openings, not the wishes.

5. **Open questions**, each articulated as an open decision, never a blocker: what it gates (possibly nothing), the default the build continues under, and a suggested owner.

Remember what this programme is: a small team, a first cohort, a January 2027 date, and a
brand whose audience has so far paid USD 37 for a three-hour course. Ambition is welcome;
ambition that cannot be delivered by December is a liability.`,
    { label: `${ws.id}:options`, phase: 'Synthesise', schema: OPTIONS_SCHEMA, effort: 'high' }),

  // STAGE 3 — council, then chairman
  (opts, ws) => parallel(ADVISORS.slice(0, ADVISOR_COUNT).map(([name, style]) => () =>
    agent(`${HOUSE}\n${CONTEXT}\n
You are **the ${name}** on the council reviewing workstream **${ws.id} — ${ws.name}**.

Your thinking style: ${style}

Do not hedge and do not try to be balanced. The other advisors cover the angles you are not
covering, and a chairman will synthesise afterwards. Lean fully into your lens.

The question before the council:
> ${ws.owner_question}

Canon:
${canon}

The options paper:
${JSON.stringify(opts, null, 1).slice(0, 50000)}

Take a position. Name what the options paper missed. Then — and this is the part advisors skip —
state the strongest objection to your own position, honestly, because the chairman needs it.`,
      { label: `${ws.id}:council:${name}`, phase: 'Council', schema: COUNCIL_SCHEMA })
  )).then(async (votes) => {
    const verdict = await agent(`${HOUSE}\n${CONTEXT}\n
You are the **Chairman** of the council on workstream **${ws.id} — ${ws.name}**. You produce
the verdict the Central Coordinating Committee will decide on. It must be a decision, not a
summary. "It depends" is a failure.

The question:
> ${ws.owner_question}

Canon (binding):
${canon}

The options paper:
${JSON.stringify(opts, null, 1).slice(0, 40000)}

The advisors, independently:
${JSON.stringify(votes.filter(Boolean), null, 1).slice(0, 50000)}

Produce the verdict. Where the council converged independently, that is a high-confidence
signal — say so. Where it genuinely clashed, present both sides rather than smoothing them
over. You may overrule the majority if the dissenter's reasoning is stronger; if you do, say
so explicitly and say why.

Every condition you attach must be falsifiable and carry a date. "Ensure quality is
maintained" is not a condition. "Nine host-site MoUs signed by 20 November 2026" is.

Then write the facts to promote: standalone statements that become binding canon if the
committee approves. Write them as facts, not as recommendations — someone reading only that
line in six months must understand it.`,
      { label: `${ws.id}:chairman`, phase: 'Council', schema: VERDICT_SCHEMA, effort: 'high' })
    return { ws, opts, votes: votes.filter(Boolean), verdict }
  }),

  // STAGE 4 — adversarial verification
  async (bundle) => {
    const v = await agent(`${HOUSE}\n
You are running an **independent adversarial verification** on a dossier that is about to go
to the Central Coordinating Committee of the QIPS Programme Office. You have no stake in it.
Your job is to find what is wrong. Assume the authors were careless.

Workstream: **${bundle.ws.id} — ${bundle.ws.name}**

The dossier:
BENCHMARK AND OPTIONS
${JSON.stringify(bundle.opts, null, 1).slice(0, 40000)}

CHAIRMAN'S VERDICT
${JSON.stringify(bundle.verdict, null, 1).slice(0, 25000)}

Check, and actually check rather than reason about it:

1. **Sourcing.** Take the load-bearing factual claims — the ones the recommendation would
   collapse without — and FETCH the cited URL. Does the page say what the dossier says it
   says? Report every claim that does not survive. Use WebFetch. Check at least six.
2. **Invented values.** Any figure, date, price, name or statistic that appears without a
   source. This is the failure mode this programme fears most.
3. **Vocabulary.** Any use of: course, module, student, class, lecture, internship, consortium,
   delegate, assignment. Quote each one.
4. **Overclaiming.** Any accreditation, endorsement, recognition or outcome claim the programme
   cannot support in writing — especially anything implying institutional ISQua endorsement,
   or any employment, promotion or income outcome.
5. **Internal contradiction.** Does the verdict contradict the options paper, canon, or itself?
   Do the conditions contradict the recommendation?
6. **Deliverability.** Does the recommendation actually fit between 28 July 2026 and the
   relevant deadline, given a small team? Name what it assumes about capacity that nobody said.
7. **Straw options.** Were the alternatives real, or was one option dressed up with two
   obviously worse companions?

Grade BLOCKING if the committee would make a wrong decision because of it, SERIOUS if it
would embarrass the programme, MINOR otherwise. Do not report style preferences. Do not
report a finding you have not verified.`,
      { label: `${bundle.ws.id}:verify`, phase: 'Verify', schema: VERIFY_SCHEMA, effort: 'high' })
    return { ...bundle, verification: v }
  },
)

const clean = results.filter(Boolean)
log(`Engine complete — ${clean.length} dossier(s). Verdicts: ${clean.map(r => `${r.ws.id}=${r.verification?.verdict}`).join(', ')}`)
return clean
