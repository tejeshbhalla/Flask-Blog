from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_mail import Mail



app = Flask(__name__)
app.config['SECRET_KEY']='uU(}wQEt[yW2n-}TdU#?GpgTaq^[TU[Kx)1VKGVQp&{v&F/rxF@puuFVxT'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'

app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']='Youremail@something.com'
app.config['MAIL_PASSWORD']='Yourpassword'

mail=Mail(app)

bcrypt=Bcrypt(app)

db=SQLAlchemy(app)
db.create_all()

login_manager=LoginManager(app)
login_manager.login_view='login'


ckeditor = CKEditor(app)




from flask_blog import routes