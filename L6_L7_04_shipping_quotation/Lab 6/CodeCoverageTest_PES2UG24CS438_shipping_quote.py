"""Line coverage tests for the shipping quote application."""

import pytest

from shipping_quote import monitor_container_pressures, process_shipments


def test_approved_ground_shipment_with_handling_fee():
    result = process_shipments(
        [{"manifest_approved": True, "mode": "ground", "packages": [{"weight_kg": 10}]}],
        20.0,
    )
    assert result == {"total_quote": 60.0, "status": "CLEARED"}


def test_air_large_package_and_express_priority():
    result = process_shipments(
        [{"manifest_approved": True, "mode": "air", "express_priority": True,
          "packages": [{"weight_kg": 40}]}],
        10.0,
    )
    assert result == {"total_quote": 912.5, "status": "CLEARED"}


def test_nonfragile_hazmat_adds_surcharge():
    result = process_shipments(
        [{"manifest_approved": True, "packages": [{"weight_kg": 2, "is_hazmat": True}]}],
        5.0,
    )
    assert result == {"total_quote": 55.0, "status": "CLEARED"}


def test_unapproved_and_empty_shipments_have_no_cargo():
    assert process_shipments([], 0) == {"total_quote": 0.0, "status": "NO_CARGO"}
    assert process_shipments([{"manifest_approved": False}], 0) == {
        "total_quote": 0.0, "status": "NO_CARGO"
    }


def test_unsupported_modes_and_fragile_hazmat_are_rejected():
    result = process_shipments(
        [
            {"manifest_approved": True, "mode": "sea"},
            {"manifest_approved": True, "is_fragile": True,
             "packages": [{"weight_kg": 1, "is_hazmat": True}]},
        ],
        10.0,
    )
    assert result == {"total_quote": 0.0, "status": "NO_CARGO"}


def test_more_than_three_rejected_packages_flags_review():
    result = process_shipments(
        [{"manifest_approved": True,
          "packages": [{"weight_kg": 0}, {"weight_kg": -1},
                       {"weight_kg": 0}, {"weight_kg": -2}]}],
        0.0,
    )
    assert result == {"total_quote": 0.0, "status": "FLAGGED_REVIEW"}


@pytest.mark.parametrize("shipments, fee", [(None, 0), ([], -0.01)])
def test_invalid_arguments_raise_value_error(shipments, fee):
    with pytest.raises(ValueError, match="Invalid shipments list or handling fee"):
        process_shipments(shipments, fee)


def test_empty_pressure_logs_have_no_data():
    assert monitor_container_pressures([]) == "NO_DATA"


def test_stable_pressure_readings_and_recovery_reset_streak():
    assert monitor_container_pressures([[13.0, 14.0, 13.0, 15.0]]) == "STABLE"


def test_two_consecutive_low_pressure_readings_detect_leak():
    assert monitor_container_pressures([[14.0, 13.9, 13.99]]) == "LEAK_DETECTED"
