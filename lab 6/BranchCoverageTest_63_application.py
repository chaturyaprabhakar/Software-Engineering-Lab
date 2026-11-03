import pytest
from house_painting_quote import painting_quote, paint_litres, crew_days

#Branch-focused test cases: these flip the conditions that the
#CodeCoverageTest file left on only one side (True-only or False-only),
#so every if/elif gets both a True and a False run between the two files.

def test_invalid_coats_raises():
    # area_sqft is valid here, coats is not -> exercises the other half
    # of the "area_sqft <= 0 or coats < 1" branch.
    with pytest.raises(ValueError):
        painting_quote("emulsion", 500, 0, False)

def test_large_area_exterior_gets_bulk_discount():
    # area_sqft > 2000 True branch, combined with is_exterior True,
    # on top of the already-tested area_sqft <= 2000 case.
    assert painting_quote("emulsion", 3000, 1, True) == 67500

def test_rough_litres_exact_division():
    # surface == "rough" True branch, with needed % coverage == 0 (False)
    assert paint_litres(120, 1, "rough") == 2

def test_smooth_litres_with_remainder():
    # needed % coverage != 0 True branch (litres rounds up)
    assert paint_litres(121, 1, "smooth") == 2

def test_crew_days_with_remainder_and_wallpaper_removal():
    # area_sqft % per_day != 0 True branch, has_wallpaper_removal True branch
    assert crew_days(801, 2, True) == 4
