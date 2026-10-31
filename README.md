# semverkit

Parse, compare, bump and range-match semantic versions.

## Usage

```python
from semverkit import Version, satisfies

v = Version.parse("1.4.2-beta.1")
v.bump("minor")                 # -> 1.5.0
satisfies("1.4.9", "^1.4.0")    # -> True
```

## Test

```bash
pip install pytest && pytest
```

## License

MIT
