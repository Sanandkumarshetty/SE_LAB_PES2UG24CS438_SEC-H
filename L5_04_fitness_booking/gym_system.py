"""Manage gym class bookings and export class rosters."""

import json
from pathlib import Path


class_capacity = {"Yoga": 3, "HIIT": 2, "Spin": 4}
rosters = {}


def book_class(member_id, class_name, attendance_log=None):
    """Book a member if the named class has an available seat."""
    if class_name not in class_capacity:
        raise ValueError(f"Unknown class: {class_name}")

    roster = rosters.setdefault(class_name, [])
    if len(roster) >= class_capacity[class_name]:
        print(f"Class full: {class_name}")
        return False
    if member_id in roster:
        return False

    roster.append(member_id)
    if attendance_log is not None:
        attendance_log.append(f"{member_id} -> {class_name}")
    return True


def cancel_booking(member_id, class_name):
    """Cancel a member's booking, returning whether one was removed."""
    roster = rosters.get(class_name, [])
    if member_id not in roster:
        print("Nothing to cancel")
        return False
    roster.remove(member_id)
    return True


def set_capacity(class_name, seats):
    """Set a class capacity to a non-negative integer."""
    if class_name not in class_capacity:
        raise ValueError(f"Unknown class: {class_name}")
    if isinstance(seats, bool) or not isinstance(seats, int) or seats < 0:
        raise ValueError("Capacity must be a non-negative integer")
    class_capacity[class_name] = seats


def add_members(class_name, count):
    """Add up to count uniquely named walk-in guests to a class."""
    if class_name not in class_capacity:
        raise ValueError(f"Unknown class: {class_name}")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("Guest count must be a non-negative integer")

    roster = rosters.setdefault(class_name, [])
    guest_number = 1
    booked = 0
    while booked < count:
        guest_id = f"GUEST-{guest_number}"
        guest_number += 1
        if guest_id in roster:
            continue
        if not book_class(guest_id, class_name):
            break
        booked += 1
    return booked


def export_roster(file="gym_schedule.json"):
    """Write all rosters to a UTF-8 JSON file."""
    with Path(file).open("w", encoding="utf-8") as roster_file:
        json.dump(rosters, roster_file, indent=2)


def clear_old_exports(prefix="old_"):
    """Remove matching old JSON exports from the current directory."""
    valid_prefix = prefix and all(
        char.isalnum() or char in "_-" for char in prefix
    )
    if not valid_prefix:
        raise ValueError(
            "Export prefix may contain only letters, numbers, '_' or '-'")
    for export_file in Path.cwd().glob(f"{prefix}*.json"):
        if export_file.is_file():
            export_file.unlink()


def show_rosters():
    """Print each class roster."""
    for class_name, members in rosters.items():
        print(f"{class_name}: {', '.join(str(member) for member in members)}")


def main():
    """Run the interactive booking demonstration."""
    book_class("M1", "Yoga")
    book_class("M2", "Yoga")
    book_class("M3", "Yoga")
    book_class("M4", "Yoga")
    book_class(55, "HIIT")
    set_capacity("Spin", 2)
    add_members("Spin", 3)
    cancel_booking("M9", "Boxing")

    prompt = "How many walk-in guests for HIIT? (Enter for 1): "
    guest_count = input(prompt) or "1"
    try:
        add_members("HIIT", int(guest_count))
    except ValueError as error:
        print(f"Invalid guest count: {error}")

    clear_old_exports()
    export_roster()
    show_rosters()


if __name__ == "__main__":
    main()
