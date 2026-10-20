import pandas as pd
import streamlit as st
from formula_logic import INGREDIENTS, calculate_formula, describe_layers

# Thu Vũ — công cụ tính toán công thức nước hoa mùa thu.
st.set_page_config(page_title="Thu Vũ", layout="wide")

APP_TITLE = "Thu Vũ"
SAFETY_NOTE = "Cần giáo viên duyệt an toàn trước khi pha."

def make_csv(df):
    # utf-8-sig helps spreadsheet programs recognize Vietnamese text correctly.
    return df.to_csv(index=False, float_format="%.3f").encode("utf-8-sig")


st.title(APP_TITLE)
st.caption("Công cụ tính toán công thức nước hoa mùa thu")

with st.container(border=True):
    st.subheader("1. Thiết lập mẻ")
    volume_ml = st.number_input(
        "Thể tích mẻ (mL)",
        min_value=1.0,
        max_value=20.0,
        value=10.0,
        step=0.5,
        help="Chọn thể tích từ 1 đến 20 mL.",
    )

st.subheader("2. Điều chỉnh thành phần")
st.caption(
    "Các giới hạn đang dùng theo cấu hình dự án hiện tại. "
    "Hãy xác nhận chúng với giáo viên trước khi sử dụng."
)

percentages = {}
cols = st.columns(2)
for index, (name, config) in enumerate(INGREDIENTS.items()):
    with cols[index % 2]:
        percentages[name] = st.slider(
            f"{name} (%)",
            min_value=0.0,
            max_value=float(config["max"]),
            value=float(config["default"]),
            step=0.01,
            format="%.2f",
            key=f"pct_{index}",
        )

df, errors, total_pct, fragrance_total, solvent_pct = calculate_formula(
    volume_ml, percentages
)

st.subheader("3. Kết quả công thức")
metric1, metric2, metric3 = st.columns(3)
metric1.metric("Thể tích mẻ", f"{volume_ml:.3f} mL")
metric2.metric("Tổng 5 thành phần điều chỉnh", f"{fragrance_total:.3f}%")
metric3.metric("Dung môi còn lại", f"{solvent_pct:.3f}%")

display_df = df.copy()
display_df["Tỉ lệ (%)"] = display_df["Tỉ lệ (%)"].map(lambda x: f"{x:.3f}")
display_df["Thể tích (mL)"] = display_df["Thể tích (mL)"].map(lambda x: f"{x:.3f}")
st.dataframe(display_df, use_container_width=True, hide_index=True)

st.caption(
    "Công thức mặc định: bốn loại tinh dầu tạo hương chiếm 10%; "
    "chất lưu hương được tính riêng 3%. Vì vậy, tổng năm thành phần điều chỉnh là 13%."
)

st.subheader("4. Mô tả tầng hương")
for layer, total, names in describe_layers(df):
    st.write(f"**{layer} — {total:.3f}%:** {names}.")

st.warning(SAFETY_NOTE)

if errors:
    for error in errors:
        st.error(error)
    st.info("Hãy điều chỉnh công thức để sửa các lỗi trước khi xuất CSV.")
else:
    st.success("Công thức hợp lệ về mặt toán học.")
    st.download_button(
        "Tải bảng công thức CSV",
        data=make_csv(df),
        file_name="thu_vu_cong_thuc_mua_thu.csv",
        mime="text/csv",
        help="Tệp CSV dùng mã hóa UTF-8 có BOM để hỗ trợ tiếng Việt.",
    )

with st.expander("Giới hạn và cách tính"):
    st.write(
        "- Dung môi được tính bằng 100% trừ tổng năm thành phần điều chỉnh.\n"
        "- Phần dung môi được chia thành nước và cồn theo tỉ lệ ban đầu 0,4 : 8,3.\n"
        "- Các con số hiển thị được làm tròn đến ba chữ số thập phân; phép tính nội bộ dùng giá trị đầy đủ.\n"
        "- Ứng dụng chỉ kiểm tra tính hợp lệ về mặt toán học, không xác nhận độ an toàn hoặc độ phù hợp khi sử dụng trên da."

