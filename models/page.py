from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

#Page model
class Page(Base):
	__tablename__ = 'pages'
	id = Column(Integer, primary_key=True)
	category = Column(Integer, ForeignKey('categories.id'))
	title = Column(String(32))
	url = Column(String(32))
	views = Column(Integer)
	user = Column(Integer, ForeignKey('users.id'))

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id'	: self.id,
			'title' : self.title,
			'views' : self.views,
			'url' : self.url,
			'category' : self.category,
			'user' : self.user
		}
