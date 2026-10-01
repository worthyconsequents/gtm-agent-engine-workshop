import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


class ProspectInfoTest(unittest.TestCase):
    def setUp(self):
        self.prospect_id = "LEAD-39002"
        self.record = data_service.PROSPECTS[self.prospect_id]
        self.original_tech_stack = list(self.record["tech_stack"])
        data_service._PROFILES.pop(self.prospect_id, None)

    def tearDown(self):
        self.record["tech_stack"] = self.original_tech_stack
        data_service._PROFILES.pop(self.prospect_id, None)

    def test_update_persists_and_invalidates_cached_profile(self):
        cached = build_prospect_profile.invoke({"prospect_id": self.prospect_id})
        self.assertNotIn("Terraform", cached["prospect_profile"]["tech_stack"])

        result = data_service.update_prospect_info(self.prospect_id, "Terraform")

        self.assertTrue(result["updated"])
        self.assertIn("Terraform", data_service.fetch_tech_stack(self.prospect_id))
        profile = build_prospect_profile.invoke({"prospect_id": self.prospect_id})
        self.assertIn("Terraform", profile["prospect_profile"]["tech_stack"])

        duplicate = data_service.update_prospect_info(self.prospect_id, "Terraform")

        self.assertFalse(duplicate["updated"])
        self.assertEqual(
            data_service.fetch_tech_stack(self.prospect_id).count("Terraform"),
            1,
        )


if __name__ == "__main__":
    unittest.main()
