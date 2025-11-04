# Cloud-smart-storage (Smart Drive)

A mini Google Drive: users register/login, upload files to AWS S3, list, share via presigned links, and delete. Backend: Flask + JWT + DynamoDB + S3. Frontend: HTML/CSS/Bootstrap + vanilla JS.

## Features
- JWT-based auth (register/login)
- Upload files to S3 (per-user folder prefix)
- Store file metadata in DynamoDB
- List files for logged-in user
- Delete files (S3 + DynamoDB)
- Generate 1-hour presigned GET URLs for sharing

## Tech Stack
- Backend: Flask, Flask-JWT-Extended, Flask-CORS, boto3
- Frontend: HTML, Bootstrap 5, Vanilla JS (fetch + localStorage)
- DB: AWS DynamoDB
- Storage: AWS S3

## Project Structure
```
smart-drive/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   └── utils/
│       └── db.py
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── script.js
│   └── style.css
└── README.md
```

## AWS Setup
1. S3: create bucket `smart-drive-files` (or your own name)
2. DynamoDB:
   - Files table: name `SmartDriveFiles`, partition key `username` (String), sort key `file_name` (String)
   - Users table: name `SmartDriveUsers`, partition key `username` (String)
3. IAM policy (attach to app credentials):
   - S3: `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`
   - DynamoDB on above tables: `GetItem`, `PutItem`, `DeleteItem`, `Query`

## Backend – Local Run
Prereqs: Python 3.10+, AWS credentials with the above permissions

```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
export AWS_REGION=us-east-1
export S3_BUCKET_NAME=smart-drive-files
export DDB_FILES_TABLE=SmartDriveFiles
export DDB_USERS_TABLE=SmartDriveUsers
export JWT_SECRET_KEY=change-me
# Standard AWS env vars must be set too:
# export AWS_ACCESS_KEY_ID=...
# export AWS_SECRET_ACCESS_KEY=...
# optionally: export AWS_SESSION_TOKEN=...
python app.py
```
Server runs at `http://localhost:5000`.

## API Endpoints
- POST `/register` { username, password }
- POST `/login` { username, password } → { access_token }
- POST `/upload` (multipart `file`) [JWT]
- GET `/files` [JWT]
- DELETE `/delete/<filename>` [JWT]
- GET `/share/<filename>` [JWT]

Notes:
- S3 key format: `<username>/<filename>`
- Presigned link validity: 3600 seconds

## Frontend – Local Preview
Open `frontend/index.html` directly in a browser, or serve statically.

Configure API URL if not default:
```
# In browser console or small inline script (optional)
localStorage.setItem('API_URL', 'http://localhost:5000');
```

## Deployment
### Backend (EC2 / Render)
- Set environment variables: `AWS_REGION`, `S3_BUCKET_NAME`, `DDB_FILES_TABLE`, `DDB_USERS_TABLE`, `JWT_SECRET_KEY`, and AWS credentials.
- Run with `gunicorn` or `python app.py`. Make port public (e.g., 5000/80) and enable CORS.

### Frontend (Vercel / Netlify)
- Deploy the `frontend/` folder as a static site.
- Point it to your backend by setting `localStorage.setItem('API_URL', 'https://your-backend.example.com')`.

## Security Notes
- Never commit real AWS credentials. Use env vars or instance roles.
- Use strong `JWT_SECRET_KEY` in production.
- Consider S3 bucket with private ACLs (default). All access should go through presigned URLs.

## Troubleshooting
- 401 on file endpoints: ensure `Authorization: Bearer <token>` header is set.
- 403 from S3: check IAM policy and bucket region; ensure correct bucket name.
- DynamoDB `ValidationException`: verify table keys match (`username` PK, `file_name` SK) and region.

## License
MIT


