from unittest.mock import MagicMock
from api_request import api_request


def test_api_request_returns_text():
    mock_client = MagicMock()
    mock_client.messages.create.return_value.content = [MagicMock(text="Quantum computing uses quantum mechanics.")]

    result = api_request(client=mock_client)

    assert result == "Quantum computing uses quantum mechanics."
