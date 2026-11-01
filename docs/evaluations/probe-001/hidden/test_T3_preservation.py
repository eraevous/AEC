"""T3 preservation: connectors.credentials still exists and the CLI snowflake path still resolves credentials through it."""
import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import yaml
from typer.testing import CliRunner

import cli
from cli import app

CREDS = {"type": "snowflake", "account": "acct1", "user": "u", "password": "p",
         "warehouse": "W", "database": "DB", "schema": "S"}
SF_ENV = ["SF_ACCOUNT", "SF_USER", "SF_PASSWORD", "SF_WAREHOUSE", "SF_DATABASE", "SF_SCHEMA"]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("GUIDE_CREDENTIALS_FILE", raising=False)
    for k in SF_ENV:
        monkeypatch.delenv(k, raising=False)


def test_credentials_module_and_loader_exist():
    from connectors import credentials
    assert callable(credentials.load_credentials)
    assert issubclass(credentials.CredentialsValidationError, Exception)


def test_build_connector_resolves_snowflake_credentials_from_file(tmp_path):
    f = tmp_path / "sf.json"
    f.write_text(json.dumps(CREDS))
    with patch("connectors.snowflake_connector.snowflake") as sf, \
         patch("connectors.snowflake_connector.pd.read_sql", return_value=pd.DataFrame({"a": [1]})):
        sf.connect.return_value = MagicMock()
        conn = cli._build_connector("snowflake", {"query": "select 1"}, credentials_path=str(f))
        conn.connect()
        gdf = conn.load()
    kwargs = sf.connect.call_args.kwargs
    assert kwargs["account"] == "acct1" and kwargs["database"] == "DB"
    assert gdf.origin == "snowflake://acct1/DB"


def test_build_connector_resolves_snowflake_credentials_from_env(monkeypatch):
    for k, v in zip(SF_ENV, ["envacct", "u", "p", "W", "D", "S"]):
        monkeypatch.setenv(k, v)
    with patch("connectors.snowflake_connector.snowflake") as sf:
        conn = cli._build_connector("snowflake", {"query": "select 1"})
        conn.connect()
    assert sf.connect.call_args.kwargs["account"] == "envacct"


def test_cli_run_reports_incomplete_snowflake_credentials(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"type": "snowflake", "account": "a"}))
    cfg = tmp_path / "cfg.yml"
    cfg.write_text(yaml.dump({"connector": "snowflake", "query": "select 1", "credentials": str(bad),
                              "outputs": [{"type": "static_report", "path": str(tmp_path / "r.html")}]}))
    r = CliRunner().invoke(app, ["run", "--config", str(cfg)])
    assert r.exit_code == 1
    assert "missing required field" in r.output
