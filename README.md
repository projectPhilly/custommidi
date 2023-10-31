## How to run Locally:

1. Clone the repo and then cd into it
    * Open terminal and do cd ./filepath/to/folder where you want to store the repo.
    * Make sure you have git installed `git version`
    * Clone the repo `git clone https://github.com/projectPhilly/custommidi.git`
    * Then open in VSCode (if you have the VSCode cli installed then it's `code ./custommidi` otherwise you can navigate to it in the file browser.)
    * See more git tricks lower down
2. Create a virtual python environment:
```
python3 -m venv venv
```
3. Start the virtual py environment:
```
. venv/bin/activate
```
(you can use `deactivate` to stop it)
4. Bundle the program so it can be installed:
```
pip install -e .
```
5. Check to make sure it is installed:
```
pip list
```
6. Start a python command shell:
```
pip install ipython
ipython
```
7. Add the "app" to the global context:
```
from custommidi import create_app
app = create_app()
app.app_context().push()
```
8. Initialize the database:
```
from custommidi import db
db.create_all()
```
9. Add in the Admin user:
```
from custommidi import User
from werkzeug.security import generate_password_hash
admin = User(username='ProjectPhillyAdmin', password_hash=generate_password_hash('SingingIsLyfe'), isadmin=True)
db.session.add(admin)
db.session.commit()
```
10. Check you successfully added it:
```
User.query.all()
```
11. Start the application with:
```
flask run
```
12. Go to `http://127.0.0.1:5000` to see the live site.


### Starting when you return to work on it:
1. Start the virtual py environment:
```
. venv/bin/activate
```
2. Start the application with:
```
flask run
```

### Troubleshooting:
If flask run errors out with something about can't import Markdown from jinja2, then run `pip install Jinja2==3.0.0` to revert to version 3.0 of jinja2 

### Turn on debug mode
run `export FLASK_ENV=development` in the venv console

### Note:
In order for the midis to upload and download properly, you need to add an empty folder called `midifiles` and another inside that called `1`. Might try to add this to the git repo so this comment becomes moot

## Migrating the Database:
1. Install Flask-Migrate if it isn't there already
```
pip install Flask-Migrate
```
2. Create a migration repository (folder) if there isn't one already
```
flask db init
```
3. Generate an initial migration file if there isn't one already
```
flask db migrate -m "Initial migration.
```
4. Create a new migration template
```
flask db revision
```
5. Go in and add your upgrade and downgrade functions. This link may be helpful: [Docs](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script)
6. Run the migration
```
flask db upgrade
```

TODO:
make tracks not show if not real?
add in full list of instruments?
make an error logger?
make troubleshooting page?
could we use mido to make them play aloud?
double check that midis actually line up right


## Midi File Byte index

### MThd = header 
    00 00 00 06 => length of MThd (in bites, is always 6)
    00 01 => format 1
    00 07 => 7 tracks in the file
    XX XX => 2 more bites to indicate the increment of delta-time

### MTrk = signals the beginning of a track
    00 00 00 44 => length of the MTrk (in bites, here 68)
    00 FF 03 (06 text) => track name (06 is the length in bites of the name, then the actual name will follow)
    00 FF 58 (04 04 02 18 08) => the time signature
    00 FF 59 02 (xx xx) => key signature
    00 FF 51 => tempo
    00 B0 07 (64) => change volume (to 100)

## Working With Git:
### Create a branch
When you first download the project and want to begin working on it you may want to create your own branch so you can save your changes. To do this, use the following code:
`git checkout -b name-of-your-new-branch`

Notes about this:
* The branch name can't have any spaces in it
* The branch you are currently on is going to be the one you are branching off of (so if this is your first time doing it, it will be `main`). Hopefully your terminal window should indicate automatically what branch you are on. Basically this means that if you create a new branch off of main, make and commit some changes, and then make another branch of of that branch, you'll have the changes you made, rather than a fresh branch off of main.

### Ready to commit changes?
Once you've made some changes that you're happy with, you're ready to commit your work (and if you're on your own branch, you can and should do this as often as you like/can; the changes won't be live until you push them up to a remote branch). To do this, you must first select the files that you want to keep, which is called "Staging" them. Basically, you'll "add files to the staging area" to tell git that these are the ones you want it to remember. 

To facilitate this, use the `git status` command. This will show you all the files you have changed. The staged ones will be in red, and the staged one will be green. Untracked files will be at the end of the list; these are files that are new to git and have never been added to the repo before.

WARNING: Never commit api keys, secrets, env files, or anything that can't be public. Also avoid committing images, and in the case of this repo, no midi files. There is a `.gitignore` file which tells git which folders not to look at automatically.

#### The full flow:
* See what files you've changed: 
```
git status
```
* Use one or multiple of the following (`git add -A` means add all files)
```
git add filename
git add path/to/filename
git add -A
```
* Run git status again to make sure you've staged the files you meant to:
```
git status
```
* Commit the files. Here are 2 ways to do that:
1. with the `-m` tag to add a message inline
```
git commit -m 'Descriptive message of what the commit contains'
```
2. Without that tag. If you do it without that tag, terminal will open the text editor vim (probably... other text editors include nano and emacs). To add a commit message, press the `i` key, then you should be able to type a message. When finished, press `esc` then type `:wq` then press enter (`w` is for "write" `q` is for "quit"). Apparently for emacs it is ctrl S to save and ctrl C to exit. If none of these work, see if you can figure out what "command line text editor" you're using and look up the commands for that. Apparently the windows git bash editor might have the same `i` to "insert"/edit and then save and exit with `esc` then `:x!` (`:q!` to exit without saving)

### Push to a remote
Your commits and your branches still exist only on your local machine. To make them available for others to look at, or to request to merge them to the main branch (to apply your changes to the live site), you'll need to push the branch to a remote repository. Here are some commands for that
* This will print a list of the remote repositories you have linked. They will also have the name of the repository
```
git remote -v
```

* This will push the repository to the remote depository called "origin". There will always be an "origin" remote as that is meant to be the source of your repo. It will be automatically named that from the remote that you cloned the repo from originally
```
git push origin branch-name
```

* Once you've done this, you can go onto the github site and create a "Pull Request" (sort of a misnomer... it a request to merge the code). This will allow you to see the differences between your code and the main branch and then someone can review it to decide if it's ready to merge

### Keeping your local main branch up to date
Your local `main` branch is a copy of the remote one, and will not update automatically. In order to add new changes to your local main branch and get the most up-to-date version of the app, run the following command to pull the latest version of the branch. You can also do this with any other branch, if changes were made somewhere other than your local env (applied github suggestions are an example of this).
```
git fetch
git checkout main
git pull main
```

### Switching between branches
You can switch between the branches that you have by doing the following command. Press the tab button to autocomplete the branch name. (Sometimes git will error saying that you have local changes with conflicts so you can't switch branches. in this case, you can do `git stash` to stash your changes without committing them)
```
git checkout branch-name
```

### Stashing
You can stash changes without committing them. This makes it so that you can temporarily remove your changes and put them back later if you want to. This doesn't count as committing them.
```
git stash
```

### A super useful tool:

I highly recommend using a GUI (Guided User Interface) for git. It lets you do all the stuff I just mentioned above, but it lets you actually look at what changes you've made and easily select specific files to stage. Fork is the one I use because it's free, GitKraken is also popular but a lot of features are behind paywalls. Links below:
* [Fork](https://git-fork.com/)
* [GitKraken](https://www.gitkraken.com/)

