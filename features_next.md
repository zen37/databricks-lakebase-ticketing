**What feature would you add next?**

Now that the core system works, the next step is to make it smarter and more production-ready. I'd prioritize:

**AI-assisted support** (the natural next stage for this app)
- Auto-suggest a list of likely answers as soon as a ticket is created.
- Auto-triage new tickets — have an LLM propose the priority and category from the title and description.
- Retrieve similar *past resolved* tickets to recommend proven solutions (retrieval over the existing Lakebase data).
- Summarize long conversation threads so an agent picking up a ticket gets the gist quickly.

**Workflow & SLA**
- A status-change history table that records how long each ticket has spent in every status, so SLA timers and escalations can be triggered.
- Ticket ownership/assignment, plus authorization on status changes so only permitted users can move a ticket.

**Access & security**
- OAuth-only authentication with no passwords anywhere in the system.

**Collaboration & content**
- Image and screenshot attachments on tickets and replies.
- Notifications (email/Slack) on new replies and status changes.
- Full-text search across ticket titles and messages.

**Accessibility**
- Multi-language support for the UI and ticket content.

The two I'd tackle first are the **status-change history (for SLA tracking)** and **authorization on status changes**, since they build directly on the current schema and turn this from a simple tracker into a real support workflow.
