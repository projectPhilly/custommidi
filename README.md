## How to run Locally:

1. Clone the repo and then cd into it
2. Create a virtual python environment:
`python3 -m venv venv`
3. Start the virtual py environment:
`. venv/bin/activate`
(you can use `deactivate` to stop it)
4. Bundle the program so it can be installed:
`pip install -e .`
5. Check to make sure it is installed:
`pip list`
6. Start a python command shell:
`pip install ipython`
`ipython`
7. Add the "app" to the global context:
`from custommidi import create_app`
`app = create_app()`
`app.app_context().push()`
8. Initialize the database:
`from custommidi import db`
`db.create_all()`
9. Add in the Admin user:
`from werkzeug.security import generate_password_hash`
`admin = User(username='ProjectPhillyAdmin', password_hash=generate_password_hash('SingingIsLyfe'), isadmin=True)`
`db.session.add(admin)`
`db.session.commit()`
10. Check you successfully added it:
`User.query.all()`
11. Start the application with:
`flask run`
12. Go to `http://127.0.0.1:5000` to see the live site.
