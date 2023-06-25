from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ...client import Client
from ...models.service import Service
from ...types import Response


def _get_kwargs(
    service_id: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/services/{service_id}".format(client.base_url, service_id=service_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, Service]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Service.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = cast(Any, None)
        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, Service]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    service_id: str,
    *,
    client: Client,
) -> Response[Union[Any, Service]]:
    """Get a single service

    Args:
        service_id (str):

    Returns:
        Response[Union[Any, Service]]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    service_id: str,
    *,
    client: Client,
) -> Optional[Union[Any, Service]]:
    """Get a single service

    Args:
        service_id (str):

    Returns:
        Response[Union[Any, Service]]
    """

    return sync_detailed(
        service_id=service_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    service_id: str,
    *,
    client: Client,
) -> Response[Union[Any, Service]]:
    """Get a single service

    Args:
        service_id (str):

    Returns:
        Response[Union[Any, Service]]
    """

    kwargs = _get_kwargs(
        service_id=service_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    service_id: str,
    *,
    client: Client,
) -> Optional[Union[Any, Service]]:
    """Get a single service

    Args:
        service_id (str):

    Returns:
        Response[Union[Any, Service]]
    """

    return (
        await asyncio_detailed(
            service_id=service_id,
            client=client,
        )
    ).parsed
