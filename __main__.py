import asyncio
import sys
from bandcamp import Bandcamp

async def main():
  author = None
  try:
    author = sys.argv[1].strip()
    print(f"Start to searching for {author}'s songs.")
  except:
    print("The author has not been set.")
    return
  
  if not author or author == "":
    print("The author has not been set.")
    return

  bandcamp = Bandcamp()
  await bandcamp.addAllAlbums(author)
  await bandcamp.downloadAlbums()

if __name__ == '__main__':
  asyncio.run(main())