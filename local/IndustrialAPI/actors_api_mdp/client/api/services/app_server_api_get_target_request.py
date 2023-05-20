from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ...client import Client
from ...types import Response


def _get_kwargs(
    target_id: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/get-target-request/{target_id}".format(client.base_url, target_id=target_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, str]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = cast(str, response.json())
        return response_200
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = cast(Any, None)
        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    target_id: str,
    *,
    client: Client,
) -> Response[Union[Any, str]]:
    """Get a target request

    Args:
        target_id (str):

    Returns:
        Response[Union[Any, str]]
    """

    kwargs = _get_kwargs(
        target_id=target_id,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    target_id: str,
    *,
    client: Client,
) -> Optional[Union[Any, str]]:
    """Get a target request

    Args:
        target_id (str):

    Returns:
        Response[Union[Any, str]]
    """

    return sync_detailed(
        target_id=target_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    target_id: str,
    *,
    client: Client,
) -> Response[Union[Any, str]]:
    """Get a target request

    Args:
        target_id (str):

    Returns:
        Response[Union[Any, str]]
    """

    kwargs = _get_kwargs(
        target_id=target_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    target_id: str,
    *,
    client: Client,
) -> Optional[Union[Any, str]]:
    """Get a target request

    Args:
        target_id (str):

    Returns:
        Response[Union[Any, str]]
    """

    return (
        await asyncio_detailed(
            target_id=target_id,
            client=client,
        )
    ).parsed
