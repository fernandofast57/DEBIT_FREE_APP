
from app import create_app, db
from app.models.models import User

app = create_app()

with app.app_context():
    admin = User(
        email='admin@example.com',
        username='admin',
        is_admin=True
    )
    admin.set_password('adminpassword')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully")
