import unittest

from notifier.renderer import (
    DEFAULT_FAILED_TEMPLATE,
    DEFAULT_SUCCESS_TEMPLATE,
    FAILED_LABEL,
    SUCCESS_LABEL,
    render_message,
)


class RendererTests(unittest.TestCase):
    def test_default_success_template_contains_success_label(self) -> None:
        message = render_message(
            DEFAULT_SUCCESS_TEMPLATE,
            summary="ok",
            reason="",
            status="success",
        )
        self.assertIn(SUCCESS_LABEL, message)
        self.assertIn("ok", message)

    def test_default_failed_template_contains_failed_label(self) -> None:
        message = render_message(
            DEFAULT_FAILED_TEMPLATE,
            summary="",
            reason="boom",
            status="failed",
        )
        self.assertIn(FAILED_LABEL, message)
        self.assertIn("boom", message)

    def test_custom_template_can_place_label_anywhere(self) -> None:
        message = render_message(
            "状态={status} | {summary} | {label}",
            summary="hello",
            reason="",
            status="success",
        )
        self.assertEqual(f"状态=success | hello | {SUCCESS_LABEL}", message)


if __name__ == "__main__":
    unittest.main()
