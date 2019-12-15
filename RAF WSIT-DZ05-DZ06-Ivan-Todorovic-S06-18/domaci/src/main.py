from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')

@app.route('/RAFraspored')

def raspored():
	f = open("RAFraspored.csv","r")
	redovi = f.readlines()

	sva_imena = [red.split(',')[2] for red in redovi]
	jedinstvena_imena = []
	for ime in sva_imena:
		if ime not in jedinstvena_imena:
			jedinstvena_imena.append(ime)

	
	sve_ucionice = [red.split(',')[6] for red in redovi]
	posebne_ucionice = []
	for ucionica in sve_ucionice:
		if ucionica not in posebne_ucionice:
			posebne_ucionice.append(ucionica)

	return render_template("RAFraspored.html",redovi = redovi, sva_imena = jedinstvena_imena, sve_ucionice = posebne_ucionice)

if __name__ == '__main__':
	app.run()