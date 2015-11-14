from .. import db
from . import Address
from random import randint


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    website = db.Column(db.Text)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'))
    reviews = db.relationship('ResourceReview', backref='resource',
                              lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, description, website, address):
        self.name = name
        self.description = description
        self.website = website
        self.address = address

    def __repr__(self):
        return '<Resource \'%s\'>' % self.name

    @staticmethod
    def generate_fake(count=10):
        """Generate count fake Resources for testing."""
        from faker import Faker
        from random import choice

        fake = Faker()

        for i in range(count):
            r = Resource(
                name=fake.name(),
                description=fake.sentences(),
                website=fake.url(),
                address=choice(Address.query.all())
            )
            db.session.add(r)
            db.session.commit()


class ResourceReview(db.Model):
    __tablename__ = 'resource_reviews'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    content = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1 to 5
    count_likes = db.Column(db.Integer, default=0)
    count_dislikes = db.Column(db.Integer, default=0)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<ResourceReview <Resource \'%s\'> \'%s\'>' % self.resource_id,\
               self.content

    @staticmethod
    def generate_fake(count=10):
        """Generate count fake Reviews for testing."""
        from faker import Faker

        fake = Faker()

        for i in range(count):
            r = ResourceReview(
                timestamp=fake.date_time(),
                content=fake.sentences(),
                rating=randint(1, 5),
                count_likes=randint(1, 500),
                count_dislikes=randint(1, 500)
            )
            db.session.add(r)
            db.session.commit()
