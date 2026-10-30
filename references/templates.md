# Templates for fireflies-review deliverables

## team-summary.md (the group message)

The lead posts this themselves, so it is in their voice: first person, plain, warm but direct, short sentences, no `#` headings, plain section labels on their own line. About 300 to 550 words.

```
Hi all, here's what came out of today's <team> standup and what's already changed.

The priority: <the lead's main message from the meeting, in one or two sentences>.

Changed today (live on <product>)
- <What a user of the product now sees, in their words. Before and after, no function or file names.>

What I found after the meeting
- <Facts that change someone's plan: a wrong assumption, something already built, a red check and whose it is.>
- <Anything waiting on the lead, said as "I'll decide X, so please don't Y yet.">

What I need from each of you
- <Name>: <their two or three items, outcome first>.

I'm sending each of you a note to paste into your Claude session.
```

Rules that matter here:
- Name what changed for the user, never the function or the file.
- Every claim about data is something you checked in step 4, with the number.
- Credit and blame by fact ("two from Sam, one from Alex"), never by tone.
- If someone said something on the call that turned out wrong, the lead included, correct it here in one plain sentence.

## handover-<name>.md (developer)

Written for their Claude Code session, which starts cold. It needs file paths, commit ids, the reasons and the traps. It does not need encouragement.

```
# Handover for <Name>'s Claude sessions: <Product>, <d Mon yyyy>

Paste this into a new Claude Code session in the <repo> repo before you start. It comes from <Lead>'s session, which went through the <date> <meeting> recording and pushed <N> changes to main the same day.

## What changed on main today
<For changes in their area: commit id, what it does, the main files and functions, how it was checked, what is still not covered. For changes outside their area: one sentence each, saying they do not touch their code.>

## Fix first: <only if something of theirs is red or broken>

## Your items from the meeting
1. <Item title in plain text, no bold>. <The lead's words in quotes when they gave a direction.> <Where the code is, what already exists to reuse, the trap, the issue or card id.>
   - <Sub-points only when they are separate facts.>

## Working rules in this repo
<One paragraph: pull and rebase before each change and each push, one commit per push, never force-push, how deploys happen, how to test signed in, and any repo-specific gate.>
```

## handover-<name>.md (non-developer: writer, ops, sales)

Two parts. Part 1 is a note to the person: what the lead asked of them, the answer to anything they raised (what you found when you checked it), and exactly where in the product to do the thing (menu path, field name, character limit). Part 2 is a ready prompt they paste into Claude for the recurring task they do by hand today (reviewing an article, checking a report, drafting a reply), with bracketed slots for their inputs and an instruction to report sentences, rules and suggested rewrites rather than rewriting everything. Close with how to pass what Claude finds to the developer who owns the fix.
