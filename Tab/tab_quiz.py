import streamlit as st
import google.generativeai as genai
import json
from database import get_connection


def render_tab_quiz():
    st.markdown("### 📝 Kiểm tra phản xạ từ vựng (AI Quiz)")
    st.write("Hệ thống sẽ bốc ngẫu nhiên các từ vựng Band 8.0 trong Kho của bạn và tạo ra các câu hỏi ngữ cảnh hoàn toàn mới.")

    api_key = st.session_state.get('api_key', "")

    if st.button("Tạo đề thi mới 🎲", type="primary"):
        if not api_key:
            st.warning(
                "⚠️ Bạn chưa cấu hình API Key. Vui lòng sang Tab **⚙️ Cài đặt** để nhập và lưu API Key trước khi tạo đề!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Lấy cả từ cơ bản và câu trả lời nâng cao
            cursor.execute(
                "SELECT TOP 5 TargetWord, AIResponse FROM SavedVocab WHERE UserID = ? ORDER BY NEWID()", (st.session_state['user_id'],))
            vocab_data = cursor.fetchall()
            conn.close()

            if len(vocab_data) < 5:
                st.warning(
                    "Kho từ vựng của bạn cần có ít nhất 5 từ để tạo bài kiểm tra. Hãy sang Tab Tra cứu để tìm và lưu thêm từ nhé!")
                return

            vocab_context = ""
            for basic_word, ai_response in vocab_data:
                vocab_context += f"- Basic word: {basic_word}\n- Advanced synonyms learned:\n{ai_response}\n\n"

            with st.spinner("AI đang soạn đề thi nâng cao (IELTS Band 8.0)..."):
                genai.configure(api_key=api_key)
                available_models = [m.name for m in genai.list_models(
                ) if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(available_models[0])

                prompt = f"""
                You are an expert IELTS examiner. 
                Below are 5 vocabulary entries from the user's study vault. Each entry contains a basic word and a list of advanced IELTS synonyms they learned.
                
                {vocab_context}
                
                Task: Create a multiple-choice vocabulary quiz testing the user on the ADVANCED synonyms.
                For EACH of the 5 entries, pick exactly ONE ADVANCED synonym from the provided text and test the user on it. 
                CRITICAL: DO NOT use the basic word as the correct answer. The correct answer MUST be an advanced synonym.

                For each chosen advanced word, write a high-level academic sentence (IELTS style) with a blank space (____) where the advanced word should fit.
                Provide 4 options (A, B, C, D) where one is the correct advanced word and the others are tricky distractors.
                Output ONLY a valid JSON array of objects. Do NOT wrap it in Markdown code blocks (like ```json).
                Format exactly like this:
                [
                    {{
                        "question": "The government has implemented _____ measures to control inflation.",
                        "options": ["A. stringent", "B. rapid", "C. archaic", "D. minute"],
                        "answer": "A. stringent",
                        "explanation": "Stringent (nghiêm ngặt) is an advanced synonym. Measures for controlling inflation are usually described as stringent."
                    }}
                ]
                """
                response = model.generate_content(prompt)

                raw_json = response.text.replace(
                    "```json", "").replace("```", "").strip()
                quiz_data = json.loads(raw_json)

                st.session_state['current_quiz'] = quiz_data
                st.session_state['quiz_submitted'] = False
                st.session_state['quiz_saved'] = False  # Reset trạng thái lưu

        except json.JSONDecodeError:
            st.error(
                "AI đã trả về định dạng không chuẩn. Vui lòng bấm 'Tạo đề thi mới' lần nữa.")
        except Exception as e:
            st.error(f"Lỗi: {e}")

    # --- KHU VỰC HIỂN THỊ ĐỀ THI ---
    if 'current_quiz' in st.session_state:
        st.markdown("---")
        quiz_data = st.session_state['current_quiz']

        with st.form("quiz_form"):
            user_answers = {}
            for i, q in enumerate(quiz_data):
                st.markdown(f"**Câu {i+1}:** {q['question']}")
                user_answers[i] = st.radio(
                    "Chọn đáp án:", q['options'], key=f"q_{i}", index=None, label_visibility="collapsed")
                st.write("")

            submitted = st.form_submit_button("Nộp bài 💯")

            if submitted:
                if None in user_answers.values():
                    st.warning(
                        "⚠️ Bạn chưa hoàn thành tất cả các câu hỏi! Vui lòng chọn đáp án cho mọi câu trước khi nộp bài.")
                else:
                    st.session_state['quiz_submitted'] = True
                    st.session_state['user_answers'] = user_answers
                    st.rerun()

        # --- KHU VỰC CHẤM ĐIỂM VÀ LƯU TRỮ ---
        if st.session_state.get('quiz_submitted'):
            st.markdown("### 📊 Kết quả của bạn:")
            score = 0
            user_answers = st.session_state['user_answers']

            for i, q in enumerate(quiz_data):
                correct_ans = q['answer']
                user_ans = user_answers[i]

                if user_ans == correct_ans:
                    score += 1
                    st.success(f"**Câu {i+1}: Chính xác!** ({user_ans})")
                else:
                    st.error(
                        f"**Câu {i+1}: Sai rồi.** (Đáp án của bạn: {user_ans} | Đúng: {correct_ans})")

                st.caption(f"💡 Giải thích từ AI: {q['explanation']}")
                st.write("---")

            st.info(f"**Điểm tổng: {score}/{len(quiz_data)}**")
            if score == len(quiz_data):
                st.balloons()

            # Tính năng Lưu Lịch sử Thi
            if not st.session_state.get('quiz_saved', False):
                if st.button("💾 Lưu kết quả bài thi này", type="primary"):
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()

                        # Tự động tạo bảng Lịch sử thi (nếu chưa có)
                        cursor.execute("""
                        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[QuizHistory]') AND type in (N'U'))
                        BEGIN
                            CREATE TABLE QuizHistory (
                                HistoryID INT IDENTITY(1,1) PRIMARY KEY,
                                UserID INT,
                                Score INT,
                                Total INT,
                                QuizDetails NVARCHAR(MAX),
                                CreatedAt DATETIME DEFAULT GETDATE()
                            )
                        END
                        """)
                        conn.commit()

                        # Đóng gói dữ liệu câu hỏi và câu trả lời của người dùng
                        saved_details = []
                        for i, q in enumerate(quiz_data):
                            saved_details.append({
                                "question": q["question"],
                                "correct_answer": q["answer"],
                                "user_answer": user_answers[i],
                                "explanation": q["explanation"]
                            })

                        json_details = json.dumps(
                            saved_details, ensure_ascii=False)

                        cursor.execute("INSERT INTO QuizHistory (UserID, Score, Total, QuizDetails) VALUES (?, ?, ?, ?)",
                                       (st.session_state['user_id'], score, len(quiz_data), json_details))
                        conn.commit()
                        conn.close()

                        st.session_state['quiz_saved'] = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi lưu bài thi: {e}")
            else:
                st.success("✅ Đã lưu bài thi này vào Lịch sử!")

    # --- KHU VỰC XEM LẠI LỊCH SỬ THI ---
    st.markdown("---")
    st.markdown("### 📚 Lịch sử các bài thi cũ")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Kiểm tra xem bảng QuizHistory đã tồn tại chưa để tránh lỗi truy vấn khi app mới chạy
        cursor.execute(
            "IF OBJECT_ID('QuizHistory', 'U') IS NOT NULL SELECT 1 ELSE SELECT 0")
        if cursor.fetchone()[0] == 1:
            cursor.execute(
                "SELECT HistoryID, Score, Total, QuizDetails, CreatedAt FROM QuizHistory WHERE UserID = ? ORDER BY CreatedAt DESC", (st.session_state['user_id'],))
            histories = cursor.fetchall()

            if histories:
                for hist in histories:
                    h_id, h_score, h_total, h_details, h_date = hist
                    with st.expander(f"📝 Bài thi ngày {h_date.strftime('%d/%m/%Y %H:%M')} - Điểm: {h_score}/{h_total}"):
                        details_list = json.loads(h_details)
                        for idx, item in enumerate(details_list):
                            st.markdown(f"**Câu {idx+1}:** {item['question']}")

                            if item['user_answer'] == item['correct_answer']:
                                st.success(
                                    f"**Bạn chọn đúng:** {item['user_answer']}")
                            else:
                                st.error(
                                    f"**Bạn chọn sai:** {item['user_answer']} (Đúng: {item['correct_answer']})")

                            st.caption(f"💡 {item['explanation']}")
                            st.write("---")
            else:
                st.info("Bạn chưa lưu bài thi nào.")
        else:
            st.info("Bạn chưa lưu bài thi nào.")

        conn.close()
    except Exception as e:
        pass  # Bỏ qua lỗi nhẹ nếu database chưa đồng bộ
