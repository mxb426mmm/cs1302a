"""Unit tests for fitpick scoring logic."""

import pytest

from fitpick import scoring
from fitpick.scoring import Food


def _food(**overrides):
    defaults = dict(
        name="Test Food",
        form="solid",
        serving_size=100,
        protein=15,
        sugar=5,
        fat=3,
        sodium=100,
        calories=200,
        price=10,
        taste=7,
    )
    defaults.update(overrides)
    return Food(**defaults)


# --- value_for_money ---

def test_value_for_money_basic():
    # 100g serving, 20g protein per 100g -> 20g protein, price 10 -> 2.0
    f = _food(protein=20, price=10)
    assert scoring.value_for_money(f) == 2.0


def test_value_for_money_scales_with_serving():
    # 50g serving of the same food -> half the protein
    f = _food(protein=20, price=10, serving_size=50)
    assert scoring.value_for_money(f) == 1.0


def test_value_for_money_zero_price():
    f = _food(price=0)
    assert scoring.value_for_money(f) == 0.0


# --- suggested_use ---

def test_high_protein_solid_is_staple():
    f = _food(protein=25, sugar=2, calories=180)
    assert scoring.suggested_use(f) == "main meal / staple"


def test_high_protein_liquid_is_supplement():
    f = _food(form="liquid", protein=20, sugar=2)
    assert scoring.suggested_use(f) == "post-workout supplement / shake"


def test_high_sugar_low_protein_is_treat():
    f = _food(protein=3, sugar=15)
    assert scoring.suggested_use(f) == "treat (limit intake)"


def test_mid_protein_low_sugar_is_light_snack():
    f = _food(protein=8, sugar=2, calories=120)
    assert scoring.suggested_use(f) == "light snack"


# --- recommendation_score ---

def test_score_bounds():
    # Score must always be within [0, 100].
    best = _food(protein=40, sugar=0, fat=0, sodium=0, calories=150, taste=10)
    worst = _food(protein=0, sugar=30, fat=30, sodium=1000, calories=600, taste=1)
    assert 0 <= scoring.recommendation_score(best) <= 100
    assert 0 <= scoring.recommendation_score(worst) <= 100


def test_high_quality_food_scores_high():
    chicken = _food(protein=31, sugar=0, fat=3, sodium=70, calories=165, taste=7)
    assert scoring.recommendation_score(chicken) >= 80


def test_junk_food_scores_low():
    cola = _food(form="liquid", protein=0, sugar=11, fat=0, sodium=10, calories=42, taste=8)
    assert scoring.recommendation_score(cola) <= 60


# --- score_label ---

def test_score_label_ranges():
    assert scoring.score_label(90) == "Excellent — highly recommended"
    assert scoring.score_label(75) == "Good — recommended"
    assert scoring.score_label(60) == "Fair — recommended with caution"
    assert scoring.score_label(45) == "Mediocre — only if no better option"
    assert scoring.score_label(10) == "Poor — not recommended"


# --- grade helper ---

def test_grade_lower_is_better():
    assert scoring._grade(3, 5, 10) == "good"
    assert scoring._grade(7, 5, 10) == "mid"
    assert scoring._grade(15, 5, 10) == "bad"


def test_protein_grade_solid():
    f_high = _food(protein=20)
    f_low = _food(protein=3)
    assert scoring._protein_grade(f_high) == "good"
    assert scoring._protein_grade(f_low) == "bad"


# --- calorie-free drink detection ---

def test_zero_calorie_drink_detected():
    tea = _food(form="liquid", protein=0, sugar=0, fat=0, sodium=0, calories=0)
    assert scoring.is_calorie_free_drink(tea) is True


def test_sugary_drink_not_calorie_free():
    cola = _food(form="liquid", protein=0, sugar=11, calories=42)
    assert scoring.is_calorie_free_drink(cola) is False


def test_calorie_free_drink_gets_hydration_label():
    tea = _food(form="liquid", protein=0, sugar=0, calories=0)
    assert scoring.suggested_use(tea) == "sugar-free drink / hydration"


def test_calorie_free_drink_not_penalized_for_low_protein():
    # A zero-calorie tea should score well despite having no protein.
    tea = _food(form="liquid", protein=0, sugar=0, fat=0, sodium=0, calories=0, price=6, taste=7)
    assert scoring.recommendation_score(tea) >= 70
