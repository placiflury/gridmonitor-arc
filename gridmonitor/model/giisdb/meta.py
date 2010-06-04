"""SQLAlchemy Metadata and Session object """
from sqlalchemy import MetaData

__all__ = ['engine', 'metadata', 'Session']

# SQLAlchemy database engine.  Updated by init_giisdb_model().
engine = None

# SQLAlchemy session manager.  Updated by init_giisdb_model().
Session = None

# Global metadata. If you have multiple databases with overlapping table 
# names, you'll need a metadata for each database.
metadata = MetaData()
