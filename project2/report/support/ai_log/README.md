# support/ai_log — audit trail for Appendix A

The report's AI Transparency Log (Appendix A) makes three claim audits and says
the underlying transcripts are kept separately. This folder is that separate
location.

| File | Contents |
|---|---|
| `transcript_excerpts.md` | For each of the three audits in table A.2: the question asked, what the assistant returned, what was wrong with it, and the check that settled it. Also the one proposed formula that was rejected. |

## Integrity hash

```
SHA-256  transcript_excerpts.md
77f13be9ba0b9481c4c982e77a9f136a36e1f1e2d1c82415edb6f8d045c619ff
```

The same hash is printed in Appendix A of the report, so the reader can confirm
that the extract has not changed since submission:

```bash
shasum -a 256 support/ai_log/transcript_excerpts.md     # macOS
sha256sum support/ai_log/transcript_excerpts.md         # Linux
```

## What is not here

Full session logs (several thousand messages across the project) are retained by
the contributor, Meichen Ding, and can be produced on request. They are not
committed because they contain unrelated coursework. What is committed is the
part that changed a claim.
