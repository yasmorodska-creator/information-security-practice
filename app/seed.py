from app.security import hash_password
from app.database import SessionLocal
from app.models import Role, Permission, User, Group, Subject


def seed():
    db = SessionLocal()
    try:
        # Якщо вже є ролі — значить база вже засіяна
        if db.query(Role).first():
            print("Database already seeded.")
            return

        # --- Ролі ---
        admin = Role(name="admin", description="Адміністратор деканату")
        teacher = Role(name="teacher", description="Викладач")
        student = Role(name="student", description="Студент")
        db.add_all([admin, teacher, student])
        db.flush()

        # --- Права ---
        perms = [
            Permission(name="read_grades", description="Перегляд оцінок"),
            Permission(name="edit_grades", description="Редагування оцінок"),
            Permission(name="read_schedule", description="Перегляд розкладу"),
            Permission(name="manage_users", description="Управління користувачами"),
            Permission(name="manage_groups", description="Управління групами"),
            Permission(name="manage_subjects", description="Управління дисциплінами"),
            Permission(name="view_reports", description="Перегляд звітів"),
        ]
        db.add_all(perms)
        db.flush()

        # --- Призначення прав ---
        admin.permissions.extend(perms)

        teacher.permissions.extend([
            p for p in perms if p.name in (
                "read_grades",
                "edit_grades",
                "read_schedule",
                "view_reports"
            )
        ])

        student.permissions.extend([
            p for p in perms if p.name in (
                "read_grades",
                "read_schedule"
            )
        ])

        # --- Група ---
        group = Group(name="КН-31", department="Комп'ютерні науки", year=3)
        db.add(group)
        db.flush()

        # --- Предмет ---
        subject = Subject(
            name="Безпека інформаційних систем",
            credits=4.0,
            semester=5
        )
        db.add(subject)

        # --- Тестові користувачі (З ХЕШЕМ) ---
        admin_user = User(
            username="admin",
            email="admin@university.edu",
            full_name="Адміністратор Системи",
            password_hash=hash_password("Admin123!@#"),
            is_active=True
        )
        admin_user.roles.append(admin)

        teacher_user = User(
            username="teacher01",
            email="teacher@university.edu",
            full_name="Іваненко П.М.",
            password_hash=hash_password("Teacher123!")
        )
        teacher_user.roles.append(teacher)

        student_user = User(
            username="student01",
            email="student@university.edu",
            full_name="Петренко М.О.",
            password_hash=hash_password("Student123!"),
            group_id=group.id
        )
        student_user.roles.append(student)

        db.add_all([admin_user, teacher_user, student_user])

        # --- Збереження ---
        db.commit()
        print("✅ Seed completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()