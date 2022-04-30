"""
Routes and views for the flask application.
"""
import os
import subprocess
import main
from datetime import datetime
from flask import Flask, render_template, url_for,request,redirect,send_file, flash
#from example_flask_dockerApp import app
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["XML_UPLOADS"] =  os.getcwd()
app.config["ALLOWED_FILE_EXTENSIONS"] = ["XML","xml"]
def allowed_xmlfile(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else:
        return False

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/tool')
def tool():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("saved file successfully")
      #send file name as parameter to download
            return redirect('/downloadfile/'+ filename)


    """Renders the tool page."""
    return render_template(
        'tool.html',
        title='Tool',
        year=datetime.now().year,
        message='Import your SBOL2 file(.xml) from SBOL Canvas Below'
    )
 
@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )










@app.route("/upload-xml", methods=["GET", "POST"])

def upload_xml():
    #upload xml file function 
    if request.method == "POST":

        if request.files:

            xmlfile = request.files["xmlfile"]

            if xmlfile.filename == "":
                print("No filename")
                return redirect(request.url)

            if allowed_xmlfile(xmlfile.filename):

                filename = secure_filename(xmlfile.filename)
                print(filename)

                xmlfile.save(os.path.join(app.config["XML_UPLOADS"],"XML_UPLOADS//" + filename))
                subprocess.Popen(r'explorer /select,".\DOWNLOAD_FOLDER\ReadME.txt"')
                #xmlfile.save(os.path.join(app.config["XML_UPLOADS"], + filename))
                #THIS IS WHERE THE MAGIC IS GOIN TO HAPPEN....
                #once we have successfully checked that the XML file is valid, before writing it to the 
                #output folder, we are going to run all our back end code on the input to produce a 
                #sequence accurate backend 

                #get assembly method
                assembly = int(request.form.get("select"))
                # call main - backend code to make SBOL2 file sequence accurate
                main.saSBOL(filename,assembly)

                #save newXML
                # very hard to make a way to make not save local .... lots of security issues for browser and path intereaction

               
                print("xml file saved")

                return redirect(request.url)

            else:
                print("That file extension is not allowed")
                return redirect(request.url)

    return render_template("upload_xml.html")














#@app.route('/download')
#def downloadFile ():
#    #For windows you need to use drive name [ex: F:/Example.pdf]
#    path = "/Examples.pdf"
#    return send_file(path, as_attachment=True)


#@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
#def download(filename):
#    # Appending app path to upload folder path within app root folder
#    uploads = os.path.join(example_flask_dockerApp.root_path, app.config['UPLOAD_FOLDER'])
#    # Returning file from appended path
#    return send_from_directory(directory=uploads, filename=filename)


#@app.route('/uploadfile', methods=['GET', 'POST'])
#def upload_file():
#    if request.method == 'POST':
#        # check if the post request has the file part
#        if 'file' not in request.files:
#            print('no file')
#            return redirect(request.url)
#        file = request.files['file']
#        # if user does not select file, browser also
#        # submit a empty part without filename
#        if file.filename == '':
#            print('no filename')
#            return redirect(request.url)
#        else:
#            filename = secure_filename(file.filename)
#            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#            print("saved file successfully")
#      #send file name as parameter to download
#            return redirect('/downloadfile/'+ filename)
#    return render_template('upload_file.html')
@app.route('/upload')
def upload_file():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])


#def upload_file():
#   if request.method == 'POST':
#      f = request.files['file']
#      f.save(secure_filename(f.filename))
#      return 'file uploaded successfully'

# Download API
@app.route("/downloadfile/<filename>", methods = ['GET'])
def download_file(filename):
    return render_template('download.html',value=filename)



@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


@app.after_request
def cache_control(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
    