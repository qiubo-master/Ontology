import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class DeploymentContractTests(unittest.TestCase):
    def test_required_forgeops_assets_exist(self):
        for relative in (
            "Dockerfile",
            "docker-compose.yml",
            ".github/workflows/ci.yml",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_runtime_can_bind_inside_container(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('os.getenv("APP_HOST", "127.0.0.1")', source)
        self.assertIn('os.getenv("APP_PORT", "8000")', source)

    def test_ci_has_no_production_secrets(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertNotIn("DEPLOY_SSH_KEY", workflow)
        self.assertNotIn("TS_OAUTH_SECRET", workflow)
        self.assertIn("docker build", workflow)


if __name__ == "__main__":
    unittest.main()
