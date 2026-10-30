"""Offline checks for scripts/ff.py. Run: python3 -m unittest discover tests"""
import json
import os
import sys
import tempfile
import unittest
from argparse import Namespace
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import ff  # noqa: E402

FAKE = {
    "id": "abc123", "title": "Weekly standup", "date": 1793282400000, "duration": 31.6,
    "participants": ["sam@example.com", "alex@example.com"], "organizer_email": "sam@example.com",
    "video_url": "https://example.com/video.mp4", "transcript_url": None,
    "summary": {"overview": "Talked about the release.", "action_items": "Alex: ship it"},
    "sentences": [
        {"speaker_name": "Sam", "text": "Morning.", "start_time": 3},
        {"speaker_name": "Sam", "text": "Where are we on the release?", "start_time": 5},
        {"speaker_name": "Alex", "text": "Blocked on the login bug.", "start_time": 3725},
    ],
}


class FetchTest(unittest.TestCase):
    def test_groups_lines_by_speaker_and_stamps_each_turn(self):
        with tempfile.TemporaryDirectory() as out, mock.patch.object(ff, "gql", return_value={"transcript": FAKE}):
            ff.cmd_fetch(Namespace(id="abc123", out=out))
            md = open(os.path.join(out, "transcript.md")).read()
            meta = json.load(open(os.path.join(out, "meta.json")))
        self.assertIn("**Sam** (00:03)\nMorning.\nWhere are we on the release?", md)
        self.assertIn("**Alex** (01:02:05)\nBlocked on the login bug.", md)
        self.assertIn("- Invite emails: sam@example.com, alex@example.com", md)
        self.assertEqual(meta["speakers"], ["Alex", "Sam"])
        self.assertEqual(meta["sentence_count"], 3)

    def test_warns_when_fireflies_is_still_processing(self):
        short = dict(FAKE, sentences=FAKE["sentences"][:1])
        with tempfile.TemporaryDirectory() as out, mock.patch.object(ff, "gql", return_value={"transcript": short}), \
                mock.patch("builtins.print") as printed:
            ff.cmd_fetch(Namespace(id="abc123", out=out))
        self.assertTrue(any("still be processing" in str(c) for c in printed.call_args_list))


class FramesTest(unittest.TestCase):
    def test_refuses_a_timestamp_that_is_not_mm_ss(self):
        with tempfile.TemporaryDirectory() as out, mock.patch.object(ff, "gql", return_value={"transcript": FAKE}), \
                mock.patch("subprocess.Popen") as popen:
            with self.assertRaises(SystemExit):
                ff.cmd_frames(Namespace(id="abc123", times=["90s"], out=out))
            popen.assert_not_called()


class KeyTest(unittest.TestCase):
    def test_missing_key_exits_with_instructions(self):
        with mock.patch.dict(os.environ, {"FIREFLIES_API_KEY": ""}):
            with self.assertRaises(SystemExit) as e:
                ff.api_key()
        self.assertIn("export FIREFLIES_API_KEY", str(e.exception))


if __name__ == "__main__":
    unittest.main()
