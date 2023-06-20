# model_transformer

A small library aimed to help cleaning input json data, and allowing a more centered source of truth.

## Installation

```
pip install model-transformer
```

## Usage

This basic sample will show how to extract field `name` from input data, and how to create a calculated field `age` also from input data.

```python
from datetime import datetime

from model_transformer import Transformer, Field

class SampleTransformer(Transformer):
    name = Field("name") # This field will extract name from input data.

    def get_age(self, row: dict) -> int:
        birth = datetime.fromisoformat(row.get("birth"))

        diff = datetime.now() - birth

        return diff.days // 365

data = [
    {
        "name": "John Doe",
        "birth": "1998-05-01T00:00:00",
        "email": "john@company.com",
    }
]

transformer = SampleTransformer()
transformer.transform(data)
#... [
#...     {
#...         "name": "John Doe",
#...         "age": 25
#...     }
#... ]
```