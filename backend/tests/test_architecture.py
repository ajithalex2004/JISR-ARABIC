"""Regression checks for the approved, behavior-preserving service extraction."""
import ast
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.modules.curriculum import audio


class TestArchitecture(unittest.TestCase):
    def test_services_do_not_depend_on_http_adapters(self):
        modules = Path(__file__).resolve().parents[1] / "modules"
        for path in modules.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                elif isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                else:
                    continue
                for name in names:
                    self.assertFalse(
                        name.startswith(("fastapi", "starlette", "backend.routes", "backend.api")),
                        f"{path.name} imports HTTP layer {name}",
                    )

    def test_services_receive_database_sessions_explicitly(self):
        from inspect import Parameter, signature
        from backend.modules.identity import service as identity
        from backend.modules.assessment import attempts
        from backend.modules.billing import service as billing
        from backend.modules.progress import reporting
        from backend.modules.tutoring import service as tutoring
        from backend.modules.curriculum import service as curriculum
        for operation in (
            identity.login, attempts.submit_attempt, billing.checkout_term,
            reporting.get_parent_dashboard, tutoring.submit_for_tutor,
            curriculum.get_lesson_content,
        ):
            self.assertIs(signature(operation).parameters["db"].default, Parameter.empty)

    def test_missing_authorization_preserves_http_error(self):
        # No lifespan/startup: this check must not run migrations or seeding.
        client = TestClient(app)
        response = client.get("/api/auth/me")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Missing or invalid authentication token"})

    def test_file_not_found_preserves_http_error(self):
        client = TestClient(app)
        response = client.get("/api/admin/page-image/999999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Page image not found"})

    def test_scanned_page_still_resolves_from_project_root(self):
        from backend.modules.curriculum.authoring import get_page_image
        folder = Path(__file__).resolve().parents[2] / "pdf_pages_sample"
        sample = next(folder.glob("page_*.png"), None)
        if sample is None:
            self.skipTest("No scanned page fixture available")
        page = int(sample.stem.removeprefix("page_"))
        self.assertEqual(Path(get_page_image(page)).resolve(), sample.resolve())
        response = TestClient(app).get(f"/api/admin/page-image/{page}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/png")
        self.assertEqual(response.content, sample.read_bytes())

    def test_query_defaults_and_overrides_survive_extraction(self):
        client = TestClient(app)
        response = client.get("/api/audio/synthesize", params={"text": "مرحبا"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), audio.synthesize_audio(text="مرحبا"))
        response = client.get(
            "/api/audio/synthesize",
            params={"text": "مرحبا", "speed": 0.6, "lang": "ar-AE"},
        )
        self.assertEqual(response.json(), audio.synthesize_audio(text="مرحبا", speed=0.6, lang="ar-AE"))
        self.assertEqual(client.get("/api/audio/synthesize").status_code, 422)
