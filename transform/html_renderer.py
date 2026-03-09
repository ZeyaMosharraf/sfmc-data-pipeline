import json
import re
import pandas as pd


def render_blocks(html, blocks):
    if not html or not blocks:
        return html or ""

    for block_key, block_data in blocks.items():
        block_content = block_data.get("content", "")

        nested_slots = block_data.get("slots")
        if nested_slots:
            block_content = render_slots(block_content, nested_slots)

        pattern = (
            r'<div\s+data-type="block"\s+data-key="'
            + re.escape(block_key)
            + r'"(?:\s+data-original-key="[^"]*")?\s*>\s*</div>'
        )

        html, count = re.subn(pattern, block_content, html)

    return html


def render_slots(html, slots):
    if not html or not slots:
        return html or ""

    for slot_key, slot_data in slots.items():
        if not slot_data:
            continue

        slot_content = slot_data.get("content", "")
        blocks = slot_data.get("blocks", {})

        slot_content = render_blocks(slot_content, blocks)

        pattern = (
            r'<div\s+data-type="slot"\s+data-key="'
            + re.escape(slot_key)
            + r'"(?:\s+data-original-key="[^"]*")?\s*>\s*</div>'
        )

        html, count = re.subn(pattern, slot_content, html)

    return html


def render_asset(asset):

    asset_id = asset.get("id")
    asset_name = asset.get("name")

    if "views.html.content" in asset:
        template_html = asset.get("views.html.content")
        slots = asset.get("views.html.slots") or {}
    else:
        html_view = (asset.get("views") or {}).get("html") or {}
        template_html = html_view.get("content")
        slots = html_view.get("slots") or {}

    if not template_html:
        return None

    if not slots:
        return template_html

    final_html = render_slots(template_html, slots)

    return final_html


if __name__ == "__main__":

    with open("output/sfmc_html.json", "r", encoding="utf-8") as f:
        raw = json.load(f)

    assets = raw if isinstance(raw, list) else [raw]

    results = []

    for asset in assets:

        html = render_asset(asset)

        results.append({
            "id": asset.get("id"),
            "name": asset.get("name"),
            "html_content": html
        })

    for r in results:
        if r["html_content"]:
            filename = f"output/html_content/{r['id']}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(r["html_content"])

    df = pd.DataFrame(results)

    df.to_excel("output/html_content.xlsx", index=False)

    print(f"\nProcessed {len(results)} assets")
    print("Saved Excel file: output/html_content.xlsx")