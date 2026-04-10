import streamlit as st
from database import get_connection
from srs_engine import update_srs_logic


def render_tab_review():
    st.markdown("### 🎯 Mục tiêu hôm nay")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """SELECT TOP 7 VocabID, OriginalSentence, TargetWord, AIResponse, NextReviewDate
                   FROM SavedVocab WHERE UserID = ? AND (NextReviewDate <= GETDATE() OR NextReviewDate IS NULL)
                   ORDER BY NextReviewDate ASC"""
        cursor.execute(query, (st.session_state['user_id'],))
        review_items = cursor.fetchall()
        conn.close()

        if review_items:
            st.info(f"Bạn có {len(review_items)} từ cần ôn tập hôm nay.")
            for item in review_items:
                v_id, sentence, word, response, next_date = item
                with st.expander(f"🔔 {word} (Nhấn để xem nghĩa)"):
                    st.markdown(
                        f"**Câu gốc:** {sentence}\n---\n{response}\n---")
                    st.caption("Bạn thấy từ này thế nào?")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("🔴 Khó", key=f"hard_{v_id}"):
                            update_srs_logic(v_id, 1)
                            st.rerun()
                    with c2:
                        if st.button("🟡 Trung bình", key=f"mid_{v_id}"):
                            update_srs_logic(v_id, 2)
                            st.rerun()
                    with c3:
                        if st.button("🟢 Dễ", key=f"easy_{v_id}"):
                            update_srs_logic(v_id, 3)
                            st.rerun()
        else:
            st.success("🎉 Bạn đã hoàn thành mục tiêu ôn tập hôm nay!")
    except Exception as e:
        st.error(f"Lỗi: {e}")
