// slider.js — slider ảnh sản phẩm, thuần JS, không cần thư viện ngoài
(function () {
    function khoiTaoSlider(sliderEl) {
        var khungAnh = sliderEl.querySelector(".vn-slider-anh");
        var soAnh = khungAnh.children.length;
        if (soAnh <= 1) return; // 1 ảnh thì không cần nút/chấm điều hướng

        var viTriHienTai = 0;

        var nutTruoc = document.createElement("button");
        nutTruoc.className = "vn-slider-nut truoc";
        nutTruoc.setAttribute("aria-label", "Ảnh trước");
        nutTruoc.innerHTML = "&#8249;";

        var nutSau = document.createElement("button");
        nutSau.className = "vn-slider-nut sau";
        nutSau.setAttribute("aria-label", "Ảnh sau");
        nutSau.innerHTML = "&#8250;";

        var khungCham = document.createElement("div");
        khungCham.className = "vn-slider-cham";
        var cacCham = [];
        for (var i = 0; i < soAnh; i++) {
            var cham = document.createElement("button");
            cham.setAttribute("aria-label", "Xem ảnh " + (i + 1));
            (function (chiSo) {
                cham.addEventListener("click", function () { chuyenDen(chiSo); });
            })(i);
            khungCham.appendChild(cham);
            cacCham.push(cham);
        }

        sliderEl.appendChild(nutTruoc);
        sliderEl.appendChild(nutSau);
        sliderEl.appendChild(khungCham);

        function chuyenDen(chiSo) {
            viTriHienTai = (chiSo + soAnh) % soAnh;
            khungAnh.style.transform = "translateX(-" + (viTriHienTai * 100) + "%)";
            cacCham.forEach(function (c, idx) {
                c.classList.toggle("dang-chon", idx === viTriHienTai);
            });
        }

        nutTruoc.addEventListener("click", function () { chuyenDen(viTriHienTai - 1); });
        nutSau.addEventListener("click", function () { chuyenDen(viTriHienTai + 1); });

        chuyenDen(0);
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".vn-slider").forEach(khoiTaoSlider);
    });
})();
