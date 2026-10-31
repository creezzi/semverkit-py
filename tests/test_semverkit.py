import pytest

from semverkit import Version, satisfies


def test_parse_and_str_roundtrip():
    text = "1.2.3-alpha.1+build.5"
    v = Version.parse(text)
    assert (v.major, v.minor, v.patch) == (1, 2, 3)
    assert v.prerelease == ("alpha", "1") and str(v) == text


@pytest.mark.parametrize("bad", ["1.2", "01.2.3", "1.2.3-", "a.b.c", ""])
def test_invalid(bad):
    with pytest.raises(ValueError):
        Version.parse(bad)


def test_ordering_follows_spec_example():
    chain = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta",
             "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]
    versions = [Version.parse(c) for c in chain]
    assert versions == sorted(versions)
    assert len(set(versions)) == len(versions)


def test_build_metadata_ignored_in_comparison():
    assert Version.parse("1.0.0+a") == Version.parse("1.0.0+b")


def test_bump():
    v = Version.parse("1.4.2")
    assert str(v.bump("major")) == "2.0.0"
    assert str(v.bump("minor")) == "1.5.0"
    assert str(v.bump("patch")) == "1.4.3"
    assert str(Version.parse("1.4.2-rc.1").bump("patch")) == "1.4.2"


@pytest.mark.parametrize("version,constraint,expected", [
    ("1.4.9", "^1.4.0", True), ("2.0.0", "^1.4.0", False), ("0.2.5", "^0.2.0", True),
    ("0.3.0", "^0.2.0", False), ("0.0.4", "^0.0.3", False),
    ("1.2.9", "~1.2.3", True), ("1.3.0", "~1.2.3", False),
    ("1.5.0", ">=1.0.0 <2.0.0", True), ("2.0.0", ">=1.0.0 <2.0.0", False),
    ("1.0.0", "1.0.0", True), ("1.0.1", "=1.0.0", False),
])
def test_satisfies(version, constraint, expected):
    assert satisfies(version, constraint) is expected
