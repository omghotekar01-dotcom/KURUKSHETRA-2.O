from app.services import github_client


def test_write_readiness_confirms_push_without_exposing_token(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_ALLOWED_REPOSITORIES", "owner/repo")
    monkeypatch.setenv("GITHUB_TOKEN", "super-secret-test-token")

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"permissions": {"pull": True, "push": True}}

    def fake_get(url, *, headers, timeout, follow_redirects):
        assert url.endswith("/repos/owner/repo")
        assert headers["Authorization"].startswith("Bearer ")
        assert timeout == 6.0
        assert follow_redirects is True
        return FakeResponse()

    monkeypatch.setattr(github_client.httpx, "get", fake_get)
    result = github_client.github_write_readiness("owner/repo")
    assert result["status"] == "READY"
    assert result["write_access"] is True
    assert result["auth_source"] == "ENV_TOKEN"
    assert "super-secret" not in str(result)


def test_write_readiness_reports_auth_required_without_credentials(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_ALLOWED_REPOSITORIES", "owner/repo")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("ALLOW_GH_CLI_AUTH", "false")

    result = github_client.github_write_readiness("owner/repo")
    assert result["status"] == "AUTH_REQUIRED"
    assert result["write_access"] is False


def test_write_readiness_blocks_non_allowlisted_repository(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_ALLOWED_REPOSITORIES", "owner/repo")

    result = github_client.github_write_readiness("someone/other")
    assert result["status"] == "BLOCKED"
    assert result["write_access"] is False
