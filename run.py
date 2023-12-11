import os

from controls import app

port = int(os.getenv("PORT", 5000))

app.secret_key = os.urandom(24)
app.run(debug=True, port=port, host='0.0.0.0')
