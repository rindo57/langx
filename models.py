from flask_pymongo import PyMongo
from bson import ObjectId
from geopy.distance import geodesic

# Initialize MongoDB
mongo = PyMongo()

# AppUser Model
class AppUser:
    def __init__(self, firstname, lastname, lookup_address, fluent_languages, other_languages, 
                 email, password, interests, geom=None, profile_pic='default.jpg', coord_latitude=None, coord_longitude=None):
        self.firstname = firstname
        self.lastname = lastname
        self.lookup_address = lookup_address
        self.fluent_languages = fluent_languages
        self.other_languages = other_languages
        self.email = email
        self.password = password
        self.interests = interests
        self.profile_pic = profile_pic
        self.coord_latitude = coord_latitude
        self.coord_longitude = coord_longitude
        self.geom = geom  # This is a GeoJSON point or a custom spatial representation
    
    @classmethod
    def from_mongo(cls, data):
        """Create an AppUser instance from a MongoDB document."""
        return cls(
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            lookup_address=data.get('lookup_address'),
            fluent_languages=data.get('fluent_languages'),
            other_languages=data.get('other_languages'),
            email=data.get('email'),
            password=data.get('password'),
            interests=data.get('interests'),
            profile_pic=data.get('profile_pic', 'default.jpg'),
            coord_latitude=data.get('coord_latitude'),
            coord_longitude=data.get('coord_longitude'),
            geom=data.get('geom')
        )
    
    def to_dict(self):
        """Convert the AppUser instance to a dictionary for MongoDB."""
        return {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'lookup_address': self.lookup_address,
            'fluent_languages': self.fluent_languages,
            'other_languages': self.other_languages,
            'email': self.email,
            'password': self.password,
            'interests': self.interests,
            'profile_pic': self.profile_pic,
            'coord_latitude': self.coord_latitude,
            'coord_longitude': self.coord_longitude,
            'geom': self.geom
        }

    @staticmethod
    def get_items_within_radius(latitude, longitude, radius):
        """Find users within a given radius from a location using geospatial queries."""
        # MongoDB needs a geospatial index on the 'geom' field for geo queries.
        results = mongo.db.app_users.find({
            'geom': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [longitude, latitude]
                    },
                    '$maxDistance': radius * 1000  # Convert radius to meters
                }
            }
        })
        users = [AppUser.from_mongo(user) for user in results]
        return users

# SampleLocation Model
class SampleLocation:
    def __init__(self, description, latitude, longitude, geom=None):
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
        self.geom = geom or {'type': 'Point', 'coordinates': [longitude, latitude]}

    def insert(self):
        """Insert the location into the MongoDB collection."""
        mongo.db.sample_locations.insert_one(self.to_dict())
    
    def to_dict(self):
        """Convert the SampleLocation instance to a dictionary for MongoDB."""
        return {
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'geom': self.geom
        }

    @staticmethod
    def from_mongo(data):
        """Create a SampleLocation instance from a MongoDB document."""
        return SampleLocation(
            description=data.get('description'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            geom=data.get('geom')
        )

    @staticmethod
    def get_locations_nearby(latitude, longitude, radius):
        """Find locations within a given radius from a point."""
        # MongoDB needs a geospatial index on the 'geom' field for geo queries.
        results = mongo.db.sample_locations.find({
            'geom': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [longitude, latitude]
                    },
                    '$maxDistance': radius * 1000  # Radius in meters
                }
            }
        })
        locations = [SampleLocation.from_mongo(location) for location in results]
        return locations

# SpatialConstants for geospatial functions (e.g., creating GeoJSON points)
class SpatialConstants:
    @staticmethod
    def point_representation(latitude, longitude):
        """Return a GeoJSON-like Point representation."""
        return {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }

# Helper function to calculate distance between two lat-longs (in meters)
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters
