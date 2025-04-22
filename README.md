Step 1: Download srouce code <hr/>
Step 2: Create file with fortmat.
`DATABASE_URL=
SESSION_SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_PORT=
MAIL_SERVER=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/auth/google/callback`
<hr/>
Step 3: Run cmd "pip install fastapi uvicorn sqlalchemy psycopg2-binary passlib[bcrypt] python-dotenv email-validator python-multipart authlib httpx python-dotenv" <hr/>
Step 4: Run cmd "uvicorn app.main:app --reload"
