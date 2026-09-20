from database.database import engine, Base
from database.models import User


def init_database():
    Base.metadata.create_all(bind=engine)
    print("Palm Mitra database initialized successfully.")


if __name__ == "__main__":
    init_database()