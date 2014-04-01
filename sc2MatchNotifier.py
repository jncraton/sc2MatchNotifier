import sys

if len(sys.argv) == 1:
    print(
"""# sc2MatchNotifier

Sends a notification email if the user's 
match history has been updated since the 
last run.

Account credentials should be configured
within the script.

Usage: sc2MatchNotifier {bnet profile url}
""")
    exit(0)

gmail_sender = ''
gmail_password = ''
email_to = ''

def get_games(url):
    import urllib
    import urllib2
    import re

    response = urllib2.urlopen(url + 'matches')
    html = response.read()

    games_html = re.findall('<tr class="match-row custom">(.*?)</tr', html, flags=re.MULTILINE|re.DOTALL)

    games = []

    for game_html in games_html:
        game_match = re.search('.*?<td>(.*?)</td>.*?<td class="align-center">(.*?)</td>.*?<span class="match-win">(.*?)</span>.*?<td class="align-right">[\r\n\t]*(.*?)[\r\n\t]*</td>', game_html, flags=re.MULTILINE|re.DOTALL)
        
        game = {}
        
        if game_match:
            game['map'] = game_match.group(1)
            game['type'] = game_match.group(2)
            game['outcome'] = game_match.group(3)
            game['date'] = game_match.group(4)
            games.append(game)
            
    return games

def send_mail(subject, message):
    import smtplib
    
    msg = "\r\n".join([
      "From: " + gmail_sender,
      "To: " + email_to,
      "Subject: " + subject,
      "",
      message
      ])

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(gmail_sender,gmail_password)
    server.sendmail(gmail_sender, email_to, msg)
    server.quit()

def hash(obj):
    import hashlib
    import pickle
    
    sha = hashlib.sha256()
    sha.update(pickle.dumps(obj))
    
    return sha.hexdigest()

def check_account(url):
    slug = url.replace('http://', '').replace('/', '-')
    
    filename = "hash_" + slug + ".sha256"
    
    import re
    
    user = re.search('/\d/(.*?)/$', url).group(1)
    
    games = get_games(url)

    new_hash = hash(games)
    old_hash = ''

    try:
        with open (filename) as hash_file:
            old_hash = hash_file.read()
    except:
        old_hash = ''
        
    if new_hash != old_hash:
        message = 'Map: %s\r\nType: %s\r\nOutcome: %s\r\nDate: %s\r\n' %(games[0]['map'], games[0]['type'], games[0]['outcome'], games[0]['date'])
    
        send_mail(user + ' played SC2', message)

        with open (filename, "w") as hash_file:
            hash_file.write(new_hash)

check_account(sys.argv[1])