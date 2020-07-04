# secure-twitter-messaging-using-rsa
makes Twitter dms secure using RSA algorithm atop of Twitter API

# dependencies
- tweepy `` pip install tweepy ``
- rsa  `` pip install rsa `` 

# usage
  user must have a Twitter developer account
   - https://developer.twitter.com/

  using python interactive console `python -i index.py`
   - generate RSA keys using ``generate_rsa_keys()``
   - to retrieve your dms `get_dms()`
   - send message `send_dm(<recipient_id/username>, 'your message here')`
