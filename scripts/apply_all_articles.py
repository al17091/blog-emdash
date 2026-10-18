# -*- coding: utf-8 -*-
"""
Master script to apply deep A4-report class content to seed/seed.json.
Merges Travel (JA) and Tech (EN) articles into EmDash Portable Text schema.
"""

import json
import os
import re
import uuid

from articles_travel import ARTICLES_TRAVEL
from articles_tech_infra import ARTICLES_TECH_INFRA
from articles_tech_sec_ai import ARTICLES_TECH_SEC_AI


def make_key(prefix="k"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def markdown_to_portable_text(md_text):
    lines = md_text.strip().split("\n")
    blocks = []
    i = 0
    buffer = []

    def flush_buffer():
        nonlocal buffer
        if buffer:
            text = " ".join(buffer).strip()
            if text:
                blocks.append({
                    "_type": "block",
                    "style": "normal",
                    "_key": make_key("b"),
                    "children": [{
                        "_type": "span",
                        "_key": make_key("s"),
                        "text": text
                    }]
                })
            buffer = []

    while i < len(lines):
        line = lines[i]
        trimmed = line.strip()

        if not trimmed:
            flush_buffer()
            i += 1
            continue

        if trimmed.startswith("### "):
            flush_buffer()
            blocks.append({
                "_type": "block",
                "style": "h3",
                "_key": make_key("b"),
                "children": [{
                    "_type": "span",
                    "_key": make_key("s"),
                    "text": trimmed[4:].strip()
                }]
            })
            i += 1
        elif trimmed.startswith("## "):
            flush_buffer()
            blocks.append({
                "_type": "block",
                "style": "h2",
                "_key": make_key("b"),
                "children": [{
                    "_type": "span",
                    "_key": make_key("s"),
                    "text": trimmed[3:].strip()
                }]
            })
            i += 1
        elif trimmed.startswith("> "):
            flush_buffer()
            blocks.append({
                "_type": "block",
                "style": "blockquote",
                "_key": make_key("b"),
                "children": [{
                    "_type": "span",
                    "_key": make_key("s"),
                    "text": trimmed[2:].strip()
                }]
            })
            i += 1
        elif trimmed.startswith("```"):
            flush_buffer()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code_text = "\n".join(code_lines)
            blocks.append({
                "_type": "block",
                "style": "normal",
                "_key": make_key("b"),
                "children": [{
                    "_type": "span",
                    "_key": make_key("s"),
                    "text": code_text
                }]
            })
            if i < len(lines) and lines[i].strip().startswith("```"):
                i += 1
        elif trimmed.startswith("- ") or trimmed.startswith("* ") or re.match(r"^\d+\.\s", trimmed) or trimmed.startswith("|"):
            flush_buffer()
            blocks.append({
                "_type": "block",
                "style": "normal",
                "_key": make_key("b"),
                "children": [{
                    "_type": "span",
                    "_key": make_key("s"),
                    "text": trimmed
                }]
            })
            i += 1
        elif trimmed.startswith("[📷 写真:"):
            flush_buffer()
            blocks.append({
                "_type": "block",
                "style": "blockquote",
                "_key": make_key("b"),
                "children": [{
                    "_type": "span",
                    "_key": make_key("s"),
                    "text": trimmed
                }]
            })
            i += 1
        elif trimmed == "---":
            flush_buffer()
            i += 1
        else:
            buffer.append(trimmed)
            i += 1

    flush_buffer()
    return blocks


def main():
    seed_file = os.path.abspath("seed/seed.json")
    with open(seed_file, "r", encoding="utf-8") as f:
        seed_data = json.load(f)

    all_articles = {}
    all_articles.update(ARTICLES_TRAVEL)
    all_articles.update(ARTICLES_TECH_INFRA)
    all_articles.update(ARTICLES_TECH_SEC_AI)

    print(f"Loaded {len(all_articles)} deep articles for expansion.")

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
            post["data"]["content"] = markdown_to_portable_text(art["markdown"])
            if "taxonomies" in art:
                post["taxonomies"] = art["taxonomies"]
            post["status"] = "draft"
            updated_count += 1
            print(f"  [UPDATED] {slug} -> {len(post['data']['content'])} blocks")

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
                    "content": markdown_to_portable_text(art["markdown"])
                }
            }
            posts.append(new_post)
            created_count += 1
            print(f"  [CREATED] {slug} -> {len(new_post['data']['content'])} blocks")

    print(f"\nSuccessfully processed posts: {updated_count} updated, {created_count} created (total {len(posts)}).")

    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, ensure_ascii=False, indent=2)

    print("seed/seed.json written successfully.")


if __name__ == "__main__":
    main()

