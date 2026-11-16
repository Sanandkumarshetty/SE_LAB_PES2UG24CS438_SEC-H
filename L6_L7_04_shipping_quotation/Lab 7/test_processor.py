from hypothesis import given, strategies as st
from processor import calculate_dimensional_weight, format_tracking_label, parse_package_manifest

@given(st.text() | st.none())
def test_calculate_dimensional_weight_no_crash(s):
    try:
        result = calculate_dimensional_weight(s)
    except ValueError:
        # Invalid fuzzed inputs are rejected with a documented validation error.
        return
    assert isinstance(result, float)
    assert result >= 0

@given(st.text() | st.none())
def test_format_tracking_label_safe(s):
    try:
        result = format_tracking_label(s)
    except ValueError:
        # Invalid fuzzed inputs are rejected with a documented validation error.
        return
    assert len(result) >= 8
    assert result[0].isalpha() and result[1] == '-'
    assert result[2:].isdigit()

@given(st.text() | st.none())
def test_parse_package_manifest_safe(s):
    try:
        result = parse_package_manifest(s)
    except ValueError:
        # Invalid fuzzed inputs are rejected with a documented validation error.
        return
    assert isinstance(result, float)
    assert result > 0
