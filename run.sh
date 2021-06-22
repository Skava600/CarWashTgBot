python3 -m flask db init;
python3 -m flask db migrate &&
python3 -m flask db upgrade;
python3 /home/src/app/main.py
