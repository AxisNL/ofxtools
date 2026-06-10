# Ofxtools

This is a project with a small web application to convert all kinds of financial transaction files (csv, ofx) to 
different formats, for example to import into Quickbooks Online.

It is a containerized Django Python web application. It's ugly code, but it works, and needs a lot of improvement ;)

## Using ofxtools

Go to the ofxtools directory, and run:

    docker build -t axisnl/ofxtools .

Then run it:

    docker run -it --rm -p 8000:8000 axisnl/ofxtools

And then connect your browser to http://localhost:8000 to use the application.