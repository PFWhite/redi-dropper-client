"""
This file shows how to create a user through the dropper API.

Importantly, it requires an existing user with a token that is
made through the interface. Once one exists, you are able to make
new users with tokens. The tokens will expire after one year so
they will need to be re-generated.

Note that users created this way dont need to actually have emails
for the user name.

Identity and role permissions will be enforced when using token.
"""
import requests as req
import json

dropper_url = 'https://localhost:7088'
admin_email = 'asura@ufl.edu'
admin_token = '79KE8E1QK0JIQP2VUWQEX7F96QMTXAQW'
creds = (admin_email, admin_token)

username = 'quail'

def url_path(path):
    return '/'.join([dropper_url, path])

print('trying save')
print(url_path('api/save_user'))
res = req.post(url_path('api/save_user'), auth=creds, data={
    'email': username,
    'first': 'api',
    'last': 'token',
    'minitial': 'X',
}, verify=False)

print(res.content)
user_data = json.loads(res.content).get('data')

res = req.post(url_path('api/verify_email'), auth=creds, data={
    'email': username,
    'tok': user_data.get('verify_token')
}, verify=False)

res = req.post(url_path('api/gen_token'), auth=creds, data={
    'user_id': user_data.get('user').get('id')
}, verify=False)

token = json.loads(res.content).get('data')

print("""
Your token for user {username} is:
{token}
""".format(username=username, token=token))
