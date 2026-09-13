import os
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class DeploymentContractTests(unittest.TestCase):
    def test_required_forgeops_assets_exist(self):
        for relative in (
            "Dockerfile",
            "docker-compose.yml",
            ".github/workflows/ci.yml",
            ".github/workflows/deploy.yml",
            "ops/deploy-ontology.sh",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_runtime_can_bind_inside_container(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('os.getenv("APP_HOST", "127.0.0.1")', source)
        self.assertIn('os.getenv("APP_PORT", "8000")', source)

    def test_deployment_has_health_check_and_no_force_push(self):
        workflow = (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8")
        script = (ROOT / "ops/deploy-ontology.sh").read_text(encoding="utf-8")
        self.assertIn("/api/health", script)
        self.assertIn("--no-build --pull never", script)
        self.assertNotIn("git push --force", workflow)
        self.assertTrue(os.access(ROOT / "ops/deploy-ontology.sh", os.R_OK))


if __name__ == "__main__":
    unittest.main()

