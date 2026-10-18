import streamlit as st
import pandas as pd

st.title("Thu Vũ - công thức tương tác")

volume = st.number_input(
    "Thể tích mẻ (mL)", 1.0, 20.0, 10.0, 0.5
)

rules = {
    "Tinh dầu hương cam": (3.0, 1.38, "Đầu"),
    "Tinh dầu gỗ thông": (7.0, 4.83, "Giữa"),
    "Tinh dầu hoa nhài": (3.0, 2.07, "Cuối"),
    "Tinh dầu vanilla": (2.5, 1.72, "Cuối"),
    "Chất lưu hương": (3.0, 3.0, "Lưu hương"),
}

rows, errors = [], []

for name, (limit, default, note) in rules.items():
    pct = st.slider(
        name + " (%)",
        min_value=0.0,
        max_value=limit,
        value=default,
        step=0.01
    )

    rows.append({
        "Thành phần": name,
        "Tầng": note,
        "%": pct
    })

    if pct > limit:
        errors.append(name + " vượt giới hạn dự án")

# Tính dung môi tự động
fragrance = sum(row["%"] for row in rows)
solvent = 100.0 - fragrance

if solvent < 0:
    errors.append("Tổng nhóm hương và chất lưu hương vượt 100%")

# Tách dung môi theo công thức gốc:
# Nước 0,4 mL; cồn 8,3 mL trên tổng 10 mL
water_pct = max(0.0, solvent) * (0.4 / 8.7)
alcohol_pct = max(0.0, solvent) * (8.3 / 8.7)

rows.extend([
    {"Thành phần": "Nước", "Tầng": "Dung môi", "%": water_pct},
    {"Thành phần": "Cồn", "Tầng": "Dung môi", "%": alcohol_pct},
])

for row in rows:
    row["%"] = round(row["%"], 3)
    row["mL"] = round(volume * row["%"] / 100, 3)

df = pd.DataFrame(rows)

st.subheader("Bảng kết quả")
st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Mô tả tầng hương")
st.write("**Hương đầu:** Cam.")
st.write("**Hương giữa:** Gỗ thông.")
st.write("**Hương cuối:** Hoa nhài, vanilla.")

st.caption(
    "Hợp lệ về mặt toán học không đồng nghĩa với an toàn. "
    "Cần giáo viên duyệt trước khi pha."
)

if errors:
    for error in errors:
        st.error(error)
else:
    st.success("Đủ điều kiện gửi giáo viên xem xét")
    st.download_button(
        "Tải CSV",
        df.to_csv(index=False).encode("utf-8-sig"),
        "thu_vu.csv",
        "text/csv"
    )
