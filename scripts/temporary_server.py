"""Password-protected temporary sharing. Listen only on loopback behind an HTTPS tunnel."""
import base64
import json
import os
from pathlib import Path
import secrets
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import create_app

credential_file=Path(__file__).resolve().parents[1]/'instance/temporary-access.json'

def require_access(environ,start_response):
    supplied=environ.get('HTTP_AUTHORIZATION','')
    username=password=''
    try:
        kind,encoded=supplied.split(' ',1)
        if kind.lower()=='basic': username,password=base64.b64decode(encoded,validate=True).decode().split(':',1)
    except (ValueError,UnicodeError):pass
    configured=os.environ.get('PREVIEW_PASSWORD')
    credentials={'username':os.environ.get('PREVIEW_USERNAME','preview'),'password':configured} if configured else json.loads(credential_file.read_text())
    valid_user=secrets.compare_digest(username.encode(),credentials['username'].encode())
    valid_password=secrets.compare_digest(password.encode(),credentials['password'].encode())
    if not (valid_user and valid_password):
        start_response('401 Unauthorized',[('Content-Type','text/plain; charset=utf-8'),('WWW-Authenticate','Basic realm="Course Studio temporary access", charset="UTF-8"'),('Cache-Control','no-store')])
        return [b'Temporary access credentials are required.']
    return application(environ,start_response)

application=create_app()
application.config.update(SESSION_COOKIE_SECURE=True)
