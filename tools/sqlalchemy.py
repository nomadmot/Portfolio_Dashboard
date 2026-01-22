from sqlalchemy import create_engine, MetaData

DATABASE_URI = "sqlite://///Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/DATA/portfolio-test.db"
print(f"Connecting to: {DATABASE_URI}")
engine = create_engine(DATABASE_URI)
connection = engine.connect()
metadata = engine.raw_connection()
