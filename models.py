# Model za bazu podataka

from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
from hashlib import md5
import datetime

DATABASE = SqliteDatabase('social.db')

class User(UserMixin, Model):  # Model je klasa za rad sa tabelarnom bazom podataka. Moze postojati vise parent klasa
    username = CharField(unique=True)  # UserMixin sadrzava metode get_id(), validaciju, autentikaciju...
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)  # U slucaju sortiranja, od zadnjeg pridruzenog

    def get_posts(self):  # Funkcija kojom se primaju svi postovi za trenutnog usera
        return Post.select().where(Post.user == self)

    def get_stream(self):  # Funkcija koja se ponasa kao newsfeed postova sa postovima povezanih usera
        return Post.select().where(
            (Post.user << self.following()) | (Post.user == self)
        )

    def following(self):    # Vraca sve usere koje pratimo
        return(
            User.select().join(Relationship, on=Relationship.to_user).where(
                Relationship.from_user == self)
        )

    def followers(self):    # Vraca sve usere koje prate selektiranog usera
        return(
            User.select().join(Relationship, on=Relationship.from_user).where(
                Relationship.to_user == self)
        )

    def avatar(self, size):     # Funkcija koja dohvaca avatar sa Gravatar-a
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    # Classmethod dekorator upucuje na to da funkcija pravi instancu klase
    # Metoda za kreiranje novih usera
    # Metoda ne prima self, nego cls(klasu), tako da se ne treba svaki put praviti nova instanca usera
    # koja poziva metodu create_user
    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:  # Try catch blok
            with DATABASE.transaction():  # Transaction ako uspije nastavi, ako ne onda izbrise sve napravljeno
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists!")  # U slucaju istog usernamea ili emaila

class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    # rel_model upucuje na related Model tj. User model u ovom slucaju
    # related_name je naziv s kojim rel_model poziva ovaj model
    # Oboje su potrebni za foreign key field
    # ForeignKeyField - polje koje upucuje na zapis u bazi podataka
    user = ForeignKeyField(User, rel_model=User, related_name='posts')
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)  # Sortiranje prema zadnjem zabiljezenom vremenu

class Relationship(Model):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = DATABASE
        indexes = ((('from_user', 'to_user'), True),)

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()
