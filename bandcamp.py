from typing import Union, Optional, Dict, List, Any
from bs4 import BeautifulSoup
from pathlib import Path
import httpx

try:
  import ujson as json
except ModuleNotFoundError:
  import json

def printDividingLine():
  print("=" * 15)

AlbumInfo = Dict[str, Any]
AlbumList = List[AlbumInfo]
class Bandcamp:
  soup: Optional[BeautifulSoup]
  authorSoup: Optional[BeautifulSoup]
  headers: Dict[str, str]
  timeout: int
  albums: AlbumList

  def __init__(self) -> None:
    self.soup = None
    self.authorSoup = None
    self.headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }
    self.timeout = 5000
    self.albums = []

  async def getAlbums(self, author: str) -> List[dict]:
    res = None
    async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as cl:
      res = await cl.get(Bandcamp.generateAuthorUrl(author))
    if res.status_code != 200:
      raise RuntimeError(f"Request {Bandcamp.generateAuthorLog(author)} failed, HTTP status code: ${res.status_code}")
    
    self.authorSoup = BeautifulSoup(res.text, "html.parser")

    rawAlbumList = self.authorSoup.find("ol", { "id": "music-grid" }).findChildren("li")
    authorName = self.authorSoup.find("p", { "id": "band-name-location" }).findChild("span", { "class": "title" }).getText(strip=True)
    print(f"The playlists of {Bandcamp.generateAuthorLog(authorName)} has been got")
    albums = []
    for i, rawAlbum in enumerate(rawAlbumList):
      link: str = rawAlbum.find("a").attrs["href"]
      print(f"Playlist {i}: ")
      albums.append(await self.getAlbumInfo(author, link[link.rindex("/") + 1:]))

    return albums

  async def getAlbumInfo(self, author: str, album: str) -> dict:
    res = None
    async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as cl:
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

    printDividingLine()

    return albumInfo
  
  async def addAlbum(self, author: str, album: str) -> dict:
    albumInfo = await self.getAlbumInfo(author, album)
    self.albums.append(albumInfo)
    return albumInfo
  
  async def addAllAlbums(self, author: str) -> List[dict]:
    albums = await self.getAlbums(author)
    self.albums = albums
    return albums

  async def download(self, url: str) -> None:
    res = None
    async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as cl:
      res = await cl.get(url)
    if res.status_code != 200:
      raise RuntimeError(f"Request \"{url}\" failed, HTTP status code: ${res.status_code}")
    
    return res.content
    
  async def downloadAlbums(self) -> None:
    for album in self.albums:
      print(f"Start to download {self.generateAlbumLog(album['author'], album['title'])}")
      folder = Path(album["title"])
      folder.mkdir(parents=True, exist_ok=True)

      print(f"Downloading the cover")
      with (folder / "cover.jpg").open("wb") as f:
        f.write(await self.download(album["cover"]))
      
      for song in album["songs"]:
        print(f"Downloading {self.generateMusicLog(album['author'], album['title'], song['title'])}")
        with (folder / Path(song["title"] + ".mp3")).open("wb") as f:
          f.write(await self.download(song["file"]))

  @staticmethod
  def generateAuthorUrl(author: str) -> str:
    return f"https://{author}.bandcamp.com"

  @staticmethod
  def generateAlbumUrl(author: str, album: str) -> str:
    return f"{Bandcamp.generateAuthorUrl(author)}/album/{album}"
  
  @staticmethod
  def generateMusicUrl(author: str, music: str) -> str:
    return f"{Bandcamp.generateAuthorUrl(author)}/track/{music}"
  
  @staticmethod
  def generateAuthorLog(author: str) -> str:
    return f"[ Author: {author} ]"
  
  @staticmethod
  def generateAlbumLog(author: str, album: str) -> str:
    return f"[ Author: {author} Playlist: {album} ]"
  
  @staticmethod
  def generateMusicLog(author: str, album: str, music: str) -> str:
    return f"[ Author: {author} Playlist: {album} Music: {music} ]"