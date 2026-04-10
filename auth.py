import streamlit as st
import hashlib
from database import get_connection

# Hàm mã hóa mật khẩu
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# --- MÀN HÌNH ĐĂNG NHẬP / ĐĂNG KÝ ---
def login_signup_ui():
    st.title("🔐 V LEPENSEUR IELTS")
    st.write("Vui lòng đăng nhập để lưu trữ từ vựng và lịch sử học tập của bạn.")
    st.write("---")

    tab_login, tab_signup = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký tài khoản"])

    # 1. TAB ĐĂNG NHẬP
    with tab_login:
        username_login = st.text_input("Tên đăng nhập", key="login_user")
        password_login = st.text_input("Mật khẩu", type="password", key="login_pass")

        if st.button("Đăng nhập", type="primary", use_container_width=True):
            if username_login and password_login:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    hashed_pw = hash_password(password_login)

                    cursor.execute("SELECT UserID, Username FROM Users WHERE Username=? AND PasswordHash=?",
                                   (username_login, hashed_pw))
                    user = cursor.fetchone()

                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user[0]
                        st.session_state['username'] = user[1]
                        st.rerun()
                    else:
                        st.error("Sai tên đăng nhập hoặc mật khẩu!")
                    conn.close()
                except Exception as e:
                    st.error(f"Lỗi kết nối CSDL: {e}")
            else:
                st.warning("Vui lòng nhập đầy đủ thông tin.")

    # 2. TAB ĐĂNG KÝ
    with tab_signup:
        new_username = st.text_input("Tên đăng nhập mới", key="reg_user")
        new_password = st.text_input("Mật khẩu", type="password", key="reg_pass")
        confirm_password = st.text_input("Nhập lại mật khẩu", type="password", key="reg_pass_confirm")

        if st.button("Đăng ký", use_container_width=True):
            if len(new_username) < 3:
                st.error("Tên đăng nhập phải có ít nhất 3 ký tự!")
            elif new_password != confirm_password:
                st.error("Mật khẩu nhập lại không khớp!")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute("SELECT UserID FROM Users WHERE Username=?", (new_username,))
                    if cursor.fetchone():
                        st.error("Tên đăng nhập này đã có người sử dụng!")
                    else:
                        hashed_pw = hash_password(new_password)
                        cursor.execute("INSERT INTO Users (Username, PasswordHash) VALUES (?, ?)",
                                       (new_username, hashed_pw))
                        conn.commit()
                        st.success("Tạo tài khoản thành công! Bạn có thể chuyển sang tab Đăng nhập.")
                    conn.close()
                except Exception as e:
                    st.error(f"Lỗi kết nối CSDL: {e}")