pip3 install flask_sqlalchemy
pip3 install flask_cors
pip3 install flask --upgrade
pip3 uninstall flask-socketio -y
service postgresql start
psql -U postgres -p 5433 -f "backend/setup.sql"
psql -U postgres -p 5433 -d trivia -f "backend/trivia.psql"
psql -U postgres -p 5433 -d trivia_test -f "backend/trivia.psql"
