from http import HTTPStatus
from typing import Any, Dict

import httpx

from ...client import Client
from ...types import Response


def _get_kwargs(
    service_id: str,
    *,
    client: Client,
    json_body: str,
) -> Dict[str, Any]:
    url = "{}/execute-service-action/{service_id}".format(client.base_url, service_id=service_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _build_response(*, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=None,
    )


def sync_detailed(
    service_id: str,
    *,
    client: Client,
    json_body: str,
) -> Response[Any]:
    """Request a service to execute an action

    Args:
        service_id (str):
        json_body (str):

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        client=client,
        json_body=json_body,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    service_id: str,
    *,
    client: Client,
    json_body: str,
) -> Response[Any]:
    """Request a service to execute an action

    Args:
        service_id (str):
        json_body (str):

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)
