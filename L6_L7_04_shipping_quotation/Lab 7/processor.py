import json
import math
import re

def calculate_dimensional_weight(dimensions_str):
    if not isinstance(dimensions_str, str):
        raise ValueError("dimensions must be a string in 'LxWxH' format")

    dims = dimensions_str.split('x')
    if len(dims) != 3:
        raise ValueError("dimensions must contain exactly three values separated by 'x'")

    try:
        length, width, height = (float(value.strip()) for value in dims)
    except (TypeError, ValueError) as exc:
        raise ValueError("each dimension must be a number") from exc

    if not all(math.isfinite(value) and value > 0 for value in (length, width, height)):
        raise ValueError("dimensions must be finite positive numbers")

    dimensional_weight = (length * width * height) / 5000.0
    if not math.isfinite(dimensional_weight):
        raise ValueError("dimensional weight is too large to calculate")
    return round(dimensional_weight, 2)

def format_tracking_label(raw_code):
    if not isinstance(raw_code, str) or not re.fullmatch(r"[A-Za-z][0-9]+", raw_code):
        raise ValueError("tracking code must be one letter followed by one or more digits")

    prefix = raw_code[0].upper()
    tracking_num = int(raw_code[1:])
    return f"{prefix}-{tracking_num:06d}"

def parse_package_manifest(json_payload):
    if not isinstance(json_payload, str):
        raise ValueError("manifest payload must be a JSON string")

    try:
        data = json.loads(json_payload)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("manifest payload must contain valid JSON") from exc

    if not isinstance(data, dict) or "weight" not in data:
        raise ValueError("manifest must be a JSON object containing 'weight'")

    weight_value = data["weight"]
    if isinstance(weight_value, bool):
        raise ValueError("weight must be a finite positive number")
    try:
        weight = float(weight_value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("weight must be a finite positive number") from exc

    if not math.isfinite(weight) or weight <= 0:
        raise ValueError("weight must be a finite positive number")
    return weight

def main():
    print("==== Running calculate_dimensional_weight ====")
    dims_input = input("Enter dimensions LxWxH in cm (e.g. 20x30x10): ")
    dim_weight = calculate_dimensional_weight(dims_input)
    print("Dimensional Weight (kg):", dim_weight)

    print("\n==== Running format_tracking_label ====")
    code_input = input("Enter raw code (e.g. E123): ")
    label = format_tracking_label(code_input)
    print("Formatted Label:", label)

    print("\n==== Running parse_package_manifest ====")
    json_input = input('Enter manifest JSON (e.g. {"weight": 12.5}): ')
    weight = parse_package_manifest(json_input)
    print("Manifest Weight:", weight)

if __name__ == "__main__":
    main()
