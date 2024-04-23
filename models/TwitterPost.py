from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from models.BaseModel import EntityMeta
from sqlalchemy.orm import relationship

class TwitterPost(EntityMeta):
    __tablename__ = "twitter_posts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True))
    post_type = Column(String)
    
    user = relationship("User", back_populates="twitter_posts")