import streamlit as st
import google.generativeai as genai
from database import get_connection


def render_tab_ai():
    st.markdown("### 🧠 Phân tích Từ vựng IELTS bằng AI")

    # --- LẤY API KEY NGẦM TỪ BỘ NHỚ (TAB CÀI ĐẶT) ---
    api_key = st.session_state.get('api_key', "")

    col1, col2 = st.columns([3, 1])
    with col1:
        sentence = st.text_input(
            "Nhập câu tiếng Anh gốc:", placeholder="The building is very big.")
    with col2:
        target_word = st.text_input("Từ muốn nâng cấp:", placeholder="big")

    if st.button("Phân tích AI 🚀", type="primary"):
        # Kiểm tra API Key riêng
        if not api_key:
            st.warning(
                "⚠️ Bạn chưa cấu hình API Key. Vui lòng sang Tab **⚙️ Cài đặt** để nhập và lưu API Key trước khi tra cứu!")
        # Kiểm tra nội dung nhập riêng
        elif not sentence or not target_word:
            st.warning("Vui lòng nhập đầy đủ câu gốc và từ muốn nâng cấp!")
        else:
            with st.spinner("Đợi tí nhé..."):
                try:
                    genai.configure(api_key=api_key)
                    available_models = [m.name for m in genai.list_models(
                    ) if 'generateContent' in m.supported_generation_methods]
                    if not available_models:
                        st.error("API Key không hỗ trợ tạo văn bản.")
                        st.stop()

                    model = genai.GenerativeModel(available_models[0])
                    prompt = f"""
                    You are an expert IELTS examiner.
                    Original sentence: "{sentence}"
                    Word to replace: "{target_word}"
                    Task: Suggest 3 advanced vocabulary words (IELTS Band 7.5 - 9.0) to replace the target word, ensuring they perfectly fit the grammatical and semantic context of the original sentence.
                    Format the output clearly with:
                    1. The advanced word.
                    2. Brief explanation in Vietnamese.
                    3. A new example sentence.
                    """
                    response = model.generate_content(prompt)

                    st.session_state['last_ai_response'] = response.text
                    st.session_state['last_sentence'] = sentence
                    st.session_state['last_target'] = target_word

                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO SearchHistory (UserID, OriginalSentence, TargetWord, AIResponse) VALUES (?, ?, ?, ?)",
                                   (st.session_state['user_id'], sentence, target_word, response.text))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    st.error(f"Lỗi: {e}")

    if 'last_ai_response' in st.session_state:
        st.markdown("### 🎯 Kết quả đề xuất:")
        st.info(st.session_state['last_ai_response'])
        if st.button("⭐ Lưu kết quả này vào Kho Từ Vựng"):
            try:
                conn = get_connection()
                cursor = conn.cursor()

                # Kiểm tra trùng lặp
                cursor.execute("SELECT VocabID FROM SavedVocab WHERE UserID=? AND TargetWord=?",
                               (st.session_state['user_id'], st.session_state['last_target']))

                if cursor.fetchone():
                    st.warning(
                        "⚠️ Từ này đã có trong Kho từ vựng của bạn rồi!")
                else:
                    cursor.execute(
                        "INSERT INTO SavedVocab (UserID, OriginalSentence, TargetWord, AIResponse, NextReviewDate) VALUES (?, ?, ?, ?, GETDATE())",
                        (st.session_state['user_id'], st.session_state['last_sentence'],
                         st.session_state['last_target'], st.session_state['last_ai_response'])
                    )
                    conn.commit()
                    st.success(
                        "✅ Đã lưu thành công! Hãy sang Tab Kho Từ Vựng để xem.")

                conn.close()
            except Exception as e:
                st.error(f"Lỗi khi lưu: {e}")
