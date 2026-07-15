# -*- coding: utf-8 -*-
"""builder.py — Orchestrator: đọc toàn bộ nội dung nguồn, render và ghi ra _ketqua/."""
import os
import re
import shutil
import sys

from .config import doc_cau_hinh, doc_du_lieu
from .template import BoMayTemplate
from .content import (
    doc_front_matter, kiem_tra_truong_bat_buoc, render_markdown,
    tinh_excerpt, tinh_thoi_gian_doc, lay_slug,
)
from .seo import sinh_the_seo
from .loi import LoiVNSITE, LoiTrungSlug
from .slug import chuyen_thanh_slug

_RE_NGAY_TU_TEN_FILE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-")


def _ghi_file(duong_dan: str, noi_dung: str):
    os.makedirs(os.path.dirname(duong_dan), exist_ok=True)
    with open(duong_dan, "w", encoding="utf-8") as f:
        f.write(noi_dung)


def _doc_mot_bai_viet(duong_dan_file, cau_hinh):
    fm, noi_dung_md = doc_front_matter(duong_dan_file)
    kiem_tra_truong_bat_buoc(fm, duong_dan_file, ["tieu_de"])

    ten_file = os.path.basename(duong_dan_file)
    m_ngay = _RE_NGAY_TU_TEN_FILE.match(ten_file)
    if fm.get("ngay"):
        ngay = str(fm["ngay"])
    elif m_ngay:
        ngay = f"{m_ngay.group(1)}-{m_ngay.group(2)}-{m_ngay.group(3)}"
    else:
        ngay = "1970-01-01"
    nam, thang, _ngay_trong_thang = ngay.split("-")

    # Mục II.4: category/chuyen_muc quyết định thư mục output; thiếu -> mặc định "bai-viet"
    chuyen_muc = chuyen_thanh_slug(fm["chuyen_muc"]) if fm.get("chuyen_muc") else "bai-viet"
    slug = lay_slug(fm, duong_dan_file)

    tags = fm.get("tags") or fm.get("the") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    noi_dung_html = render_markdown(noi_dung_md)
    excerpt = tinh_excerpt(noi_dung_md, cau_hinh["so_tu_tomtat_mac_dinh"])
    thoi_gian_doc = tinh_thoi_gian_doc(noi_dung_md, cau_hinh["so_tu_moi_phut_doc"])

    url = f"/{chuyen_muc}/{nam}/{thang}/{slug}/"

    return {
        "tieu_de": fm["tieu_de"],
        "mo_ta": fm.get("mo_ta", excerpt_thanh_text(excerpt)),
        "ngay": ngay,
        "nam": nam,
        "thang": thang,
        "chuyen_muc": chuyen_muc,
        "slug": slug,
        "tags": tags,
        "noi_dung": noi_dung_html,
        "excerpt": excerpt,
        "thoi_gian_doc": thoi_gian_doc,
        "url": url,
        "anh_bia": fm.get("anh_bia", ""),
        "nhap": bool(fm.get("nhap", False)),
        "duong_dan_nguon": duong_dan_file,
        "_fm": fm,
    }


def excerpt_thanh_text(excerpt_html: str) -> str:
    return re.sub("<[^>]+>", "", excerpt_html).strip()


def _doc_mot_du_an(duong_dan_file):
    fm, noi_dung_md = doc_front_matter(duong_dan_file)
    kiem_tra_truong_bat_buoc(fm, duong_dan_file, ["tieu_de", "mo_ta_ngan"])
    slug = lay_slug(fm, duong_dan_file)
    cong_nghe = fm.get("cong_nghe", [])
    # Ghi chú: bộ máy template (template.py) không hỗ trợ {% moi %} lồng nhau
    # (regex non-greedy sẽ khớp nhầm {% het %} của vòng lặp bên trong), nên
    # ở đây dựng sẵn chuỗi HTML <li> cho danh sách công nghệ, dùng trực tiếp
    # bằng {{ du_an.cong_nghe_html }} thay vì lặp lồng trong vòng lặp dự án.
    cong_nghe_html = "".join(f"<li>{c}</li>" for c in cong_nghe)
    return {
        "tieu_de": fm["tieu_de"],
        "mo_ta_ngan": fm["mo_ta_ngan"],
        "anh_dai_dien": fm.get("anh_dai_dien", ""),
        "cong_nghe": cong_nghe,
        "cong_nghe_html": cong_nghe_html,
        "link_demo": fm.get("link_demo", ""),
        "link_github": fm.get("link_github", ""),
        "slug": slug,
        "url": f"/du-an/{slug}/",
        "noi_dung": render_markdown(noi_dung_md),
    }



def _lay_bai_lien_quan(bai_hien_tai, tat_ca_bai, so_luong=3):
    """Related posts: xếp hạng theo số tag trùng nhau nhiều nhất (mục V)."""
    the_hien_tai = set(bai_hien_tai["tags"])
    if not the_hien_tai:
        return []
    ung_vien = []
    for bai in tat_ca_bai:
        if bai["url"] == bai_hien_tai["url"]:
            continue
        trung = len(the_hien_tai & set(bai["tags"]))
        if trung > 0:
            ung_vien.append((trung, bai))
    ung_vien.sort(key=lambda x: x[0], reverse=True)
    return [bai for _, bai in ung_vien[:so_luong]]


_DUOI_BO_QUA_O_GOC = (".py", ".yml", ".yaml", ".md")
_TEN_FILE_BO_QUA_O_GOC = {"requirements.txt"}


def _sao_chep_file_tinh_o_goc(goc, dich):
    """Sao chép các file tĩnh nằm thẳng ở gốc dự án (robots.txt, sitemap.xml,
    rss.xml, manifest.webmanifest, favicon.svg, v.v.) sang gốc _ketqua/.
    Đây là phần mở rộng nhỏ ngoài đặc tả gốc: engine chỉ copy tainguyen/ và
    các trang .html có {% ke_thua %}, nhưng các file phục vụ tìm kiếm/PWA vẫn
    cần nằm đúng ở gốc domain, không thể đặt trong tainguyen/.
    """
    for ten_file in os.listdir(goc):
        duong_dan = os.path.join(goc, ten_file)
        if not os.path.isfile(duong_dan):
            continue
        if ten_file.startswith("."):
            continue
        if ten_file.endswith(".html") or ten_file.endswith(_DUOI_BO_QUA_O_GOC):
            continue
        if ten_file in _TEN_FILE_BO_QUA_O_GOC:
            continue
        shutil.copy2(duong_dan, os.path.join(dich, ten_file))


def _sao_chep_tainguyen(goc, dich):
    thu_muc_nguon = os.path.join(goc, "tainguyen")
    thu_muc_dich = os.path.join(dich, "tainguyen")
    if os.path.isdir(thu_muc_nguon):
        if os.path.isdir(thu_muc_dich):
            shutil.rmtree(thu_muc_dich)
        shutil.copytree(thu_muc_nguon, thu_muc_dich)

    # "Gộp" các file .scss thành main.css (chỉ nối chuỗi thô — xem mục II.6 của đặc tả:
    # nếu không biên dịch biến/nesting thật thì phải gọi đúng tên bản chất là CSS thuần).
    thu_muc_css = os.path.join(thu_muc_dich, "css")
    if os.path.isdir(thu_muc_css):
        file_scss = sorted(f for f in os.listdir(thu_muc_css) if f.endswith(".scss"))
        if file_scss:
            noi_dung_gop = []
            for f in file_scss:
                with open(os.path.join(thu_muc_css, f), "r", encoding="utf-8") as fh:
                    noi_dung_gop.append(f"/* --- {f} --- */\n" + fh.read())
            _ghi_file(os.path.join(thu_muc_css, "main.css"), "\n\n".join(noi_dung_gop))


def _sinh_chi_muc_tim_kiem(tat_ca_bai, thu_muc_output):
    """Tự sinh tainguyen/js/search-data.js từ danh sách bài viết THẬT mỗi lần
    build, để URL trong chỉ mục tìm kiếm không bao giờ bị lệch so với URL
    thật của trang (lỗi thường gặp nếu để file này viết tay/copy thủ công).
    """
    import json as _json

    muc = []
    for bai in tat_ca_bai:
        muc.append({
            "title": bai["tieu_de"],
            "url": bai["url"],
            "category": bai.get("_fm", {}).get("danh_muc", bai.get("chuyen_muc", "")),
            "desc": bai.get("mo_ta", ""),
        })
    noi_dung = (
        "// Chỉ mục tìm kiếm — SINH TỰ ĐỘNG bởi vnsite_engine/builder.py "
        "(_sinh_chi_muc_tim_kiem) mỗi lần build.\n"
        "// KHÔNG chỉnh tay tệp này — hãy sửa front matter bài viết trong "
        "_cacbaiviet/ rồi build lại.\n"
        "export const searchIndex = " + _json.dumps(muc, ensure_ascii=False, indent=2) + ";\n"
    )
    duong_dan = os.path.join(thu_muc_output, "tainguyen", "js", "search-data.js")
    os.makedirs(os.path.dirname(duong_dan), exist_ok=True)
    with open(duong_dan, "w", encoding="utf-8") as f:
        f.write(noi_dung)


def build(duong_dan_goc: str, che_do_preview: bool = False, im_lang: bool = False):
    """Hàm build chính. Trả về số trang đã sinh ra. Ném LoiVNSITE nếu có lỗi cấu hình/nội dung."""
    def log(msg):
        if not im_lang:
            print(msg)

    cau_hinh = doc_cau_hinh(duong_dan_goc)
    du_lieu = doc_du_lieu(duong_dan_goc)
    thu_muc_output = os.path.join(duong_dan_goc, cau_hinh["thu_muc_output"])

    if os.path.isdir(thu_muc_output):
        shutil.rmtree(thu_muc_output)
    os.makedirs(thu_muc_output, exist_ok=True)

    engine = BoMayTemplate(duong_dan_goc)
    thu_muc_layout = engine.thu_muc_layout

    # ---------- 1. Đọc toàn bộ bài viết ----------
    thu_muc_bai_viet = os.path.join(duong_dan_goc, "_cacbaiviet")
    tat_ca_bai = []
    slug_da_thay = {}  # (chuyen_muc, slug) -> duong_dan_file, để phát hiện trùng
    if os.path.isdir(thu_muc_bai_viet):
        for ten_file in sorted(os.listdir(thu_muc_bai_viet)):
            if not ten_file.endswith(".md"):
                continue
            duong_dan_file = os.path.join(thu_muc_bai_viet, ten_file)
            bai = _doc_mot_bai_viet(duong_dan_file, cau_hinh)
            if bai["nhap"] and not che_do_preview:
                log(f"  (bỏ qua bản nháp: {ten_file})")
                continue

            khoa = (bai["chuyen_muc"], bai["slug"])
            if khoa in slug_da_thay:
                loi_trung = LoiTrungSlug(bai["slug"], slug_da_thay[khoa], duong_dan_file)
                log(str(loi_trung))
            slug_da_thay[khoa] = duong_dan_file

            tat_ca_bai.append(bai)

    tat_ca_bai.sort(key=lambda b: b["ngay"], reverse=True)

    # ---------- 2. Đọc toàn bộ dự án (portfolio) ----------
    thu_muc_du_an = os.path.join(duong_dan_goc, "_duan")
    tat_ca_du_an = []
    if os.path.isdir(thu_muc_du_an):
        for ten_file in sorted(os.listdir(thu_muc_du_an)):
            if ten_file.endswith(".md"):
                tat_ca_du_an.append(_doc_mot_du_an(os.path.join(thu_muc_du_an, ten_file)))

    # ---------- 3. Danh sách tag ----------
    tat_ca_tag = sorted({tag for bai in tat_ca_bai for tag in bai["tags"]})

    # Giai đoạn 3 (tùy chọn): khung bình luận giscus, chỉ sinh HTML nếu được bật trong cấu hình
    giscus_cfg = cau_hinh.get("giscus", {}) or {}
    if giscus_cfg.get("bat"):
        khoi_giscus = (
            '<div class="giscus-binh-luan">'
            f'<script src="https://giscus.app/client.js" '
            f'data-repo="{giscus_cfg.get("repo", "")}" '
            f'data-repo-id="{giscus_cfg.get("repo_id", "")}" '
            f'data-category="{giscus_cfg.get("category", "")}" '
            f'data-category-id="{giscus_cfg.get("category_id", "")}" '
            f'data-mapping="pathname" data-theme="preferred_color_scheme" '
            f'crossorigin="anonymous" async></script></div>'
        )
    else:
        khoi_giscus = ""

    ngu_canh_goc = {
        "cau_hinh": cau_hinh,
        "du_lieu": du_lieu,
        "site": cau_hinh,  # bí danh ngắn gọn dùng trong template
        "tat_ca_bai_viet": tat_ca_bai,
        "tat_ca_du_an": tat_ca_du_an,
        "tat_ca_tag": tat_ca_tag,
        "khoi_giscus": khoi_giscus,
    }

    so_trang_da_sinh = 0

    # ---------- 4. Render từng bài viết ----------
    duong_dan_layout_bai_viet = os.path.join(thu_muc_layout, "baiviet.html")
    for bai in tat_ca_bai:
        ngu_canh = dict(ngu_canh_goc)
        ngu_canh["bai_viet"] = bai
        ngu_canh["bai_lien_quan"] = _lay_bai_lien_quan(bai, tat_ca_bai)
        ngu_canh["tieu_de_trang"] = f'{bai["tieu_de"]} — {cau_hinh["ten_trangweb"]}'
        ngu_canh["the_seo"] = sinh_the_seo(
            cau_hinh, bai["tieu_de"], bai["mo_ta"], bai["url"], bai.get("anh_bia")
        )
        html = engine.render_trang(duong_dan_layout_bai_viet, ngu_canh)
        _ghi_file(os.path.join(thu_muc_output, bai["url"].strip("/"), "index.html"), html)
        so_trang_da_sinh += 1
    log(f"✓ Đã sinh {len(tat_ca_bai)} bài viết")

    # ---------- 5. Render từng trang dự án ----------
    duong_dan_layout_trangweb = os.path.join(thu_muc_layout, "trangweb.html")
    for du_an in tat_ca_du_an:
        ngu_canh = dict(ngu_canh_goc)
        ngu_canh["du_an"] = du_an
        ngu_canh["mo_dau_du_an"] = (
            f'<article class="chi-tiet-du-an"><h1>{du_an["tieu_de"]}</h1>'
            f'<p class="mo-ta-ngan">{du_an["mo_ta_ngan"]}</p>'
            f'<div class="noi-dung-markdown">{du_an["noi_dung"]}</div></article>'
        )
        ngu_canh["tieu_de_trang"] = f'{du_an["tieu_de"]} — {cau_hinh["ten_trangweb"]}'
        ngu_canh["the_seo"] = sinh_the_seo(cau_hinh, du_an["tieu_de"], du_an["mo_ta_ngan"], du_an["url"])
        html = engine.render_trang(duong_dan_layout_trangweb, ngu_canh)
        _ghi_file(os.path.join(thu_muc_output, du_an["url"].strip("/"), "index.html"), html)
        so_trang_da_sinh += 1
    log(f"✓ Đã sinh {len(tat_ca_du_an)} trang dự án")

    # ---------- 6. Trang liệt kê theo tag ----------
    for tag in tat_ca_tag:
        bai_theo_tag = [b for b in tat_ca_bai if tag in b["tags"]]
        ngu_canh = dict(ngu_canh_goc)
        ngu_canh["tag_hien_tai"] = tag
        ngu_canh["danh_sach_bai_viet"] = bai_theo_tag
        ngu_canh["tieu_de_liet_ke"] = f"Tag: #{tag}"
        ngu_canh["noi_dung_trang"] = ""
        ngu_canh["tieu_de_trang"] = f'Tag: {tag} — {cau_hinh["ten_trangweb"]}'
        ngu_canh["the_seo"] = sinh_the_seo(cau_hinh, f"Tag: {tag}", cau_hinh["mo_ta"], f"/tag/{tag}/")
        html = engine.render_trang(duong_dan_layout_trangweb, ngu_canh)
        _ghi_file(os.path.join(thu_muc_output, "tag", tag, "index.html"), html)
        so_trang_da_sinh += 1
    log(f"✓ Đã sinh {len(tat_ca_tag)} trang tag")

    # ---------- 7. Trang tĩnh trong gốc dự án (index.html người dùng tự viết, v.v.) ----------
    # Bất kỳ file .html ở gốc dự án dùng {% ke_thua %} sẽ được coi là 1 "trang tĩnh".
    for ten_file in os.listdir(duong_dan_goc):
        if ten_file.endswith(".html"):
            duong_dan_file = os.path.join(duong_dan_goc, ten_file)
            ngu_canh = dict(ngu_canh_goc)
            ngu_canh["danh_sach_bai_viet"] = tat_ca_bai
            ngu_canh["danh_sach_du_an"] = tat_ca_du_an
            ngu_canh["noi_dung_trang"] = ""
            ngu_canh["tieu_de_trang"] = cau_hinh["ten_trangweb"]
            ngu_canh["the_seo"] = sinh_the_seo(cau_hinh, cau_hinh["ten_trangweb"], cau_hinh["mo_ta"], "/")
            html = engine.render_trang(duong_dan_file, ngu_canh)
            _ghi_file(os.path.join(thu_muc_output, ten_file), html)
            so_trang_da_sinh += 1

    # ---------- 8. Sao chép tài nguyên tĩnh (css/js/hình ảnh) ----------
    _sao_chep_tainguyen(duong_dan_goc, thu_muc_output)
    _sao_chep_file_tinh_o_goc(duong_dan_goc, thu_muc_output)
    _sinh_chi_muc_tim_kiem(tat_ca_bai, thu_muc_output)

    # ---------- 9. File hỗ trợ GitHub Pages ----------
    _ghi_file(os.path.join(thu_muc_output, ".nojekyll"), "")

    log(f"✓ Build hoàn tất: {so_trang_da_sinh} trang → '{cau_hinh['thu_muc_output']}/'")
    return so_trang_da_sinh
