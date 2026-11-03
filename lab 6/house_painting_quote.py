PAINT_RATE = {"distemper": 12, "emulsion": 20, "enamel": 30}


def painting_quote(paint, area_sqft, coats, is_exterior):
    if paint not in PAINT_RATE:
        raise ValueError("unknown paint")
    if area_sqft <= 0 or coats < 1:
        raise ValueError("invalid job")
    if is_exterior and paint == "distemper":
        raise ValueError("distemper is for interiors only")
    cost = area_sqft * PAINT_RATE[paint] * coats
    if is_exterior:
        cost += area_sqft * 5
    if area_sqft > 2000:
        cost -= cost // 10
    if cost < 5000:
        return 5000
    return cost


def paint_litres(area_sqft, coats, surface):
    if surface == "smooth":
        coverage = 100
    elif surface == "rough":
        coverage = 60
    else:
        raise ValueError("unknown surface")
    needed = area_sqft * coats
    litres = needed // coverage
    if needed % coverage:
        litres += 1
    return litres


def crew_days(area_sqft, painters, has_wallpaper_removal):
    if painters < 1:
        raise ValueError("need at least one painter")
    per_day = painters * 400
    days = area_sqft // per_day
    if area_sqft % per_day:
        days += 1
    if has_wallpaper_removal:
        days += 2
    return days
