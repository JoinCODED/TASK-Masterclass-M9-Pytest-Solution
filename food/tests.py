import json
import math
import string
from functools import partial

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from graphene_django.utils.testing import graphql_query
from hypothesis import HealthCheck, assume, given, settings, strategies as st

from conftest import GraphQLQuery
from food.models import Ingredient
from food.utils import get_total


@given(a=st.floats(), b=st.floats())
def test_total(a: float, b: float) -> None:
    assume(not (math.isnan(a) or math.isnan(b)))
    res = get_total(a, b)
    assert math.isnan(res) or res == (a + b)


@pytest.fixture
@pytest.mark.django_db
def ingredient() -> Ingredient:
    return Ingredient.objects.create(name="foo", origin="bar")


@pytest.mark.django_db
def test_ingredient_query(
    client_query: partial[graphql_query],
    ingredient: Ingredient,
) -> None:
    response = client_query(
        f"""
        query {{
            ingredient(ingredientId: {ingredient.id}) {{
                id
                name
                origin
            }}
        }}
        """
    )

    content = json.loads(response.content)
    assert "errors" not in content

    data = content["data"]["ingredient"]
    assert data["name"] == ingredient.name
    assert data["origin"] == ingredient.origin


def test_invalid_ingredient(
    client_query: partial[graphql_query],
) -> None:
    response = client_query(
        """
        query {
            ingredient(ingredientId: -1) {
                id
                name
                origin
            }
        }
        """
    )

    content = json.loads(response.content)
    assert "errors" in content


@pytest.mark.django_db
def test_delete_ingredient(
    client_query: GraphQLQuery, ingredient: Ingredient
) -> None:
    response = client_query(
        """
        mutation deleteIngredient($id: Int!) {
            deleteIngredient(id: $id) {
                status
            }
        }
        """,
        op_name="deleteIngredient",
        variables={"id": ingredient.id},
    )

    content = response.json()
    assert "errors" not in content

    data = content["data"]["deleteIngredient"]
    assert data["status"]

    with pytest.raises(Ingredient.DoesNotExist):
        ingredient.refresh_from_db()


@given(
    name=st.text(string.ascii_letters), origin=st.text(string.ascii_letters)
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.django_db
def test_create_ingredient(
    client_query: GraphQLQuery, name: str, origin: str
) -> None:
    with transaction.atomic():
        response = client_query(
            """
            mutation createIngredient($name: String!, $origin: String!) {
                createIngredient(name: $name, origin: $origin) {
                    ingredient {
                        id
                        name
                        origin
                    }
                }
            }
            """,
            op_name="createIngredient",
            variables={"name": name, "origin": origin},
        )

    content = response.json()
    assert "errors" not in content

    data = content["data"]["createIngredient"]["ingredient"]
    assert data["name"] == name
    assert data["origin"] == origin


@pytest.mark.django_db
def test_create_cuisine(client_query: GraphQLQuery) -> None:
    response = client_query(
        """
        mutation createCuisine($name: String!, $banner: Upload) {
            createCuisine(name: $name, banner: $banner) {
                cuisine {
                    name
                    banner
                }
            }
        }
        """,
        op_name="createCuisine",
        variables={"name": "foo"},
        files={
            "banner": SimpleUploadedFile(
                "coconuts.txt",
                content=b"Are you suggesting coconuts migrate?",
                content_type="text/plain",
            ),
        },
    )

    content = response.json()
    assert "errors" not in content

    data = content["data"]["createCuisine"]["cuisine"]

    assert data["banner"] is not None
    assert data["name"] == "foo"
