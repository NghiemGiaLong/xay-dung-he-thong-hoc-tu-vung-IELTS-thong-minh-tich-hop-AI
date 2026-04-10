import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_connection
import altair as alt


def render_tab_dashboard():
    st.markdown("### 📊 Tổng quan học tập cá nhân")

    try:
        conn = get_connection()

        # --- 1. LẤY DỮ LIỆU TỔNG QUAN (Metrics) ---
        total_vocab = pd.read_sql("SELECT COUNT(*) as total FROM SavedVocab WHERE UserID = ?",
                                  conn, params=[st.session_state['user_id']]).iloc[0]['total']

        due_today = pd.read_sql("SELECT COUNT(*) as due FROM SavedVocab WHERE UserID = ? AND (NextReviewDate <= GETDATE() OR NextReviewDate IS NULL)",
                                conn, params=[st.session_state['user_id']]).iloc[0]['due']

        recent_searches = pd.read_sql("SELECT COUNT(*) as recent FROM SearchHistory WHERE UserID = ? AND SearchTime >= GETDATE() - 7",
                                      conn, params=[st.session_state['user_id']]).iloc[0]['recent']

        # Hiển thị 3 thẻ số liệu lớn (Metrics)
        col1, col2, col3 = st.columns(3)
        col1.metric("📚 Tổng từ trong Kho", f"{total_vocab} từ")
        col2.metric("🎯 Cần ôn hôm nay", f"{due_today} từ", delta="- Cố lên!" if due_today >
                    0 else "Hoàn thành", delta_color="inverse" if due_today > 0 else "normal")
        col3.metric("🔥 Tra cứu tuần này", f"{recent_searches} lần")

        st.write("---")

        # --- 2. VẼ BIỂU ĐỒ HOẠT ĐỘNG 7 NGÀY QUA (Line Chart) ---
        st.markdown("#### 📈 Hoạt động tra cứu 7 ngày gần nhất")
        query_trend = """
            SELECT CONVERT(date, SearchTime) as Date, COUNT(*) as SearchCount
            FROM SearchHistory
            WHERE UserID = ? AND SearchTime >= GETDATE() - 7
            GROUP BY CONVERT(date, SearchTime)
            ORDER BY Date
        """
        df_trend = pd.read_sql(query_trend, conn, params=[
                               st.session_state['user_id']])

        if not df_trend.empty:
            df_trend['Date'] = pd.to_datetime(
                df_trend['Date']).dt.strftime('%d/%m')
            df_trend.set_index('Date', inplace=True)
            st.line_chart(df_trend['SearchCount'], color="#F63366")
        else:
            st.info("Chưa có dữ liệu tra cứu trong 7 ngày qua.")

        st.write("---")

        # --- 3. VẼ BIỂU ĐỒ CHẤT LƯỢNG GHI NHỚ (Bar Chart với Altair) ---
        st.markdown("#### 🧠 Mức độ làm chủ từ vựng")
        query_mastery = """
            SELECT 
                SUM(CASE WHEN EaseFactor > 2.5 THEN 1 ELSE 0 END) as Easy,
                SUM(CASE WHEN EaseFactor = 2.5 THEN 1 ELSE 0 END) as Medium,
                SUM(CASE WHEN EaseFactor < 2.5 THEN 1 ELSE 0 END) as Hard
            FROM SavedVocab WHERE UserID = ?
        """
        df_mastery = pd.read_sql(query_mastery, conn, params=[
                                 st.session_state['user_id']])

        # Rút trích dữ liệu an toàn
        easy_count = df_mastery.iloc[0]['Easy'] or 0
        mid_count = df_mastery.iloc[0]['Medium'] or 0
        hard_count = df_mastery.iloc[0]['Hard'] or 0

        total_rated = easy_count + mid_count + hard_count

        # Chỉ vẽ biểu đồ khi có ít nhất 1 từ đã được đánh giá độ khó
        if total_rated > 0:
            chart_data = pd.DataFrame({
                "Trạng thái": ["🟢 Dễ", "🟡 Trung bình", "🔴 Khó"],
                "Số lượng": [easy_count, mid_count, hard_count]
            })

            # Ép chữ trục X nằm ngang tuyệt đối (labelAngle=0)
            bar_chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Trạng thái', axis=alt.Axis(labelAngle=0, title=None)),
                y=alt.Y('Số lượng', title='Số lượng từ'),
                color=alt.Color('Trạng thái', legend=None)
            ).properties(height=350)

            st.altair_chart(bar_chart, use_container_width=True)

        else:
            st.info(
                "Chưa có dữ liệu tính toán. Hãy sang **🎯 Phòng Ôn tập** đánh giá độ khó của vài từ để AI vẽ biểu đồ nhé!")

        conn.close()
    except Exception as e:
        st.error(f"Lỗi khi tải Dashboard: {e}")
