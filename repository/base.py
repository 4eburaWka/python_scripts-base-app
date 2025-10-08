from database.database import AsyncSession, get_db


class BaseRepository:
    db: AsyncSession
    
    def __init__(self, db: AsyncSession = get_db()):
        self.db = db
        