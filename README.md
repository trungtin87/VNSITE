# VNSITE — Trình tạo website tĩnh tự động cho người Việt

Triển khai theo `VNSITE_dac_ta_v2.md`. Chỉ dùng Python 3.8+, không phụ thuộc
Node.js/npm. Phù hợp cho blog cá nhân và portfolio.

## Cài đặt

```bash
pip install -r requirements.txt
```

## Sử dụng

```bash
python taowebsite.py build            # Build 1 lần ra thư mục _ketqua/
python taowebsite.py build --preview   # Build kèm cả bài viết đang để "nhap: true"
python taowebsite.py serve             # Dev server local, tự rebuild khi lưu file
python taowebsite.py serve --port 9000 --preview
python taowebsite.py favicon           # (tùy chọn) sinh favicon nhiều kích thước
```

Sau khi chạy `serve`, mở `http://localhost:8000/`. Mọi thay đổi trong
`_bocuctrang/`, `_thanhphantrang/`, `_cacbaiviet/`, `_duan/`, `tainguyen/`,
`_dulieu/`, `_cauhinhtrangweb.yml` hoặc các file `.html` ở gốc dự án sẽ được
tự động phát hiện và rebuild.

## Cấu trúc thư mục

```
_cauhinhtrangweb.yml     Cấu hình chung của trang web
taowebsite.py            Điểm vào CLI

_bocuctrang/             Layout: trangmacdinh.html (gốc), baiviet.html, trangweb.html
_thanhphantrang/         Component tái sử dụng: header, nav, footer, sidebar
_cacbaiviet/             Bài viết blog (.md, có front matter)
_duan/                   Dự án portfolio (.md, có front matter)
_dulieu/                 Dữ liệu YAML dùng trong template (thành viên, CV...)
tainguyen/                CSS (vnstyle.css + main.scss — xem ghi chú bên dưới), JS, hình ảnh
_ketqua/                 (sinh ra khi build) — kết quả HTML tĩnh cuối cùng
```

## Cú pháp template

| Tag                                           | Ý nghĩa                                            |
| --------------------------------------------- | ---------------------------------------------------- |
| `{% ke_thua "trangmacdinh.html" %}`         | Kế thừa 1 layout cha (đặt ở dòng đầu file)   |
| `{% khoi ten %} ... {% end %}`              | Vùng nội dung có thể ghi đè khi kế thừa      |
| `{% nhung "ten_component.html" %}`          | Nhúng 1 thành phần từ`_thanhphantrang/`        |
| `{% moi x trong duong.dan %} ... {% het %}` | Lặp qua 1 danh sách trong ngữ cảnh (context)     |
| `{{ ten_bien }}` / `{{ x.thuoc_tinh }}`   | Chèn giá trị biến, hỗ trợ truy cập lồng nhau |

Bóc tách `<style>` trong mỗi component được cache trong bộ nhớ và chỉ chèn
1 lần vào `<head>` mỗi trang — không bị lặp `<style>` dù nhúng nhiều lần.

## Front matter cho bài viết (`_cacbaiviet/*.md`)

```yaml
---
tieu_de: "Tiêu đề bắt buộc"        # 🔴 bắt buộc
chuyen_muc: "lap-trinh"           # 🔴 quyết định thư mục output, mặc định "bai-viet"
tags: [python, huong-dan]         # 🟡 dùng cho trang liệt kê theo tag
mo_ta: "Mô tả ngắn cho SEO"       # 🟡 nếu thiếu sẽ tự lấy từ excerpt
ngay: "2026-07-13"                 # 🟡 nếu thiếu sẽ lấy từ tiền tố tên file YYYY-MM-DD-
nhap: true                         # 🟢 đánh dấu bản nháp, không xuất bản trừ khi --preview
slug: "duong-dan-tuy-chinh"        # 🟢 ghi đè slug tự sinh từ tiêu đề
anh_bia: "/tainguyen/hinhanh/anh.jpg"  # 🟢 ảnh og:image riêng cho bài
---

Excerpt tự động cắt tới marker `<!--tomtat-->` nếu có, ngược lại cắt N từ đầu
theo `so_tu_tomtat_mac_dinh` trong `_cauhinhtrangweb.yml`.
```

## Front matter cho dự án (`_duan/*.md`)

```yaml
---
tieu_de: "Tên dự án"              # 🔴 bắt buộc
mo_ta_ngan: "Mô tả 1-2 câu"       # 🔴 bắt buộc
anh_dai_dien: "/tainguyen/hinhanh/du-an.png"
cong_nghe: [Python, VNLang]
link_demo: "https://..."
link_github: "https://github.com/..."
---
```

## Ghi chú quan trọng

- **Nền CSS: VNSTYLE** (`tainguyen/css/vnstyle.css`) — framework classless
  Việt hóa dựa trên kiến trúc Pico CSS, tự động style mọi thẻ HTML thuần
  (`h1`-`h6`, `a`, `button`, `article`, `nav`, form...) và có sẵn dark/light
  mode qua thuộc tính `data-theme="light"/"dark"` trên `<html>`. Container
  canh giữa dùng thuộc tính `hien-thi="khung-chua"` (không phải class
  `.container` như bản gốc). Đây là file CSS đã biên dịch sẵn — **không**
  chỉnh sửa trực tiếp, coi như thư viện ngoài.
- **`tainguyen/css/main.scss`** là lớp bổ sung riêng của VNSITE, nạp SAU
  `vnstyle.css` — chỉ chứa phần VNSTYLE chưa có sẵn: layout header/nav/footer,
  tag pill, lưới bài viết/dự án, mục lục (TOC), nút copy code, ô tìm kiếm,
  trang CV. Toàn bộ dùng lại biến `--vn-*` có sẵn (`--vn-mau-chinh`,
  `--vn-mau-nen`, `--vn-mo-nhat-mau-chu`...) để tự động đồng bộ theo
  dark/light mode — không tự định nghĩa biến màu riêng.
- **`.scss` ở đây chỉ được gộp thô** (concat) thành `main.css`, KHÔNG biên dịch
  biến `$x`/nesting kiểu Sass thật. Nếu cần Sass thật, xem
  `vnsite_engine/favicon.py` để biết mẫu cách tích hợp 1 công cụ ngoài
  (dart-sass) qua `subprocess` — đây là hướng mở rộng 🟢 tùy chọn, chưa cài sẵn.
- **Đổi màu chủ đạo / font chữ toàn site**: sửa biến `--vn-mau-chinh`,
  `--vn-phong-chu-khong-chan`... ngay trong khối `:root, :host` ở đầu
  `vnstyle.css` (dòng ~250 cho theme sáng, ~514 cho theme tối) — không cần
  sửa gì trong `main.scss`.
- **`baseurl`**: nếu deploy dạng project site (`user.github.io/ten-repo`), đặt
  `baseurl: "/ten-repo"` trong `_cauhinhtrangweb.yml` — mọi link tài nguyên
  trong layout đều dùng tiền tố `{{ cau_hinh.baseurl }}`.
- **Trùng slug** giữa 2 bài viết chỉ in cảnh báo ra console, không chặn build
  (bài xuất bản sau sẽ ghi đè bài trước trong `_ketqua/`).

## Trạng thái triển khai theo giai đoạn (mục IX của đặc tả)

- ✅ **Giai đoạn 1** (lõi dùng được): kế thừa layout, cache style khi nhúng
  component, slug tiếng Việt, category/chuyên mục, xử lý lỗi rõ ràng, theme
  CSS variables, dev server + watch/rebuild.
- ✅ **Giai đoạn 2** (chuẩn blog thật): dark/light mode, TOC + scroll-spy, nút
  copy code, tag, excerpt tự động, draft (`nhap: true`), thẻ SEO/Open Graph.
- ✅ **Giai đoạn 3** (mở rộng):
  - Collection `_duan/` cho portfolio + trang liệt kê `/du-an/`
  - Trang CV/Resume tự động (`cv.html` + `_dulieu/ho_so.yml` → `/cv/`)
  - Tìm kiếm phía client: bật bằng `tim_kiem.bat: true`, builder sinh
    `search-index.json`, `tainguyen/js/tim-kiem.js` lọc theo chuỗi con
    (không dùng lunr.js hay bất kỳ thư viện ngoài nào — giữ đúng triết lý
    "chỉ Python + JS thuần", không cần tải gì từ CDN)
  - Giscus: khung sẵn trong `thanhben.html`, bật bằng `giscus.bat: true`
    trong `_cauhinhtrangweb.yml`
  - Sinh favicon nhiều kích thước: `python taowebsite.py favicon` (cần
    Pillow, đọc từ `tainguyen/hinhanh/favicon-nguon.png`)
  - Related posts theo tag trùng (đã có trong `builder.py`, hiển thị ở
    cuối mỗi bài trong `baiviet.html`)

## Tính năng tìm kiếm — chi tiết

1. Đặt `tim_kiem.bat: true` trong `_cauhinhtrangweb.yml`
2. `python taowebsite.py build` sẽ tự sinh `_ketqua/search-index.json`
   (tiêu đề + văn bản excerpt đã bỏ HTML + tags của mọi bài viết đã xuất bản)
3. Ô tìm kiếm tự xuất hiện trong header mọi trang; gõ vào là lọc ngay theo
   chuỗi con, không phân biệt hoa/thường và không phân biệt dấu tiếng Việt
   (gõ "jekyll" hoặc "jekyl" đều ra kết quả tương ứng nếu khớp chuỗi con)

## Trang CV — chi tiết

1. Điền thông tin vào `_dulieu/ho_so.yml` (họ tên, chức danh, kinh nghiệm,
   học vấn, kỹ năng)
2. `cv.html` ở gốc dự án tự động lặp qua các trường đó và xuất ra `/cv/`
3. Muốn đổi giao diện CV thì sửa trực tiếp `cv.html` — nó dùng cùng cơ chế
   `{% ke_thua %}` / `{% moi %}` như mọi trang khác trong VNSITE
