import pytest
from house_painting_quote import painting_quote, paint_litres, crew_days

#Example test cases:
def test_exterior_enamel():
    assert painting_quote("enamel", 500, 2, True) == 32500

def test_smooth_litres():
    assert paint_litres(200, 1, "smooth") == 2

#Additional test cases for code (line) coverage:
def test_interior_distemper_small_job_hits_minimum():
    # is_exterior False, cost works out below 5000, so the minimum-charge
    # line gets executed too.
    assert painting_quote("distemper", 100, 1, False) == 5000

def test_unknown_paint_raises():
    with pytest.raises(ValueError):
        painting_quote("gold_leaf", 500, 1, False)

def test_invalid_area_raises():
    with pytest.raises(ValueError):
        painting_quote("emulsion", 0, 1, False)

def test_exterior_distemper_raises():
    with pytest.raises(ValueError):
        painting_quote("distemper", 500, 1, True)

def test_unknown_surface_raises():
    with pytest.raises(ValueError):
        paint_litres(200, 1, "glossy")

def test_painters_less_than_1_raises():
    with pytest.raises(ValueError):
        crew_days(500, 0, False)

def test_crew_days_exact_division():
    assert crew_days(800, 2, False) == 1

def test_exterior_large_area_gets_bulk_discount():
    assert painting_quote("enamel", 2500, 1, True) == 78750

def test_rough_surface_litres():
    assert paint_litres(300, 1, "rough") == 5

def test_crew_days_with_remainder_and_wallpaper():
    assert crew_days(900, 2, True) == 4
