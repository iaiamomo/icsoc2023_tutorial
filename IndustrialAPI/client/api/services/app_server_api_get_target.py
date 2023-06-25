from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.target import Target
from ...types import Response


def _get_kwargs(
    target_id: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/targets/{target_id}".format(client.base_url, target_id=target_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[Any, Target]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = Target.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = cast(Any, None)
        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[Any, Target]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    target_id: str,
    *,
    client: Client,
) -> Response[Union[Any, Target]]:
    """Get a single target service

    Args:
        target_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Target]]
    """

    kwargs = _get_kwargs(
        target_id=target_id,
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    target_id: str,
    *,
    client: Client,
) -> Optional[Union[Any, Target]]:
    """Get a single target service

    Args:
        target_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Target]
    """

    return sync_detailed(
        target_id=target_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    target_id: str,
    *,
    client: Client,
) -> Response[Union[Any, Target]]:
    """Get a single target service

    Args:
        target_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Target]]
    """

    kwargs = _get_kwargs(
        target_id=target_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    target_id: str,
    *,
    client: Client,
) -> Optional[Union[Any, Target]]:
    """Get a single target service

    Args:
        target_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Target]
    """

    return (
        await asyncio_detailed(
            target_id=target_id,
            client=client,
        )
    ).parsed
