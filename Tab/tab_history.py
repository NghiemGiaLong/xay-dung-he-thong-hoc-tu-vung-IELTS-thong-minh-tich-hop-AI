import streamlit as st
from database import get_connection


def render_tab_history():
    st.markdown("### 🕒 Lịch sử tra cứu của bạn")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Lấy đầy đủ dữ liệu bao gồm cả AIResponse
        query = """
            SELECT OriginalSentence, TargetWord, AIResponse, SearchTime 
            FROM SearchHistory 
            WHERE UserID = ? 
            ORDER BY SearchTime DESC
        """
        cursor.execute(query, (st.session_state['user_id'],))
        history_items = cursor.fetchall()
        conn.close()

        if history_items:
            st.caption(
                f"Bạn đã tra cứu tổng cộng: **{len(history_items)}** từ.")

            for idx, item in enumerate(history_items):
                sentence, word, response, search_time = item

                # Vẽ giao diện thẻ mở rộng
                with st.expander(f"🕒 {word} (Tra lúc: {search_time.strftime('%d/%m/%Y %H:%M')})"):
                    st.markdown(f"**Câu gốc:** {sentence}")
                    st.markdown("---")

                    # Xử lý các từ cũ chưa được lưu kết quả AI
                    if response is None:
                        st.warning(
                            "⚠️ Lịch sử này được tra cứu từ phiên bản cũ của app nên không lưu lại kết quả. Hãy dùng Tab Tra cứu để tìm lại nhé!")
                    else:
                        st.markdown(response)
                        st.write("---")

                        # Nút thêm trực tiếp vào kho từ vựng
                        if st.button("⭐ Thêm vào Kho Từ Vựng & Ôn tập", key=f"save_hist_{idx}"):
                            try:
                                conn_save = get_connection()
                                cur_save = conn_save.cursor()

                                # Kiểm tra xem đã có trong Kho chưa để tránh lưu trùng lặp
                                cur_save.execute("SELECT VocabID FROM SavedVocab WHERE UserID=? AND TargetWord=?",
                                                 (st.session_state['user_id'], word))
                                if cur_save.fetchone():
                                    st.warning(
                                        "Từ này đã có trong Kho từ vựng của bạn rồi!")
                                else:
                                    cur_save.execute(
                                        "INSERT INTO SavedVocab (UserID, OriginalSentence, TargetWord, AIResponse, NextReviewDate) VALUES (?, ?, ?, ?, GETDATE())",
                                        (st.session_state['user_id'],
                                         sentence, word, response)
                                    )
                                    conn_save.commit()
                                    st.success(
                                        "✅ Đã thêm vào Kho từ vựng thành công! Hãy sang Tab Ôn tập để kiểm tra.")
                                conn_save.close()
                            except Exception as e:
                                st.error(f"Lỗi khi lưu: {e}")
        else:
            st.info("Bạn chưa có lịch sử tìm kiếm nào.")
    except Exception as e:
        st.error(f"Lỗi tải lịch sử: {e}")
