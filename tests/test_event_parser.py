import json
import unittest

from notifier.event_parser import parse_event


class EventParserTests(unittest.TestCase):
    def test_stop_event_notifies(self) -> None:
        reason, summary, notify = parse_event(
            json.dumps(
                {
                    "hook_event_name": "Stop",
                    "stop_reason": "end_turn",
                    "transcript_path": "",
                }
            )
        )
        self.assertEqual("end_turn", reason)
        self.assertEqual("", summary)
        self.assertTrue(notify)

    def test_subagent_stop_is_ignored(self) -> None:
        reason, summary, notify = parse_event(
            json.dumps(
                {
                    "hook_event_name": "SubagentStop",
                    "stop_reason": "end_turn",
                    "transcript_path": "/tmp/none",
                }
            )
        )
        self.assertEqual("done", reason)
        self.assertEqual("", summary)
        self.assertFalse(notify)

    def test_error_occurred_recoverable_is_ignored(self) -> None:
        reason, summary, notify = parse_event(
            json.dumps(
                {
                    "hook_event_name": "ErrorOccurred",
                    "recoverable": True,
                    "error": {"name": "TimeoutError", "message": "network timeout"},
                }
            )
        )
        self.assertEqual("error", reason)
        self.assertIn("TimeoutError", summary)
        self.assertIn("network timeout", summary)
        self.assertFalse(notify)

    def test_error_occurred_unrecoverable_notifies(self) -> None:
        reason, summary, notify = parse_event(
            json.dumps(
                {
                    "hook_event_name": "ErrorOccurred",
                    "recoverable": False,
                    "error": {"name": "RuntimeError", "message": "fatal"},
                }
            )
        )
        self.assertEqual("error", reason)
        self.assertIn("RuntimeError", summary)
        self.assertIn("fatal", summary)
        self.assertTrue(notify)

    def test_session_end_complete_notifies(self) -> None:
        reason, summary, notify = parse_event(
            json.dumps(
                {
                    "hook_event_name": "SessionEnd",
                    "reason": "complete",
                    "finalMessage": "all done",
                }
            )
        )
        self.assertEqual("complete", reason)
        self.assertEqual("all done", summary)
        self.assertTrue(notify)

    def test_session_end_error_is_ignored_to_avoid_duplicate(self) -> None:
        reason, summary, notify = parse_event(
            json.dumps(
                {
                    "hook_event_name": "SessionEnd",
                    "reason": "error",
                    "finalMessage": "failed",
                }
            )
        )
        self.assertEqual("error", reason)
        self.assertEqual("", summary)
        self.assertFalse(notify)


if __name__ == "__main__":
    unittest.main()
