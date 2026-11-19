
import re

from .onet_api import search_occupations


def normalize_title(value):
    """Normalize a career title for comparison."""
    value = value.casefold().strip()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value


def title_tokens(value):
    """Return meaningful words from a career title."""
    return set(normalize_title(value).split())


def rank_occupations(career, occupations):
    """Rank O*NET results by how closely their titles match."""
    query = normalize_title(career)
    query_words = title_tokens(career)

    ranked = []

    for item in occupations:
        title = item.get("title", "")
        normalized_title = normalize_title(title)
        title_words = title_tokens(title)

        if not normalized_title:
            continue

        # Exact title match is the strongest match.
        if normalized_title == query:
            score = 100

        # Prefer titles containing the complete search phrase.
        elif query in normalized_title:
            score = 85

        # Next, prefer titles whose words contain all query words.
        elif query_words and query_words.issubset(title_words):
            score = 75

        else:
            # Partial overlap is useful for ranking alternatives,
            # but is not strong enough for automatic selection.
            overlap = len(query_words & title_words)
            score = (
                40 * overlap / len(query_words)
                if query_words
                else 0
            )

        ranked.append((score, item))

    # Stable ordering preserves O*NET's original order when scores tie.
    ranked.sort(key=lambda entry: entry[0], reverse=True)

    return ranked


def resolve_career(career):
    career = career.strip() if isinstance(career, str) else ""

    if not career:
        return {
            "matched": False,
            "message": "Please enter a career name.",
            "occupations": [],
        }

    results = search_occupations(career)

    if not results:
        return {
            "matched": False,
            "message": "No matching career found in O*NET.",
            "occupations": [],
        }

    ranked = rank_occupations(career, results)

    if not ranked:
        return {
            "matched": False,
            "message": "No suitable occupation titles were found.",
            "occupations": [],
        }

    # Return the best three alternatives in relevance order.
    occupations = [item for _, item in ranked[:3]]

    return {
        "matched": True,
        "query": career,
        "occupations": occupations,
        "best_match_score": ranked[0][0],
    }


def get_best_occupation(career, occupation_code=None):
    result = resolve_career(career)

    if not result["matched"]:
        return None, result

    occupations = result["occupations"]

    # Respect the student's explicit selection.
    if occupation_code:
        for item in occupations:
            if item["code"] == occupation_code:
                return item, result

        # Search the original O*NET results again so a valid
        # selection is not rejected just because it was not in
        # the three displayed alternatives.
        all_results = search_occupations(career)

        for item in all_results:
            if item["code"] == occupation_code:
                return item, result

        return None, {
            "matched": False,
            "message": (
                "The selected occupation was not found in the "
                "current O*NET search results. Search again and "
                "select an available occupation."
            ),
            "occupations": occupations,
        }

    best_score = result["best_match_score"]

    # Automatically select only a strong title match.
    if best_score == 100:
        return occupations[0], result

    # Otherwise, let the student choose from the best alternatives.
    return None, {
        "matched": True,
        "selection_required": True,
        "message": (
            "Please select the occupation that best matches "
            "your intended career."
        ),
        "occupations": occupations,
    }
