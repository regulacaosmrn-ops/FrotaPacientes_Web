from app import db
from app import User, Patient, Trip

db.create_all()

admin = User(username='admin')
admin.set_password('admin123')
db.session.add(admin)
db.session.commit()
print('Banco inicializado com sucesso!')
