"""Job discovery via web search.

This module provides search query generation for job discovery.
The actual searching is performed by the plugin orchestrator using
the WebSearch/FireCrawl tools available in the Claude environment.
"""

from job_search.config.loader import get_target_roles, get_locations


def generate_search_queries(config=None):
    roles = get_target_roles(config)
    locations = get_locations(config)
    primary_location = locations.get("primary", ["Bengaluru"])[0]

    queries = []

    for role in roles.get("tier1", []):
        queries.append({
            "query": f"{role} jobs {primary_location} fresher 2025 2026",
            "tier": 1,
            "role": role,
        })

    for role in roles.get("tier2", []):
        queries.append({
            "query": f"{role} jobs {primary_location} entry level 2025 2026",
            "tier": 2,
            "role": role,
        })

    queries.append({
        "query": f"APM program India 2025 2026 hiring fresher",
        "tier": 1,
        "role": "APM Program",
    })
    queries.append({
        "query": f"Associate Product Manager Bengaluru entry level hiring",
        "tier": 1,
        "role": "APM",
    })
    queries.append({
        "query": f"Product Analyst fresher Bengaluru hiring 2026",
        "tier": 1,
        "role": "Product Analyst",
    })
    queries.append({
        "query": f"AI Product Manager entry level India remote 2026",
        "tier": 1,
        "role": "AI Product Manager",
    })

    return queries


def generate_linkedin_queries(config=None):
    roles = get_target_roles(config)
    queries = []

    for role in roles.get("tier1", []):
        queries.append(f"site:linkedin.com/jobs \"{role}\" Bengaluru entry level")

    for role in roles.get("tier2", [])[:3]:
        queries.append(f"site:linkedin.com/jobs \"{role}\" Bengaluru fresher")

    return queries


def generate_ats_queries(config=None):
    roles = get_target_roles(config)
    queries = []

    ats_sites = ["greenhouse.io", "lever.co", "ashbyhq.com"]

    for role in roles.get("tier1", [])[:3]:
        for ats in ats_sites:
            queries.append(f"site:{ats} \"{role}\" India")

    return queries
