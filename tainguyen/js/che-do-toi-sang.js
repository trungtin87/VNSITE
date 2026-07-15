// che-do-toi-sang.js — Dark/Light mode toggle (mục IV, 🔴 bắt buộc)
// Dùng thuộc tính "data-theme" với giá trị "light"/"dark" — đúng theo quy ước
// mà VNSTYLE (tainguyen/css/vnstyle.css) đã định nghĩa sẵn cho toàn bộ theme.
(function () {
    "use strict";
    var KHOA_LUU = "vnsite-theme";
    var the_html = document.documentElement;
    var nut = document.getElementById("nut-doi-che-do");

    function ap_dung(che_do) {
        the_html.setAttribute("data-theme", che_do);
        if (nut) {
            var bieu_tuong = nut.querySelector(".bieu-tuong-che-do");
            if (bieu_tuong) bieu_tuong.textContent = che_do === "dark" ? "☀️" : "🌙";
        }
    }

    // 1. Xác định chế độ ban đầu: localStorage > sở thích hệ điều hành > mặc định sáng
    var da_luu = null;
    try { da_luu = localStorage.getItem(KHOA_LUU); } catch (loi) { /* Safari riêng tư có thể chặn */ }

    var che_do_ban_dau;
    if (da_luu === "light" || da_luu === "dark") {
        che_do_ban_dau = da_luu;
    } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
        che_do_ban_dau = "dark";
    } else {
        che_do_ban_dau = "light";
    }
    ap_dung(che_do_ban_dau);

    // 2. Bắt sự kiện bấm nút chuyển đổi
    if (nut) {
        nut.addEventListener("click", function () {
            var hien_tai = the_html.getAttribute("data-theme");
            var moi = hien_tai === "dark" ? "light" : "dark";
            ap_dung(moi);
            try { localStorage.setItem(KHOA_LUU, moi); } catch (loi) { /* bỏ qua nếu không lưu được */ }
        });
    }
})();
