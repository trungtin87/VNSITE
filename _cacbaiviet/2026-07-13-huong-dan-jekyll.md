---
tieu_de: "Hướng dẫn dùng VNSITE cho người Việt"
chuyen_muc: "lap-trinh"
tags: [jekyll, static-site, huong-dan]
mo_ta: "Tổng quan nhanh về Jekyll và vì sao VNSITE ra đời để thay thế nó cho người dùng Việt."
---
Jekyll là một trong những trình tạo website tĩnh phổ biến nhất, đặc biệt vì được
GitHub Pages hỗ trợ sẵn. Tuy nhiên, với người dùng Việt Nam, Jekyll có vài điểm
bất tiện: cú pháp Liquid tiếng Anh, phụ thuộc Ruby, và không tối ưu cho nội dung
tiếng Việt (slug, dấu, bộ gõ).

<!--tomtat-->

## Vì sao cần một giải pháp riêng

VNSITE ra đời với 3 mục tiêu chính:

1. Chỉ dùng Python — không cần cài Ruby hay Node.js
2. Cú pháp template bằng tiếng Việt (`{% ke_thua %}`, `{% moi ... trong ... %}`)
3. Xử lý đúng các vấn đề đặc thù tiếng Việt: bỏ dấu khi tạo slug, chuyên mục,
   phân loại bài viết theo tháng/năm

## Ví dụ một khối code

Dưới đây là ví dụ cách một bài viết VNSITE khai báo front matter:

```yaml
---
tieu_de: "Tiêu đề bài viết"
chuyen_muc: "lap-trinh"
tags: [python, vnsite]
---
```

Nút "Sao chép" ở góc phải mỗi khối code sẽ giúp người đọc copy nhanh mà không
cần bôi đen thủ công.

## Kết luận

Nếu bạn đang tìm một công cụ blog tĩnh tối giản, hoàn toàn thân
thiện với người Việt, VNSITE là một lựa chọn xứng đáng.
