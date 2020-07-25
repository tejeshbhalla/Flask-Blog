from flask_wtf import FlaskForm 
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flask_blog.models import User
from flask_login import current_user
from flask_ckeditor import CKEditorField

class Register_form(FlaskForm):
	username=StringField('Username',
		validators=[DataRequired(),Length(min=2,max=20)])
	email=StringField('Email',validators=[DataRequired(),Email()])

	password=PasswordField('Password',validators=[DataRequired()])

	confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])

	submit=SubmitField('Sign Up')

	def validate_username(self,username):

		user=User.query.filter_by(username=username.data).first()

		if user:
			raise ValidationError('Username is taken . Please choose a different Username !  ')

	def validate_email(self,email):

		email=User.query.filter_by(email=email.data).first()

		if email:
			raise ValidationError('Email is taken . Please choose a different  Email !  ')



class LoginForm(FlaskForm):
	username=StringField('Username',
		validators=[DataRequired()])

	password=PasswordField('Password',validators=[DataRequired()])

	remember=BooleanField('Remember Me')
	submit=SubmitField('Login')




class Account_Form(FlaskForm):
	username=StringField('Username',
		validators=[DataRequired(),Length(min=2,max=20)])
	email=StringField('Email',validators=[DataRequired(),Email()])

	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

	submit=SubmitField('Update Details')



	def validate_username(self,username):

		if username.data!=current_user.username:

			user=User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('Username is taken . Please choose a different Username !  ')

	def validate_email(self,email):
		if email.data!=current_user.email:
			email=User.query.filter_by(email=email.data).first()
			if email:
				raise ValidationError('Email is taken . Please choose a different  Email !  ')



class PostForm(FlaskForm):
	title=StringField('Title',validators=[DataRequired()])
	content=CKEditorField('Body',validators=[DataRequired()])
	submit=SubmitField('Post')




class Request_Reset(FlaskForm):
	email=StringField('Email',validators=[DataRequired(),Email()])

	submit=SubmitField('Request Reset Mail')




	def validate_email(self,email):
			email=User.query.filter_by(email=email.data).first()
			if email is None:
				raise ValidationError('No User with this email exists !  ')



class Reset_Form(FlaskForm):
	password=PasswordField('Password',validators=[DataRequired()])

	confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])

	submit=SubmitField('Confirm Change')