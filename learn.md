# Lakebase project

A Lakebase project is the closest analog to "a server": it's the hard boundary. Each project has its own roles, its own set of databases, its own compute, and you can't casually cross-query from one project into another, just like two separate Postgres servers. If your mental model is "separate project = separate server instance," that'll steer you correctly for deciding *when* to create one.

But the analogy breaks in three ways that are worth knowing, because a project is actually more capable than a server:

**Compute and storage are decoupled.** On a traditional server, the CPU/RAM and the disk are the same box—if the box is off, nothing runs and nothing is reachable. Lakebase (built on Neon's architecture) splits these: the project holds your *storage*, and *compute endpoints* are separate, elastic things that can autoscale and even scale to zero when idle. So "the server" isn't one fixed machine—it's storage that compute attaches to on demand. This is why you saw autoscaling in the product name.

**Branching.** A project isn't a single copy of your data—it can have multiple *branches* (you're on `production`), and each branch is a near-instant copy-on-write clone of the data. There's no server equivalent to this; it's closer to git branches for your database. You'd branch to test a migration against real data without touching production.

**Multiple computes can share one dataset.** You can point several compute endpoints at the same branch for read scaling, without duplicating the data. On a classic single server, scaling reads means replicas and copying data around.

One correction to the ladder I gave you earlier, now that this matters: databases don't sit directly under the project—they sit under a **branch**. The real nesting is:

**Project → Branch → (Computes + Roles + Databases) → Schemas → Tables**

So "multiple databases in one project" more precisely means multiple databases in a *branch* of a project. For your tutorial that's all invisible—you're in project `ticketing`, branch `production`, database `databricks_postgres`, schema `public`—but it's why a Lakebase project is best thought of as "a server, plus elastic compute, plus git-style branching," rather than a plain server.
