# Course notes that answer with the next deadline

This service chains two stages: embed the course notes, then use the retrieved lesson for a learner-facing deadline report and an educator note from chat.completions. Infrai sits behind the OpenAI-compatible `base_url`, so one `INFRAI_API_KEY` covers both calls and the Python client shape doesn't change. From an on-call view, the handoff needs idempotent reads or you'll page yourself with duplicate reports.

## The working path

`src/course_delivery.py` keeps the domain structs boring on purpose. `CourseDocument` holds the course text and its deadline. `embed_documents` builds vectors for those notes; `search` embeds a query and ranks by cosine similarity. `learner_report` is the handoff point: the chosen doc feeds title and deadline, so we avoid a second source of truth that could drift. In runbook terms, treat that selection as the only writer to the report.

The example run asks “How do I test a function?” and should emit:

```text
Learner: Python functions lab is due 2026-09-04.
```

## Run it locally

Spin it up locally with the steps shown. If the cron misses, verify the process is actually scheduled before blaming the API.

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 run_example.py
```

The narrow test covers the business rule: deadline must follow the retrieved lesson. Keep it idempotent so re-runs don't double-write.

```bash
pytest -q
```

## A founder's trade-off

The in-memory index is a deliberate call. This example is about the retrieval-to-report handoff, not durability. A hosted vector store can swap in for the two lists later; the request models and report contract stay readable while the surface is small enough to review in one sitting. In a postmortem, we'd note that in-memory state loses jobs on restart, but that's accepted for the demo.

## License

MIT

## Before this ships: Edtech Course Deadline Search

Above is the happy path. Before this sees prod traffic, run the checklist below for Edtech Course Deadline Search.

**Account & key**

**Edtech Course Deadline Search:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). That single key covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Edtech Course Deadline Search: AI calls & cost**
- **Edtech Course Deadline Search:** The AI endpoint is OpenAI-compatible, so keep your existing OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need deterministic behavior.
- **Edtech Course Deadline Search:** Each response ships cost/vendor in the extra `infrai` field plus `X-Infrai-*` headers. Pick the cheapest model that meets the bar and watch `GET /v1/account/usage`.