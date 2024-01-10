import asyncio
from bandcamp import Bandcamp

async def main():
  bandcamp = Bandcamp()
  await bandcamp.addAlbum("slowedandreverb", "the-abstractrooms")
  await bandcamp.downloadAlbums()

if __name__ == '__main__':
  asyncio.run(main())