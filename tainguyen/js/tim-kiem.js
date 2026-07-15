// tim-kiem.js — Tìm kiếm phía client, thuần vanilla JS (mục VI, 🟢 tùy chọn).
// Không dùng lunr.js hay bất kỳ thư viện ngoài nào để giữ đúng triết lý
// "chỉ dùng Python + JS thuần" của VNSITE — chỉ so khớp chuỗi con (substring),
// đủ dùng cho blog cá nhân vài chục tới vài trăm bài viết.
(function () {
    "use strict";
    var o_tim_kiem = document.getElementById("o-tim-kiem");
    var vung_ket_qua = document.getElementById("ket-qua-tim-kiem");
    if (!o_tim_kiem || !vung_ket_qua) return; // Tính năng đang tắt trên trang này

    var goc = (window.VNSITE_BASEURL || "");
    var chi_muc = null;
    var dang_tai = false;

    function bo_dau(chuoi) {
        return chuoi
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/đ/g, "d")
            .replace(/Đ/g, "D")
            .toLowerCase();
    }

    function tai_chi_muc(xong) {
        if (chi_muc) { xong(); return; }
        if (dang_tai) return;
        dang_tai = true;
        fetch(goc + "/search-index.json")
            .then(function (res) { return res.json(); })
            .then(function (du_lieu) {
                chi_muc = du_lieu.map(function (bai) {
                    return {
                        tieu_de: bai.tieu_de,
                        url: bai.url,
                        van_ban: bai.van_ban,
                        tags: bai.tags || [],
                        khoa_khong_dau: bo_dau(bai.tieu_de + " " + bai.van_ban + " " + (bai.tags || []).join(" ")),
                    };
                });
                dang_tai = false;
                xong();
            })
            .catch(function () {
                dang_tai = false;
                vung_ket_qua.innerHTML = "<li class=\"loi-tim-kiem\">Không tải được chỉ mục tìm kiếm.</li>";
            });
    }

    function hien_thi_ket_qua(tu_khoa) {
        vung_ket_qua.innerHTML = "";
        if (!tu_khoa) { vung_ket_qua.classList.remove("dang-mo"); return; }

        var tu_khoa_khong_dau = bo_dau(tu_khoa);
        var ket_qua = chi_muc.filter(function (bai) {
            return bai.khoa_khong_dau.indexOf(tu_khoa_khong_dau) !== -1;
        }).slice(0, 8);

        if (ket_qua.length === 0) {
            vung_ket_qua.innerHTML = "<li class=\"khong-co-ket-qua\">Không tìm thấy bài viết phù hợp.</li>";
        } else {
            ket_qua.forEach(function (bai) {
                var dong = document.createElement("li");
                var lien_ket = document.createElement("a");
                lien_ket.href = goc + bai.url;
                lien_ket.textContent = bai.tieu_de;
                dong.appendChild(lien_ket);
                vung_ket_qua.appendChild(dong);
            });
        }
        vung_ket_qua.classList.add("dang-mo");
    }

    var thoi_gian_cho = null;
    o_tim_kiem.addEventListener("input", function () {
        var tu_khoa = o_tim_kiem.value.trim();
        clearTimeout(thoi_gian_cho);
        thoi_gian_cho = setTimeout(function () {
            tai_chi_muc(function () { hien_thi_ket_qua(tu_khoa); });
        }, 120); // debounce nhẹ để không lọc lại trên từng phím gõ
    });

    // Đóng danh sách kết quả khi bấm ra ngoài
    document.addEventListener("click", function (su_kien) {
        if (!o_tim_kiem.parentElement.contains(su_kien.target)) {
            vung_ket_qua.classList.remove("dang-mo");
        }
    });
})();
