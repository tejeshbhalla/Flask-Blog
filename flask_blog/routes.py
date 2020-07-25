import secrets
import os 
from PIL import Image
from flask import render_template,url_for,flash,redirect,request,abort
from flask_blog.forms import Register_form, LoginForm,Account_Form,PostForm,Request_Reset,Reset_Form
from flask_blog.models import User,POST
from flask_blog import app
from flask_blog import bcrypt,db,mail
from flask_login import login_user,current_user,logout_user,login_required
from flask_blog import ckeditor 
from flask_mail import Message


@app.route('/home')
@app.route('/')
def home():
	page_no=request.args.get('page',1,type=int)
	posts=POST.query.order_by(POST.date_posted.desc()).paginate(per_page=5,page=page_no)
	return render_template('home.html',posts=posts,title='Myblog')


@app.route('/about')
def about():
	return render_template('about.html')


@app.route('/register',methods=['POST','GET'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form=Register_form()
	if form.validate_on_submit():
		hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user=User(username=form.username.data,email=form.email.data,password=hashed_password)
		db.session.add(user)
		db.session.commit()


		flash(f'Account Created for {form.username.data}','success')
		return redirect(url_for('login'))
	return render_template('register.html',form=form)

@app.route('/login',methods=['POST','GET'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form=LoginForm()
	if form.validate_on_submit():
			user=User.query.filter_by(username=form.username.data).first()

			if user and bcrypt.check_password_hash(user.password,form.password.data):
				login_user(user,remember=form.remember.data)
				flash(f'Login Successfull for {form.username.data} ','success')
				return redirect(url_for('home'))
			else:
				flash(f'Incorrect Details ! Check your username and password','danger')
	return render_template('login.html',title='Login',form=form)


def save_picture(picture_data):
	
	random_hex=secrets.token_hex(8)

	_,f_ext=os.path.splitext(picture_data.filename)

	picture_fn=random_hex+f_ext

	picture_path=os.path.join(app.root_path,'static/profile_pics',picture_fn)


	output_size=(125,125)

	i=Image.open(picture_data)

	i.thumbnail(output_size)

	i.save(picture_path)

	return picture_fn









@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))




@app.route('/account',methods=['POST','GET'])
def account():

	if not current_user.is_authenticated:
		flash(f'Please Login First','info')
		return redirect('login')
	image_file=url_for('static',filename='profile_pics/'+current_user.image_file)
	form=Account_Form()
	if form.validate_on_submit():
		if form.picture.data:
			image_file=save_picture(form.picture.data)
			current_user.image_file=image_file
		current_user.username=form.username.data
		current_user.email=form.email.data
		db.session.commit()

		flash(f'Your Details Have Been Updated','success')
		return redirect(url_for('account'))

	elif request.method=='GET':
		form.username.data=current_user.username
		form.email.data=current_user.email

	return  render_template('account.html',title='account',image=image_file,form=form,is_post=True)





@app.route('/post_new',methods=['POST','GET'])
def new_post():
	if not current_user.is_authenticated:
		flash(f'Please Login First','info')
		return redirect('login')

	form=PostForm()

	if form.validate_on_submit():
		post=POST(title=form.title.data,content=form.content.data,author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your Post has Been Created','success')
		return(redirect('home'))

	return render_template('create_post.html',title='New Post',form=form,legend='New Post',is_post=True)





@app.route('/post/<int:post_id>')
def post(post_id):
	post=POST.query.get_or_404(post_id)
	return render_template('post.html',title=post.title,post=post,is_post=True)





@app.route('/post/<int:post_id>/edit',methods=['POST','GET'])
def edit_post(post_id):
	post=POST.query.get_or_404(post_id)

	if post.author!=current_user:
		abort(403)

	form=PostForm()


	if form.validate_on_submit():
		post.title=form.title.data
		post.content=form.content.data
		db.session.commit()

		flash(f'Your post  has been updated !','success')
		return redirect(url_for('post',post_id=post.id))



	if request.method=='GET':
		form.title.data=post.title
		form.content.data=post.content

	return render_template('create_post.html',title='Edit Post',legend='Edit Post',form=form,is_post=True)






@app.route('/post/<int:post_id>/delete',methods=['POST','GET'])
def delete_post(post_id):
	post=POST.query.get_or_404(post_id)


	if post.author!=current_user:
		abort(403)

	db.session.delete(post)
	db.session.commit()

	flash(f'Your post  has been deleted !','success')

	return render_template('deleted.html',is_post=True)



def send_reset_email(user):
	token=user.get_reset_token()
	msg=Message('Password Reset Request',sender='noreply@mail.com',recipients=[user.email])

	msg.body=f""" Hi {user.username}, To reset your password visit the following link 
	link- {url_for('reset_token',token=token,_external=True)}
	*** The token will expire in 30 mins *** """

	mail.send(msg)


@app.route('/reset_password',methods=['GET','POST'])

def reset_request():
	if current_user.is_authenticated:
		return redirect('home')

	form=Request_Reset()

	if request.method=='POST':

		user=User.query.filter_by(email=form.email.data).first()

		if user is None:
			flash('No email with that user exists ! Register First','warning')
			return redirect(url_for('reset_request'))
		send_reset_email(user)

		flash('An Email With Instructions To Reset Password Has Been Sent On Your Email','success')



	return render_template('reset_request.html',title='Reset Password',form=form,is_post=True)







@app.route('/reset_password/<token>',methods=['POST','GET'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	user=User.verify_token(token)

	if user is None:
		flash('Invalid or Expired Token','warning')
		return redirect(url_for('reset_request'))

	form=Reset_Form()

	if request.method=='POST':

		hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password=hashed_password
		db.session.commit()


		flash(f'Password Changed!, You Can Now Log-In ','success')
		return redirect(url_for('login'))



	return render_template('reset_password.html',title='Reset Password',form=form)




#error handling 



@app.errorhandler(404)
def error_404(e):
	Message=f'Error Page Not Found- {404}'
	return render_template('error.html',title='Error',Message=Message),404



@app.errorhandler(403)
def error_403(e):
	Message=f'You are Not Allowed to Perform This Action-{403}'
	return render_template('error.html',title='Error',Message=Message),403


@app.errorhandler(500)
def error_404(e):
	Message='The Website Has Encountered Some Issues . It Must Be An Error On Our Side !. Please Try Again Later -{500}'
	return render_template('error.html',title='Error',Message=Message),500


