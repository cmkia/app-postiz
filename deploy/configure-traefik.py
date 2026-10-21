"""Enable a dedicated HTTP ACME resolver; preserves existing Traefik arguments.

Run on the Swarm manager before deploying Postiz. This restarts the shared proxy
once when arguments change. No other services or certificate resolvers change.
"""
import json
import shlex
import subprocess

name = 'im-contabo_traefik'
service = json.loads(subprocess.check_output(['docker', 'service', 'inspect', name], text=True))[0]
args = service['Spec']['TaskTemplate']['ContainerSpec']['Args']
assert '--providers.swarm=true' in args
extra = [
    '--certificatesresolvers.postiz-http.acme.httpchallenge.entrypoint=web',
    '--certificatesresolvers.postiz-http.acme.email=adm@cmkia.com',
    '--certificatesresolvers.postiz-http.acme.storage=/letsencrypt/postiz-http.json',
]
missing = [value for value in extra if value not in args]
if missing:
    subprocess.run(['docker', 'service', 'update', '--args', shlex.join(args + missing), name], check=True)
else:
    print('Postiz HTTP certificate resolver already configured.')
