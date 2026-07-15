# -*- coding: utf-8 -*-
"""
template.py — Bộ máy template tối giản của VNSITE.

Cú pháp hỗ trợ:
  {% ke_thua "ten_layout.html" %}      -> khai báo kế thừa, đặt ở dòng đầu file layout con
  {% khoi ten_khoi %} ... {% end %}    -> vùng nội dung có thể ghi đè (dùng ở cả cha lẫn con)
  {% nhung "ten_component.html" %}     -> nhúng 1 thành phần từ _thanhphantrang/
  {% moi x trong duong.dan %} ... {% het %}   -> lặp qua danh sách trong context
  {{ ten_bien }} / {{ x.thuoc_tinh }}  -> chèn giá trị biến

Thứ tự xử lý cho MỖI trang (đúng mục II.1 và II.2 của đặc tả):
  1. Giải quyết kế thừa layout (đệ quy cha/con, gộp các {% khoi %})
  2. Nhúng component — luôn dùng bản đã bóc tách <style> có sẵn trong cache
     bộ nhớ (self._cache_html / self._cache_css), KHÔNG đọc lại đĩa mỗi lần
  3. Xử lý vòng lặp {% moi %}
  4. Thay biến {{ }} còn lại
  5. Gom toàn bộ CSS đã bóc tách (không trùng lặp) chèn vào trước </head>
"""
import os
import re

from .loi import LoiIncludeKhongTonTai, LoiLayoutKhongTonTai

_RE_KE_THUA = re.compile(r'{%\s*ke_thua\s+"([^"]+)"\s*%}\s*\n?')
_RE_KHOI = re.compile(r'{%\s*khoi\s+(\w+)\s*%}(.*?){%\s*end\s*%}', re.DOTALL)
_RE_NHUNG = re.compile(r'{%\s*nhung\s+"([^"]+)"\s*%}')
_RE_MOI = re.compile(
    r'{%\s*moi\s+(\w+)\s+trong\s+([\w.]+)\s*%}(.*?){%\s*het\s*%}', re.DOTALL
)
_RE_BIEN = re.compile(r'{{\s*([\w.]+)\s*}}')
_RE_STYLE = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)


class BoMayTemplate:
    def __init__(self, duong_dan_goc: str):
        self.goc = duong_dan_goc
        self.thu_muc_layout = os.path.join(duong_dan_goc, "_bocuctrang")
        self.thu_muc_component = os.path.join(duong_dan_goc, "_thanhphantrang")
        # Cache toàn cục cho cả lần build: tránh đọc lại đĩa & tránh lặp <style>
        self._cache_html = {}   # ten_component -> html đã bóc tách style
        self._cache_css = {}    # ten_component -> nội dung css (str) hoặc "" nếu không có

    # ----------------------------------------------------------------- #
    # Tiện ích đọc file
    # ----------------------------------------------------------------- #
    @staticmethod
    def _doc(duong_dan):
        with open(duong_dan, "r", encoding="utf-8") as f:
            return f.read()

    # ----------------------------------------------------------------- #
    # Bước 3: bóc tách <style>, lưu cache; Bước 4: nhúng dùng bản cache
    # ----------------------------------------------------------------- #
    def _lay_component(self, ten_component: str, file_goi: str) -> str:
        """Trả về HTML đã làm sạch (không còn <style>) của 1 component, dùng cache."""
        if ten_component in self._cache_html:
            return self._cache_html[ten_component]

        duong_dan = os.path.join(self.thu_muc_component, ten_component)
        if not os.path.isfile(duong_dan):
            raise LoiIncludeKhongTonTai(ten_component, file_goi)

        noi_dung_goc = self._doc(duong_dan)

        # Component có thể tự nhúng component khác -> giải quyết đệ quy TRƯỚC khi bóc style
        # để style của component con cũng được gom vào cache riêng của nó.
        noi_dung_da_nhung = self._xu_ly_nhung(noi_dung_goc, file_goi=duong_dan)

        # Bóc tách toàn bộ khối <style> ra khỏi HTML, gộp lại thành 1 khối css
        cac_khoi_css = _RE_STYLE.findall(noi_dung_da_nhung)
        html_sach = _RE_STYLE.sub("", noi_dung_da_nhung)

        self._cache_html[ten_component] = html_sach
        self._cache_css[ten_component] = "\n".join(c.strip() for c in cac_khoi_css if c.strip())
        return html_sach

    def _xu_ly_nhung(self, html: str, file_goi: str) -> str:
        def _thay(m):
            return self._lay_component(m.group(1), file_goi)
        # lặp cho tới khi không còn tag nhúng nào (phòng trường hợp nhúng lồng nhau ở tầng trang)
        truoc = None
        while truoc != html:
            truoc = html
            html = _RE_NHUNG.sub(_thay, html)
        return html

    # ----------------------------------------------------------------- #
    # Bước 1: kế thừa layout + khối ghi đè
    # ----------------------------------------------------------------- #
    def _giai_quyet_ke_thua(self, duong_dan_file: str) -> str:
        noi_dung = self._doc(duong_dan_file)
        m = _RE_KE_THUA.search(noi_dung)
        if not m:
            # File này không kế thừa ai -> chính nó là gốc, trả về nguyên văn
            return noi_dung

        ten_layout_cha = m.group(1)
        noi_dung_con = _RE_KE_THUA.sub("", noi_dung, count=1)

        duong_dan_cha = os.path.join(self.thu_muc_layout, ten_layout_cha)
        if not os.path.isfile(duong_dan_cha):
            raise LoiLayoutKhongTonTai(ten_layout_cha, duong_dan_file)

        # Layout cha có thể tự kế thừa layout khác nữa -> đệ quy
        html_cha = self._giai_quyet_ke_thua(duong_dan_cha)

        # Lấy các khối mà file con định nghĩa (ghi đè)
        khoi_con = {ten: noi_dung_khoi for ten, noi_dung_khoi in _RE_KHOI.findall(noi_dung_con)}

        # Thay từng {% khoi ten %}...{% end %} trong cha bằng bản của con nếu có,
        # nếu con không ghi đè thì giữ nguyên nội dung mặc định đã có sẵn trong cha.
        def _thay_khoi(m2):
            ten_khoi = m2.group(1)
            noi_dung_mac_dinh = m2.group(2)
            return khoi_con.get(ten_khoi, noi_dung_mac_dinh)

        return _RE_KHOI.sub(_thay_khoi, html_cha)

    # ----------------------------------------------------------------- #
    # Bước 3: vòng lặp dữ liệu
    # ----------------------------------------------------------------- #
    def _lay_theo_duong_dan(self, context: dict, duong_dan_cham: str):
        gia_tri = context
        for phan in duong_dan_cham.split("."):
            if isinstance(gia_tri, dict):
                gia_tri = gia_tri.get(phan)
            else:
                gia_tri = getattr(gia_tri, phan, None)
            if gia_tri is None:
                return None
        return gia_tri

    def _xu_ly_vong_lap(self, html: str, context: dict) -> str:
        def _thay(m):
            ten_bien, duong_dan, than_vong_lap = m.group(1), m.group(2), m.group(3)
            danh_sach = self._lay_theo_duong_dan(context, duong_dan) or []
            ket_qua = []
            for phan_tu in danh_sach:
                ngu_canh_con = dict(context)
                ngu_canh_con[ten_bien] = phan_tu
                # Cho phép vòng lặp lồng nhau: xử lý đệ quy thân vòng lặp trước
                than_da_lap = self._xu_ly_vong_lap(than_vong_lap, ngu_canh_con)
                ket_qua.append(self._thay_bien(than_da_lap, ngu_canh_con))
            return "".join(ket_qua)
        return _RE_MOI.sub(_thay, html)

    # ----------------------------------------------------------------- #
    # Bước 4: thay biến
    # ----------------------------------------------------------------- #
    def _thay_bien(self, html: str, context: dict) -> str:
        def _thay(m):
            gia_tri = self._lay_theo_duong_dan(context, m.group(1))
            return "" if gia_tri is None else str(gia_tri)
        return _RE_BIEN.sub(_thay, html)

    # ----------------------------------------------------------------- #
    # Bước 5: chèn CSS gom được (không trùng lặp) vào trước </head>
    # ----------------------------------------------------------------- #
    def _chen_css_da_gom(self, html: str, ten_cac_component_da_dung: list) -> str:
        css_duy_nhat = []
        da_them = set()
        for ten in ten_cac_component_da_dung:
            css = self._cache_css.get(ten, "")
            if css and ten not in da_them:
                css_duy_nhat.append(css)
                da_them.add(ten)
        if not css_duy_nhat:
            return html
        khoi_style = "<style>\n" + "\n\n".join(css_duy_nhat) + "\n</style>\n"
        if "</head>" in html:
            return html.replace("</head>", khoi_style + "</head>", 1)
        return khoi_style + html

    # ----------------------------------------------------------------- #
    # API chính: render 1 trang hoàn chỉnh từ 1 file layout, với context
    # ----------------------------------------------------------------- #
    def render_trang(self, duong_dan_file_layout: str, context: dict) -> str:
        html = self._giai_quyet_ke_thua(duong_dan_file_layout)
        html = self._xu_ly_nhung(html, file_goi=duong_dan_file_layout)
        html = self._xu_ly_vong_lap(html, context)
        html = self._thay_bien(html, context)
        html = self._chen_css_da_gom(html, list(self._cache_css.keys()))
        return html
