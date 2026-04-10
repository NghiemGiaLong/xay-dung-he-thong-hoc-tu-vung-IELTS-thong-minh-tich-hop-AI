import streamlit as st
from datetime import datetime
from database import get_connection

# Hàm xử lý xóa từ vựng


def delete_vocab(vocab_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM SavedVocab WHERE VocabID = ?", (vocab_id,))
        conn.commit()
        conn.close()
        st.success("✅ Đã xóa từ vựng thành công!")
        st.rerun()  # Tải lại trang để cập nhật danh sách ngay lập tức
    except Exception as e:
        st.error(f"Lỗi khi xóa: {e}")


def render_tab_vault():
    st.markdown("### 📚 Tất cả từ vựng của bạn")

    # --- ĐIỂM NÂNG CẤP: Tùy chọn sắp xếp thông minh thay vì kéo thả ---
    sort_option = st.radio(
        "Sắp xếp danh sách theo:",
        ["🕒 Mới thêm gần đây", "🔥 Cần ôn tập gấp"],
        horizontal=True
    )
    st.write("---")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --- ĐIỂM SỬA CHỮA: Lấy thêm VocabID và thay đổi logic ORDER BY ---
        if sort_option == "🔥 Cần ôn tập gấp":
            # Đẩy những từ có NextReviewDate cũ nhất (cần học nhất) lên đầu
            query = "SELECT VocabID, OriginalSentence, TargetWord, AIResponse, NextReviewDate FROM SavedVocab WHERE UserID = ? ORDER BY NextReviewDate ASC"
        else:
            # Mặc định: Từ nào mới lưu thì nằm ở trên (VocabID giảm dần)
            query = "SELECT VocabID, OriginalSentence, TargetWord, AIResponse, NextReviewDate FROM SavedVocab WHERE UserID = ? ORDER BY VocabID DESC"

        cursor.execute(query, (st.session_state['user_id'],))
        vault_items = cursor.fetchall()
        conn.close()

        if vault_items:
            st.caption(f"Tổng cộng: **{len(vault_items)}** từ đang được lưu.")

            for item in vault_items:
                vocab_id, sentence, word, response, next_date = item

                if next_date is None:
                    next_date = datetime.now()
                is_due = next_date <= datetime.now()
                status = "🔔 Cần ôn ngay" if is_due else f"Hẹn ôn: {next_date.strftime('%d/%m/%Y')}"

                with st.expander(f"📌 {word} ({status})"):
                    st.markdown(f"**Câu gốc:** {sentence}")
                    st.markdown("---")
                    st.markdown(response)

                    # --- ĐIỂM NÂNG CẤP: Khu vực thao tác ---
                    st.write("")  # Tạo khoảng trắng cho thoáng
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        # Thêm key độc nhất (vocab_id) để Streamlit phân biệt các nút bấm
                        if st.button("🗑️ Xóa từ", key=f"del_{vocab_id}", type="secondary", use_container_width=True):
                            delete_vocab(vocab_id)
        else:
            st.info(
                "Kho từ vựng đang trống. Hãy sang Tab Tra cứu AI để thêm từ mới nhé!")

    except Exception as e:
        st.error(f"Lỗi tải kho từ vựng: {e}")
