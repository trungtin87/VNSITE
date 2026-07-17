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
    tinh_excerpt, tinh_thoi_gian_doc, lay_slug, dam_bao_co_front_matter,
)
from .seo import sinh_the_seo
from .loi import LoiVNSITE, LoiTrungSlug
from .slug import chuyen_thanh_slug
from .permalink import sinh_permalink
from .sitemap import sinh_sitemap
from .rss import sinh_rss

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
    # the_tag: dùng cho template — "ten" để hiển thị (giữ dấu/hoa như người viết gõ),
    # "slug" để làm URL /tag/slug/ (không dấu, không hoa, không khoảng trắng)
    # -> click vào tag không còn bị lỗi "không tìm thấy" khi tag có dấu/khoảng trắng/viết hoa.
    the_tag = [{"ten": t, "slug": chuyen_thanh_slug(t)} for t in tags]

    noi_dung_html = render_markdown(noi_dung_md)
    excerpt = tinh_excerpt(noi_dung_md, cau_hinh["so_tu_tomtat_mac_dinh"])
    thoi_gian_doc = tinh_thoi_gian_doc(noi_dung_md, cau_hinh["so_tu_moi_phut_doc"])

    mau_permalink = cau_hinh.get("permalink_bai_viet") or "/:chuyen_muc/:nam/:thang/:slug/"
    url = sinh_permalink(mau_permalink, chuyen_muc=chuyen_muc, nam=nam, thang=thang, slug=slug)

    return {
        "tieu_de": fm["tieu_de"],
        "mo_ta": fm.get("mo_ta", excerpt_thanh_text(excerpt)),
        "ngay": ngay,
        "nam": nam,
        "thang": thang,
        "chuyen_muc": chuyen_muc,
        "slug": slug,
        "tags": tags,
        "the_tag": the_tag,
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


def _doc_mot_du_an(duong_dan_file, cau_hinh):
    fm, noi_dung_md = doc_front_matter(duong_dan_file)
    kiem_tra_truong_bat_buoc(fm, duong_dan_file, ["tieu_de", "mo_ta_ngan"])
    slug = lay_slug(fm, duong_dan_file)
    mau_permalink = cau_hinh.get("permalink_du_an") or "/du-an/:slug/"
    return {
        "tieu_de": fm["tieu_de"],
        "mo_ta_ngan": fm["mo_ta_ngan"],
        "anh_dai_dien": fm.get("anh_dai_dien", ""),
        "cong_nghe": fm.get("cong_nghe", []),
        "gia": fm.get("gia", ""),
        "anh_slider": fm.get("anh_slider") or ([fm["anh_dai_dien"]] if fm.get("anh_dai_dien") else []),
        "link_demo": fm.get("link_demo", ""),
        "link_github": fm.get("link_github", ""),
        "khach_hang": fm.get("khach_hang", ""),
        "danh_muc": fm.get("danh_muc", ""),
        "ngay_du_an": fm.get("ngay_du_an", ""),
        "layout": fm.get("layout", "trangweb.html"),
        "slug": slug,
        "url": sinh_permalink(mau_permalink, slug=slug),
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
            if dam_bao_co_front_matter(duong_dan_file, loai="bai_viet"):
                log(f"  (tự sinh front matter nháp cho: {ten_file} — vào sửa lại cho đúng ý)")
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
                duong_dan_file = os.path.join(thu_muc_du_an, ten_file)
                if dam_bao_co_front_matter(duong_dan_file, loai="du_an"):
                    log(f"  (tự sinh front matter nháp cho: {ten_file} — vào sửa lại cho đúng ý)")
                tat_ca_du_an.append(_doc_mot_du_an(duong_dan_file, cau_hinh))

    # ---------- 3. Danh sách tag ----------
    # Gom theo SLUG (không dấu/không hoa/không khoảng trắng) để nhiều cách viết
    # cùng 1 tag (vd "Python" và "python") không tạo ra 2 trang tag khác nhau,
    # và để URL /tag/.../ luôn hợp lệ dù tag gốc có dấu tiếng Việt.
    nhan_tag = {}  # slug -> tên hiển thị gốc (giữ lần xuất hiện đầu tiên)
    for bai in tat_ca_bai:
        for t in bai["tags"]:
            nhan_tag.setdefault(chuyen_thanh_slug(t), t)
    tat_ca_tag = sorted(nhan_tag.keys())

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

    # Giai đoạn 3 (tùy chọn): ô tìm kiếm phía client, chỉ sinh HTML nếu được bật
    if (cau_hinh.get("tim_kiem") or {}).get("bat"):
        khoi_tim_kiem = (
            '<div hien-thi="khung-chua" class="hop-tim-kiem">'
            '<input type="search" id="o-tim-kiem" placeholder="Tìm bài viết..." '
            'aria-label="Tìm bài viết" autocomplete="off">'
            '<ul id="ket-qua-tim-kiem" class="ket-qua-tim-kiem"></ul>'
            '</div>'
        )
    else:
        khoi_tim_kiem = ""

    ngu_canh_goc = {
        "cau_hinh": cau_hinh,
        "du_lieu": du_lieu,
        "site": cau_hinh,  # bí danh ngắn gọn dùng trong template
        "tat_ca_bai_viet": tat_ca_bai,
        "tat_ca_du_an": tat_ca_du_an,
        "tat_ca_tag": tat_ca_tag,
        "khoi_giscus": khoi_giscus,
        "khoi_tim_kiem": khoi_tim_kiem,
    }

    so_trang_da_sinh = 0
    url_cho_sitemap = []  # list các (url, lastmod) gom dần trong lúc build, dùng sinh sitemap.xml cuối cùng

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
        url_cho_sitemap.append((bai["url"], str(bai["ngay"])[:10]))
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
        # Mỗi dự án có thể chọn layout riêng qua front matter "layout:"
        # (mặc định trangweb.html; đặt "agency-duan-chitiet.html" để dùng giao diện Agency)
        duong_dan_layout_du_an_nay = os.path.join(thu_muc_layout, du_an.get("layout") or "trangweb.html")
        html = engine.render_trang(duong_dan_layout_du_an_nay, ngu_canh)
        _ghi_file(os.path.join(thu_muc_output, du_an["url"].strip("/"), "index.html"), html)
        url_cho_sitemap.append((du_an["url"], None))
        so_trang_da_sinh += 1
    log(f"✓ Đã sinh {len(tat_ca_du_an)} trang dự án")

    # ---------- 6. Trang liệt kê theo tag ----------
    mau_permalink_tag = cau_hinh.get("permalink_tag") or "/tag/:slug/"
    for slug_tag in tat_ca_tag:
        ten_tag = nhan_tag[slug_tag]
        url_tag = sinh_permalink(mau_permalink_tag, slug=slug_tag)
        bai_theo_tag = [b for b in tat_ca_bai if slug_tag in {chuyen_thanh_slug(t) for t in b["tags"]}]
        ngu_canh = dict(ngu_canh_goc)
        ngu_canh["tag_hien_tai"] = ten_tag
        ngu_canh["danh_sach_bai_viet"] = bai_theo_tag
        ngu_canh["tieu_de_liet_ke"] = f"Tag: #{ten_tag}"
        ngu_canh["noi_dung_trang"] = ""
        ngu_canh["tieu_de_trang"] = f'Tag: {ten_tag} — {cau_hinh["ten_trangweb"]}'
        ngu_canh["the_seo"] = sinh_the_seo(cau_hinh, f"Tag: {ten_tag}", cau_hinh["mo_ta"], url_tag)
        html = engine.render_trang(duong_dan_layout_trangweb, ngu_canh)
        _ghi_file(os.path.join(thu_muc_output, url_tag.strip("/"), "index.html"), html)
        url_cho_sitemap.append((url_tag, None))
        so_trang_da_sinh += 1
    log(f"✓ Đã sinh {len(tat_ca_tag)} trang tag")

    # ---------- 6b. Trang liệt kê /bai-viet/ (CÓ PHÂN TRANG) và /du-an/ ----------
    so_bai_moi_trang = cau_hinh.get("so_bai_moi_trang") or 10
    tong_so_trang_bv = max(1, -(-len(tat_ca_bai) // so_bai_moi_trang))  # chia lấy trần
    for so_trang in range(1, tong_so_trang_bv + 1):
        bat_dau = (so_trang - 1) * so_bai_moi_trang
        bai_trong_trang = tat_ca_bai[bat_dau: bat_dau + so_bai_moi_trang]
        url_trang_nay = "/bai-viet/" if so_trang == 1 else f"/bai-viet/trang-{so_trang}/"

        ngu_canh = dict(ngu_canh_goc)
        ngu_canh["danh_sach_bai_viet"] = bai_trong_trang
        ngu_canh["danh_sach_du_an"] = []
        ngu_canh["tieu_de_liet_ke"] = "Tất cả bài viết" if so_trang == 1 else f"Bài viết — trang {so_trang}"
        ngu_canh["noi_dung_trang"] = ""
        ngu_canh["tieu_de_trang"] = f'Bài viết — {cau_hinh["ten_trangweb"]}'
        ngu_canh["the_seo"] = sinh_the_seo(cau_hinh, "Bài viết", cau_hinh["mo_ta"], url_trang_nay)
        # Ngữ cảnh phân trang, dùng trong template bằng {% neu phan_trang.co_trang_truoc %}...
        ngu_canh["phan_trang"] = {
            "trang_hien_tai": so_trang,
            "tong_so_trang": tong_so_trang_bv,
            "co_trang_truoc": so_trang > 1,
            "co_trang_sau": so_trang < tong_so_trang_bv,
            "url_trang_truoc": "/bai-viet/" if so_trang == 2 else f"/bai-viet/trang-{so_trang - 1}/",
            "url_trang_sau": f"/bai-viet/trang-{so_trang + 1}/",
        }
        html = engine.render_trang(duong_dan_layout_trangweb, ngu_canh)
        _ghi_file(os.path.join(thu_muc_output, url_trang_nay.strip("/"), "index.html"), html)
        url_cho_sitemap.append((url_trang_nay, None))
        so_trang_da_sinh += 1

    ngu_canh = dict(ngu_canh_goc)
    ngu_canh["danh_sach_bai_viet"] = []
    ngu_canh["danh_sach_du_an"] = tat_ca_du_an
    ngu_canh["tieu_de_liet_ke"] = "Dự án"
    ngu_canh["noi_dung_trang"] = ""
    ngu_canh["tieu_de_trang"] = f'Dự án — {cau_hinh["ten_trangweb"]}'
    ngu_canh["the_seo"] = sinh_the_seo(cau_hinh, "Dự án", cau_hinh["mo_ta"], "/du-an/")
    html = engine.render_trang(duong_dan_layout_trangweb, ngu_canh)
    _ghi_file(os.path.join(thu_muc_output, "du-an", "index.html"), html)
    url_cho_sitemap.append(("/du-an/", None))
    so_trang_da_sinh += 1
    log(f"✓ Đã sinh trang liệt kê /bai-viet/ ({tong_so_trang_bv} trang) và /du-an/")

    # ---------- 7. Trang tĩnh trong gốc dự án (index.html người dùng tự viết, v.v.) ----------
    # Bất kỳ file .html ở gốc dự án dùng {% ke_thua %} sẽ được coi là 1 "trang tĩnh".
    # "index.html" giữ nguyên ở gốc (URL "/"); các file khác xuất thành ten/index.html
    # để khớp với URL có dấu "/" ở cuối (ví dụ "/gioi-thieu/" trong _cauhinhtrangweb.yml).
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

            if ten_file == "index.html":
                duong_dan_ra = os.path.join(thu_muc_output, "index.html")
                url_trang_tinh = "/"
            else:
                ten_khong_duoi = os.path.splitext(ten_file)[0]
                duong_dan_ra = os.path.join(thu_muc_output, ten_khong_duoi, "index.html")
                url_trang_tinh = f"/{ten_khong_duoi}/"

            _ghi_file(duong_dan_ra, html)
            url_cho_sitemap.append((url_trang_tinh, None))
            so_trang_da_sinh += 1

    # ---------- 8. Sao chép tài nguyên tĩnh (css/js/hình ảnh) ----------
    _sao_chep_tainguyen(duong_dan_goc, thu_muc_output)

    # ---------- 8b. Tìm kiếm phía client: sinh search-index.json (mục VI, 🟢 tùy chọn) ----------
    if (cau_hinh.get("tim_kiem") or {}).get("bat"):
        import json
        chi_muc = [
            {
                "tieu_de": b["tieu_de"],
                "url": b["url"],
                "van_ban": excerpt_thanh_text(b["excerpt"]),
                "tags": b["tags"],
            }
            for b in tat_ca_bai
        ]
        _ghi_file(
            os.path.join(thu_muc_output, "search-index.json"),
            json.dumps(chi_muc, ensure_ascii=False),
        )
        log(f"✓ Đã sinh search-index.json ({len(chi_muc)} bài viết)")

    # ---------- 9. File hỗ trợ GitHub Pages ----------
    _ghi_file(os.path.join(thu_muc_output, ".nojekyll"), "")

    # ---------- 10. sitemap.xml (chuẩn sitemaps.org) ----------
    _ghi_file(os.path.join(thu_muc_output, "sitemap.xml"), sinh_sitemap(cau_hinh, url_cho_sitemap))
    if not cau_hinh.get("url"):
        log("  (lưu ý: chưa khai 'url:' trong _cauhinhtrangweb.yml -> sitemap.xml sẽ thiếu tên miền đầy đủ)")
    log("✓ Đã sinh sitemap.xml")

    # ---------- 11. rss.xml (RSS 2.0, các bài viết mới nhất) ----------
    _ghi_file(
        os.path.join(thu_muc_output, "rss.xml"),
        sinh_rss(cau_hinh, tat_ca_bai, excerpt_thanh_text),
    )
    log("✓ Đã sinh rss.xml")

    # ---------- 12. robots.txt (trỏ tới sitemap.xml) ----------
    goc_va_baseurl = f'{(cau_hinh.get("url") or "").rstrip("/")}{cau_hinh.get("baseurl") or ""}'
    _ghi_file(
        os.path.join(thu_muc_output, "robots.txt"),
        f"User-agent: *\nAllow: /\nSitemap: {goc_va_baseurl}/sitemap.xml\n",
    )

    log(f"✓ Build hoàn tất: {so_trang_da_sinh} trang → '{cau_hinh['thu_muc_output']}/'")
    return so_trang_da_sinh
