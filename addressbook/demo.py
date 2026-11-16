"""Clearly fictional contacts for reproducible assignment demonstrations."""

SAMPLE_CONTACTS = [
    {
        "name": "Alice Chen", "company": "FZU–MU Study Group", "job_title": "Project partner",
        "notes": "Fictional demonstration contact. Prefers university email.", "bookmarked": True,
        "methods": [
            {"type": "phone", "label": "Mobile", "value": "+86 138 0000 0101"},
            {"type": "phone", "label": "Home", "value": "001234567890"},
            {"type": "email", "label": "University", "value": "alice.chen@example.com"},
            {"type": "email", "label": "Personal", "value": "alice.personal@example.org"},
            {"type": "social", "label": "WeChat", "value": "alice_demo"},
        ],
    },
    {
        "name": "James Wilson", "company": "Design Society", "job_title": "Designer",
        "notes": "Fictional demonstration contact. Meet after the weekly workshop.", "bookmarked": False,
        "methods": [
            {"type": "email", "label": "Work", "value": "james.wilson@example.com"},
            {"type": "website", "label": "Portfolio", "value": "https://example.com/james"},
            {"type": "address", "label": "Studio", "value": "12 Example Street, Fuzhou"},
        ],
    },
    {
        "name": "Sofia Patel", "company": "Campus Volunteers", "job_title": "Coordinator",
        "notes": "Fictional demonstration contact. Available on weekdays.", "bookmarked": True,
        "methods": [
            {"type": "phone", "label": "Mobile", "value": "+44 7700 900123"},
            {"type": "email", "label": "Volunteer", "value": "sofia.patel@example.org"},
            {"type": "social", "label": "Social", "value": "@sofia_demo"},
            {"type": "other", "label": "Office", "value": "Example Building, Room 204"},
        ],
    },
    {
        "name": "林浩 Lin Hao", "company": "Engineering Club", "job_title": "Developer",
        "notes": "Fictional demonstration contact. Unicode names are supported.", "bookmarked": False,
        "methods": [
            {"type": "phone", "label": "Mobile", "value": "+86 139 0000 0202"},
            {"type": "email", "label": "Club", "value": "lin.hao@example.com"},
        ],
    },
]
