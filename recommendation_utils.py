def generate_final_recommendation(health_condition, rules, conflicts):
    from collections import defaultdict

    def normalize(text):
        return text.strip().lower()

    def remove_conflicts(recommendations, conflict_list):
        cleaned = []
        normalized = [normalize(r) for r in recommendations]
        for i, item in enumerate(normalized):
            skip = False
            for c1, c2 in conflict_list:
                if item == normalize(c1) and normalize(c2) in normalized:
                    skip = True
                    break
                if item == normalize(c2) and normalize(c1) in normalized:
                    skip = True
                    break
            if not skip:
                cleaned.append(recommendations[i])
        return list(set(cleaned))

    def group_similar(recommendations):
        merged_map = {
            ("rest", "use cool compress"): "Rest and use cool compress",
            ("consult a doctor", "consult doctor"): "Consult a doctor",
            ("monitor stress levels", "manage stress"): "Manage and monitor stress levels",
            ("medication if prescribed", "follow prescribed medications"): "Follow prescribed medications",
            ("avoid caffeine", "avoid caffeine and alcohol"): "Avoid caffeine and alcohol",
            ("no heavy lifting", "avoid heavy exertion"): "Avoid heavy exertion",
            ("no processed food", "avoid processed food"): "Avoid processed food",
            ("no refined sugars", "avoid refined sugars"): "Avoid refined sugars",
            ("walking", "light walking"): "Walking",
            ("yoga", "yoga, light walking"): "Yoga",
            ("cycling", "brisk walking"): "Brisk walking or cycling"
        }

        lowered = [normalize(item) for item in recommendations]
        result = []
        used = set()

        for i, item in enumerate(lowered):
            if item in used:
                continue
            merged = False
            for (a, b), combined in merged_map.items():
                if item in (normalize(a), normalize(b)):
                    if normalize(a) in lowered and normalize(b) in lowered:
                        result.append(combined)
                        used.update([normalize(a), normalize(b)])
                        merged = True
                        break
            if not merged:
                result.append(recommendations[i])
                used.add(item)
        return result

    categories = ['do', 'dont', 'diet', 'exercise']
    final = defaultdict(list)

    for key, val in health_condition.items():
        if key == 'oxygen':
            rule_key = 'spo2'
        else:
            rule_key = key

        condition = int(val)
        recs = rules[key].get(condition, {})
        for category in categories:
            final[category].extend(recs.get(category, []))

    for category in categories:
        final[category] = remove_conflicts(final[category], conflicts.get(category, []))
        final[category] = group_similar(final[category])

    return final
