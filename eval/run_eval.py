import json
import time
from pathlib import Path

import httpx

API_URL = "http://localhost:8000/extract"
CASES_FILE = Path(__file__).parent / "test_cases.json"

SIMPLE_FIELDS = [
    "rfq_number",
    "buyer_company",
    "issue_date",
    "response_deadline",
    "delivery_location",
    "delivery_date",
    "payment_terms",
    "currency",
]


def score_simple(expected, actual):
    """Text field. If expected is None, the model must also return null."""
    if expected is None:
        return 1.0 if actual in (None, "") else 0.0
    if actual is None:
        return 0.0
    return 1.0 if expected.lower() in str(actual).lower() else 0.0


def score_items(expected_items, actual_items):
    """Fraction of expected line items found with the right quantity and unit."""
    if not expected_items:
        return 1.0 if not actual_items else 0.0
    matched = 0
    used = set()
    for exp in expected_items:
        for i, act in enumerate(actual_items):
            if i in used:
                continue
            qty_ok = act.get("quantity") == exp["quantity"]
            unit_ok = (
                exp["unit"] is None
                or exp["unit"].lower() in str(act.get("unit") or "").lower()
            )
            if qty_ok and unit_ok:
                matched += 1
                used.add(i)
                break
    return matched / len(expected_items)


def score_requirements(expected_keywords, actual_list):
    """Fraction of expected keywords found in the special requirements."""
    if not expected_keywords:
        return 1.0 if not actual_list else 0.0
    text = " ".join(actual_list).lower()
    found = sum(1 for k in expected_keywords if k.lower() in text)
    return found / len(expected_keywords)


def score_case(expected, actual):
    scores = {}
    for field in SIMPLE_FIELDS:
        scores[field] = score_simple(expected[field], actual.get(field))
    scores["items"] = score_items(expected["items"], actual.get("items", []))
    scores["special_requirements"] = score_requirements(
        expected["special_requirements"], actual.get("special_requirements", [])
    )
    return scores


def main():
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    all_fields = SIMPLE_FIELDS + ["items", "special_requirements"]
    totals = {f: [] for f in all_fields}
    failed_cases = 0

    for number, case in enumerate(cases, start=1):
        print(f"\nCase {number}: {case['name']}")
        start = time.time()
        try:
            r = httpx.post(API_URL, json={"text": case["text"]}, timeout=300)
            if r.status_code != 200:
                print(f"  REQUEST FAILED: HTTP {r.status_code}")
                print(f"  Server said: {r.text}")
                failed_cases += 1
                scores = {f: 0.0 for f in all_fields}
                actual = {}
            else:
                actual = r.json()
                scores = score_case(case["expected"], actual)
        except Exception as e:
            print(f"  REQUEST FAILED: {e}")
            failed_cases += 1
            scores = {f: 0.0 for f in all_fields}
            actual = {}
        elapsed = round(time.time() - start, 1)

        for field, value in scores.items():
            totals[field].append(value)
            if value < 1.0 and actual:
                print(f"  MISS  {field}: score {value:.2f}, model returned: {actual.get(field)}")
        print(f"  ({elapsed} sec)")

    print("\n" + "=" * 46)
    print("ACCURACY PER FIELD (average across all cases)")
    print("=" * 46)
    grand = []
    for field in all_fields:
        avg = sum(totals[field]) / len(totals[field])
        grand.append(avg)
        print(f"{field:<22} {avg * 100:5.0f}%")
    print("-" * 46)
    print(f"{'OVERALL':<22} {sum(grand) / len(grand) * 100:5.0f}%")
    if failed_cases:
        print(f"\nWARNING: {failed_cases} case(s) failed to run. Fix that before trusting these scores.")


if __name__ == "__main__":
    main()