# -*- coding: utf-8 -*-
"""content.py — Đọc & xử lý 1 file nội dung (.md): front matter + markdown + các phép tính phụ."""
import os
import re
import yaml
import markdown as md_lib

from .loi import LoiFrontMatter
from .slug import chuyen_thanh_slug

_RE_FRONT_MATTER = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)$', re.DOTALL)
_MARKER_TOMTAT = "<!--tomtat-->"

_TIEN_ICH_MARKDOWN = ["extra", "toc", "codehilite", "sane_lists"]


def doc_front_matter(duong_dan_file: str):
    """Trả về (front_matter: dict, noi_dung_markdown: str)."""
    with open(duong_dan_file, "r", encoding="utf-8") as f:
        toan_van = f.read()
    m = _RE_FRONT_MATTER.match(toan_van)
    if not m:
        raise LoiFrontMatter(duong_dan_file, "--- front matter ---")
    fm = yaml.safe_load(m.group(1)) or {}
    return fm, m.group(2)


def kiem_tra_truong_bat_buoc(fm: dict, duong_dan_file: str, cac_truong: list):
    for truong in cac_truong:
        if truong not in fm or fm[truong] in (None, ""):
            raise LoiFrontMatter(duong_dan_file, truong)


def render_markdown(noi_dung_md: str) -> str:
    return md_lib.markdown(noi_dung_md, extensions=_TIEN_ICH_MARKDOWN)


def tinh_excerpt(noi_dung_md: str, so_tu_mac_dinh: int) -> str:
    """Excerpt tự động: dùng marker <!--tomtat--> nếu có, ngược lại cắt N từ đầu."""
    if _MARKER_TOMTAT in noi_dung_md:
        phan_dau = noi_dung_md.split(_MARKER_TOMTAT, 1)[0]
        return render_markdown(phan_dau.strip())

    tu = noi_dung_md.split()
    phan_dau = " ".join(tu[:so_tu_mac_dinh])
    if len(tu) > so_tu_mac_dinh:
        phan_dau += "…"
    return render_markdown(phan_dau)


def tinh_thoi_gian_doc(noi_dung_md: str, so_tu_moi_phut: int) -> int:
    so_tu = len(noi_dung_md.split())
    phut = max(1, round(so_tu / so_tu_moi_phut))
    return phut


def lay_slug(fm: dict, duong_dan_file: str) -> str:
    if fm.get("slug"):
        return chuyen_thanh_slug(str(fm["slug"]))
    ten_file = os.path.splitext(os.path.basename(duong_dan_file))[0]
    # Bỏ tiền tố ngày YYYY-MM-DD- nếu có, giữ lại phần tiêu đề để tạo slug từ chính nó
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", ten_file)
    goc = m.group(1) if m else ten_file
    if fm.get("tieu_de"):
        return chuyen_thanh_slug(str(fm["tieu_de"]))
    return chuyen_thanh_slug(goc)
