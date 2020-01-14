from flask import Flask, render_template, redirect, url_for, request, session
from pymongo import MongoClient
from flask_uploads import UploadSet, IMAGES, configure_uploads
from bson import ObjectId
import datetime	
import hashlib
import time

app = Flask(__name__)
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static'
configure_uploads(app, photos)
app.config['SECRET_KEY'] = 'NEKI RANDOM STRING'
client = MongoClient("mongodb+srv://admin:admin@cluster0-qwp57.mongodb.net/test?retryWrites=true&w=majority")
db = client.get_database("db_test")
users = db["users"]
proizvodi = db["proizvodi"]



@app.route('/')
@app.route('/index')
def index():
	p = list(proizvodi.find())
	korisnik = {}
	korisnik['type'] = "test"
	
	if '_id' in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
		return render_template('index.html', proizvodi = p,korisnik = korisnik,korisnici = users.find())
	return render_template('index.html',proizvodi=p,korisnik = korisnik,korisnici = users.find())

@app.route('/register',methods = ["POST","GET"])
def registracija():
	if request.method == 'GET':
		return render_template('register.html')

	
	if users.find_one({"username": request.form['username']}) is not None:
		return 'Username vec postoji!'
	username = request.form["username"]
	if 'photo' in request.files:
		photos.save(request.files['photo'], 'img', request.form['username'] + '.png')
	slika_korisnika = request.form["username"] + ".png"
	email = request.form["email"]
	password = request.form["password"]
	confirmPassword = request.form["confirmPassword"]
	if password != confirmPassword:
		return "Passwords don't match!"
	hash_object = hashlib.sha256(request.form['password'].encode())
	password_hashed = hash_object.hexdigest()
	hash_object2 = hashlib.sha256(request.form['confirmPassword'].encode())
	confirmPassword_hashed = hash_object2.hexdigest()
	gender = request.form["gender"]
	date_of_birth = request.form["date"]
	tip_korisnika = request.form["usertype"]
	
	unos = {
		"username":username,
		"email":email,
		"password":password_hashed,
		"confirmPassword":confirmPassword_hashed,
		"gender":gender,
		"date":date_of_birth,
		"created": time.strftime("%d-%m-%Y.%H:%M:%S"),
		"type": tip_korisnika,
		'photo':"/static/img/" + slika_korisnika
	}
	users.insert_one(unos)
	return redirect(url_for('login'))
@app.route('/logout')
def logout():
	if "_id" in session:
		session.pop('_id',None)
		session['_id'] = None
		session.clear()
		return redirect(url_for('index'))
	return redirect(url_for('index'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == "GET":
		return render_template('login.html')
	username = request.form["username"]
	password = request.form["password"].encode('utf-8')
	hashpass = hashlib.sha256(password).hexdigest()
	k = users.find_one({"username":username,"password":hashpass})
	if k == None:
		return "Korisnik sa tim imenom ne postoji ili se sifre ne poklapaju"
		
	session['_id'] = str(k['_id'])
	session['type'] = k['type']
	session ['username'] = username
	return redirect(url_for('index'))
@app.route('/dodaj_proizvod',methods = ["POST","GET"])
def dodaj_proizvod():
	if session["type"] != "seller":
		return redirect(url_for('logout'))
	if request.method == "GET":
		return render_template("dodaj_proizvod.html")
	naziv = request.form["naziv"]
	cena = request.form['cena']
	kolicina = request.form['kolicina']
	naziv_slike = request.form["naziv"] + ".png"
	if 'slika' in request.files:
			photos.save(request.files['slika'], 'img', request.form['naziv'] + '.png')
	p = {
		"naziv":naziv,
		'cena':cena,
		'kolicina':kolicina,
		"prodavacId": str(session['_id']),
		'slika': "/static/img/" + naziv_slike
		
	}
	proizvodi.insert_one(p)
	return redirect(url_for('index'))


@app.route('/updateKR/<_id>', methods = ["POST","GET"])
def updateKR(_id):
	k = users.find()
	x = ObjectId(_id)
	korisnik = {}
	korisnik['type'] = "test"
	if "_id" in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
	if request.method == "GET":
		return render_template('update.html',korisnici = k,_id = _id, x = x,korisnik = korisnik)
	email = request.form['email']
	password = request.form['password']	
	gender = request.form['gender']	
	date = request.form['date']
	typeofuser = request.form['usertype']
	k = {
		'email':email,
		"password":password,
		"gender":gender,
		"date":date,
		"typeofuser":typeofuser,
	}		
	users.update_one({"_id":x},{'$set':k})
	return redirect(url_for('index'))



@app.route('/update/<_id>', methods = ["POST", "GET"])
def update(_id):
	p = proizvodi.find()
	x = ObjectId(_id)
	if request.method == "GET":
		return render_template('update.html', proizvodi = p,_id = _id, x = x)
	naziv = request.form["naziv"]
	cena = request.form['cena']
	kolicina = request.form['kolicina']
	
	if 'slika' in request.files:
			photos.save(request.files['slika'], 'img', request.form['naziv'] + '.png')
	naziv_slike = request.form["naziv"] + ".png"
	p = {
		'naziv':naziv,
		"cena":cena,
		"kolicina": kolicina,
		'slika': "/static/img/" + naziv_slike
		
	}
	
	proizvodi.update_one({"_id":x},{'$set':p})
	
	return redirect(url_for('index'))




@app.route('/delete/<_id>', methods = ["POST","GET"])
def delete(_id):
	k = users.find()
	x = ObjectId(_id)
	korisnik = {}
	korisnik['type'] = "test"
	if "_id" in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
	if request.method == "GET":
		return render_template('delete.html',korisnici = k,_id = _id, x = x,korisnik = korisnik)
	users.delete_one({"_id":x})
	return redirect(url_for('index'))

@app.route('/deletePRO/<_id>', methods = ["POST","GET"])
def deletePRO(_id):
	p = proizvodi.find()
	x = ObjectId(_id)
	if request.method == "GET":
		return render_template('delete.html',proizvodi = p, _id = _id, x = x)
	proizvodi.delete_one({"_id":x})	
	return redirect(url_for('index'))		

	

if __name__ == '__main__':
	app.run(debug=True)