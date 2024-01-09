from typing import Union, Optional, Dict, List, Any
from bs4 import BeautifulSoup
import httpx

try:
  import ujson as json
except ModuleNotFoundError:
  import json

AlbumInfo = Dict[str, Any]
AlbumList = List[AlbumInfo]
class Bandcamp:
  soup: Optional[BeautifulSoup]
  headers: Dict[str, str]
  session: httpx.AsyncClient

  albums: AlbumList

  def __init__(self) -> None:
    self.soup = None
    self.headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }
    self.session = httpx.AsyncClient(headers=self.headers, timeout=5000)

    self.albums = []

  async def getAlbums() -> dict:
    pass

  async def getAlbumInfo(self, author: str, album: str) -> dict:
    async with self.session:
      res = await self.session.get(Bandcamp.generateAlbumUrl(author, album))
    if res.status_code != 200:
      raise RuntimeError(f"{Bandcamp.generateAlbumLog(author, album)}请求失败，返回码：${res.status_code}")
    
    self.soup = BeautifulSoup(res.text, "html.parser")

    rawAlbumInfo = None
    scriptImports = self.soup.findAll("script")
    for script in scriptImports:
      if script and "data-tralbum" in script.attrs.keys():
        rawAlbumInfo = json.loads(script.attrs["data-tralbum"])
        break

    albumInfo = {
      "id": rawAlbumInfo["id"],
      "title": rawAlbumInfo["current"]["title"],
      "author": rawAlbumInfo["artist"],
      "songs": []
    }
    print(f"The information of {Bandcamp.generateAlbumLog(albumInfo['author'], albumInfo['title'])} has been got")
    print(f"The playlist has {len(rawAlbumInfo['trackinfo'])} song(s), here them are:")
    for i, song in enumerate(rawAlbumInfo["trackinfo"]):
      if len(song["file"].keys()) > 0:
        albumInfo["songs"].append({
          "id": song["id"],
          "title": song["title"],
          "file": song["file"][list(song["file"].keys())[0]],
        })
        print(f"{i + 1}: {Bandcamp.generateMusicLog(albumInfo['author'], albumInfo['title'], song['title'])}")

    return albumInfo

  async def downloadMusic(self, url: str) -> None:
    pass

  @staticmethod
  def generateAuthorUrl(author: str) -> str:
    return f"https://{author}.bandcamp.com"

  @staticmethod
  def generateAlbumUrl(author: str, album: str) -> str:
    return f"{Bandcamp.generateAuthorUrl(author)}/album/{album}"
  
  @staticmethod
  def generateMusicUrl(author: str, path: str) -> str:
    return f"{Bandcamp.generateAuthorUrl(author)}{path}"
  
  @staticmethod
  def generateAlbumLog(author: str, album: str) -> str:
    return f"[ Author: {author} Playlist: {album} ]"
  
  @staticmethod
  def generateMusicLog(author: str, album: str, music: str) -> str:
    return f"[ Author: {author} Playlist: {album} Music: {music} ]"