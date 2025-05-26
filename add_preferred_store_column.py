from main import db, app
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE ingredient ADD COLUMN preferred_store VARCHAR(100);"))
        db.session.commit()
        print("✅ Стовпець preferred_store успішно додано.")
    except Exception as e:
        print("❌ Помилка при додаванні стовпця:", e)
