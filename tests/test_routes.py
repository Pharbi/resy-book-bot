import sys
import types
import importlib
from flask import Flask, Response
import pytest


# helper fixture to create fake 'app' package with required attributes
@pytest.fixture
def fake_app(monkeypatch):
    fake_app = types.ModuleType("app")
    fake_app.__path__ = []
    fake_app.logger = None
    fake_app.bot_domain = "example.com"
    fake_app.account_handler = types.SimpleNamespace(
        get_resy_token=lambda uid: "token", remove_resy_token=lambda uid: None
    )
    fake_app.task_handler = types.SimpleNamespace()
    fake_app.resy_client = types.SimpleNamespace(
        auth_check=lambda payload: Response(status=200)
    )

    forms_pkg = types.ModuleType("app.forms")
    forms_pkg.__path__ = []
    rf = types.ModuleType("app.forms.resy_form")

    class ResyTokenForm:
        pass

    rf.ResyTokenForm = ResyTokenForm
    uf = types.ModuleType("app.forms.user_account_forms")

    class RegistrationForm:
        pass

    uf.RegistrationForm = RegistrationForm
    forms_pkg.resy_form = rf
    forms_pkg.user_account_forms = uf

    routes_pkg = types.ModuleType("app.routes")
    routes_pkg.__path__ = ["backend/app/routes"]

    modules = {
        "app": fake_app,
        "app.forms": forms_pkg,
        "app.forms.resy_form": rf,
        "app.forms.user_account_forms": uf,
        "app.routes": routes_pkg,
    }
    for name, mod in modules.items():
        sys.modules[name] = mod

    yield fake_app

    for name in modules.keys():
        sys.modules.pop(name, None)


def create_app(module_path):
    mod = importlib.import_module(module_path)
    name = module_path.split(".")[-1]
    blueprint = getattr(mod, f"{name}_bp", None)
    if blueprint is None:
        for candidate in [
            "resy_bp",
            "user_bp",
            "resy_bot_bp",
            "base_bp",
            "meta_bp",
        ]:
            if hasattr(mod, candidate):
                blueprint = getattr(mod, candidate)
                break
    if blueprint is None:
        raise AttributeError(f"No blueprint found in {module_path}")
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    return app


def test_search_requires_auth(fake_app):
    app = create_app("app.routes.resy_interactions")
    client = app.test_client()
    resp = client.post("/resy/search")
    assert resp.status_code == 403


def test_check_token_success(fake_app):
    fake_app.resy_client.auth_check = lambda payload: Response(status=200)
    app = create_app("app.routes.user")
    client = app.test_client()
    resp = client.get("/user/check-token", query_string={"userId": "1"})
    assert resp.status_code == 200


def test_check_token_failure(fake_app):
    removed = {}

    def remove(uid):
        removed["uid"] = uid

    fake_app.account_handler.remove_resy_token = remove
    fake_app.resy_client.auth_check = lambda payload: Response(status=500)
    app = create_app("app.routes.user")
    client = app.test_client()
    resp = client.get("/user/check-token", query_string={"userId": "1"})
    assert resp.status_code == 401
    assert removed["uid"] == "1"

def test_venue_details_requires_auth(fake_app):
    app = create_app("app.routes.resy_interactions")
    client = app.test_client()
    resp = client.get("/resy/venue-details")
    assert resp.status_code == 403

