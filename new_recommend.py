
#1.recommendation rules

recommendation_rules = {
    'heart_rate': {
        0: {
            'do': ['Increase physical activity gradually', 'Practice breathing exercises'],
            'dont': ['Avoid heavy exertion', 'Do not skip meals'],
            'diet': ['Foods rich in iron and protein', 'Stay hydrated'],
            'exercise': ['Walking', 'Stretching']
        },
        1: {
            'do': ['Maintain current activity levels'],
            'dont': ['Avoid overexertion'],
            'diet': ['Balanced diet'],
            'exercise': ['Regular light exercise']
        },
        2: {
            'do': ['Monitor stress levels', 'Stay cool'],
            'dont': ['Avoid caffeine and alcohol', 'No heavy lifting'],
            'diet': ['Low sodium, high potassium foods'],
            'exercise': ['Yoga', 'Light cardio']
        }
    },
    'glucose': {
        0: {
            'do': ['Eat frequent small meals'],
            'dont': ['Avoid sugar crashes'],
            'diet': ['High-protein snacks', 'Whole grains'],
            'exercise': ['Light walking']
        },
        1: {
            'do': ['Maintain regular eating schedule'],
            'dont': ['Avoid sugary drinks'],
            'diet': ['Low-GI foods'],
            'exercise': ['Normal physical activity']
        },
        2: {
            'do': ['Check blood sugar regularly'],
            'dont': ['No refined sugars'],
            'diet': ['High-fiber, low-carb foods'],
            'exercise': ['Brisk walking', 'Cycling']
        }
    },
    'temperature': {
        0: {
            'do': ['Dress warmly'],
            'dont': ['Avoid cold exposure'],
            'diet': ['Warm fluids'],
            'exercise': ['Indoor light workouts']
        },
        1: {
            'do': ['Stay hydrated'],
            'dont': ['Avoid dehydration'],
            'diet': ['Normal diet'],
            'exercise': ['Regular activity']
        },
        2: {
            'do': ['Use cool compress', 'Rest'],
            'dont': ['Avoid hot environments'],
            'diet': ['Cold fluids', 'Fruits'],
            'exercise': ['None until fever subsides']
        }
    },
    'oxygen': {
        0: {
            'do': ['Practice breathing exercises', 'Use humidifier'],
            'dont': ['Avoid smoke exposure'],
            'diet': ['Iron-rich food'],
            'exercise': ['Guided respiratory therapy']
        },
        1: {
            'do': ['Stay active'],
            'dont': ['Avoid pollutants'],
            'diet': ['Balanced diet'],
            'exercise': ['Moderate aerobic exercise']
        },
        2: {
            'do': ['Consult a doctor', 'Reduce oxygen therapy'],
            'dont': ['Avoid excessive oxygen use'],
            'diet': ['As prescribed'],
            'exercise': ['Consult doctor']
        }
    },
    'systolic': {
        0: {
            'do': ['Increase fluid intake', 'Eat more salt'],
            'dont': ['Avoid alcohol'],
            'diet': ['Salted foods, caffeine (moderate)'],
            'exercise': ['Light leg exercises']
        },
        1: {
            'do': ['Maintain regular check-ups'],
            'dont': ['Avoid stress'],
            'diet': ['Balanced diet'],
            'exercise': ['Moderate aerobic']
        },
        2: {
            'do': ['Reduce sodium intake', 'Manage stress'],
            'dont': ['No processed food', 'Avoid caffeine'],
            'diet': ['Fruits, vegetables, whole grains'],
            'exercise': ['Walking, swimming']
        }
    },
    'diastolic': {
        0: {
            'do': ['Hydrate well', 'Stretch regularly'],
            'dont': ['Avoid standing too long'],
            'diet': ['Increased salt, fluids'],
            'exercise': ['Yoga, light walking']
        },
        1: {
            'do': ['Maintain current lifestyle'],
            'dont': ['Avoid drastic changes'],
            'diet': ['Balanced diet'],
            'exercise': ['Normal exercise']
        },
        2: {
            'do': ['Relaxation techniques', 'Medication if prescribed'],
            'dont': ['Avoid high-sodium foods'],
            'diet': ['Leafy greens, oats, beets'],
            'exercise': ['Mild aerobic']
        }
    }
}
# ------------------------------
# 2. Conflict Pairs
# ------------------------------
internal_conflicts = {
    'do': [
        ("increase physical activity", "maintain current activity"),
        ("stay active", "rest"),
        ("practice breathing exercises", "rest")
    ],
    'dont': [
        ("avoid heavy exertion", "no heavy exertion"),
    ],
    'diet': [
        ("high sodium", "low sodium"),
        ("sugar", "no sugar"),
        ("caffeine", "avoid caffeine")
    ],
    'exercise': [
        ("brisk walking", "none until fever subsides"),
        ("walking", "avoid walking"),
        ("moderate aerobic", "no exercise"),
        ("yoga", "no yoga"),
        ("cycling", "avoid cycling")
    ]
}

def generate_final_recommendation(health_condition, rules, conflicts):
    def normalize(text):
        return text.strip().lower()

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
        grouped = []
        used = set()

        for keys, replacement in merged_map.items():
            if all(any(k in item for item in lowered) for k in keys):
                grouped.append(replacement)
                used.update(keys)

        for item in recommendations:
            if all(normalize(item).find(key) == -1 for key in used):
                grouped.append(item.strip())

        return sorted(set(grouped))

    final_recommendation = {'do': [], 'dont': [], 'diet': [], 'exercise': []}

    for param, level in health_condition.items():
        param_rules = rules.get(param, {}).get(level, {})
        for key in final_recommendation:
            final_recommendation[key].extend(param_rules.get(key, []))

    for key in final_recommendation:
        # Normalize and deduplicate first
        final_recommendation[key] = sorted(set(map(str.strip, final_recommendation[key])))
        # Group similar
        final_recommendation[key] = group_similar(final_recommendation[key])
        # Remove conflicts
        for a, b in conflicts.get(key, []):
            normalized = [item.lower() for item in final_recommendation[key]]
            if a in normalized and b in normalized:
                final_recommendation[key] = [
                    item for item in final_recommendation[key]
                    if a not in item.lower() and b not in item.lower()
                ]

    return final_recommendation

# 5. Generate and Print Recommendations
user_health = {
    'glucose': 1,
    'systolic': 1,
    'diastolic': 1,
    'temperature': 1,
    'oxygen': 1,
    'heart_rate': 1
}

recommendation = generate_final_recommendation(user_health, recommendation_rules, internal_conflicts)

# print("\n📋 Final Health Recommendation (Cleaned, Grouped, Conflict-Free, Duplicate-Free):")
# for key in ['do', 'dont', 'diet', 'exercise']:
#     print(f"\n🔸 {key.upper()}:")
#     for val in recommendation[key]:
#         print(f"  ✅ {val}")


print("recommendation",recommendation)