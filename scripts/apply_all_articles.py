# -*- coding: utf-8 -*-
"""
Master script to apply deep A4-report class content to seed/seed.json.
Merges Travel (JA) and Tech (EN) articles as raw Markdown (type: "text") into EmDash schema.
"""

import json
import os

from articles_travel import ARTICLES_TRAVEL
from articles_tech_infra import ARTICLES_TECH_INFRA
from articles_tech_sec_ai import ARTICLES_TECH_SEC_AI


def main():
    seed_file = os.path.abspath("seed/seed.json")
    with open(seed_file, "r", encoding="utf-8") as f:
        seed_data = json.load(f)

    # Ensure posts collection content field is type "text" (Raw Markdown)
    for col in seed_data.get("collections", []):
        if col.get("slug") == "posts":
            for field in col.get("fields", []):
                if field.get("slug") == "content":
                    field["type"] = "text"
                    field["label"] = "Content (Markdown)"
                    field["options"] = {"rows": 25}

    all_articles = {}
    all_articles.update(ARTICLES_TRAVEL)
    all_articles.update(ARTICLES_TECH_INFRA)
    all_articles.update(ARTICLES_TECH_SEC_AI)

    print(f"Loaded {len(all_articles)} deep articles (Raw Markdown).")

    posts = seed_data["content"]["posts"]
    updated_count = 0
    created_count = 0
    existing_slugs = set()

    for post in posts:
        slug = post.get("slug")
        if slug:
            existing_slugs.add(slug)
        if slug in all_articles:
            art = all_articles[slug]
            post["data"]["title"] = art["title"]
            post["data"]["excerpt"] = art["excerpt"]
            post["data"]["content"] = art["markdown"].strip()
            if "taxonomies" in art:
                post["taxonomies"] = art["taxonomies"]
            post["status"] = "draft"
            updated_count += 1
            print(f"  [UPDATED] {slug} -> {len(post['data']['content'])} chars (Markdown)")

    for slug, art in all_articles.items():
        if slug not in existing_slugs:
            new_post = {
                "id": f"posts:{slug}",
                "slug": slug,
                "status": "draft",
                "taxonomies": art.get("taxonomies", {
                    "theme": ["engineering"],
                    "category": ["infrastructure"],
                    "tag": ["cdn", "architecture", "devops"]
                }),
                "data": {
                    "title": art["title"],
                    "excerpt": art["excerpt"],
                    "content": art["markdown"].strip()
                }
            }
            posts.append(new_post)
            created_count += 1
            print(f"  [CREATED] {slug} -> {len(new_post['data']['content'])} chars (Markdown)")

    print(f"\nSuccessfully processed posts: {updated_count} updated, {created_count} created (total {len(posts)}).")

    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, ensure_ascii=False, indent=2)

    print("seed/seed.json written successfully.")


if __name__ == "__main__":
    main()


