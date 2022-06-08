import re
from typing import Union

import graphene
from django.db.models.fields.files import FieldFile


def get_case_insensitive_regex(values: list[str]) -> str:
    joined = "|".join([re.escape(n) for n in values])
    return rf"({joined})"


def build_absolute_uri(
    info: graphene.ResolveInfo, file: Union[FieldFile, None]
) -> Union[str, None]:
    return info.context.build_absolute_uri(file.url) if file else None


def get_total(a: float, b: float) -> float:
    return a + b
