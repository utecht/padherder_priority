import requests
import getpass

# stupid hacky python2 trick to reduce requirements
try:
    input = raw_input
except NameError:
    pass

username = input("Padherder Username: ")
password = getpass.getpass("Padherder Password: ")

headers = { 'accept': "application/json", 'user-agent': 'mass-prority' }

print("Priority is an integer between 0 (zero) and 3 (high)")
target_prio = int(input("Change all to priority: "))
exclude_prio = input("Ignore priorities greater than or equal to (leave blank for all): ")

if exclude_prio is not '':
    exclude_prio = int(exclude_prio)

if target_prio not in (0, 1, 2, 3) or (exclude_prio and exclude_prio not in (0, 1, 2, 3)):
    print("Priority must be a number between 0 and 3")
    exit()

translate = { 0: 'zero',
              1: 'low',
              2: 'medium',
              3: 'high' }

conf_dialog = "This will change the priority of all monsters for the account {} to {}. [y/n] ".format(username, translate[target_prio])

if exclude_prio is not '':
    conf_dialog = "This will change the priority of all monsters for the account {} below {} priority to {}. [y/n] ".format(username, translate[exclude_prio], translate[target_prio])

confirm = input(conf_dialog)

if confirm != 'y' or confirm != 'Y':
    exit()


session = requests.Session()
session.auth = (username, password)
session.headers = headers
# Limit the session to a single concurrent connection
session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1))
session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1))

r = session.get("http://padherder.com/user-api/user/{}".format(username))
for monster in r.json()['monsters']:
    monster_url = monster['url']
    monster_id = monster['monster']
    prio = monster['priority']
    if exclude_prio and prio < exclude_prio:
        payload = { "monster": monster_id, "priority": target_prio }
        session.patch(monster_url, json=payload)
