import aiohttp
import json
from bs4 import BeautifulSoup
from io import BufferedReader
from yarl import URL
from random import randint
from pathlib import Path
import urllib
import time
import re

class ProgressFileReader(BufferedReader):
    def __init__(self, filename, read_callback):
        f = open(filename, "rb")
        self.start = time.time()
        self.__read_callback = read_callback
        super().__init__(raw=f)
        self.length = Path(filename).stat().st_size

    def read(self, size=None):
        start= time.time()
        calc_sz = size
        if not calc_sz:
            calc_sz = self.length - self.tell()
        self.__read_callback(self.tell(), self.length,self.start)
        return super(ProgressFileReader, self).read(size)
       
class aiohttp_client:
	def __init__(self,ServerUrl,UserName,PassWord,RepoId,Session):
		self.ServerUrl: str = ServerUrl
		self.Username: str = UserName
		self.Password: str = PassWord
		self.RepoId: str = RepoId
		self.Session = Session
		
	async def login(self):
		try:
			 async with self.Session.get(self.ServerUrl+"/login/index.php",timeout=aiohttp.ClientTimeout(total=20),ssl=False) as response:
			 	html = await response.text()
			 	
			 try:
			 	soup = BeautifulSoup(html,"html.parser")
			 	token = soup.find("input", attrs={"name": "logintoken"})["value"]
			 		
			 	payload = {"anchor":"",
			 	"logintoken":token,
			 	"username":self.Username,
			 	"password":self.Password,
			 	"rememberusername":1}
			 		
			 except:
			 	payload = {"anchor":"",
			 	"username":self.Username,
			 	"password":self.Password,
			 	"rememberusername":1}
			 	
			 async with self.Session.post(self.ServerUrl+"/login/index.php",data=payload,timeout=aiohttp.ClientTimeout(total=20),ssl=False) as response:
			 	await response.text()
			 	
			 if str(response.url).lower() == (self.ServerUrl+"/login/index.php").lower():
			 	return False
			 else:
			 	return True
			 		
		except:
			return None
		
	async def upload_file_draft(self,path,read_callback):
		try:
			 async with self.Session.get(self.ServerUrl+"/user/edit.php",timeout=aiohttp.ClientTimeout(total=20),ssl=False) as response:
			 	resp_1 = await response.text()
			 	
			 soup = BeautifulSoup(resp_1,"html.parser")
			 sesskey = soup.find("input", attrs={"name": "sesskey"})["value"]
			 
			 query = URL(soup.find("object", attrs={"type": "text/html"})["data"]).query
			 
			 client_id_pattern = '"client_id":"\w{13}"'
			 client_id = re.findall(client_id_pattern, resp_1)
			 client_id = re.findall("\w{13}", client_id[0])[0]
			 itemid = query["itemid"]
			 
			 file = ProgressFileReader(path,read_callback)
			 data = aiohttp.FormData()
			 data.add_field("title", "")
			 data.add_field("author", self.Username)
			 data.add_field("license", "allrightsreserved")
			 data.add_field("itemid", itemid)
			 data.add_field("repo_id", str(self.RepoId))
			 data.add_field("p", "")
			 data.add_field("page", "")
			 data.add_field("env", "filemanager")
			 data.add_field("sesskey", sesskey)
			 data.add_field("client_id", client_id)
			 data.add_field("maxbytes", query["maxbytes"])
			 data.add_field("areamaxbytes", str(1024 * 1024 * 1024 * 4))
			 data.add_field("ctx_id", query["ctx_id"])
			 data.add_field("savepath", "/")
			 data.add_field("repo_upload_file", file)
			 
			 async with self.Session.post(self.ServerUrl+"/repository/repository_ajax.php?action=upload",data=data,timeout=aiohttp.ClientTimeout(connect=30,total=60*60),ssl=False) as response:
			 	html = await response.text()
			 	
			 	resp = json.loads(html)["url"]
			 	return resp
		except:
			return None
		
	async def upload_file_token(self,path,token,read_callback):
		try:
			UploadUrl = self.ServerUrl+"/webservice/upload.php"
			file = ProgressFileReader(path,read_callback)
			data = aiohttp.FormData()
			data.add_field("token",token)
			data.add_field("itemid","0")
			data.add_field("filearea","draft")
			data.add_field("file",file)
			async with self.Session.post(UploadUrl,data=data,ssl=False) as response:
				html = await response.text()
				resp = json.loads(html)[0]
				contextid,itemid,filename = resp["contextid"],resp["itemid"],resp["filename"]
				url = f"{self.ServerUrl}/draftfile.php/{contextid}/user/draft/{itemid}/{urllib.parse.quote(filename)}"
			
			url_convert = f"{self.ServerUrl}/webservice/rest/server.php?moodlewsrestformat=json"
			url_plus = urllib.parse.quote_plus(url)
			
			payload_convert =  {"formdata":f"name=Evento&eventtype=user&timestart[day]=5&timestart[month]=2&timestart[year]&timestart[year]=5000&timestart[hour]=23&timestart[minute]=55&description[text]={url_plus}&description[format]=1&description[itemid]={randint(100000000,999999999)}&location=&duration=0&repeat=0&id=0&userid={resp['userid']}&visible=1&instance=1&_qf__core_calendar_local_event_forms_create=1",
			           "moodlewssettingfilter":"true",
			           "moodlewssettingfileurl":"true",
			           "wsfunction":"core_calendar_submit_create_update_form",
			           "wstoken":token}
			           
			async with self.Session.post(url_convert,data=payload_convert,ssl=False) as resp:
			 	try:
			 		r = json.loads(await resp.text())
			 		return re.findall("https?://[^\s\<\>]+[a-zA-z0-9]",r["event"]["description"])[-1]
			 	except:
			 		return url
		except Exception as exc:
			print(exc)
			return None