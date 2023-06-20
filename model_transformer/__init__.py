from typing import Any

from functools import wraps, partial


class BaseField:
    def __call__(self, row: dict) -> Any:
        raise NotImplementedError("BaseField is an abstract class")


class Field(BaseField):
    def __init__(self, name, default=None, filter=None) -> None:
        self.name = name
        self.filter = filter
        self.default = default

    def __call__(self, row: dict) -> Any:
        data = row.get(self.name, self.default)

        if self.filter:
            data = self.filter(data)

        return data


class Transformer:
    """Schema is a base class for all schemas defined.

    It provides a way to define a schema for a given data source.
    """

    @property
    def fields(self):
        defined_fields = {
            key: value
            for key, value in vars(self.__class__).items()
            if isinstance(value, BaseField)
        }

        dynamic_fields = {
            key[4:]: partial(value, self)
            for key, value in vars(self.__class__).items()
            if key.startswith("get_") and not isinstance(value, BaseField)
        }

        return {**defined_fields, **dynamic_fields}

    @property
    def field_names(self):
        return self.fields.keys()

    def transform_row(self, row: dict) -> dict:
        return {k: field(row) for k, field in self.fields.items()}

    def transform(self, rows: list[dict]) -> Any:
        return [self.transform_row(row) for row in rows]


class CombineTransformers:
    def __init__(self, **transformers) -> None:
        assert all(isinstance(t, Transformer) for t in transformers.values())

        self.transformers = transformers

    def transform(self, rows: list[dict]) -> Any:
        return {
            name: transformer.transform(rows)
            for name, transformer in self.transformers.items()
        }

    def transform_row(self, row: dict) -> dict:
        return {
            name: transformer.transform_row(row)
            for name, transformer in self.transformers.items()
        }
