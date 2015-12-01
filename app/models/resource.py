from .. import db
from . import Address, User
from random import randint


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    website = db.Column(db.Text)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviews = db.relationship('ResourceReview', backref='resource',
                              lazy='dynamic')

    def __init__(self, name, description, website, address_id, user_id):
        self.name = name
        self.description = description
        self.website = website
        self.address_id = address_id
        self.user_id = user_id

    @staticmethod
    def get_by_resource(name, description, website, address_id, user_id):
        """Helper for searching by all resource fields."""
        result = Resource.query.filter_by(name=name,
                                          description=description,
                                          website=website,
                                          address_id=address_id,
                                          user_id=user_id).first()
        return result

    @staticmethod
    def create_resource(name, description, website, address_id, user_id):
        """
        Helper to create an Resource entry. Returns the newly created Resource
        or the existing entry if all resource fields are already in the table.
        """
        result = Resource.get_by_resource(name,
                                          description,
                                          website,
                                          address_id,
                                          user_id)
        if result is None:
            result = Resource(name=name,
                              description=description,
                              website=website,
                              address_id=address_id,
                              user_id=user_id)
            db.session.add(result)
            db.session.commit()
        return result

    @staticmethod
    def generate_fake(count=10):
        """Generate count fake Resources for testing."""
        from faker import Faker
        from random import choice

        fake = Faker()

        addresses = Address.query.all()
        users = User.query.all()
        for i in range(count):
            r = Resource(
                name=fake.name(),
                description=fake.text(),
                website=fake.url(),
                # TODO: model is address_id and user_id -- why's "_id" left out
                address=choice(addresses),
                user=choice(users)
            )
            db.session.add(r)
            db.session.commit()

    def __repr__(self):
        return '<Resource \'%s\'>' % self.name


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

    def __init__(self, timestamp, content, rating, resource_id, user_id):
        self.timestamp = timestamp
        self.content = content
        self.rating = rating
        self.resource_id = resource_id
        self.user_id = user_id

    @staticmethod
    def generate_fake(count=10):
        """Generate count fake Reviews for testing."""
        from faker import Faker

        fake = Faker()

        # TODO: how can resource_id and user_id be left out of fake data?
        for i in range(count):
            r = ResourceReview(
                timestamp=fake.date_time(),
                content=fake.text(),
                rating=randint(1, 5),
                count_likes=randint(1, 500),
                count_dislikes=randint(1, 500)
            )
            db.session.add(r)
            db.session.commit()

    def __repr__(self):
        return '<ResourceReview <Resource \'%s\'> \'%s\'>' % self.resource_id,\
               self.content
