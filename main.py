import requests
import json
import twitch
import random
import time 

with open('config.json') as fin:
  config = json.load(fin)

helix = twitch.Helix(config.get('twitch_client_id'), config.get('twitch_client_secret'))
lichess_token = config.get('lichess_token')

header = {'Authorization': f'Bearer {lichess_token}'}
url = 'https://lichess.org/api/stream/event'

s = requests.Session()

getting_challenges = False
counter = 0
challengers = list()

def draw(tournament_id, num_drawings):
  players = list()
  scores = list()
  page = 1
  url = f'https://lichess.org/api/tournament/{tournament_id}'
  while True:
    response = requests.get(url, params={'page': page})
    competitors = response.json().get('standing').get('players')
    if len(competitors) == 0:
      break

    for player in competitors:
      players.append(player.get('name'))
      scores.append(player.get('score'))
    page += 1

  return random.choices(players, scores, k=num_drawings)

def handle_message(message: twitch.chat.Message) -> None:
  global getting_challenges, counter

  if message.text.startswith('!queue'):
    if getting_challenges:
      return
    else:
      getting_challenges = True

    message.chat.send('Querying queue size from Lichess... This may take up to 5 seconds.')

    counter = 0
    challengers = list()

    with s.get(url, headers=header, stream=True) as resp:
      for line in resp.iter_lines():
        if line:
          line = json.loads(line)
          if line.get('type') == 'challenge':
            counter += 1
            challengers.append(line.get('challenge').get('challenger').get('name'))
        else:
          response = f'@{message.user.display_name}, the queue has {counter} challenge{"" if counter == 1 else "s"}.'
          message.chat.send(response)
          getting_challenges = False
          return
  elif message.text.startswith('!subdrawing'):
    if message.user.display_name.lower() != 'koreanamericanchessnoob':
      return
    else:
      if len(message.text.split()) < 3:
        return
      tournament_id, num_drawings = message.text.split()[1:3]
      num_drawings = int(num_drawings)
      winners = draw(tournament_id, num_drawings)
      message.chat.send(f'Drawing winners are: {", ".join(winners)}')
  #elif message.text.

def is_playing():
  url = f'https://lichess.org/api/users/status?ids=krnamericanchessnoob'
  response = requests.get(url)
  response_json = response.json()
  print(response_json)
  if 'playing' in response_json[0]: 
    return True 
  else: 
    return False 

# def delete_move_suggestions():

def main():
  chat = twitch.Chat(channel=f'#{config.get("twitch_channel")}',
                     nickname='KoreanAmericanChessBot',
                     oauth=config.get('twitch_oauth'),
                     helix=helix)

  chat.subscribe(handle_message)

if __name__ == '__main__':
  main()
