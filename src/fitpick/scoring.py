"""Core scoring logic for fitpick.

This module implements the nutrition rules that turn raw food data into
(a) a value-for-money rating, (b) a suggested use, and (c) a 0-100
recommendation score.

The thresholds are derived from widely-used public nutrition standards:
  * China GB28050 (for "high protein" / "low fat" / "low sodium" claims)
  * ISSN / ACSM sports-nutrition guidance for protein intake
  * AHA / WHO general guidance for sugar and sodium limits
"""

from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

Form = Literal["solid", "liquid"]


@dataclass
class Food:
    """A single food entry, as provided by the user."""

    name: str
    form: Form
    serving_size: float          # grams for solid, ml for liquid
    protein: float               # per 100 g / 100 ml
    sugar: float                 # per 100 g / 100 ml
    fat: float                   # per 100 g / 100 ml
    sodium: float                # mg per 100 g / 100 ml
    calories: float              # kcal per 100 g / 100 ml
    price: float                 # price per serving (currency-agnostic)
    taste: float                 # 1-10, user self-rated


# ---------------------------------------------------------------------------
# Thresholds (per 100 g for solid, per 100 ml for liquid)
# ---------------------------------------------------------------------------

# "High protein" thresholds follow the GB28050 claim rules, which require
# solid foods to have >= 12 g protein / 100 g and liquids >= 6 g / 100 ml.
HIGH_PROTEIN = {"solid": 12.0, "liquid": 6.0}

# "Low fat" thresholds follow GB28050 (<= 3 g / 100 g solid, <= 1.5 g / 100 ml).
LOW_FAT = {"solid": 3.0, "liquid": 1.5}

# Sodium thresholds: low <= 120 mg (GB28050 "low sodium"), high > 400 mg.
SODIUM_LOW = 120.0
SODIUM_HIGH = 400.0

# Sugar thresholds: low <= 5 g, mid 5-10 g, high > 10 g (per serving-scale guidance).
SUGAR_LOW = 5.0
SUGAR_HIGH = 10.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _grade(value: float, low: float, high: float, lower_is_better: bool = True) -> str:
    """Return 'good', 'mid', or 'bad' for a value against two thresholds.

    When ``lower_is_better`` is True (sugar, sodium, fat), a value below ``low``
    is "good" and above ``high`` is "bad".
    """
    if lower_is_better:
        if value <= low:
            return "good"
        if value >= high:
            return "bad"
        return "mid"
    # higher is better (e.g. protein)
    if value >= high:
        return "good"
    if value <= low:
        return "bad"
    return "mid"


def _protein_grade(food: Food) -> str:
    """Protein is the one dimension where higher is better."""
    threshold = HIGH_PROTEIN[food.form]
    if food.protein >= threshold:
        return "good"
    # Treat anything below half the "high protein" line as clearly low.
    if food.protein < threshold * 0.5:
        return "bad"
    return "mid"


# ---------------------------------------------------------------------------
# Food-category detection
# ---------------------------------------------------------------------------

def is_calorie_free_drink(food: Food) -> bool:
    """Detect a zero-calorie, sugar-free drink (tea, black coffee, sparkling water).

    Such drinks have no meaningful protein, sugar, fat, or calories — their
    value is "zero-guilt hydration", a totally different axis from protein-rich
    foods. They deserve their own scoring path rather than being penalised for
    lacking protein.
    """
    return (
        food.form == "liquid"
        and food.sugar <= 0.5
        and food.calories <= 5
        and food.protein < 1.0
    )


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def value_for_money(food: Food) -> float:
    """Protein (g) bought per unit of money spent per serving.

    Returns grams of protein per currency unit (e.g. per yuan / dollar).
    A higher number means more protein for your money.
    """
    if food.price <= 0:
        return 0.0
    # protein per serving = per-100g value scaled to the serving size
    protein_per_serving = food.protein * (food.serving_size / 100.0)
    return round(protein_per_serving / food.price, 2)


def suggested_use(food: Food) -> str:
    """Classify the food into a suggested eating role.

    Rules (in priority order):
      1. Zero-calorie sugar-free drink  -> sugar-free drink / hydration
      2. High sugar + low protein       -> treat / junk (limit intake)
      3. High protein + liquid          -> post-workout supplement / shake
      4. High protein + solid           -> main meal / staple
      5. Mid protein                    -> occasional snack / light snack
      6. Low protein, not sweet         -> side dish / filler
    """
    p_grade = _protein_grade(food)
    high_sugar = food.sugar > SUGAR_HIGH
    high_cal = food.calories >= 250

    # Zero-calorie sugar-free drinks are their own category.
    if is_calorie_free_drink(food):
        return "sugar-free drink / hydration"

    # Junk: sweet but not protein-rich.
    if p_grade == "bad" and high_sugar:
        return "treat (limit intake)"

    # Protein-rich foods: anchor of a fitness diet.
    if p_grade == "good":
        if food.form == "liquid":
            return "post-workout supplement / shake"
        return "main meal / staple"

    # Mid protein.
    if p_grade == "mid":
        if high_sugar:
            return "occasional snack"
        if high_cal:
            return "main meal / staple"
        return "light snack"

    # Low protein, not sweet.
    return "side dish / filler"


def recommendation_score(food: Food) -> int:
    """Compute a 0-100 recommendation score.

    Two scoring paths exist:

    * **Protein-rich foods** — scored on protein (35), sugar (20), fat (15),
      sodium (15), and taste (15).
    * **Zero-calorie sugar-free drinks** — protein is irrelevant, so they are
      scored on being truly zero-guilt (60), taste (25), and price
      reasonableness (15).
    """
    # Zero-calorie sugar-free drinks use a dedicated rubric.
    if is_calorie_free_drink(food):
        zero_pts = 60
        taste = max(1.0, min(10.0, food.taste))
        taste_pts = round((taste - 1) / 9 * 25)
        if food.price <= 5:
            price_pts = 15
        elif food.price >= 20:
            price_pts = 0
        else:
            price_pts = round((1 - (food.price - 5) / 15) * 15)
        total = zero_pts + taste_pts + price_pts
        return max(0, min(100, total))

    # Protein (35 pts)
    p_grade = _protein_grade(food)
    protein_pts = {"good": 35, "mid": 22, "bad": 8}[p_grade]

    # Sugar (20 pts)
    sugar_pts = {"good": 20, "mid": 12, "bad": 4}[_grade(food.sugar, SUGAR_LOW, SUGAR_HIGH)]

    # Fat (15 pts)
    fat_pts = {"good": 15, "mid": 9, "bad": 3}[_grade(food.fat, LOW_FAT[food.form] * 2, LOW_FAT[food.form] * 4)]

    # Sodium (15 pts)
    sodium_pts = {"good": 15, "mid": 9, "bad": 3}[_grade(food.sodium, SODIUM_LOW, SODIUM_HIGH)]

    # Taste (15 pts), scaled from the 1-10 rating.
    taste = max(1.0, min(10.0, food.taste))
    taste_pts = round((taste - 1) / 9 * 15)

    total = protein_pts + sugar_pts + fat_pts + sodium_pts + taste_pts
    return max(0, min(100, total))


def score_label(score: int) -> str:
    """Map a 0-100 score to a human-readable label."""
    if score >= 85:
        return "Excellent — highly recommended"
    if score >= 70:
        return "Good — recommended"
    if score >= 55:
        return "Fair — recommended with caution"
    if score >= 40:
        return "Mediocre — only if no better option"
    return "Poor — not recommended"
