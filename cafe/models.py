from cafe import db, bcrypt


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password_hash = db.Column(db.String())
    reservations = db.relationship("Reservation", backref="reserved_user", lazy=True)
    confirmed = db.Column(db.Boolean(), nullable=False, default=False)

    @property                           #PASSWORD HASHING
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
            

    def __repr__(self):
        return f"{self.name}"

class Reservation(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.String())
    time = db.Column(db.String())
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
        return f"{self.date}"