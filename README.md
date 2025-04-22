Step 1: Download srouce code <hr/>
Step 2: Create file `.env` with fortmat.<br/>
DATABASE_URL= <br/>
SESSION_SECRET_KEY= <br/>
ALGORITHM=HS256 <br/>
ACCESS_TOKEN_EXPIRE_MINUTES=30 <br/>
MAIL_USERNAME= <br/>
MAIL_PASSWORD= <br/>
MAIL_FROM= <br/>
MAIL_PORT= <br/>
MAIL_SERVER= <br/>
GOOGLE_CLIENT_ID= <br/>
GOOGLE_CLIENT_SECRET= <br/>
GOOGLE_REDIRECT_URI=
<hr/>
Step 3: Run cmd "pip install fastapi uvicorn sqlalchemy psycopg2-binary passlib[bcrypt] python-dotenv email-validator python-multipart authlib httpx python-dotenv" <hr/>
Step 4: Run cmd "uvicorn app.main:app --reload"
