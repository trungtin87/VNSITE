# Bài Giảng CSS Có Hệ Thống — Từ Nền Tảng Đến Nâng Cao

---

# GIAI ĐOẠN 1: NỀN TẢNG CÚ PHÁP

## 1.1. CSS là gì, viết ở đâu?

CSS (Cascading Style Sheets) là ngôn ngữ mô tả **cách hiển thị** của HTML. Có 3 cách gắn CSS vào HTML:

```html
<!-- Cách 1: Inline - viết ngay trong thẻ, KHÔNG NÊN DÙNG vì khó bảo trì -->
<p style="color: red;">Xin chào</p>

<!-- Cách 2: Internal - viết trong thẻ style ở head -->
<head>
  <style>
    p { color: red; }
  </style>
</head>

<!-- Cách 3: External - file .css riêng, CÁCH CHUẨN nên dùng -->
<head>
  <link rel="stylesheet" href="style.css">
</head>
```

## 1.2. Cú pháp cơ bản

```css
selector {
  thuoc-tinh: gia-tri;
  thuoc-tinh-khac: gia-tri-khac;
}
```

Ví dụ:
```css
p {
  color: blue;
  font-size: 16px;
}
```

## 1.3. Các loại Selector (bộ chọn)

```css
/* Chọn theo thẻ */
p { color: black; }

/* Chọn theo class - dùng dấu chấm, có thể lặp lại nhiều lần trong trang */
.tieu-de-chinh { color: green; }

/* Chọn theo id - dùng dấu #, CHỈ dùng 1 lần trong trang */
#header { background: gray; }

/* Chọn theo thuộc tính */
input[type="text"] { border: 1px solid gray; }

/* Chọn con trực tiếp (child) - dùng dấu > */
.danh-sach > li { list-style: none; }

/* Chọn con cháu (descendant) - dùng khoảng trắng */
.danh-sach li { color: red; }

/* Chọn phần tử liền kề */
h1 + p { margin-top: 0; }

/* Kết hợp nhiều selector */
h1, h2, h3 { font-weight: bold; }

/* Pseudo-class - trạng thái */
a:hover { color: orange; }
li:first-child { font-weight: bold; }

/* Pseudo-element - tạo phần tử ảo */
p::first-letter { font-size: 2em; }
```

### Độ ưu tiên (Specificity)

Khi nhiều rule cùng áp dụng lên 1 phần tử, CSS chọn theo độ ưu tiên:

1. `!important` (tránh dùng, phá vỡ luồng CSS)
2. Inline style
3. ID (`#id`)
4. Class, attribute, pseudo-class (`.class`, `[type]`, `:hover`)
5. Thẻ (`p`, `div`)

Ví dụ: `#header .tieu-de { color: red; }` sẽ thắng `.tieu-de { color: blue; }` vì có ID.

## 1.4. Box Model — QUAN TRỌNG NHẤT giai đoạn này

Mọi phần tử HTML đều là 1 hình hộp gồm 4 lớp từ trong ra ngoài:

```
┌─────────────────────────────────────┐
│              margin                   │  ← khoảng cách với phần tử khác
│   ┌───────────────────────────────┐  │
│   │           border                │  │  ← viền
│   │   ┌───────────────────────┐    │  │
│   │   │      padding            │    │  │  ← khoảng đệm trong viền
│   │   │   ┌─────────────────┐  │    │  │
│   │   │   │     content       │  │    │  │  ← nội dung thật
│   │   │   └─────────────────┘  │    │  │
│   │   └───────────────────────┘    │  │
│   └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

```css
.hop {
  width: 300px;
  height: 200px;
  padding: 20px;        /* đệm bên trong, giữa nội dung và viền */
  border: 2px solid black;
  margin: 10px;          /* khoảng cách bên ngoài với phần tử khác */
}

/* Viết tắt theo chiều kim đồng hồ: trên - phải - dưới - trái */
.hop-tat {
  padding: 10px 20px 10px 20px;
}

/* Chỉ 2 giá trị: trên-dưới trái-phải */
.hop-2gia-tri {
  margin: 10px 20px;
}
```

### box-sizing — bẫy phổ biến nhất khi mới học

Mặc định, `width` chỉ tính phần **content**, khi thêm padding/border thì hộp sẽ **phình to hơn** kích thước bạn đặt. Cách khắc phục:

```css
* {
  box-sizing: border-box; /* width sẽ bao gồm luôn padding + border */
}
```

Gần như mọi dự án thực tế đều đặt dòng này ở đầu file CSS.

## 1.5. Màu sắc, chữ, văn bản

```css
.van-ban {
  color: #333333;            /* màu chữ - mã hex */
  color: rgb(51, 51, 51);    /* hoặc rgb */
  color: rgba(51, 51, 51, 0.8); /* rgb + độ trong suốt */

  font-family: "Arial", sans-serif;
  font-size: 16px;
  font-weight: bold;         /* hoặc 400, 700... */
  font-style: italic;

  text-align: center;        /* left, right, center, justify */
  line-height: 1.5;          /* khoảng cách dòng, nên đặt để dễ đọc */
  text-decoration: underline;
  text-transform: uppercase;
}
```

---

# GIAI ĐOẠN 2: LAYOUT CƠ BẢN

## 2.1. Thuộc tính `display`

Quyết định phần tử được hiển thị theo kiểu nào trong luồng trang.

```css
/* block: chiếm hết chiều ngang, luôn xuống dòng mới. VD: div, p, h1 */
.khoi { display: block; }

/* inline: chỉ chiếm đúng phần nội dung, KHÔNG áp dụng được width/height/margin-top. VD: span, a */
.dong { display: inline; }

/* inline-block: nằm cùng dòng NHƯNG áp dụng được width/height như block */
.dong-khoi { display: inline-block; }

/* none: ẩn hoàn toàn, không chiếm chỗ */
.an { display: none; }
```

Bảng ghi nhớ nhanh:

| Display | Xuống dòng? | Đặt width/height? | Ví dụ thẻ mặc định |
|---|---|---|---|
| block | Có | Có | div, p, ul, h1-h6 |
| inline | Không | Không | span, a, strong |
| inline-block | Không | Có | img, button |

## 2.2. Thuộc tính `position`

```css
/* static: mặc định, nằm theo luồng tự nhiên, top/left KHÔNG có tác dụng */
.tinh { position: static; }

/* relative: vẫn chiếm chỗ ở vị trí gốc, nhưng có thể dịch chuyển bằng top/left
   so với chính vị trí gốc của nó */
.tuong-doi {
  position: relative;
  top: 10px;
  left: 20px;
}

/* absolute: thoát khỏi luồng, định vị theo phần tử cha gần nhất
   có position khác static (thường là relative) */
.tuyet-doi {
  position: absolute;
  top: 0;
  right: 0;
}

/* fixed: định vị theo màn hình (viewport), cuộn trang vẫn đứng yên
   VD: nút chat, thanh menu dính trên cùng */
.co-dinh {
  position: fixed;
  bottom: 20px;
  right: 20px;
}

/* sticky: kết hợp relative + fixed, dính lại khi cuộn tới 1 điểm nhất định */
.dinh {
  position: sticky;
  top: 0;
}
```

Mẫu thường gặp: cha `relative`, con `absolute` để định vị con theo cha:

```css
.cha {
  position: relative;
}
.con-huy-hieu {
  position: absolute;
  top: -5px;
  right: -5px;
}
```

*Ghi chú: `float` là kỹ thuật layout cũ (trước Flexbox/Grid), giờ chỉ dùng cho việc bao chữ quanh ảnh, không cần học sâu.*

---

# GIAI ĐOẠN 3: LAYOUT HIỆN ĐẠI (QUAN TRỌNG NHẤT)

## 3.1. Flexbox — bố cục 1 chiều

Dùng khi sắp xếp phần tử theo **hàng ngang hoặc hàng dọc**.

```css
.vung_chua {
  display: flex;
  flex-direction: row;        /* row (ngang, mặc định) | column (dọc) */
  justify-content: center;    /* canh theo trục chính: flex-start, center, flex-end,
                                  space-between, space-around, space-evenly */
  align-items: center;        /* canh theo trục ngang (vuông góc): flex-start, center,
                                  flex-end, stretch */
  gap: 16px;                  /* khoảng cách giữa các phần tử con */
  flex-wrap: wrap;            /* cho phép xuống dòng khi hết chỗ */
}

.phan_tu_con {
  flex: 1;    /* co giãn chiếm đều không gian còn lại */
  /* flex là viết tắt của flex-grow flex-shrink flex-basis */
}
```

Ví dụ thực tế — thanh menu ngang:

```css
.thanh_menu {
  display: flex;
  justify-content: space-between; /* logo bên trái, menu bên phải */
  align-items: center;
  padding: 16px;
}
```

Ví dụ — căn giữa 1 phần tử cả 2 chiều (bài toán kinh điển):

```css
.vung_can_giua {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
```

**Trục chính (main axis) vs trục ngang (cross axis):** khi `flex-direction: row`, trục chính nằm ngang → `justify-content` canh ngang, `align-items` canh dọc. Khi đổi sang `column`, 2 trục đảo ngược lại.

## 3.2. Grid — bố cục 2 chiều

Dùng khi cần sắp xếp theo **cả hàng và cột** cùng lúc, phù hợp cho layout tổng thể trang.

```css
.luoi_chinh {
  display: grid;
  grid-template-columns: 250px 1fr;  /* cột 1 rộng 250px, cột 2 chiếm phần còn lại */
  grid-template-rows: auto 1fr auto; /* header - nội dung - footer */
  gap: 20px;
  min-height: 100vh;
}

/* Hoặc chia đều cột bằng hàm repeat */
.luoi_the {
  display: grid;
  grid-template-columns: repeat(3, 1fr);  /* 3 cột bằng nhau */
  gap: 16px;
}

/* Responsive tự động không cần media query */
.luoi_tu_dong {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
```

Đặt vị trí phần tử con cụ thể trong lưới:

```css
.header { grid-column: 1 / -1; }  /* chiếm hết chiều ngang, từ cột đầu đến cột cuối */
.sidebar { grid-row: 2 / 3; }
```

### Khi nào dùng Flexbox, khi nào dùng Grid?

| Tình huống | Dùng |
|---|---|
| Thanh menu ngang, nhóm nút, canh giữa 1 phần tử | Flexbox |
| Bố cục tổng thể trang (header - sidebar - content - footer) | Grid |
| Danh sách card co giãn theo hàng | Flexbox (wrap) |
| Danh sách card cần thẳng hàng cả ngang lẫn dọc | Grid |

Thực tế 2 cái thường **dùng chung**: Grid cho bố cục lớn, Flexbox cho từng khối nhỏ bên trong.

---

# GIAI ĐOẠN 4: RESPONSIVE (THÍCH ỨNG ĐA THIẾT BỊ)

## 4.1. Media Query

```css
/* Mặc định viết CSS cho mobile trước (mobile-first) */
.hop {
  width: 100%;
}

/* Khi màn hình rộng từ 768px trở lên (tablet) */
@media (min-width: 768px) {
  .hop {
    width: 50%;
  }
}

/* Khi màn hình rộng từ 1024px trở lên (desktop) */
@media (min-width: 1024px) {
  .hop {
    width: 33.33%;
  }
}
```

Các mốc (breakpoint) phổ biến: 480px (điện thoại nhỏ), 768px (tablet), 1024px (desktop nhỏ), 1280px (desktop lớn). Không cần nhớ chính xác, thường tùy chỉnh theo thiết kế thực tế.

## 4.2. Đơn vị linh hoạt

```css
.vi_du {
  width: 80%;         /* % theo phần tử cha */
  font-size: 1.2rem;  /* rem: theo font-size gốc của thẻ html (thường 16px) */
  padding: 1em;       /* em: theo font-size của chính phần tử đó */
  height: 100vh;      /* vh: 1% chiều cao màn hình */
  width: 50vw;        /* vw: 1% chiều rộng màn hình */
}
```

**Nguyên tắc chọn đơn vị:**
- `rem` cho font-size, spacing → đồng bộ toàn trang, dễ scale
- `%` cho width trong layout co giãn
- `vh/vw` cho các phần tử cần theo đúng kích thước màn hình (VD: section full màn hình)
- `px` cho những thứ cần cố định tuyệt đối (border, box-shadow)

## 4.3. Tư duy Mobile-first

Viết CSS mặc định cho màn hình nhỏ nhất trước, sau đó dùng `min-width` để mở rộng dần lên màn hình lớn hơn. Lý do: dễ kiểm soát, tránh phải ghi đè quá nhiều CSS.

---

# GIAI ĐOẠN 5: NÂNG CAO

## 5.1. CSS Variables (biến dùng lại)

```css
:root {
  --mau_chinh: #2563eb;
  --mau_chu: #333333;
  --khoang_cach_chuan: 16px;
  --be_mat_bo_goc: 8px;
}

.nut_bam {
  background-color: var(--mau_chinh);
  padding: var(--khoang_cach_chuan);
  border-radius: var(--be_mat_bo_goc);
}
```

Lợi ích: đổi 1 chỗ, áp dụng toàn trang. Cực kỳ hữu ích khi làm dark mode hoặc đổi theme.

```css
/* Dark mode đơn giản bằng biến */
:root {
  --mau_nen: white;
  --mau_chu: black;
}
[data-theme="toi"] {
  --mau_nen: #1a1a1a;
  --mau_chu: #f0f0f0;
}
body {
  background: var(--mau_nen);
  color: var(--mau_chu);
}
```

## 5.2. Transition — chuyển động mượt

```css
.nut_bam {
  background-color: blue;
  transition: background-color 0.3s ease, transform 0.2s ease;
}
.nut_bam:hover {
  background-color: darkblue;
  transform: scale(1.05);
}
```

Cú pháp: `transition: [thuộc-tính] [thời-gian] [kiểu-chuyển-động];`

## 5.3. Animation cơ bản

```css
@keyframes mo_dan {
  from { opacity: 0; }
  to { opacity: 1; }
}

.phan_tu_xuat_hien {
  animation: mo_dan 0.5s ease-in;
}
```

## 5.4. Sau khi vững CSS gốc rồi mới học framework

- **Tailwind CSS**: viết class trực tiếp trong HTML (`class="flex items-center p-4"`), rất nhanh khi đã hiểu CSS gốc, nhưng nếu chưa vững sẽ chỉ copy-paste không hiểu bản chất
- **SCSS/SASS**: CSS mở rộng với biến, hàm, lồng selector — hữu ích cho dự án lớn

---

# TÓM TẮT LỘ TRÌNH

| Giai đoạn | Trọng tâm | Thời gian gợi ý |
|---|---|---|
| 1 | Selector, Box Model, màu chữ | 1 tuần |
| 2 | display, position | 1-2 tuần |
| 3 | **Flexbox + Grid** (quan trọng nhất) | 2 tuần |
| 4 | Media query, đơn vị linh hoạt | 1 tuần |
| 5 | Variables, transition, animation | Song song thực hành |

**Lời khuyên thực hành:** đọc xong mỗi giai đoạn, lập tức làm lại 1 trang tĩnh nhỏ áp dụng đúng nội dung vừa học, đừng đọc hết cả 5 giai đoạn rồi mới thực hành — sẽ quên ngay.
