"""Command-line interface for fitpick."""

import argparse
import sys

from . import __version__, scoring


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

_GRADE_LABEL = {
    "good": "GOOD",
    "mid": "MID",
    "bad": "BAD",
}


def _grade_display(value: str) -> str:
    return _GRADE_LABEL.get(value, value.upper())


def _stars(score: int) -> str:
    """Render a 0-100 score as a 5-star string."""
    filled = round(score / 20)  # 0-5 stars
    return "\u2605" * filled + "\u2606" * (5 - filled)


def _report(food: scoring.Food) -> str:
    score = scoring.recommendation_score(food)
    vfm = scoring.value_for_money(food)
    use = scoring.suggested_use(food)
    label = scoring.score_label(score)

    p_grade = _grade_display(scoring._protein_grade(food))
    sugar_grade = _grade_display(
        scoring._grade(food.sugar, scoring.SUGAR_LOW, scoring.SUGAR_HIGH)
    )
    fat_grade = _grade_display(
        scoring._grade(
            food.fat,
            scoring.LOW_FAT[food.form] * 2,
            scoring.LOW_FAT[food.form] * 4,
        )
    )
    sodium_grade = _grade_display(
        scoring._grade(food.sodium, scoring.SODIUM_LOW, scoring.SODIUM_HIGH)
    )

    unit = "g / 100 ml" if food.form == "liquid" else "g / 100 g"

    lines = [
        f"\n{food.name}",
        "-" * 40,
        f"Category        : {food.form.title()}",
        f"Serving size    : {food.serving_size} {'ml' if food.form == 'liquid' else 'g'}",
        f"Price / serving : {food.price:.2f}",
        "",
        f"Protein         : {food.protein} {unit}   ({p_grade})",
        f"Sugar           : {food.sugar} {unit}   ({sugar_grade})",
        f"Fat             : {food.fat} {unit}   ({fat_grade})",
        f"Sodium          : {food.sodium} mg/100 {'ml' if food.form == 'liquid' else 'g'}   ({sodium_grade})",
        f"Calories        : {food.calories} kcal/100 {'ml' if food.form == 'liquid' else 'g'}",
        f"Taste (self)    : {food.taste}/10",
        "",
        f"Value-for-money : {vfm} g protein per unit of money",
        f"Suggested use   : {use}",
        f"Recommendation  : {score} / 100  {_stars(score)}",
        f"                  {label}",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fitpick",
        description="Score a food for fitness-conscious buying decisions.",
    )
    p.add_argument("--version", action="version", version=f"fitpick {__version__}")

    p.add_argument("--name", required=True, help="Name of the food.")
    p.add_argument(
        "--form",
        required=True,
        choices=["solid", "liquid"],
        help="Food form (solid or liquid). This selects the scoring standard.",
    )
    p.add_argument(
        "--serving",
        required=True,
        type=float,
        help="Serving size in grams (solid) or ml (liquid).",
    )
    p.add_argument("--protein", required=True, type=float, help="Protein per 100 g / ml.")
    p.add_argument("--sugar", required=True, type=float, help="Sugar per 100 g / ml.")
    p.add_argument("--fat", required=True, type=float, help="Fat per 100 g / ml.")
    p.add_argument("--sodium", required=True, type=float, help="Sodium (mg) per 100 g / ml.")
    p.add_argument("--calories", required=True, type=float, help="Calories (kcal) per 100 g / ml.")
    p.add_argument("--price", required=True, type=float, help="Price per serving.")
    p.add_argument(
        "--taste",
        required=True,
        type=float,
        help="Your own taste rating, 1 (awful) to 10 (amazing).",
    )
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    # Basic input sanity checks.
    if not (1 <= args.taste <= 10):
        print("Error: --taste must be between 1 and 10.", file=sys.stderr)
        return 1
    if args.serving <= 0:
        print("Error: --serving must be positive.", file=sys.stderr)
        return 1
    if args.price <= 0:
        print("Error: --price must be positive.", file=sys.stderr)
        return 1

    food = scoring.Food(
        name=args.name,
        form=args.form,
        serving_size=args.serving,
        protein=args.protein,
        sugar=args.sugar,
        fat=args.fat,
        sodium=args.sodium,
        calories=args.calories,
        price=args.price,
        taste=args.taste,
    )

    print(_report(food))
    return 0


if __name__ == "__&#8203;main__":
    sys.exit(main())
