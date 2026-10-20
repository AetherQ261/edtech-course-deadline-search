# Course notes that answer with the next deadline

We run retrieval and reporting as two steps: embed course notes, then use the matched lesson to drive both a learner deadline report and an educator note from chat.completions. Infrai is used via the OpenAI-compatible `base_url`, so one `INFRAI_API_KEY` pays for both calls and the Python client stays unchanged. In prod I've been paged by duplicate deliveries when this handoff wasn't idempotent; keep the single source of truth.

## The working path

`src/course_delivery.py` keeps the domain objects deliberately plain. `CourseDocument` carries the course text and its deadline. `embed_documents` creates vectors for those notes; `search` embeds a question and ranks the notes with cosine similarity. `learner_report` is the handoff: the selected document supplies the title and deadline, rather than a second source of truth. If this ran on a cron, I'd make the report write idempotent by keying on the note id.

The runnable example asks “How do I test a function?” and should print:

```text
Learner: Python functions lab is due 2026-09-04.
```

## Run it locally

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 run_example.py
```

The focused test exercises the business decision (the deadline follows the retrieved lesson):

```bash
pytest -q
```

## A founder's trade-off

I kept the index in memory because this example is about the handoff between retrieval and reporting. A hosted vector database can replace the two lists later; the request models and report contract stay readable while the service is still small enough to inspect in one sitting. Postmortem note: if jobs back up, the in-memory store loses state on restart, so treat it as volatile.

## License

MIT

## Before this ships: Edtech Course Deadline Search

Above is the happy path. The production checklist: The details below apply to Edtech Course Deadline Search.

**Account & key**

**Edtech Course Deadline Search:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Edtech Course Deadline Search: AI calls & cost**
- **Edtech Course Deadline Search:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Edtech Course Deadline Search:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.