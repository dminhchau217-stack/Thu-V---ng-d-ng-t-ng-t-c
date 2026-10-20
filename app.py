import streamlit as st
import pandas as pd

st.set_page_config(page_title="Thu Vũ", layout="centered")
st.title("Thu Vũ")

volume = st.number_input(
    "Thể tích nước hoa (mL)",
    min_value=1.0,
    max_value=20.0,
    value=10.0,
    step=0.5
)

# Giới hạn tối đa, tỉ lệ mặc định, tầng hương
rules = {
    "Cam": (3.0, 1.38, "Đầu"),
    "Gỗ thông": (7.0, 4.83, "Giữa"),
    "Hoa nhài": (3.0, 2.07, "Giữa"),
    "Vanilla": (2.5, 1.72, "Cuối"),
    "Chất lưu hương": (3.0, 3.00, "Cuối"),
}

target = sum(item[1] for item in rules.values())

def distribute(total, names):
    result = {name: 0.0 for name in names}
    active = list(names)
    remaining = total

    while active and remaining > 1e-9:
        weight_sum = sum(rules[name][1] for name in active)
        if weight_sum <= 0:
            break

        proposed = {
            name: remaining * rules[name][1] / weight_sum
            for name in active
        }

        capped = [
            name for name in active
            if proposed[name] > rules[name][0] + 1e-9
        ]

        if not capped:
            for name in active:
                result[name] = proposed[name]
            remaining = 0.0
            break

        for name in capped:
            result[name] = rules[name][0]
            remaining -= rules[name][0]
            active.remove(name)

    return result


selected = st.selectbox(
    "Thành phần cần điều chỉnh",
    list(rules.keys())
)

limit = rules[selected][0]
others = [name for name in rules if name != selected]

minimum = max(
    0.0,
    target - sum(rules[name][0] for name in others)
)

default = rules[selected][1]

chosen = st.slider(
    f"Tỉ lệ {selected} (%)",
    min_value=minimum,
    max_value=limit,
    value=default,
    step=0.01
)

percentages = {selected: chosen}
percentages.update(distribute(target - chosen, others))

rows = []
errors = []

for name, (limit, default, layer) in rules.items():
    pct = percentages[name]

    if pct < -1e-7 or pct > limit + 1e-7:
        errors.append(f"{name} vượt giới hạn 0–{limit}%.")

    rows.append({
        "Thành phần": name,
        "Tầng hương": layer,
        "Tỉ lệ (%)": pct
    })

fragrance_total = sum(percentages.values())
solvent = 100.0 - fragrance_total

if solvent < -1e-7:
    errors.append("Tổng nhóm hương vượt 100%, dung môi bị âm.")

rows.append({
    "Thành phần": "Dung môi",
    "Tầng hương": "Dung môi",
    "Tỉ lệ (%)": solvent
})

total = sum(row["Tỉ lệ (%)"] for row in rows)

if abs(total - 100.0) > 1e-6:
    errors.append(f"Tổng công thức không bằng 100%: {total:.6f}%.")

# Làm tròn phần trăm hiển thị và giữ tổng bảng bằng 100%
for row in rows[:-1]:
    row["Tỉ lệ (%)"] = round(row["Tỉ lệ (%)"], 3)

rows[-1]["Tỉ lệ (%)"] = round(
    100.0 - sum(row["Tỉ lệ (%)"] for row in rows[:-1]), 3
)

for row in rows:
    row["Thể tích (mL)"] = round(
        volume * row["Tỉ lệ (%)"] / 100.0, 3
    )

df = pd.DataFrame(rows)

st.subheader("Công thức")
st.dataframe(df, use_container_width=True, hide_index=True)

st.caption(
    f"Tổng nhóm hương mục tiêu: {target:.2f}%. "
    "Các thành phần còn lại được phân bổ theo tỉ lệ mặc định, "
    "không vượt giới hạn tối đa."
)

# Mô tả tỉ lệ các tầng hương
layers = {"Đầu": 0.0, "Giữa": 0.0, "Cuối": 0.0}

for row in rows:
    if row["Tầng hương"] in layers:
        layers[row["Tầng hương"]] += row["Tỉ lệ (%)"]

st.subheader("Tỉ lệ tầng hương")

for name, pct in layers.items():
    st.write(f"{name}: {pct:.3f}%")

if not errors:
    st.success("Công thức hợp lệ về mặt toán học.")
    st.download_button(
        "Tải CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="thu_vu_cong_thuc.csv",
        mime="text/csv"
    )
else:
    for error in errors:
        st.error(error)

st.caption(
    "Kết quả chỉ phản ánh phép tính tỉ lệ, không xác nhận độ an toàn "
    "của công thức. Cần được giáo viên xem xét trước khi pha chế."
)

