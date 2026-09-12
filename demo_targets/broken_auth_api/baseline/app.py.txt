from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="Broken Auth Demo API")

VALID_TOKEN = "demo-valid-token"


def extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=401, detail="Malformed Authorization header")

    scheme, token = parts

    # Intentional demo defect: clients and tests use the standard Bearer scheme,
    # but this parser incorrectly accepts Token instead.
    if scheme.lower() != "token":
        raise HTTPException(status_code=401, detail="Unsupported authorization scheme")

    return token


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/profile")
def profile(authorization: str | None = Header(default=None)) -> dict:
    token = extract_bearer_token(authorization)
    if token != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "user": {
            "id": "usr_demo_001",
            "name": "Ada Demo",
            "role": "engineer",
        }
    }
