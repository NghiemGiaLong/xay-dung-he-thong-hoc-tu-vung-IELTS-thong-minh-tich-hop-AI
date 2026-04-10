from datetime import datetime, timedelta
from database import get_connection

def update_srs_logic(vocab_id, quality):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT IntervalDays, EaseFactor FROM SavedVocab WHERE VocabID = ?", (vocab_id,))
    row = cursor.fetchone()
    
    interval = 0 if row[0] is None else row[0]
    ef = 2.5 if row[1] is None else row[1]

    if quality == 3:  # Dễ
        if interval == 0: new_interval = 1
        elif interval == 1: new_interval = 6
        else: new_interval = int(interval * ef)
        new_ef = ef + 0.1
    elif quality == 2:  # Trung bình
        new_interval = interval + 1 if interval < 1 else int(interval * 1.2)
        new_ef = ef
    else:  # Khó
        new_interval = 1
        new_ef = max(1.3, ef - 0.2)

    next_date = datetime.now() + timedelta(days=new_interval)

    cursor.execute("""
        UPDATE SavedVocab
        SET IntervalDays = ?, EaseFactor = ?, NextReviewDate = ?
        WHERE VocabID = ?
    """, (new_interval, new_ef, next_date, vocab_id))

    conn.commit()
    conn.close()