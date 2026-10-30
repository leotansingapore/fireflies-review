# fireflies-review

A Claude Code skill for the hour after a meeting. Point it at a Fireflies.ai recording and Claude reads the whole transcript, looks at what was on screen, checks every ask against the real code and data, fixes what it safely can, and writes a summary for the group plus a handover for each person's own Claude session.

It was built for a small team that runs its standups and review calls on Fireflies and ships to production several times a day. It has been used on dev standups, SEO team meetings and one-to-one review calls.

## What you get from one run

- Fixes that are live. Each comes as its own commit with a test that fails without it, checked against the example from the meeting, with the deploy confirmed.
- A summary in your voice, ready to post: what changed, what turned out to be different from what was said, and what you need from each person.
- A handover per attendee. Developers get commit ids, file paths and traps. Writers, ops and sales get a note and a prompt they can reuse.
- A numbered list of decisions only you can make, with the evidence for each.

## What it will not do on its own

It stops and asks before anything to do with money or billing, access grants, schema changes or writes to production data, new dependencies, or deleting customer data. It never sends anything in your name. The summary and handovers are drafts you send yourself.

## Install

You need Claude Code, Python 3.8 or newer (standard library only), `git`, and `ffmpeg` if you want frames from the video.

```bash
git clone https://github.com/leotansingapore/fireflies-review ~/.claude/skills/fireflies-review
```

Get your Fireflies API key from Settings > Developer settings in Fireflies, and put it in your shell profile:

```bash
export FIREFLIES_API_KEY=your-key-here
```

## Use

In Claude Code:

```
/fireflies-review the dev standup just now
/fireflies-review last night's call with Sam
```

Or say it in plain words, like "check the Fireflies meeting from this morning". Claude finds the meeting, works through the eight steps in `SKILL.md`, and reports progress as it goes.

Deliverables land in `./meeting-reviews/<date>-<slug>/`. Set `MEETING_REVIEW_DIR` to put them somewhere else.

The helper script also works on its own:

```bash
python3 scripts/ff.py find standup --days 2             # recent meetings, newest first
python3 scripts/ff.py fetch <id> --out /tmp/meeting     # transcript.md and meta.json
python3 scripts/ff.py frames <id> 12:30 1:02:10 --out /tmp/meeting
```

`frames` pulls one 1280px still per timestamp straight from the recording, without downloading the whole video. A meeting with no video says so, and the review carries on from the transcript.

## Make it yours

Everything is in two plain files. `SKILL.md` holds the steps, the hard stops and the traps. `references/templates.md` holds the shape of the summary and the handovers. Rules in your own `CLAUDE.md` or a repo's `CLAUDE.md` override the skill, so put your commit style, deploy steps and issue tracker there. If you use a prose linter, mention it in `CLAUDE.md` and the skill runs it on every deliverable.

## Tests

```bash
python3 -m unittest discover tests
```

The tests run offline against a fake transcript.

## License

MIT
