def clean_colour_name(name):
    """
    Turns a colour name into a lower-case code, e.g. 'Ocean Blue' -> 'ocean_blue'.
    Returns '' for any input that isn't a usable, non-empty string.
    """
    if not isinstance(name, str):
        return ''
    name = name.strip()
    if not name:
        return ''
    return name.lower().replace(' ', '_')

def room_area(text):
    """
    Converts 'LENGTHxWIDTH' into an area in square feet.
    Returns 0 for anything that doesn't parse as exactly two whole numbers
    separated by a single 'x'.
    """
    if not isinstance(text, str):
        return 0
    text = text.strip().lower()
    if text.count('x') != 1:
        return 0
    length_str, width_str = text.split('x')
    length_str = length_str.strip()
    width_str = width_str.strip()
    if not length_str.lstrip('-').isdigit() or not width_str.lstrip('-').isdigit():
        return 0
    length = int(length_str)
    width = int(width_str)
    if length < 0 or width < 0:
        return 0
    return length * width

def total_wall_area(text):
    """
    Adds up wall areas separated by semicolons.
    Ignores empty or non-numeric entries instead of crashing.
    """
    if not isinstance(text, str):
        return 0
    total = 0
    for part in text.split(';'):
        part = part.strip()
        if not part:
            continue
        if not part.lstrip('-').isdigit():
            continue
        value = int(part)
        if value < 0:
            continue
        total += value
    return total

def main():
    print("==== Running clean_colour_name ====")
    value = input("Enter a paint colour name (e.g. Ocean Blue): ")
    print("Colour code:", clean_colour_name(value))

    print("\n==== Running room_area ====")
    value = input("Enter room size as LENGTHxWIDTH in feet (e.g. 12x10): ")
    print("Room area (sq ft):", room_area(value))

    print("\n==== Running total_wall_area ====")
    value = input("Enter wall areas separated by ; (e.g. 120;95;110): ")
    print("Total wall area (sq ft):", total_wall_area(value))

if __name__ == "__main__":
    main()
