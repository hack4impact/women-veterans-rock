from .. import db
from geopy.geocoders import Nominatim


class ZIPCode(db.Model):
    __tablename__ = 'zip_codes'
    id = db.Column(db.Integer, primary_key=True)
    zip_code = db.Column(db.String(5), unique=True, index=True)
    users = db.relationship('User', backref='zip_code', lazy='dynamic')
    addresses = db.relationship('Address', backref='zip_code', lazy='dynamic')
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)

    def __init__(self, zip_code):
        """
        If possible, the helper methods get_by_zip_code and create_zip_code
        should be used instead of explicitly using this constructor.
        """
        getcoords = Nominatim(country_bias='us')
        loc = getcoords.geocode(zip_code)
        if loc is None:
            raise ValueError('zip code \'%s\' is invalid' % zip_code)
        self.longitude = loc.longitude
        self.latitude = loc.latitude
        self.zip_code = zip_code

    @staticmethod
    def get_by_zip_code(zip_code):
        """Helper for searching by 5 digit zip codes."""
        result = ZIPCode.query.filter_by(zip_code=zip_code).first()
        return result

    @staticmethod
    def create_zip_code(zip_code):
        """
        Helper to create a ZIPCode entry. Returns the newly created ZIPCode
        or the existing entry if zip_code is already in the table.
        """
        result = ZIPCode.get_by_zip_code(zip_code)
        if result is None:
            result = ZIPCode(zip_code)
            db.session.add(result)
            db.session.commit()
        return result

    @staticmethod
    def generate_fake():
        """
        Populate the zip_codes table with arbitrary but real zip codes.
        The zip codes generated by the faker library
        are not necessarily valid or guaranteed to be located in the US.
        """
        zip_codes = ['19104', '01810', '02420', '75205', '94305',
                     '47906', '60521']

        for zip_code in zip_codes:
            ZIPCode.create_zip_code(zip_code)

    def __repr__(self):
        return '<ZIPCode \'%s\'>' % self.zip_code


class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)         # ABC MOVERS
    street_address = db.Column(db.Text)  # 1500 E MAIN AVE STE 201
    city = db.Column(db.Text)
    state = db.Column(db.String(2))
    zip_code_id = db.Column(db.Integer, db.ForeignKey('zip_codes.id'))
    resources = db.relationship('Resource', backref='address', lazy='dynamic')

    def __repr__(self):
        return '<Address \'%s\'>' % self.name

    @staticmethod
    def get_by_address(name, street_address, city, state, zip_code_id):
        """Helper for searching by all address fields."""
        result = Address.query.filter_by(name=name,
                                         street_address=street_address,
                                         city=city,
                                         state=state,
                                         zip_code_id=zip_code_id).first()
        return result

    @staticmethod
    def create_address(name, street_address, city, state, zip_code_id):
        """
        Helper to create an Address entry. Returns the newly created Address
        or the existing entry if address is already in the table.
        """
        result = Address.get_by_address(name,
                                        street_address,
                                        city,
                                        state,
                                        zip_code_id)
        if result is None:
            result = Address(name=name,
                             street_address=street_address,
                             city=city,
                             state=state,
                             zip_code_id=zip_code_id)
            db.session.add(result)
            db.session.commit()
        return result

    @staticmethod
    def generate_fake(count=10):
        """Generate count fake Addresses for testing."""
        from faker import Faker
        from random import choice

        fake = Faker()

        zip_codes = ZIPCode.query.all()
        for i in range(count):
            a = Address(
                name=fake.name(),
                street_address=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                zip_code=choice(zip_codes)
            )
            db.session.add(a)
            db.session.commit()
