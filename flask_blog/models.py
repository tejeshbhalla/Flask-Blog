from datetime import datetime
from flask_blog import db,login_manager,app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer




@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model,UserMixin):
	id=db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(20),unique=True,nullable=False)
	email=db.Column(db.String(120),unique=True,nullable=False)
	image_file=db.Column(db.String(20),nullable=False,default='default.jpg')
	password=db.Column(db.String(60),nullable=False)
	posts=db.relationship('POST',backref='author',lazy=True)    # lazy means it will return the data in one go  
	#this posts col allows us to view the user who created the post 
	def __repr__(self):
		return f"User('{self.username}','{self.email}','{self.image_file}')"


	def get_reset_token(self,expires_time=1800):
		s=Serializer(app.config['SECRET_KEY'],expires_time)

		return s.dumps({'user_id':self.id}).decode('utf-8')

	@staticmethod 
	def verify_token(token):
			s=Serializer(app.config['SECRET_KEY'])

			try:
				user_id=s.loads(token)['user_id']

			except:
				return None

			return User.query.get(user_id)


class POST(db.Model,UserMixin):
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String(100),nullable=False)
	date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
	content=db.Column(db.Text,nullable=False)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

	def __repr__(self):
		return f"Post('{self.title}','{self.date_posted}')"