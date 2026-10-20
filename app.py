
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Thu Vũ")

st.title("Thu Vũ - Công thức nước hoa")
st.caption("Ứng dụng tính toán công thức nước hoa theo thể tích.")

volume = st.number_input(
    "Thể tích mẻ (mL)", 1.0, 20.0, 10.0, 0.5
)

# (Giới hạn %, mặc định %, tầng hương)
rules = {
    "Cam": (3.0, 1.38, "Đầu"),
    "Gỗ thông": (7.0, 4.83, "Giữa"),
    "Hoa nhài": (3.0, 2.07, "Giữa"),
    "Vanilla": (2.5, 1.72, "Cuối"),
    "Chất lưu hương": (3.0, 3.00, "Cuối"),
}

rows, errors = [], []

for name, (limit, default, note) in rules.items():
    pct = st.slider(
        name + " (%)",
        0.0,
        limit,
        default,
        0.01
    )

    rows.append({
        "Thành phần": name,
        "Tầng hương": note,
        "%": pct
    })

    if pct > limit:
        errors.append(
            f"{name} vượt giới hạn {limit:.3f}%."
        )

# Tính tổng nhóm hương và dung môi
fragrance = sum(row["%"] for row in rows)
solvent = 100.0 - fragrance

if solvent < 0:
    errors.append("Dung môi âm: tổng nhóm hương vượt 100%.")

rows.append({
    "Thành phần": "Dung môi",
    "Tầng hương": "Dung môi",
    "%": solvent
})

# Kiểm tra tổng công thức
total_pct = sum(row["%"] for row in rows)

if abs(total_pct - 100.0) > 0.000001:
    errors.append(
        f"Tổng công thức không bằng 100% "
        f"(hiện tại: {total_pct:.3f}%)."
    )

# Tính thể tích và làm tròn 3 chữ số thập phân
for row in rows:
    row["%"] = round(row["%"], 3)
    row["mL"] = round(
        volume * row["%"] / 100.0, 3
    )

df = pd.DataFrame(rows)

st.subheader("Bảng kết quả")
st.dataframe(df, use_container_width=True, hide_index=True)

# Tính tỉ lệ của từng tầng hương
layers = {
    "Đầu": 0.0,
    "Giữa": 0.0,
    "Cuối": 0.0
}

for row in rows:
    if row["Tầng hương"] in layers:
        layers[row["Tầng hương"]] += row["%"]

st.subheader("Mô tả tầng hương")

max_layer = max(layers, key=layers.get)
layer_description = {
    "Đầu": "hương đầu",
    "Giữa": "hương giữa",
    "Cuối": "hương cuối"
}

st.write(
    f"{layer_description[max_layer].capitalize()} "
    f"chiếm tỉ lệ cao nhất trong công thức "
    f"({layers[max_layer]:.3f}%)."
)

st.write(
    "Tỉ lệ các tầng: "
    + " | ".join(
        f"{layer_description[name]}: {pct:.3f}%"
        for name, pct in layers.items()
    )
    + "."
)

st.caption(
    "Mô tả dựa trên tỉ lệ thành phần, không khẳng định "
    "chất lượng hoặc độ an toàn. Cần giáo viên xem xét "
    "trước khi pha chế."
)

# Chỉ cho tải CSV khi công thức hợp lệ
if errors:
    for error in errors:
        st.error(error)
else:
    st.success("Công thức hợp lệ về mặt toán học.")

    st.download_button(
        "Tải công thức CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="thu_vu_cong_thuc.csv",
        mime="text/csv"
    )
