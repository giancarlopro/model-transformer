from model_transformer import CombineTransformers, Transformer, Field


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
