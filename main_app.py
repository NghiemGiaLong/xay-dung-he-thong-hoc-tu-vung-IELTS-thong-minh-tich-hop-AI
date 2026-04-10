import streamlit as st

# Kéo các hàm vẽ giao diện từ 6 file riêng biệt vào
from Tab.tab_dashboard import render_tab_dashboard
from Tab.tab_ai import render_tab_ai
from Tab.tab_history import render_tab_history
from Tab.tab_vault import render_tab_vault
from Tab.tab_review import render_tab_review
from Tab.tab_quiz import render_tab_quiz
from Tab.tab_settings import render_tab_settings


def main_app_ui():
    st.success(
        f"🎉 Chào mừng **{st.session_state['username']}** đã quay trở lại!")

    if st.button("Đăng xuất 🚪"):
        st.session_state.clear()
        st.rerun()

    st.write("---")

    # Sắp xếp thứ tự các tab
    tabs = st.tabs([
        "📊 Tổng quan",   # Vị trí số 0
        "🧠 Tra cứu AI",  # Vị trí số 1
        "🕒 Lịch sử",     # Vị trí số 2
        "📚 Kho từ vựng",  # Vị trí số 3
        "🎯 Phòng Ôn tập",  # Vị trí số 4
        "📝 Quiz",        # Vị trí số 5
        "⚙️ Cài đặt"     # Vị trí số 6
    ])

    with tabs[0]:
        render_tab_dashboard()
    with tabs[1]:
        render_tab_ai()
    with tabs[2]:
        render_tab_history()
    with tabs[3]:
        render_tab_vault()
    with tabs[4]:
        render_tab_review()
    with tabs[5]:
        render_tab_quiz()
    with tabs[6]:
        render_tab_settings()
