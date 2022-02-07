from urllib.request import urlopen
from multiprocessing import Pool
from bs4 import BeautifulSoup
from functools import reduce
from hashlib import md5
from numpy import full
import pygame
import math
import json
import re
import os

'''
This might not be compatible depending on processor so try to use less it's throwing weird error
'''
TOTAL_WORKER = 8
TILESIZE = 16

def download_sheet(url):
  soup = BeautifulSoup(urlopen(url).read(), 'html.parser')
  name = re.sub(
    r'[^A-Za-z_0-9]', '', 
    soup.select_one('#game-info-wrapper div').text.replace(' ', '_').replace('/', '_of_').lower()
  )
  download_url = soup.select_one('#game-info-wrapper tr.rowfooter a')['href']
  folder = './data/raw/sheets'
  path = f'{folder}/{name}.png'
  if os.path.exists(path): 
    print(f'[WARNING]: File "{path}" already exists! Skipping...')
    return
  content = urlopen(f'https://www.spriters-resource.com{download_url}').read()
  with open(path, 'wb') as file:
    file.write(content)
  print(f'[INFO]: Downloaded "{path}" successfully!')

def download_sheets():
  pool = Pool(TOTAL_WORKER)
  soup = BeautifulSoup(
    urlopen('https://www.spriters-resource.com/snes/harvestmoon/').read(), 
    'html.parser'
  )
  sheet_urls = [
    f"https://www.spriters-resource.com{link['href']}"
    for link in soup.find_all('a')
    if 'href' in link.attrs and re.match(r'^\/snes\/harvestmoon\/sheet/.*$', link['href'])
  ]

  print(f'[INFO]: Downloading {len(sheet_urls)} spritesheets...')
  folder = './data/raw/sheets'
  if not os.path.exists(folder): os.makedirs(folder)
  pool.map(download_sheet, sheet_urls)

def get_surfaces(path):
  image = pygame.image.load(path)
  w, h = image.get_size()
  outdir, results, MAP = './data/raw/tiles', [], {}
  name, i = path.split('/')[-1].split('.')[0], 1
  for y in range(0, h, TILESIZE):
    rows = []
    for x in range(0, w, TILESIZE):
      surface = pygame.Surface((TILESIZE, TILESIZE))
      surface.blit(image, dest=(0, 0), area=(x, y, TILESIZE, TILESIZE))
      outpath = f'{outdir}/{name}_{str(i).zfill(4)}.png'
      _hash = md5(surface.get_buffer()).hexdigest()
      if not os.path.exists(outpath): pygame.image.save(surface, outpath)
      rows.append((outpath, _hash))
      i += 1
    results.append(rows)
  MAP['name'], MAP['map'] = name, results
  MAP['rows'], MAP['cols'] = h // TILESIZE, w // TILESIZE
  print(f'[INFO]: Done processing "{path}"!')
  return MAP

def create_tilesheets():
  pool = Pool(TOTAL_WORKER)
  SHEETS = [
    'animal_shop', 'carpenters_home', 'chicken_coop', 'church', 'cow_barn', 'ending_corn', 
    'ending_ellen', 'ending_nina', 'ending_potato', 'ending_tomato', 'ending_turnip', 'farm_fall', 
    'farms_cave', 'farm_spring', 'farm_summer', 'farm_winter', 'fortunetellers_home', 
    'golden_chickens_palace', 'jacks_house_big', 'jacks_house_medium', 'jacks_house_small', 
    'mayors_home', 'mountain_cave', 'mountain_fall', 'mountain_spring', 'mountain_star_night_festival', 
    'mountain_summer', 'mountain_top_beanstalk', 'mountain_top_fall', 'mountain_top_spring', 
    'mountain_top_star_night_festival', 'mountain_top_summer', 'mountain_top_winter', 
    'mountain_winter', 'ninas_room', 'opening_cutscene_1_of_2', 'opening_cutscene_2_of_2', 
    'restaurant', 'saloon', 'seed_shop', 'street_fall', 'street_spring', 'street_summer', 
    'street_winter', 'summer_clouds', 'tool_shed', 'tool_shop', 'village_egg_festival', 'village_fall',
    'village_flower_festival', 'village_harvest_festival', 'village_spring', 
    'village_star_night_festival', 'village_summer', 'village_winter'
  ]
  tilesheets = [
    f'./data/raw/sheets/{name}.png'
    for name in SHEETS
  ]

  print(f'[INFO]: Getting all the tiles and splitting them')
  outdir = './data/raw/tiles'
  if not os.path.exists(outdir): os.makedirs(outdir)
  maps = pool.map_async(get_surfaces, tilesheets).get()
  
  print('[INFO]: Re-calculating indices for all the tiles. This', end=' ')
  print('should takes a while so go grab a coffee...')
  hashes = []
  surfaces = {}
  for _map in maps:
    for row, rows in enumerate(_map['map']):
      for col, (path, _hash) in enumerate(rows):
        _map['map'][row][col] = len(hashes) if _hash not in hashes else hashes.index(_hash)
        if _hash in hashes: continue
        hashes.append(_hash)
        surfaces[_hash] = pygame.image.load(path)

  # Finding optimal dimension for the full tile sheet
  print(f'[INFO]: Finding optimal dimension for the full tile sheet...')
  total = len(hashes)
  for rows in range(math.floor(math.sqrt(total)), 2, -1):
    if total % rows != 0: continue
    cols = total // rows
    break

  # Creating the massive tile sheet
  print(f'[INFO]: Creating a massive tile sheet with dimension ({rows}, {cols})...')
  fullsheet = pygame.Surface((cols*TILESIZE, rows*TILESIZE))
  i = 0
  for row in range(rows):
    for col in range(cols):
      _hash = hashes[i]
      surface = surfaces[_hash]
      dest = col * TILESIZE, row * TILESIZE
      fullsheet.blit(surface, dest=dest)
      i += 1
  folder = './data/tiles'
  if not os.path.exists(folder): os.makedirs(folder)
  pygame.image.save(fullsheet, f'{folder}/sheet.png')

  print('[INFO]: Creating map (.map) and config (.json) files for each map...')
  for _map in maps:
    map_path = f"./data/tiles/{_map['name']}.map"
    with open(map_path, 'wb') as f:
      for _rows in _map['map']:
        for idx in _rows:
          f.write(idx.to_bytes(2, 'big'))
  
    config = {
      'name': _map['name'],
      'rows': _map['rows'],
      'cols': _map['cols'],
      'map': map_path
    }
    with open(f"./data/tiles/{_map['name']}.json", "w") as f:
      json.dump(config, f, indent=2)
  
  print('[INFO]: Finished! Total tiles:', len(hashes))

def separator():
  print('=' * 60)

if __name__ == '__main__':
  separator()
  print('[INFO]: Downloading relevant spritesheets...')
  download_sheets()

  separator()
  print('[INFO]: Creating tilesheets from all of the maps...')
  create_tilesheets()

  separator()
  print('[INFO]: Cleaning raw tiles folder (./data/raw/tiles/) as they are no longer needed...')
  os.rmdir('./data/raw/tiles')
