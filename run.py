import os

from views import app

app.secret_key = os.urandom(24)
app.run(debug=True)
