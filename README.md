[finance_app.py](https://github.com/user-attachments/files/24909571/finance_app.py)
import streamlit as st
import pandas as pd
import numpy as np
[requirements.txt](https://github.com/user-attachments/files/24909580/requirements.txt)streamlit
pandas
numpy

# Cấu hình trang
st.set_page_config(page_title="Tài Chính Xuân Lai - Smart Invest", layout="wide")

st.title("🚀 Smart Invest - Web App Quản Lý Mục Tiêu Tài Chính")
st.markdown("---")

# --- SIDEBAR: NHẬP LIỆU ---
st.sidebar.header("📥 Cài đặt thông số")
principal = st.sidebar.number_input("Vốn gốc ban đầu (VNĐ)", value=100000000, step=10000000)
monthly_deposit = st.sidebar.number_input("Tiền gửi thêm hàng tháng (VNĐ)", value=1000000, step=500000)
annual_rate = st.sidebar.slider("Lãi suất kỳ vọng (%/năm)", 0.0, 30.0, 12.0)
inflation_rate = st.sidebar.slider("Tỷ lệ lạm phát dự kiến (%/năm)", 0.0, 10.0, 4.0)

# --- MODULE 1: QUY TẮC GẤP ĐÔI (RULE OF 72) ---
st.header("🔍 Tra cứu mục tiêu: Khi nào tiền tăng gấp đôi?")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Theo lãi suất")
    target_rate = st.number_input("Nhập lãi suất bạn muốn (%/năm):", value=annual_rate)
    if target_rate > 0:
        years_rule_72 = 72 / target_rate
        # Tính toán chính xác bằng Logarit
        years_exact = np.log(2) / np.log(1 + (target_rate/100))
        st.info(f"👉 Ước tính (Quy tắc 72): ~**{years_rule_72:.2f} năm**")
        st.success(f"👉 Chính xác: **{years_exact:.2f} năm**")

with col2:
    st.subheader("Theo số năm")
    target_years = st.number_input("Nhập số năm bạn muốn đạt được (năm):", value=5.0)
    if target_years > 0:
        rate_rule_72 = 72 / target_years
        # Tính toán chính xác
        rate_exact = (pow(2, 1/target_years) - 1) * 100
        st.info(f"👉 Lãi suất ước tính: ~**{rate_rule_72:.2f}%/năm**")
        st.success(f"👉 Lãi suất chính xác: **{rate_exact:.2f}%/năm**")

st.markdown("---")

# --- MODULE 2: TÍNH TOÁN DÒNG TIỀN CHI TIẾT ---
st.header("📊 Lộ trình tăng trưởng tài sản")

# Tính toán
months = 120 # Giả định mặc định 10 năm để vẽ biểu đồ
monthly_rate = (annual_rate / 100) / 12
data = []
current_balance = principal

for m in range(1, months + 1):
    interest = current_balance * monthly_rate
    current_balance += interest + monthly_deposit
    # Tính giá trị thực sau lạm phát
    real_value = current_balance / pow(1 + (inflation_rate/100), m/12)
    
    data.append({
        "Tháng": m,
        "Năm": round(m/12, 1),
        "Tổng tài sản (VNĐ)": round(current_balance),
        "Giá trị thực tế (Trừ lạm phát)": round(real_value)
    })

df = pd.DataFrame(data)

# Biểu đồ
st.line_chart(df.set_index('Năm')[['Tổng tài sản (VNĐ)', 'Giá trị thực tế (Trừ lạm phát)']])

# Bảng dữ liệu rút gọn
st.subheader("📋 Bảng tổng hợp theo năm")
df_yearly = df[df['Tháng'] % 12 == 0]
st.dataframe(df_yearly.style.format("{:,.0f}"))

st.markdown("""
> **Lưu ý của Chuyên gia:** > - Kết quả dựa trên giả định lãi suất không đổi và được nhập gốc hàng tháng.
> - 'Giá trị thực tế' giúp bạn hình dung sức mua của số tiền đó tại thời điểm hiện tại.
""")
