# Lakebase Homework Grade

**Final Score:** 96/100

---

## Rubric Breakdown


Rubric Breakdown


| **Category**               | **Score** | **Maximum** | **Feedback** |
|----------------------------|-----------|-------------|--------------|
| Lakebase schema            | 20        | 20          | Well-designed two-table schema with primary keys, FK via `ticketid`, and useful `CHECK` constraints shown in README; app code consistently targets these tables and columns. |
| Sample data                | 6         | 10          | Screenshots are linked but not accessible here; cannot fully verify ≥3 tickets and ≥2 messages per ticket. Partial credit awarded based on provided links and multi-status workflow implied by the UI and code. |
| Reading from Lakebase      | 20        | 20          | Tickets and ticket messages are read via explicit SQL `SELECT`s (`lakebase.py`, `app.py`), rendered in the SPA; clear evidence of querying Lakebase (no hard-coded data). |
| Creating data              | 20        | 20          | `POST /tickets` and `POST /tickets/{id}/messages` insert into Lakebase with commits; UI calls these endpoints; implementation is sound and consistent with schema. |
| Updating ticket status     | 10        | 10          | `POST /tickets/{id}/status` updates Lakebase; UI provides dropdown + update button; persistence path implemented. |
| Deployment                 | 10        | 10          | Deployed via Databricks Apps (`app.yaml` provided) and an Apps URL is included; a deployment screenshot is linked. Credible evidence of successful deployment. |
| Submission and reflection  | 10        | 10          | All five items provided: App URL, repo URL, app screenshot, Lakebase screenshots, and a reflection addressing the prompts (with “featuresnext.md” referenced for next steps). |

---

## What You Did Well

- **Solid, production-minded schema and API design**: Including `CHECK` constraints, identity resolution, validation, and clear separation of DB access in `lakebase.py`.
- **Complete functionality**: Viewing tickets and messages, creating tickets, adding messages, updating status, plus useful bonus features (priorities, filtering, and a stats dashboard).
- **Secure configuration**: Uses Databricks Secrets to retrieve a base64-encoded Postgres URL; no credentials committed.

---

## What to Improve

- Provide **accessible proof** of sample data requirements (≥3 tickets, ≥2 messages per ticket, ≥2 statuses) with query results or screenshots that show counts clearly; consider adding a small seed script or SQL snippet plus output.
- Ensure all linked screenshots are **reliably accessible** to graders; adding a brief screen capture (GIF/MP4) demonstrating create/reply/status-update with a refresh would remove any doubt about persistence.
- **Minor polish**: Include a DDL/migration script in the repo (e.g., `schema.sql`) to let reviewers reproduce the tables exactly as used by the app.

---

## Instructor Summary

Excellent end-to-end implementation of a Lakebase-backed Databricks App with clean API endpoints, a responsive SPA, and thoughtful extras like filtering and a dashboard. The code clearly queries and writes to Lakebase, and deployment evidence is strong. The only gap is verifiable evidence of the required sample data volume; providing query outputs or accessible screenshots would make the submission airtight. Overall, this is a **robust and well-structured solution**.

---

## Evidence Limitations

- App URL may be **workspace-restricted** and not directly accessible.
- Linked screenshots for the deployed app and Lakebase tables/records were not accessible here, so sample data counts could not be verified.

---
## Security Check

✅ **No exposed credentials or secrets detected.** The repository uses Databricks Secrets and documents secure handling of the Lakebase connection URL without revealing values.

---
## Unsupported Files

The following files were not recognized (unsupported formats):
- `.pyc`, `.orighead`, `.config`, `.head`, `.description`, `.index`, `.packed-refs`, `.commiteditmsg`, `.fetchhead`, `.exclude`, `.sample`, `.pack`, `.idx`, `.rev`, and other Git/internal files.

> **Note:** For grading, supported formats are:
> - Documents: `.pdf`, `.txt`, `.md`, `.rtf`
> - Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`
> - Submission: `.zip` or a single image.

---
*DataExpert.io Community Academy*
*[Unsubscribe](link) · [Email preferences](link)*
*[Download your feedback as PDF](link)*
