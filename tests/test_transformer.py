from unittest.mock import Mock

from model_transformer import BaseField, CombineTransformers, Field, Transformer


def test_field():
    row = {"name": "John"}

    field = Field("name", default="Jane")

    assert field(row) == "John"
    assert field({}) == "Jane"

    field = Field("name", filter=lambda x: x.upper())

    assert field(row) == "JOHN"


def test_transformer():
    class TestTransformer(Transformer):
        lastname = Field("lastname")
        firstname = Field("firstname")

        def get_fullname(self, row: dict):
            return f"{row.get('firstname')} {row.get('lastname')}"

    row = {"firstname": "John", "lastname": "Doe"}

    transformer = TestTransformer()
    data = transformer.transform([row])[0]

    assert data["firstname"] == "John"
    assert data["lastname"] == "Doe"
    assert data["fullname"] == "John Doe"


def test_combined_transformers():
    class FirstTransformer(Transformer):
        person_name = Field("name")

    class SecondTransformer(Transformer):
        person_age = Field("age")

    transformer = CombineTransformers(
        first=FirstTransformer(),
        second=SecondTransformer(),
    )

    row = {"name": "John", "age": 30}

    data = transformer.transform([row])

    assert data["first"][0]["person_name"] == "John"
    assert data["second"][0]["person_age"] == 30


def test_multi_field_resets_on_different_rows():
    field_mock = Mock(return_value=(20, "John"), spec=BaseField)

    class TestTransformer(Transformer):
        age__name = field_mock

    transformer = TestTransformer()

    transformer.transform_row({})

    assert field_mock.call_count == 1

    for _ in range(10):
        assert transformer.age({}) == 20
        assert transformer.name({}) == "John"
        assert field_mock.call_count == 1

    transformer.transform_row({})
    assert field_mock.call_count == 2


def test_multi_field_works_for_different_rows():
    class TestTransformer(Transformer):
        def get_age__name(self, row: dict):
            return tuple(row.get("age__name"))

    rows = [
        {"age__name": (20, "John")},
        {"age__name": (30, "Jane")},
        {"age__name": (40, "Joe")},
        {"age__name": (50, "Jill")},
    ]

    transformer = TestTransformer()

    for row in rows:
        data = transformer.transform_row(row)
        assert data["age"] == row["age__name"][0]
        assert data["name"] == row["age__name"][1]
        assert data["name"] == row["age__name"][1]


def test_transformer_composition():
    class FirstTransformer(Transformer):
        age = Field("age")
        name = Field("name")

    class SecondTransformer(FirstTransformer):
        city = Field("city")
        state = Field("state")

    first = FirstTransformer()
    second = SecondTransformer()

    for field in ["age", "name"]:
        assert field in first.field_names

    for field in ["age", "name", "city", "state"]:
        assert field in second.field_names


def test_composition_can_override():
    class FirstTransformer(Transformer):
        age = Field("age")
        name = Field("name")

    class OverrideNameTransformer(FirstTransformer):
        name = Field("fullname")

    first = FirstTransformer()
    override = OverrideNameTransformer()

    assert first.fields["name"] != override.fields["name"]
    assert override.fields["name"].name == "fullname"


def test_field_remapping():
    class FirstTransformer(Transformer):
        age = Field("age")
        name = Field("name")

    class RenameTransformer(FirstTransformer):
        class Meta:
            rename_fields = {"name": "fullname"}

    t = RenameTransformer()

    data = t.transform_row({"age": 20, "name": "John"})

    assert data["age"] == 20
    assert data["fullname"] == "John"
    assert "name" not in data
