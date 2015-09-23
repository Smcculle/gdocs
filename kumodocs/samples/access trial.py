import gdata.gauth
import gdata.docs.client

app_refresh_token='1/Tm3-V97XwLSdh25pOoxRclMRl8_fpUrm90HE3De45ck'
app_access_token='ya29.9AGzfkwzEAkOwOzR4KtxiCd2_z4eyiZRcLdRf8dmw-Is_cdzzKqkxWA6g52E_xTzifkb'
Client_id='333741682176-nk8kmlqgr80qkbq422vph3e7d24jm3qm.apps.googleusercontent.com';
Client_secret='jzEc1cOr7WXhWm0KGvNhhAwq'
Scope='https://docs.google.com/feeds/'
User_agent='myudap'
myid = '1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps'
token = gdata.gauth.OAuth2Token(client_id=Client_id,
                                client_secret=Client_secret,
                                scope=Scope,
                                user_agent=User_agent)

client = gdata.docs.client.DocsClient(source=User_agent, auth_token=app_access_token)
#client.auth_token = app_access_token
#feed = client.GetResources()
#for entry in feed.entry:
    #print entry.title.text

#entry2 = client.GetResourceById(myid)
#print token.generate_authorize_url(redirect_uri='urn:ietf:wg:oauth:2.0:oob')
#code = raw_input('What is the verification code? ').strip()
#token.get_access_token(code)
#print "Refresh token\n"
#print token.refresh_token
#print "Access Token\n"
#print token.access_token

