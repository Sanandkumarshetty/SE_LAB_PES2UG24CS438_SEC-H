"""Tests for shipping quote calculations and pressure monitoring."""

import pytest

from shipping_quote import monitor_container_pressures, process_shipments


def test_ground_and_air_quotes():
    ground = process_shipments(
        [{"manifest_approved": True, "mode": "ground",
          "packages": [{"weight_kg": 10}]}],
        20.0,
    )
    air = process_shipments(
        [{"manifest_approved": True, "mode": "air",
          "packages": [{"weight_kg": 10}]}],
        20.0,
    )
    assert ground == {"total_quote": 60.0, "status": "CLEARED"}
    assert air == {"total_quote": 140.0, "status": "CLEARED"}


def test_large_package_hazmat_and_express_surcharges():
    result = process_shipments(
        [{"manifest_approved": True, "express_priority": True,
          "packages": [{"weight_kg": 40}, {"weight_kg": 1, "is_hazmat": True}]}],
        10.0,
    )
    assert result == {"total_quote": 375.0, "status": "CLEARED"}


def test_fragile_hazmat_cancels_shipment_cost():
    result = process_shipments(
        [{"manifest_approved": True, "is_fragile": True,
          "packages": [{"weight_kg": 1, "is_hazmat": True}]}],
        25.0,
    )
    assert result == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_unapproved_unsupported_and_empty_shipments():
    assert process_shipments([], 0) == {"total_quote": 0.0, "status": "NO_CARGO"}
    assert process_shipments([{"manifest_approved": False}], 0) == {
        "total_quote": 0.0, "status": "NO_CARGO"
    }
    assert process_shipments(
        [{"manifest_approved": True, "mode": "sea"}], 0
    ) == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_invalid_packages_and_rejections_flag_review():
    result = process_shipments(
        [{"manifest_approved": True,
          "packages": [{"weight_kg": 0}, {"weight_kg": -1},
                       {"weight_kg": 0}, {"weight_kg": -2}]}],
        0.0,
    )
    assert result == {"total_quote": 0.0, "status": "FLAGGED_REVIEW"}


@pytest.mark.parametrize("shipments, fee", [(None, 0), ([], -0.01), ((), 0)])
def test_invalid_arguments_raise_value_error(shipments, fee):
    with pytest.raises(ValueError, match="Invalid shipments list or handling fee"):
        process_shipments(shipments, fee)


def test_pressure_monitoring_empty_stable_and_leak_cases():
    assert monitor_container_pressures([]) == "NO_DATA"
    assert monitor_container_pressures([[13.0, 14.0, 13.0, 15.0]]) == "STABLE"
    assert monitor_container_pressures([[14.0, 13.9, 13.99]]) == "LEAK_DETECTED"
    assert monitor_container_pressures([[13.0], [13.0]]) == "STABLE"
