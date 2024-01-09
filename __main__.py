import asyncio
from bandcamp import Bandcamp

async def main():
  bandcamp = Bandcamp()
  await bandcamp.getAlbumInfo("slowedandreverb", "the-abstractrooms")

if __name__ == '__main__':
  asyncio.run(main())