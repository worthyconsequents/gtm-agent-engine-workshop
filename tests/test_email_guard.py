import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTests(unittest.TestCase):
    def test_disqualified_prospect_is_blocked(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-50001",
                "email": "priya.nair@brightwaveapps.com",
            },
            "A subject",
            "A body",
            runtime=None,
            from_rep={"email": "rep@example.com", "name": "Rep"},
        )

        self.assertEqual(
            result,
            {"status": "blocked", "error": "Prospect is disqualified; email not sent."},
        )

    def test_forged_eligibility_fields_do_not_bypass_guard(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-50001",
                "name": "Forged Name",
                "email": "forged@example.com",
                "disqualified": False,
            },
            "A subject",
            "A body",
            runtime=None,
            from_rep={"email": "rep@example.com", "name": "Rep"},
        )

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["error"], "Prospect is disqualified; email not sent.")

    def test_non_disqualified_prospect_is_sent(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-39002",
                "email": "chloe.rodriguez@westwindcloud.com",
                "name": "Chloe Rodriguez",
            },
            "A subject",
            "A body",
            runtime=None,
            from_rep={"email": "rep@example.com", "name": "Rep"},
        )

        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["to"], "chloe.rodriguez@westwindcloud.com")


if __name__ == "__main__":
    unittest.main()
