"""Branch coverage tests for the shipping quote application."""

import pytest

from shipping_quote import monitor_container_pressures, process_shipments


def shipment(**kwargs):
    base = {"manifest_approved": True, "packages": []}
    base.update(kwargs)
    return base


@pytest.mark.parametrize("shipments, fee", [((), 0), ([], -1)])
def test_each_input_validation_failure(shipments, fee):
    with pytest.raises(ValueError):
        process_shipments(shipments, fee)


def test_unapproved_shipment_is_skipped_and_empty_input_is_no_cargo():
    assert process_shipments([shipment(manifest_approved=False)], 5) == {
        "total_quote": 0.0, "status": "NO_CARGO"
    }
    assert process_shipments([], 5) == {"total_quote": 0.0, "status": "NO_CARGO"}


@pytest.mark.parametrize(
    "mode, package, expected",
    [
        ("air", {"weight_kg": 30}, 360.0),
        ("ground", {"weight_kg": 31}, 186.0),
        ("ground", {"weight_kg": 0}, 0.0),
    ],
)
def test_mode_weight_boundary_and_rejected_weight(mode, package, expected):
    result = process_shipments([shipment(mode=mode, packages=[package])], 0)
    if package["weight_kg"] == 0:
        assert result == {"total_quote": 0.0, "status": "NO_CARGO"}
    else:
        assert result == {"total_quote": expected, "status": "CLEARED"}


def test_unsupported_mode_counts_as_rejected():
    assert process_shipments([shipment(mode="sea")], 3) == {
        "total_quote": 0.0, "status": "NO_CARGO"
    }


def test_hazmat_fragile_cancels_shipment_cost_and_counts_rejection():
    result = process_shipments(
        [shipment(is_fragile=True, packages=[{"weight_kg": 1, "is_hazmat": True}])], 25
    )
    assert result == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_express_and_nonfragile_hazmat_charges():
    result = process_shipments(
        [shipment(express_priority=True,
                  packages=[{"weight_kg": 1, "is_hazmat": True}, {"weight_kg": 1}])], 4
    )
    assert result == {"total_quote": 72.5, "status": "CLEARED"}


def test_more_than_three_rejections_flags_review():
    result = process_shipments([shipment(packages=[{"weight_kg": 0}] * 4)], 0)
    assert result == {"total_quote": 0.0, "status": "FLAGGED_REVIEW"}


def test_unapproved_and_empty_log_inputs_take_no_data_paths():
    assert process_shipments([shipment(manifest_approved=False)], 0)["status"] == "NO_CARGO"
    assert monitor_container_pressures(None) == "NO_DATA"


@pytest.mark.parametrize(
    "logs, expected",
    [
        ([[]], "STABLE"),
        ([[14.0, 13.99, 14.0, 13.0]], "STABLE"),
        ([[13.99, 13.0]], "LEAK_DETECTED"),
    ],
)
def test_pressure_threshold_streak_and_reset(logs, expected):
    assert monitor_container_pressures(logs) == expected
