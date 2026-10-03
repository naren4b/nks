# Zero Token Architecture: Reason Once, Automate What Repeats

Published: 2026-10-03

Repeated infrastructure checks need dependable execution. When inputs and
decisions are already defined, asking a model to rediscover the procedure on
every run adds a dependency that ordinary automation may not need.

Kelsey Hightower's *Zero Token Architecture* talk offers a useful starting
point: use inference to discover a solution, capture the understood procedure
as software, and run it without repeated inference.

!!! tip "The architecture decision"
    Decide which steps need new reasoning and which steps can execute known
    rules. Keep that boundary explicit.

## Separate Discovery from Execution

AI can help explore requirements, suggest an approach and draft code.
Engineering review turns that draft into an understood, tested procedure.
The reusable artifact belongs in version control, with an owner and a
maintenance path.

| Stage | Useful work | Review question |
| --- | --- | --- |
| Understand | Define inputs, decisions and failure modes | Can the engineer explain the task? |
| Explore | Use AI where reasoning or unfamiliar context helps | Are the assumptions visible? |
| Validate | Review logic, permissions and failure handling | Does the procedure behave as intended? |
| Execute | Run the reviewed code on a schedule or event | Are results and failures observable? |
| Revisit | Reassess changed requirements or unknown situations | Does the current procedure still apply? |

This approach can reduce repeated model calls for known procedures.
It does not establish a universal saving or make the remaining infrastructure
free. Compute, storage, networking, maintenance and engineering work still
have costs.

## An Infrastructure Health Report

Consider a daily report that checks CPU usage, disk capacity and certificate
expiry. The measurements change between runs, but the decision rules may
remain the same.

!!! note "Illustrative example"
    This is an architecture example, not a deployed system or a measured
    cost-saving result. The policy below illustrates inputs and decisions;
    it is not an executable monitoring configuration.

```yaml
checks:
  cpu:
    input: average_utilization_over_defined_window
    decision: compare_with_reviewed_threshold
  disk:
    input: available_capacity
    decision: compare_with_reviewed_capacity_policy
  certificate:
    input: days_until_expiry
    decision: compare_with_reviewed_renewal_window
```

AI may help draft the implementation. An engineer still reviews data
collection, thresholds, permissions and failure behavior before scheduling it.

The runtime procedure should collect the readings, apply the reviewed rules,
record the result and surface failures. An unavailable data source should be
reported as unknown or failed, rather than silently becoming a healthy result.

If the report itself does not call a model, those routine checks can continue
during a model-service outage, provided their other dependencies remain
available.

## Changing Inputs Do Not Always Change the Procedure

A larger fleet can produce more readings without requiring a fresh
architecture decision for every reading. A changing service inventory may be
handled through discovery and configuration when its structure is understood.

The important question is whether the change alters the rules.

| Change | First response |
| --- | --- |
| New readings in the same format | Execute the existing reviewed procedure |
| More targets using the same contract | Assess capacity and update discovery or configuration |
| A changed input schema or dependency | Review compatibility, update code and test |
| New requirements or reliability objectives | Revisit the policy and design |
| An unfamiliar failure with ambiguous evidence | Investigate; use fresh inference when it helps |

Infrequent execution does not by itself justify or rule out AI.
Compare the effort to maintain automation with the need for interpretation,
the consequences of a wrong action and the dependency budget.

## Keep the Engineering Responsibilities

Reusable automation still needs tests, versioned changes, suitable access,
execution records and clear failure handling. Automated actions also need an
appropriate review boundary and a recovery path.

Before adopting generated code, an engineer should be able to explain:

- What goes in, what comes out and which decisions the code makes.
- What happens when inputs are incomplete or a dependency fails.
- Which permissions and actions are necessary.
- How to test a change and maintain the procedure without the original tool.

A useful AI-assisted workflow preserves that understanding. As requirements
change, revisit the design, validate the delta and release a reviewed update.

## Takeaway

Understand the task. Validate the solution. Automate what repeats.
Reserve new inference for the steps that benefit from new interpretation.

## Source

Inspired by [Kelsey Hightower's Zero Token Architecture talk, PlatformCon 2026](https://www.youtube.com/watch?v=A7WFt2JQ5sg).
The companion LinkedIn post and supplied transcript informed this explanation.
The infrastructure example and review tables are an interpretation of the
principle, not reported implementation results.
