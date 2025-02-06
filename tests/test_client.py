import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from httpx import Response
from audiokit import AudioKit
from audiokit.errors import APIError, AuthError, ValidationError

@pytest.fixture
def mock_client():
    return AudioKit(api_url="http://test.com")

@pytest.mark.asyncio
async def test_analyze_success(mock_client):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(200, json={"result": "success"})
        result = await mock_client.analyze("test.wav")
        assert result == {"result": "success"}

@pytest.mark.asyncio
async def test_analyze_auth_error(mock_client):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(401)
        with pytest.raises(AuthError):
            await mock_client.analyze("test.wav")

@pytest.mark.asyncio
async def test_analyze_invalid_file(mock_client):
    with pytest.raises(ValidationError):
        await mock_client.analyze("invalid.wav") 