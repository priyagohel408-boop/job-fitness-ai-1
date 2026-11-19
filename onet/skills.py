
def extract_skills(data):
    """Extract general O*NET skills without mixing in technology examples."""
    results = []

    def walk(value):
        if isinstance(value, dict):
            name = value.get("name")
            element = value.get("element")

            is_skill_record = (
                ("id" in value and isinstance(value.get("description"), str))
                or isinstance(element, (dict, str))
                or "importance" in value
                or "level" in value
            )

            if isinstance(name, str) and name.strip() and is_skill_record:
                results.append(name.strip())

            if isinstance(element, dict):
                element_name = element.get("name")
                if isinstance(element_name, str) and element_name.strip():
                    results.append(element_name.strip())

            for child in value.values():
                if isinstance(child, (dict, list)):
                    walk(child)

        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(data)
    return _deduplicate(results)


def extract_technology_skills(data):
    """
    Extract technology examples from O*NET technology-skills data.
    Category headings are deliberately not treated as individual technologies.
    """
    results = []

    def add_title(value):
        if isinstance(value, dict):
            title = value.get("title")
            if isinstance(title, str) and title.strip():
                results.append(title.strip())

    def walk_categories(value):
        if isinstance(value, dict):
            categories = value.get("category")

            if isinstance(categories, list):
                for category in categories:
                    if not isinstance(category, dict):
                        continue

                    # Only actual technology examples, not category titles.
                    for key in ("example", "example_more"):
                        examples = category.get(key, [])

                        if isinstance(examples, dict):
                            examples = [examples]

                        if isinstance(examples, list):
                            for example in examples:
                                add_title(example)

            # Support a response wrapped inside another object.
            for key, child in value.items():
                if key != "category" and isinstance(child, (dict, list)):
                    walk_categories(child)

        elif isinstance(value, list):
            for item in value:
                walk_categories(item)

    walk_categories(data)
    return _deduplicate(results)


def _deduplicate(items):
    """Remove duplicates while preserving the original order and labels."""
    unique = {}

    for item in items:
        if isinstance(item, str) and item.strip():
            cleaned = item.strip()
            unique.setdefault(cleaned.casefold(), cleaned)

    return list(unique.values())


def filter_career_skills(skills, limit=15):
    """Deduplicate skills and limit checklist size."""
    unique = _deduplicate(skills)
    return unique[:max(0, limit)]
