import asyncio
from bandcamp import Bandcamp

async def main():
  bandcamp = Bandcamp()
  await bandcamp.addAllAlbums("slowedandreverb")
  await bandcamp.downloadAlbums()

if __name__ == '__main__':
  asyncio.run(main())