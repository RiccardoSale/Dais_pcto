from flask_login import UserMixin
from dais_pcto.app import db
from dais_pcto.module_extensions import bcrypt

user_course = db.Table('user_corse',
                       db.Column('user_id', db.Integer, db.ForeignKey('users._user_id')),
                       db.Column('course_id', db.Integer, db.ForeignKey('courses._course_id'))
                       )

user_lesson = db.Table('user_lesson',
                       db.Column('user_id', db.Integer, db.ForeignKey('users._user_id')),
                       db.Column('lesson_id', db.Integer, db.ForeignKey('lessons._lesson_id'))
                       )


# tabella secondaria per relazione molti a molti tra utenti e corsi


class User(UserMixin, db.Model):
    __tablename__ = "users"

    _user_id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(64), unique=False, nullable=False)
    _surname = db.Column(db.String(64), unique=False, nullable=False)
    _email = db.Column(db.String(60), unique=True, nullable=False, index=True)
    _password = db.Column(db.String(128),
                          nullable=False)  # lunghezza dopo hashing CONTROLLARE DOPO AVER LIMITATO PASSWORD A TOT CARATTERI
    # cambiare form iscrizione aggiungendo campo choice -> con scuole !!!
    _role = db.Column(db.String(10), nullable=False,
                      default="user")  # serve per l identificazione user /admin / professor

    _courses = db.relationship("Course", secondary=user_course,
                               back_populates="_users")  # necessaria per relazione molti a molti !

    _lessons = db.relationship("Lesson", secondary=user_lesson,
                               back_populates="_users")

    _school = db.Column(db.String, db.ForeignKey(
        'h_schools._hschool_code'))

    # uno a molti -> legata a chiave esterna professor
    _courses_prof = db.relationship('Course', backref='users', cascade="all, delete")

    def __init__(self, name, surname, email, password, role):
        self._name = name
        self._surname = surname
        self._email = email
        self._password = password
        self._role = role

    def __repr__(self):
        return self._email

    def subscribe_course(self, course):
        if course:
            self._courses.append(course)
            self.update()

    def unsubscribe_course(self, course):
        if course:
            self._courses.remove(course)
            self.update()

    def subscribe_lesson(self, lesson):
        if lesson:
            self._lessons.append(lesson)
            self.update()

    def professor_course(self, course):
        if course:
            self._courses_prof.append(course)
            self.update()

    def set_password(self, password):
        if password != "":
            self._password = bcrypt.generate_password_hash(password).decode('utf8')

    def set_name(self, name):
        if name != "":
            self._name = name

    def set_surname(self, surname):
        if surname != "":
            self._surname = surname

    def set_email(self, email):
        if email != "":
            self._email = email

    def get_id(self):
        return self._user_id

def user_with_email(email):
    return db.session.query(User).filter_by(_email=email)

def user_with_id(id):
    return db.session.query(User).filter_by(_user_id=id)

def users_with_role(role):
    return db.session.query(User).filter_by(_role=role)



