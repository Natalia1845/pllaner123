from main import db, app
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE weekly_menu ADD COLUMN meal_type VARCHAR(20);"))
        db.session.commit()
        print("✅ Стовпець meal_type успішно додано.")
    except Exception as e:
        print("❌ Помилка при додаванні meal_type:", e)
