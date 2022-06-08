from typing import Any, Callable, Protocol

import pytest
from django.test import Client
from graphene_django.utils.testing import graphql_query
from graphene_file_upload.django.testing import file_graphql_query


class HttpResponse(Protocol):
    def json(self) -> Any:
        ...


GraphQLQuery = Callable[..., HttpResponse]


@pytest.fixture
def client_query(client: Client) -> GraphQLQuery:
    def query(query: Any, **kwargs: Any) -> HttpResponse:
        if kwargs.get("files"):
            return file_graphql_query(query=query, client=client, **kwargs)
        return graphql_query(query=query, client=client, **kwargs)

    return query
