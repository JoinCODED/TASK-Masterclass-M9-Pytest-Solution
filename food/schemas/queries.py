from typing import Any, Union

import graphene
import graphene_django
from django.db.models import QuerySet
from graphql import GraphQLError

from food.models import Cuisine, Ingredient, Recipe
from food.schemas.types import CuisineType, IngredientType, RecipeType
from food.utils import get_case_insensitive_regex


class FoodQuery(graphene.ObjectType):
    # Fields
    recipe = graphene.Field(
        RecipeType, recipe_id=graphene.Int(), name=graphene.String()
    )
    ingredient = graphene.Field(
        IngredientType, ingredient_id=graphene.Int(required=True)
    )
    cuisine = graphene.Field(
        CuisineType, cuisine_id=graphene.Int(required=True)
    )

    # Lists
    recipes = graphene_django.DjangoListField(
        RecipeType,
        offset=graphene.Int(),
        limit=graphene.Int(),
        name=graphene.String(),
        cuisine=graphene.String(),
        ingredients=graphene.List(graphene.String),
    )
    ingredients = graphene_django.DjangoListField(
        IngredientType,
        offset=graphene.Int(),
        limit=graphene.Int(),
        name=graphene.String(),
        origin=graphene.String(),
        used_in=graphene.List(
            graphene.String,
            description=(
                "Search for a cuisine name that used these ingredients (e.g., "
                "Italian -> Tomato, Wheat, etc...)"
            ),
        ),
    )
    cuisines = graphene_django.DjangoListField(
        CuisineType,
        offset=graphene.Int(),
        limit=graphene.Int(),
        name=graphene.String(),
        recipes=graphene.List(graphene.String),
        ingredients=graphene.List(graphene.String),
    )

    def resolve_recipe(
        root,
        info: graphene.ResolveInfo,
        recipe_id: Union[int, None] = None,
        name: Union[str, None] = None,
    ) -> Recipe:
        if recipe_id is name is None:
            raise GraphQLError("must use either recipeId or name")

        lookup: dict[str, Any] = dict(id=recipe_id, name=name)

        try:
            return Recipe.objects.get(**lookup)
        except Recipe.DoesNotExist as exc:
            raise GraphQLError(str(exc))

    def resolve_ingredient(
        root, info: graphene.ResolveInfo, ingredient_id: int
    ) -> Ingredient:
        try:
            return Ingredient.objects.get(id=ingredient_id)
        except Ingredient.DoesNotExist as exc:
            raise GraphQLError(str(exc))

    def resolve_cuisine(
        root, info: graphene.ResolveInfo, cuisine_id: int
    ) -> Cuisine:
        try:
            return Cuisine.objects.get(id=cuisine_id)
        except Cuisine.DoesNotExist as exc:
            raise GraphQLError(str(exc))

    def resolve_recipes(
        root,
        *info: graphene.ResolveInfo,
        offset: Union[int, None] = None,
        limit: Union[int, None] = None,
        name: Union[str, None] = None,
        cuisine: Union[str, None] = None,
        ingredients: Union[list[str], None] = None,
    ) -> QuerySet[Recipe]:
        q: dict[str, Any] = {}
        if name is not None:
            q.update(name__icontains=name)
        if cuisine is not None:
            q.update(cuisine__name__icontains=cuisine)
        if ingredients is not None:
            pat = get_case_insensitive_regex(ingredients)
            q.update(ingredients__name__iregex=pat)

        query = Recipe.objects.filter(**q)
        return query[slice(offset, limit)]

    def resolve_ingredients(
        root,
        *info: graphene.ResolveInfo,
        offset: Union[int, None] = None,
        limit: Union[int, None] = None,
        name: Union[str, None] = None,
        origin: Union[str, None] = None,
        used_in: Union[list[str], None] = None,
    ) -> QuerySet[Ingredient]:
        q: dict[str, Any] = {}
        if name is not None:
            q.update(name__icontains=name)
        if origin is not None:
            q.update(origin__name__icontains=origin)
        if used_in is not None:
            pat = get_case_insensitive_regex(used_in)
            q.update(recipes__cuisine__name__iregex=pat)

        query = Ingredient.objects.filter(**q)
        return query[slice(offset, limit)]

    def resolve_cuisines(
        root,
        *info: graphene.ResolveInfo,
        offset: Union[int, None] = None,
        limit: Union[int, None] = None,
        name: Union[str, None] = None,
        recipes: Union[list[str], None] = None,
        ingredients: Union[list[str], None] = None,
    ) -> QuerySet[Cuisine]:
        q: dict[str, Any] = {}
        if name is not None:
            q.update(name__icontains=name)
        if recipes is not None:
            pat = get_case_insensitive_regex(recipes)
            q.update(recipes__name__iregex=pat)
        if ingredients is not None:
            pat = get_case_insensitive_regex(ingredients)
            q.update(ingredients__name__iregex=pat)

        query = Cuisine.objects.filter(**q)
        return query[slice(offset, limit)]
