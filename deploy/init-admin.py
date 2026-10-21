#!/usr/bin/env python3
"""Create the first administrator over the container's internal HTTP API."""
import json
import os
from pathlib import Path
import secrets
import subprocess

root = Path('/opt/app-postiz')
credential_file = root / 'admin.private.json'
if credential_file.exists():
    raise SystemExit('Administrator receipt already exists; use the existing credentials.')
container = subprocess.check_output([
    'docker', 'ps', '-q', '--filter',
    'label=com.docker.swarm.service.name=app-postiz_app',
], text=True).strip()
if not container or '\n' in container:
    raise SystemExit('Expected one running Postiz app container.')
environment = dict(line.split('=', 1) for line in (root / '.env').read_text().splitlines()
                   if line and not line.startswith('#') and '=' in line)
credentials = {
    'url': 'https://' + environment['POSTIZ_DOMAIN'],
    'email': 'adm@cmkia.com',
    'password': secrets.token_urlsafe(24),
}
payload = dict(email=credentials['email'], password=credentials['password'],
               company='CMKIA', provider='LOCAL')
script = r"""
const http = require('http');
const data = PAYLOAD;
function request(path, body) {
  return new Promise((resolve,reject)=>{
    const req=http.request({hostname:'127.0.0.1',port:3000,path,method:'POST',
      headers:{'Content-Type':'application/json'}},res=>{
      let text=''; res.on('data',c=>text+=c);
      res.on('end',()=>resolve({status:res.statusCode,body:text,authenticated:!!res.headers['set-cookie']}));
    }); req.on('error',reject);req.end(JSON.stringify(body));
  });
}
(async()=>{
  const register=await request('/auth/register',data);
  if(register.status!==200)throw new Error('Administrator registration failed: HTTP '+register.status);
  const login=await request('/auth/login',{email:data.email,password:data.password,provider:'LOCAL'});
  if(login.status!==200||!login.authenticated)throw new Error('Administrator login verification failed');
  console.log('Administrator created; password login and authentication cookie verified.');
})().catch(e=>{console.error(e.message);process.exit(1)});
""".replace('PAYLOAD', json.dumps(payload))
# Save the private recovery receipt before the request so it survives partial failures.
os.umask(0o077)
credential_file.write_text(json.dumps(credentials, indent=2) + '\n')
subprocess.run(['docker', 'exec', '-i', container, 'node'], input=script, text=True, check=True)
print('Private access receipt: /opt/app-postiz/admin.private.json')
