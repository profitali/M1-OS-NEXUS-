from app.db.database import engine
from app.db import models

print("Creating database tables...")
models.Base.metadata.create_all(bind=engine)
print("Done.")
