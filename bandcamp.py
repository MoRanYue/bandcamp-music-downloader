from typing import Union, Optional, Dict, List, Any
from bs4 import BeautifulSoup
from pathlib import Path
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

  async def getAlbums(self, author: str) -> dict:
    pass

  async def getAlbumInfo(self, author: str, album: str) -> dict:
    res = None
    async with self.session as cl:
      res = await cl.get(Bandcamp.generateAlbumUrl(author, album))
    if res.status_code != 200:
      raise RuntimeError(f"Request {Bandcamp.generateAlbumLog(author, album)} failed, HTTP status code: ${res.status_code}")
    
    self.soup = BeautifulSoup(res.text, "html.parser")

    rawAlbumInfo = None
    scriptImports = self.soup.findAll("script")
    for script in scriptImports:
      if script and "data-tralbum" in script.attrs.keys():
        rawAlbumInfo = json.loads(script.attrs["data-tralbum"])
        break

    albumInfo = {
      "id": rawAlbumInfo["id"],
      "internal": album,
      "cover": self.soup.find("link", { "rel": "image_src" }).attrs["href"],
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
  
  async def addAlbum(self, author: str, album: str) -> dict:
    albumInfo = await self.getAlbumInfo(author, album)
    self.albums.append(albumInfo)
    return albumInfo

  async def download(self, url: str) -> None:
    res = None
    async with self.session as cl:
      res = await cl.get(url)
    if res.status_code != 200:
      raise RuntimeError(f"Request {Bandcamp.generateAlbumLog(author, album)} failed, HTTP status code: ${res.status_code}")
    
    return res.content
    
  async def downloadAlbums(self) -> None:
    for album in self.albums:
      print(f"Downloading {self.generateAlbumLog(album['author'], album['title'])}")
      folder = Path(album["internal"])
      folder.mkdir(parents=True, exist_ok=True)
      
      for song in album["songs"]:
        with (folder / Path(song["title"] + ".mp3")).open("wb") as f:
          f.write(await self.download(song["file"]))

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