from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

#Category model
class Category(Base):
	__tablename__ = 'categories'
	id = Column(Integer, primary_key=True)
	name = Column(String(32), index=True)
	user = Column(Integer, ForeignKey('users.id'))
	views = Column(Integer)
	likes = Column(Integer)

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id'	: self.id,
			'name' : self.name,
			'views' : self.views,
			'likes' : self.likes,
			'user' : self.user
		}
