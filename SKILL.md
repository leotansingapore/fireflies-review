---
name: fireflies-review
description: Turn a Fireflies.ai meeting recording into fixes that are live, a handover per person and a summary for the group. Use after a standup, review call or client meeting recorded by Fireflies, for requests like "review the standup", "check the Fireflies meeting with Sam", "what came out of today's call", or /fireflies-review.
---

# Fireflies meeting review

After a meeting, the person who asked for this review (the lead) wants three things: the bugs and asks that can be fixed today fixed and live, everyone else unblocked with a note they can paste into their own Claude session, and a short summary to post to the group. The value is in turning a vague verbal ask into a checked, specific change or instruction, so most of this skill is about checking before acting.

Restate progress on every turn ("step 3 of 8 done: X. Next: Y"). Do not stop for approval between steps; the hard stops in step 5 are the reasons to pause.

## Before you start

- Work out who the lead is. It is the user unless they say otherwise. Read their CLAUDE.md for their name and email, because Fireflies writes whatever name it hears and you need to recognise the lead in the transcript.
- Pick the output folder: the one the user names, else `$MEETING_REVIEW_DIR/<yyyy-mm-dd>-<slug>/` if that variable is set, else `./meeting-reviews/<yyyy-mm-dd>-<slug>/`. Working files (transcript, frames) go in a scratch folder, never in a notes vault or a repo.
- If the user's CLAUDE.md or a repo's CLAUDE.md has rules for commits, deploys, databases or writing, those win over this file wherever the two disagree.

## Step 1: find the meeting and pull everything

```bash
FF=<this skill's folder>/scripts/ff.py
W=<scratch folder>/meeting-<yyyymmdd>-<slug>
python3 $FF find "standup" --days 2          # or no keyword: the newest 10 meetings
python3 $FF fetch <ID> --out $W              # writes transcript.md and meta.json
```

- "Just now" or "last night" means the newest meeting that fits. A meeting is named after its calendar slot, so the people who actually spoke may not match the title. Check the speaker names in transcript.md before you rule a meeting out. If two meetings fit, take the newer one and say which you used.
- Fewer than 20 sentences means Fireflies is still processing. Wait a few minutes and fetch again.
- Read the whole transcript.md, not just the Fireflies summary at the top. Its action items often give a task to the wrong person, and its next steps miss asks made in passing.

## Step 2: know who is who

Fireflies writes the names it hears, and people join from accounts that are not on the invite. Map every speaker to a real person using the invite emails in transcript.md, `git log --since="14 days ago" --format="%an %ae" | sort | uniq -c` in each repo that came up, and any team notes the user keeps, then use those real names in every deliverable. Use they/them, or just names, for anyone whose pronouns you have not seen stated.

## Step 3: look at the screen

Transcripts lose whatever was on screen ("this one is still white", "why are there two of these"). For each moment like that, grab a frame and read it.

```bash
python3 $FF frames <ID> 35:30 43:46 1:02:10 --out $W
```

Timestamps are the transcript's (MM:SS or H:MM:SS from the start of the recording). Take the frame 2 or 3 seconds after the line, because presenters scroll as they talk. Ten to twenty targeted frames are usually enough; do not decode the whole video. If the meeting has no recording, say so and work from the transcript alone.

## Step 4: build the ask list

Write `$W/asks.md`: one line per ask, bug, blocker, decision or promise, each with an owner, a timestamp and the speaker's own words where they gave them. Then sort each line into one bucket:

- Fix now: concrete, checkable, inside a repo you can push to, and nobody is part-way through it.
- Owner's work in progress: someone said they are on it this week, or pushed to that area in the last day or two. Leave the code alone and put pointers in their handover.
- Lead decides: anything a reasonable person could go two ways on, plus every hard stop below.
- Waiting on someone outside: an app store review, a client's login, a vendor.

### Check that the ask is real before acting

This is where most of the value comes from. Before writing code for an ask, confirm it against the source of truth:

- Find the actual thing (the page, the record, the run, the error) in production, read-only, and quote it. A "bug" may be correct behaviour, and a "broken" feature may be a test site.
- Find the root cause: the line of code or the rule that produces what was on screen.
- Check facts the team is about to build on: what the code already does, which integrations exist, who owns the data. Half of what gets asked for in a meeting is already built and hard to find, and the right fix is often a link, a label or a menu entry.
- Read the area's recent history (`git log origin/main --since="8 days ago" -- <paths>`) and the open pull requests. If the owner pushed there today, it is in progress.
- Count before you claim. "Some leads have the wrong year" becomes "23 contacts on 2 boards", with the query that found them.

If someone said something on the call that turns out to be wrong, the lead included, say so plainly in the summary with the correct version.

## Step 5: make the fixes

For each repo with fix-now items:

1. Read the repo's CLAUDE.md sections on deploys, commits and the area you are touching, and follow them.
2. Work in a fresh worktree off `origin/main`, never in a shared checkout that other people or agents push from: `git worktree add --detach <dir> origin/main`.
3. Make the smallest complete change with a test that fails without it, and prove the test by breaking the change once and watching the test go red. If an existing test pins the old behaviour on purpose, read why before you change it, and say in the commit what changed.
4. Check it against the meeting's own example. If the meeting named a page, a record or a user, run the real code path on that case. Unit tests can all pass while the fix does nothing on the case that was shown on screen.
5. Run the typecheck, lint and build, and before blaming your change for a red check, see whether main is already red (`gh run list --branch main --limit 3`).
6. One logical change per commit, in the repo's message style. Rebase on origin/main right before you push. Confirm the deploy, not just the push: a push can succeed while the deploy is queued, cancelled or failing.

### Hard stops: hand these over or ask, never do them yourself

- Money and billing.
- Granting access or changing roles.
- Database schema changes, migrations, and writes to production data. Prepare the exact SQL with the row count and a backup step, put it in front of the lead, and run it only after an explicit yes.
- Adding a new dependency.
- Deleting or merging customer data.
- Anything sent to the team or to clients in the lead's name. Deliverables are drafts the lead sends.

## Step 6: file what is left

Put each open item where the team already tracks work: the repo's issues (`gh issue create`), the team's board, or the decisions page the repo keeps. Each item gets a title, an owner, the evidence with file paths, and whether it waits on the lead, and the ids go into the handovers. If the team tracks nothing, list the items at the end of the summary instead.

## Step 7: write the deliverables

In the output folder:

- `team-summary.md`: the message the lead posts to the group, in the lead's voice. For a one-to-one call it is the message the lead sends that one person.
- `handover-<firstname>.md`: one per attendee who has work, developers and non-developers alike.

Read `references/templates.md` for the structure of each before you write.

Write like a person. Plain words, short sentences, no headings with `#` in the summary, sentence case, ASCII punctuation. Leave out the usual tells of machine prose: bold labels at the start of list items, "it's not X, it's Y" flips, a long sentence followed by a short punchline, lists of sentence fragments, and words like "seamless", "robust", "leverage" or "delve". If the user has a prose linter, run it on every file and fix what it flags by rewriting the whole sentence. Check every number adds up ("four files" over a list of three is the slip a reader notices).

## Step 8: close out

Reply to the lead in this order:

1. One line naming the audience ("Written for: the dev team (summary) and each person's Claude session (handovers)").
2. What shipped, with commit ids, how each was checked, and whether the deploy is live.
3. What you found that changes plans, and the decisions waiting on the lead, numbered so they can answer by number.
4. Every message as a copy-paste block: the summary first, then one block per person. Fence each block with four backticks, because handovers contain triple-backtick code of their own.
5. The one next action, and one line on what you did not check.

If the user keeps notes or memory between sessions, save the meeting id, what shipped, where the deliverables are, and any trap worth knowing next time.

## Traps from past runs

- Skipping the frames. Half the asks in a standup are about something on screen.
- Trusting the meeting title, the Fireflies action items or the speaker names.
- Fixing what a teammate is building this week. Read their commits and open pull requests first.
- Building something that already exists. Search the code for the feature before writing it.
- Agreeing with a wrong statement because the lead made it on the call. Correct it in the summary.
- Leaving a chained shell command waiting on an interactive prompt (`git add -p`, `git checkout -p`). It hangs, and whatever ran before it stays half done.
- Writing deliverables into a notes vault or a repo instead of the output folder.
- Pushing from a shared checkout of a busy repo.
