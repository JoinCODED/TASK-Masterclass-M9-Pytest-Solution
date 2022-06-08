from typing import Union

import graphene
import graphene_django

from food.models import Cuisine, Ingredient, Recipe
from food.utils import build_absolute_uri


class IngredientType(graphene_django.DjangoObjectType):
    class Meta:
        model = Ingredient


class CuisineType(graphene_django.DjangoObjectType):
    class Meta:
        model = Cuisine

    def resolve_banner(root, info: graphene.ResolveInfo) -> Union[str, None]:
        return build_absolute_uri(info, root.banner)


class RecipeType(graphene_django.DjangoObjectType):
    class Meta:
        model = Recipe


class IngredientInputType(graphene.InputObjectType):
    id = graphene.Int()
    name = graphene.String()
    origin = graphene.String()


class CuisineInputType(graphene.InputObjectType):
    id = graphene.Int()
    name = graphene.String()
