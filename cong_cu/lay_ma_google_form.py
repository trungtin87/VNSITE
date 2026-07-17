# -*- coding: utf-8 -*-
"""
cong_cu/lay_ma_google_form.py
==============================
Công cụ dòng lệnh: lấy tự động mã "entry.XXXXXXX" của từng câu hỏi trong 1
Google Form công khai, để nối form liên hệ trên site VNSITE (theme Agency)
thẳng vào Google Form — không cần máy chủ, hợp với GitHub Pages.

CÁCH DÙNG
---------
1) Tạo 1 Google Form với các câu hỏi, ví dụ theo đúng thứ tự:
   Họ tên / Email / Số điện thoại / Nội dung
2) Bấm "Gửi" (Send) -> copy link dạng:
   https://docs.google.com/forms/d/e/1FAIpQLS.../viewform
3) Chạy:
   python3 cong_cu/lay_ma_google_form.py "https://docs.google.com/forms/d/e/xxxx/viewform"

   Công cụ sẽ in ra danh sách câu hỏi kèm entry.XXXX tương ứng, và hỏi bạn
   muốn ghi thẳng vào _cauhinhtrangweb.yml hay không.

LƯU Ý QUAN TRỌNG
----------------
Google KHÔNG công bố chính thức định dạng dữ liệu này (biến nội bộ
`FB_PUBLIC_LOAD_DATA_` nhúng trong trang viewform) — đây là kỹ thuật được
nhiều dự án mã nguồn mở dùng lại (vd. các thư viện "google-form-to-json"),
nhưng Google có thể đổi cấu trúc bất kỳ lúc nào khiến script này không chạy
đúng. Nếu vậy, làm thủ công:
    - Mở form ở chế độ xem trước (preview) -> bấm chuột phải -> "Xem
      nguồn trang" (View Page Source)
    - Tìm chuỗi "entry." -> mỗi câu hỏi có 1 mã entry.<số> riêng
    - Điền tay vào _cauhinhtrangweb.yml
"""
import json
import re
import sys
import urllib.request

_RE_FORM_ID = re.compile(r"/forms/d/e/([\w-]+)/")
_RE_DATA = re.compile(r"FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.*?\])\s*;", re.DOTALL)


def tai_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.read().decode("utf-8", errors="replace")


def phan_tich_cau_hoi(html: str):
    m = _RE_DATA.search(html)
    if not m:
        raise RuntimeError(
            "Không tìm thấy FB_PUBLIC_LOAD_DATA_ trong trang — có thể Google đã "
            "đổi định dạng, hoặc link chưa đúng dạng .../viewform công khai. "
            "Hãy làm thủ công theo hướng dẫn trong docstring đầu file."
        )
    du_lieu = json.loads(m.group(1))
    danh_sach_cau_hoi = du_lieu[1][1]
    ket_qua = []
    for cau_hoi in danh_sach_cau_hoi:
        ten_cau_hoi = cau_hoi[1]
        chi_tiet = cau_hoi[4]
        if not chi_tiet:
            continue
        entry_id = chi_tiet[0][0]
        ket_qua.append({"cau_hoi": ten_cau_hoi, "entry": f"entry.{entry_id}"})
    return ket_qua


def doan_truong_phu_hop(ten_cau_hoi: str) -> str:
    """Đoán field VNSITE (ho_ten/email/dien_thoai/noi_dung) dựa theo tên câu hỏi."""
    t = ten_cau_hoi.lower()
    if "email" in t or "thư điện tử" in t:
        return "email"
    if "điện thoại" in t or "sđt" in t or "phone" in t:
        return "dien_thoai"
    if "nội dung" in t or "lời nhắn" in t or "tin nhắn" in t or "message" in t:
        return "noi_dung"
    if "tên" in t or "họ" in t or "name" in t:
        return "ho_ten"
    return ""


def main():
    if len(sys.argv) < 2:
        print('Cách dùng: python3 cong_cu/lay_ma_google_form.py "<link-google-form>/viewform"')
        sys.exit(1)

    url = sys.argv[1]
    m_id = _RE_FORM_ID.search(url)
    form_id = m_id.group(1) if m_id else ""

    print(f"Đang tải form từ: {url}")
    html = tai_html(url)
    cau_hoi_list = phan_tich_cau_hoi(html)

    if not cau_hoi_list:
        print("Không tìm thấy câu hỏi nào — kiểm tra lại link form.")
        sys.exit(1)

    print(f"\nform_id: {form_id or '(không tự nhận ra, xem lại URL)'}")
    print("Danh sách câu hỏi tìm được:\n")

    goi_y = {}
    for cau_hoi in cau_hoi_list:
        truong = doan_truong_phu_hop(cau_hoi["cau_hoi"])
        print(f'  - "{cau_hoi["cau_hoi"]}"  ->  {cau_hoi["entry"]}'
              + (f"   [đoán: {truong}]" if truong else "   [chưa đoán được field]"))
        if truong:
            goi_y[truong] = cau_hoi["entry"]

    print("\n---- Dán đoạn dưới đây vào _cauhinhtrangweb.yml (mục google_form) ----\n")
    print("google_form:")
    print(f'  form_id: "{form_id}"')
    print("  entries:")
    for truong in ["ho_ten", "email", "dien_thoai", "noi_dung"]:
        print(f'    {truong}: "{goi_y.get(truong, "")}"')
    print("\n(Trường nào công cụ chưa đoán đúng, tự đối chiếu lại danh sách câu hỏi ở trên rồi sửa tay.)")


if __name__ == "__main__":
    main()
