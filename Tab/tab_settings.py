import streamlit as st
from database import get_connection
from auth import hash_password


def render_tab_settings():
    st.markdown("### ⚙️ Cài đặt ứng dụng")
    st.write("Quản lý tài khoản, cấu hình API và giao diện cá nhân.")

    # --- 1. QUẢN LÝ TÀI KHOẢN ---
    st.markdown("#### 👤 Quản lý tài khoản")

    with st.expander("Thay đổi Tên đăng nhập & Mật khẩu", expanded=False):
        with st.form("change_account_form"):
            st.info(
                f"Tên đăng nhập hiện tại của bạn là: **{st.session_state.get('username', '')}**")

            new_username = st.text_input(
                "Tên đăng nhập mới (Để trống nếu không muốn đổi):")

            st.write("---")
            current_password = st.text_input(
                "Mật khẩu hiện tại (Bắt buộc để xác thực):", type="password")
            new_password = st.text_input(
                "Mật khẩu mới (Để trống nếu không muốn đổi):", type="password")
            confirm_password = st.text_input(
                "Nhập lại Mật khẩu mới:", type="password")

            submitted = st.form_submit_button("Lưu thay đổi 💾")

            if submitted:
                if not current_password:
                    st.error(
                        "⚠️ Vui lòng nhập Mật khẩu hiện tại để hệ thống xác nhận bạn là chủ tài khoản!")
                elif new_password and new_password != confirm_password:
                    st.error(
                        "⚠️ Mật khẩu mới và Nhập lại mật khẩu không khớp nhau!")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()

                        # --- ĐIỂM SỬA CHỮA 1: Mã hóa mật khẩu hiện tại và so sánh với cột PasswordHash ---
                        hashed_current = hash_password(current_password)
                        cursor.execute("SELECT UserID FROM Users WHERE UserID = ? AND PasswordHash = ?",
                                       (st.session_state['user_id'], hashed_current))

                        if not cursor.fetchone():
                            st.error("⚠️ Mật khẩu hiện tại không chính xác!")
                        else:
                            update_queries = []
                            params = []
                            should_update = True

                            # Xử lý đổi tên
                            if new_username and new_username != st.session_state['username']:
                                cursor.execute(
                                    "SELECT UserID FROM Users WHERE Username = ?", (new_username,))
                                if cursor.fetchone():
                                    st.warning(
                                        "⚠️ Tên đăng nhập này đã có người sử dụng. Vui lòng chọn tên khác.")
                                    should_update = False
                                else:
                                    update_queries.append("Username = ?")
                                    params.append(new_username)

                            # --- ĐIỂM SỬA CHỮA 2: Mã hóa mật khẩu mới và lưu vào cột PasswordHash ---
                            if new_password:
                                hashed_new = hash_password(new_password)
                                update_queries.append("PasswordHash = ?")
                                params.append(hashed_new)

                            # Thực thi cập nhật
                            if update_queries and should_update:
                                params.append(st.session_state['user_id'])
                                sql = f"UPDATE Users SET {', '.join(update_queries)} WHERE UserID = ?"

                                cursor.execute(sql, tuple(params))
                                conn.commit()

                                if new_username:
                                    st.session_state['username'] = new_username

                                st.success(
                                    "✅ Cập nhật thông tin tài khoản thành công!")
                                st.rerun()
                            elif not update_queries and should_update:
                                st.info(
                                    "💡 Bạn chưa nhập thông tin mới nào để thay đổi.")

                        conn.close()
                    except Exception as e:
                        st.error(f"Lỗi hệ thống: {e}")

    st.write("---")

    # --- 2. CẤU HÌNH API KEY ---
    st.markdown("#### 🔑 Cấu hình Gemini API")
    current_key = st.session_state.get('api_key', "")

    new_key = st.text_input(
        "Nhập Google Gemini API Key:",
        value=current_key,
        type="password",
        help="API Key này sẽ được dùng chung cho tất cả các tính năng AI trong App."
    )

    if st.button("Lưu API Key"):
        st.session_state['api_key'] = new_key
        st.success("✅ Đã lưu API Key vào hệ thống!")

    st.write("---")

    # --- 3. HƯỚNG DẪN GIAO DIỆN CHUẨN ---
    st.markdown("#### 🎨 Tùy chỉnh giao diện Sáng / Tối")
    st.info("💡 Để đảm bảo tốc độ và không bị vỡ bố cục, ứng dụng sử dụng công cụ Theme chính chủ của Streamlit. 👉 Bạn hãy nhìn lên **góc trên cùng bên phải màn hình**, bấm vào **Dấu 3 chấm (⋮) ➡️ Settings ➡️ Theme** để chọn màu Sáng/Tối mà bạn yêu thích.")
    st.write("---")
    st.caption("Phiên bản App: 2.2.0 | Developer: V LEPENSEUR")
