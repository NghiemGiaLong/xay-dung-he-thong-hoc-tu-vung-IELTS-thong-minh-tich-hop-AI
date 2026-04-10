import streamlit as st

# Nhập các module giao diện từ các file đã tách
# (Đảm bảo file auth.py và main_app.py đang nằm cùng thư mục với file này)
from auth import login_signup_ui
from main_app import main_app_ui

# --- CẤU HÌNH TRANG WEB ---
# Lệnh này bắt buộc phải nằm đầu tiên và chỉ gọi 1 lần trong toàn bộ ứng dụng
st.set_page_config(page_title="V LEPENSEUR - IELTS AI",
                   page_icon="🔐", layout="centered")

# --- KHỞI TẠO BỘ NHỚ (SESSION STATE) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

# --- BỘ ĐỊNH TUYẾN (ROUTER) ---
# Kiểm tra xem người dùng đã đăng nhập chưa để điều hướng
if st.session_state.get('logged_in'):
    # Nếu đã đăng nhập -> Chạy giao diện AI và Kho từ vựng
    main_app_ui()
else:
    # Nếu chưa đăng nhập -> Hiện màn hình Đăng nhập / Đăng ký
    login_signup_ui()
