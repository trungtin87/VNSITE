# -*- coding: utf-8 -*-
"""sitemap.py — Sinh sitemap.xml (chuẩn sitemaps.org) từ danh sách URL đã build."""
from xml.sax.saxutils import escape


def sinh_sitemap(cau_hinh: dict, danh_sach_url: list) -> str:
    """danh_sach_url: list các tuple (url_tuong_doi, lastmod) — lastmod dạng
    "YYYY-MM-DD" hoặc None nếu không có (sẽ bỏ qua thẻ <lastmod>)."""
    goc = (cau_hinh.get("url") or "").rstrip("/")
    baseurl = cau_hinh.get("baseurl") or ""

    dong = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    da_them = set()
    for url, lastmod in danh_sach_url:
        if url in da_them:
            continue
        da_them.add(url)
        day_du = f"{goc}{baseurl}{url}"
        dong.append("  <url>")
        dong.append(f"    <loc>{escape(day_du)}</loc>")
        if lastmod:
            dong.append(f"    <lastmod>{lastmod}</lastmod>")
        dong.append("  </url>")
    dong.append("</urlset>")
    return "\n".join(dong)
