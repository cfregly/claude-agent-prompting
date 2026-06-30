import unittest

from claude_agent_harness_opt.value_bar import evaluate_value_bar


class ValueBarTests(unittest.TestCase):
    def test_value_bar_passes_with_adversarial_confirmation(self):
        result = evaluate_value_bar(
            {
                "adversarial_review": {
                    "challenge": "Known-bad traces must fail and known-good traces must pass.",
                    "failed_to_disprove": True,
                    "open_objections": [],
                },
                "baseline": {"score": 0.4},
                "candidate": {"score": 0.9},
                "claim": "The new prompt improves trace quality.",
                "metric": "trace_review.score",
                "minimum_delta": 0.2,
            }
        )
        self.assertTrue(result.passed)
        self.assertEqual(1.0, result.score)

    def test_value_bar_fails_without_adversarial_confirmation(self):
        result = evaluate_value_bar(
            {
                "adversarial_review": {
                    "challenge": "Known-bad traces must fail.",
                    "failed_to_disprove": False,
                    "open_objections": ["candidate only passed easy traces"],
                },
                "baseline": {"score": 0.8},
                "candidate": {"score": 0.85},
                "claim": "The new prompt improves trace quality.",
                "metric": "trace_review.score",
                "minimum_delta": 0.2,
            }
        )
        self.assertFalse(result.passed)
        self.assertLess(result.score, 1.0)

    def test_value_bar_fails_without_crashing_on_malformed_scores(self):
        result = evaluate_value_bar(
            {
                "adversarial_review": {
                    "challenge": "Malformed evidence should be reported, not crash the audit.",
                    "failed_to_disprove": True,
                    "open_objections": [],
                },
                "baseline": "old prose-only baseline",
                "candidate": {"score": "high"},
                "claim": "The matrix adds value.",
                "metric": "model_matrix.score",
                "minimum_delta": "some improvement",
            }
        )

        self.assertFalse(result.passed)
        self.assertIn("baseline score must be numeric", result.details)
        self.assertIn("candidate score must be numeric", result.details)
        self.assertIn("minimum_delta must be numeric", result.details)


if __name__ == "__main__":
    unittest.main()
