import unittest

from ontology.catalog import CAPABILITIES, INTENTS, OBJECT_TYPES, RULES
from ontology.runtime import OntologyRuntime


class RuntimeTests(unittest.TestCase):
    def setUp(self): self.runtime = OntologyRuntime()

    def test_catalog_scope(self):
        self.assertEqual(len(INTENTS), 20)
        self.assertEqual(len(CAPABILITIES), 13)
        self.assertEqual(len(OBJECT_TYPES), 10)
        self.assertGreaterEqual(len(RULES), 5)

    def test_recommendation_is_grounded(self):
        result = self.runtime.handle_message("s1", "C1001", "我的宝马3系想换轮胎，推荐静音的")
        self.assertEqual(result["capability"]["id"], "RecommendTire")
        self.assertTrue(result["evidence"])
        self.assertGreaterEqual(len(result["tool_results"]), 2)
        self.assertIsNone(result["action"])

    def test_every_answer_contains_auditable_decision_inputs_and_outputs(self):
        result = self.runtime.handle_message("trace-session", "C1001", "查订单 SO20260001")
        steps = result["decision_steps"]
        self.assertEqual(len(steps), 7)
        self.assertEqual([step["order"] for step in steps], list(range(1, 8)))
        self.assertEqual(steps[0]["input"]["query"], "查订单 SO20260001")
        self.assertEqual(steps[0]["output"]["intent_id"], "03-01")
        self.assertEqual(steps[3]["output"]["calls"][0]["tool"], "GetOrder")
        self.assertEqual(steps[-1]["output"]["response"], result["response"])
        for step in steps:
            self.assertEqual(step["status"], "completed")
            self.assertIn("input", step)
            self.assertIn("output", step)
            self.assertGreaterEqual(step["duration_ms"], 1)

    def test_cancel_action_requires_confirmation(self):
        result = self.runtime.handle_message("s2", "C1001", "取消预约 AP20260001")
        self.assertEqual(result["intent"]["intent_id"], "03-03")
        self.assertEqual(result["action"]["status"], "proposed")
        confirmed = self.runtime.confirm_action(result["action"]["id"])
        self.assertEqual(confirmed["status"], "executed")
        self.assertEqual(self.runtime.tools.appointments["AP20260001"]["status"], "CANCELLED")

    def test_high_risk_review_then_execute(self):
        result = self.runtime.handle_message("s3", "C1001", "我要投诉门店态度很差")
        self.assertEqual(result["risk"], "L4")
        self.assertEqual(len(self.runtime.store.reviews), 0)
        confirmed = self.runtime.confirm_action(result["action"]["id"])
        self.assertEqual(confirmed["status"], "pending_review")
        review_id = confirmed["action"]["review_id"]
        review = self.runtime.decide_review(review_id, "approved")
        self.assertEqual(review["status"], "approved")
        self.assertEqual(self.runtime.store.actions[result["action"]["id"]]["status"], "executed")

    def test_unknown_query_asks_for_clarification(self):
        result = self.runtime.handle_message("s4", "C1001", "阿巴阿巴")
        self.assertTrue(result["needs_clarification"])


if __name__ == "__main__": unittest.main()
