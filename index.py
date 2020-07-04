import tweepy
import rsa
import json
from datetime import datetime

#Twitter APIs
consumer_key = "qwerty"
consumer_secret = "sdfghj"
access_token = "jkld"
access_token_secret = "fdjhfd"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True,
	wait_on_rate_limit_notify=True)

#location of the keys
PUB_KEY_DST = 'keys/pub.pem'
PRIV_KEY_DST = 'keys/priv.pem'

def generate_rsa_keys():
	(pubkey, privkey) = rsa.newkeys(2048)
	with open(PUB_KEY_DST, 'wb+') as f:
		pk = rsa.PublicKey.save_pkcs1(pubkey, format='PEM')
		f.write(pk)
	with open(PRIV_KEY_DST, 'wb+') as f:
		pk = rsa.PrivateKey.save_pkcs1(privkey, format='PEM')
		f.write(pk)

def get_rsa_keys():
	with open(PUB_KEY_DST, mode='rb') as publicfile:
		keydata_pub = publicfile.read()
	with open(PRIV_KEY_DST, mode='rb') as privatefile:
		keydata_priv = privatefile.read()
	privkey = rsa.PrivateKey.load_pkcs1(keydata_priv)
	pubkey = rsa.PublicKey.load_pkcs1(keydata_pub)
	return { 'private':privkey, 'public':pubkey }

try:
	keys = get_rsa_keys()
except:
	generate_rsa_keys()
	print("keys generated!")

keys = get_rsa_keys()
pubkey = keys['public']
privkey = keys['private']

contacts_pubkey = {}

def get_dms():
	dms = api.list_direct_messages()
	if len(dms) > 0:
		recipient_id = dms[0].message_create['target']['recipient_id']
	for dm in dms:
		sender = ""
		timestamp = int(dm.created_timestamp[:10])
		timestamp = datetime.fromtimestamp(timestamp)
		text = dm.message_create['message_data']['text']
		sender_id = dm.message_create['sender_id']
		try:
			data = json.loads(text)
			if recipient_id not in contacts_pubkey:
				contacts_pubkey[recipient_id] = rsa.PublicKey(data['pubkey']['n'],data['pubkey']['e'])
			#if you send the message
			if recipient_id == sender_id:
				sender = "me"
				text = data['mycopy']
			else:
				sender = sender_id
				text = data['crypto']
			text = decrypt(text)
		except:
			pass

		print(f"{timestamp} >> {sender}: {text}")

def decrypt(txt):
	txt = bytes.fromhex(txt)
	msg = rsa.decrypt(txt, privkey)
	return msg.decode('utf-8')

def send_dm(recipient_id, text):
	text = text.encode('utf-8')
	#assuming that you already have saved the recipients public key
	encrypted = rsa.encrypt(text, contacts_pubkey[str(recipient_id)])
	encrypted_sender_copy = rsa.encrypt(text, pubkey)
	data = {
		"crypto": encrypted.hex(),
		"mycopy": encrypted_sender_copy.hex(),
		"pubkey": {"n": pubkey.n, "e":pubkey.e}, #senders pubkey
	}
	data = json.dumps(data) #conevrts to json string
	api.send_direct_message(recipient_id, data)
	print("message sent to", recipient_id)



