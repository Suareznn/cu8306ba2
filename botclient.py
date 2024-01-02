from pyrogram import Client
from pyrogram.types import Message

import aiohttp
import tgcrypto
import aiofiles
from aiohttp_socks import ProxyConnector
from inspect import iscoroutinefunction
from datetime import datetime
import traceback
from aio import aiohttp_client
from yarl import URL
from random import randint
from pathlib import Path
import zipfile
#from py7 import zip

import json
import os
import time
import urllib

API_ID = 16437082
API_HASH = "b93cf12736d8661004a2043f4b90a421"
BOT_TOKEN = "5416890233:AAHTaFXYaqlEnDM_eNLEKSMAWiL_0ver6xw"

bot = Client("anon",api_id=API_ID,api_hash=API_HASH,bot_token=BOT_TOKEN)

CONFIGS = {}
GRUPO_DB_ID = -871453848
ADMIN_USER = "Abdielsn"

def create_user(username):
	CONFIGS[username] = {"name":username,"user":"--","passw":"--","host":"--","repoid":"--","zips":"--","proxy":"--","custom_token":"--","uploaded":0,"downloaded":0}

def save_user(username,config):
	CONFIGS[username] = config

def get_user(username):
	try:
		return CONFIGS[username]
	except:
		return None

def wrapper(secs):
    def dec(f):
        t = [datetime.utcnow().timestamp()]

        async def wrapper(*args, **kwargs):
            now = datetime.utcnow().timestamp()
            if now - t[0] < secs:
                return
            t[0] = now
            return await f(*args, **kwargs)
        
        def a_wrapper(*args, **kwargs):
            now = datetime.utcnow().timestamp()
            if now - t[0] < secs:
                return
            t[0] = now
            return f(*args, **kwargs)
        
        if iscoroutinefunction(f):
            return wrapper
        else:
            return a_wrapper

    return dec
			
async def msg_config(username):
	config = get_user(username)
	
	proxy = "❌"
	if config['proxy'] != "--":
		proxy = "✅"
		
	msg = f"🛂 Usuario: {config['user']}\n"
	msg+=f"🔑 Contraseña: {config['passw']}\n"
	msg+=f"📡Host: {config['host']}\n"
	msg+=f"🆔RepoID: {config['repoid']}\n"
	msg+=f"📚Zips: {config['zips']}\n"
	msg+=f"⚡Proxy: {proxy}\n"
	msg+=f"✴ TOKEN: {config['custom_token']}\n\n"
	msg+=f"📁Descargado: {convertbytes(config['downloaded'])}\n"
	msg+=f"📁Subido: {convertbytes(config['uploaded'])}\n"
	return msg
	
@bot.on_message()
async def messages_handler(client: Client,message: Message):
	msg = message.text
	username = message.from_user.username
	entity_id = message.from_user.id
	
	if get_user(username):
	    pass
	else:
	    if username == ADMIN_USER:
	        create_user(username)
	    else:
	       await message.reply("❌ No tiene acceso ❌")
	       return
	
	if os.path.exists(f"{os.getcwd()}/{entity_id}/"):
		pass
	else:
		os.mkdir(f"{os.getcwd()}/{entity_id}/")
	
	
	if message.document or message.sticker or message.photo or message.audio or message.video:
		msg = await bot.send_message(entity_id,"💠 Preparando descarga 💠")
		filename = str(message).split('"file_name": ')[1].split(",")[0].replace('"',"")
		file = await bot.download_media(message,file_name=f"{entity_id}/{filename}",progress=progress_download,progress_args=(None,time.time(),msg,message))
		await upload(file,msg,message.from_user.username)
			
	if msg.lower().startswith("/start"):
		user = get_user(username)
		downloaded = user["downloaded"]
		uploaded = user["uploaded"]
		host = user["host"]
		total = downloaded+uploaded
		await message.reply(f"👤 Usuario: {username}\n📡 Host: {host}\n📦 Trafico Total: {convertbytes(total)}")
	
	if msg.lower().startswith("/acc"):
		splitmsg = msg.split(" ")
		
		if len(splitmsg)!=3:
			await message.reply("Fallo ❌")
		else:
			usern = splitmsg[1]
			password = splitmsg[2]
			
			user = get_user(username)
			if user:
				user["user"] = usern
				user["passw"] = password
				save_user(username,user)
				msg = await msg_config(username)
				await message.reply(msg)
		                
	if msg.lower().startswith("/host"):
		splitmsg = msg.split(" ")
		
		if len(splitmsg)!=2:
			await message.reply("Fallo ❌")
		else:
			host = splitmsg[1]
			
			user = get_user(username)
			if user:
				user["host"] = host
				save_user(username,user)
				msg = await msg_config(username)
				await message.reply(msg)
			    
	if msg.lower().startswith("/repoid"):
		splitmsg = msg.split(" ")
		
		if len(splitmsg)!=2:
			await message.reply("Fallo ❌")
		else:
			repoid = splitmsg[1]
			
			user = get_user(username)
			if user:
				user["repoid"] = repoid
				save_user(username,user)
				msg = await msg_config(username)
				await message.reply(msg)
	
	if msg.lower().startswith("/proxy"):
		splitmsg = msg.split(" ")
		
		if len(splitmsg)!=2:
			await message.reply("Fallo ❌")
		else:
			proxymsg = splitmsg[1]
			proxys = proxyparsed(proxymsg)
			proxy = f"socks5://{proxys}"
			
			user = get_user(username)
			if user:
				user["proxy"] = proxy
				save_user(username,user)
				msg = await msg_config(username)
				await message.reply(msg)
				
	if msg.lower().startswith("/zips"):
		splitmsg = msg.split(" ")
		
		if len(splitmsg)!=2:
			await message.reply("Fallo ❌")
		else:
			zips = splitmsg[1]
			
			user = get_user(username)
			if user:
				user["zips"] = zips
				save_user(username,user)
				msg = await msg_config(username)
				await message.reply(msg)
		
	if msg.lower().startswith("/set_token"):
		splitmsg = msg.split(" ")
		
		if len(splitmsg)!=2:
			await message.reply("Fallo ❌")
		else:
			zips = splitmsg[1]
			
			user = get_user(username)
			if user:
				user["custom_token"] = zips
				save_user(username,user)
				
				msg = await msg_config(username)
				await message.reply(msg)
		
	if msg.lower().startswith("/ls"):
	   file_path = os.path.join(os.getcwd(),str(entity_id))
	   files = os.listdir(file_path)
	   msg_f = ""
	   c = 0
	   for f in files:
	       size = Path(file_path+"/"+f).stat().st_size
	       msg_f+=f"{c} - {f} - **{convertbytes(size)}**\n📤 Subir este archivo - /upload{c}\n🗑 Borrar este archivo - /delete{c}\n\n"
	       c+=1
	   try:
	       await message.reply(msg_f)
	   except:
	       await message.reply("__No hay archivos descargados aquí__")
	  
	if msg.lower().startswith("/upload"):
		i = int(msg.split("/upload")[1])
		file_path = os.path.join(os.getcwd(),str(entity_id))
		files = os.listdir(file_path)
		msg = await bot.send_message(entity_id,"💠 Preparando subida 💠")
		await upload(file_path+"/"+files[i],msg,message.from_user.username)
	
	if msg.lower().startswith("/delete"):
	   i = int(msg.split("/delete")[1])
	   file_path = os.path.join(os.getcwd(),str(entity_id))
	   files = os.listdir(file_path)
	   os.unlink(file_path+"/"+files[i])
	   await message.reply("__🗑 Archivo borrado__")
	
	if msg.lower().startswith("/cleanall"):
	   file_path = os.path.join(os.getcwd(),str(entity_id))
	   files = os.listdir(file_path)
	   for file in files:
	       os.unlink(file_path+"/"+file)
	   await message.reply("__🗑 Archivos borrados__")
	   
	if msg.lower().startswith("/my"):
		msg = await msg_config(username)
		await message.reply(msg)
	
	if msg.lower().startswith("/add"):
		if username in ADMIN_USER:
			msg_split = msg.split(" ")
			
			user = msg_split[1]
			create_user(user)
			await message.reply("__Has permitido a un usuario en el bot ✅__")
		else:
			return
			
	if msg.lower().startswith("/ban"):
		if username in ADMIN_USER:
			msg_split = msg.split(" ")
			
			user = msg_split[1]
			del CONFIGS[user]
			await message.reply("__Has quitado a un usuario en el bot ❌__")
		else:
			return
			
	if msg.lower().startswith("https"):
		async with aiohttp.ClientSession() as session:
			async with session.get(message.text) as response:
				file_name = response.content_disposition.filename
				size = int(response.headers.get("content-length"))
				type = response.headers.get("content-type").split("/")[1]
				path = os.path.join(os.getcwd(),f"{entity_id}",file_name)
				messag = await bot.send_message(entity_id,"💠Preparando descarga💠")
				
				file = await aiofiles.open(path,"wb")
				chunkcurrent = 0
				startime = time.time()
				async for chunk in response.content.iter_chunked(1024*1024):
					chunkcurrent+=len(chunk)
					await progress_download(chunkcurrent,size,file_name,startime,messag,message)
					await file.write(chunk)
				file.close()
				
				if chunkcurrent == size:
					config = get_user(message.from_user.username)
					config["downloaded"]+=size
					save_user(message.from_user.username,config)
					await upload(path,messag,message.from_user.username)
					

	if msg.lower().startswith("/aula_gtm"):
		user = get_user(username)
		if user:
			user["user"] = ""
			user["passw"] = ""
			user["host"] = "https://aulauvs.gtm.sld.cu"
			user["repoid"] = ""
			user["zips"] = 7
			user["custom_token"] = "d2105e6f580f66d63320bb6ccf1c8fdd"
			save_user(username,user)
			msg = await msg_config(username)
			await message.reply(msg)

	if msg.lower().startswith("/aula_vcl"):
		user = get_user(username)
		if user:
			user["user"] = ""
			user["passw"] = ""
			user["host"] = "https://www.aula.vcl.sld.cu"
			user["repoid"] = ""
			user["zips"] = 50
			user["custom_token"] = "73fc3fc0f8f6bd3a89bb2d0fded00a93"
			save_user(username,user)
			msg = await msg_config(username)
			await message.reply(msg)

	if msg.lower().startswith("/uvs_ucm"):
		user = get_user(username)
		if user:
			user["user"] = ""
			user["passw"] = ""
			user["host"] = "https://uvs.ucm.cmw.sld.cu"
			user["repoid"] = ""
			user["zips"] = 50
			user["custom_token"] = "992f82ee46b1a3493ae5cf5193d8d3c4"
			save_user(username,user)
			msg = await msg_config(username)
			await message.reply(msg)

	if msg.lower().startswith("/uvs_ltu"):
		user = get_user(username)
		if user:
			user["user"] = ""
			user["passw"] = ""
			user["host"] = "https://uvs.ltu.sld.cu"
			user["repoid"] = ""
			user["zips"] = 18
			user["custom_token"] = "ee8c432b11f9715290663fcae224c558"
			save_user(username,user)
			msg = await msg_config(username)
			await message.reply(msg)

	if msg.lower().startswith("/off_token"):
		user = get_user(username)
		if user:
			user["custom_token"] = ""
			save_user(username,user)
			msg = await msg_config(username)
			await message.reply(msg)
		
	
	if msg.lower().startswith("/apagar_proxy"):	
		user = get_user(username)
		if user:
			user["proxy"] = "--"
			save_user(username,user)
			msg = await msg_config(username)
			await message.reply(msg)
					
@wrapper(2)				
async def progress_download(chunkcurrent,total,file_name,start,message,messag):
	speed = chunkcurrent / (time.time() - start)
	percent = int(chunkcurrent * 100 / total)
	msg = f"📌 Nombre: {file_name}\n"
	if file_name is None:
		msg = ""
	msg+=f"📥 Descargando: {convertbytes(chunkcurrent)}\n"
	msg+=f"📦 Total: {convertbytes(total)}\n"
	msg+=f"⚡ Velocidad: {convertbytes(speed)}/s\n"
	msg+=f"📊 Progreso: {percent}%\n"
	try:
		await message.edit(msg)
	except:
		pass
	
	if chunkcurrent == total:
		config = get_user(messag.from_user.username)
		config["downloaded"]+=total
		save_user(messag.from_user.username,config)
			
async def upload(pathfull,message,username):
	user = get_user(username)
	proxy = user["proxy"]
	if proxy == "--":
		connector = aiohttp.TCPConnector()
	else:
		connector = ProxyConnector.from_url(proxy)
	
	zips = user["zips"]
	
	name = pathfull.split("/")[-1]
	
	size = os.path.getsize(pathfull)
	esize = 1024*1024*int(zips)
	
	if size > esize:
		await message.edit("Comprimiendo...")
		files = zipfile.MultiFile(pathfull,esize)
		zips = zipfile.ZipFile(files,mode="w",compression=zipfile.ZIP_DEFLATED)
		zips.write(pathfull)
		zips.close()
		files.close()
		FILES = files.files

		
		async with aiohttp.ClientSession(connector=connector,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}) as session:
			client = aiohttp_client(user['host'],user['user'],user['passw'],user['repoid'],session)
			error  = 0
			links = []
			while error < 10:
				try:
					token = await gettoken(user["user"],user["passw"],session,user["host"])
					if token:
						await message.edit("Se encontro token con las credenciales actuales ✅")
						for f in FILES:
							r = await client.upload_file_token(f,token,read_callback=lambda current,total,start: progress_upload(current,total,start,message,f.split("/")[-1]))
							if r:
								ws = r.replace("pluginfile.php","webservice/pluginfile.php")
								link =  ws+f"?token={token}"
								await bot.send_message(username,f"✅ Upload Done ✅\n📌 {Path(f).name}\n📦{convertbytes(Path(f).stat().st_size)}\n\n📌Links📌\n{link}")
								links.append(link)
						break
					elif not token:
						await message.edit("Usando token personal ✅")
						token = user["custom_token"]
						for f in FILES:
							r = await client.upload_file_token(f,token,read_callback=lambda current,total,start: progress_upload(current,total,start,message,f.split("/")[-1]))
							if r:
								ws = r.replace("pluginfile.php","webservice/pluginfile.php")
								link =  ws+f"?token={token}"
								await bot.send_message(username,f"✅ Upload Done ✅\n📌 {Path(f).name}\n📦{convertbytes(Path(f).stat().st_size)}\n\n📌Links📌\n{link}")
								links.append(link)
							else:
								login = await client.login()
								if login:
									await message.edit("Subiendo mediante login ✅")
									r = await client.upload_file_draft(pathfull,read_callback=lambda current,total,start: progress_upload(current,total,start,message,f.split("/")[-1]))
									if r:
									    await bot.send_message(username,f"✅ Upload Done ✅\n📌 {Path(f).name}\n📦{convertbytes(Path(f).stat().st_size)}\n\n📌Links📌\n{r}")
									    links.append(r)
						break
				except Exception as ex:
					print(ex)
					error+=1
			
			if error == 10:
				await message.edit("❌ Problemas en el servidor o error en las credenciales ❌")
				return
			
			if len(links) == len(FILES):
				config = get_user(username)
				config["uploaded"]+=size
				save_user(username,config)
				
				txtsend = ""
				for url in links:
					txtsend+=url+"\n"
					#dagd = await shorturl(url)
				
				with open(name+".txt","w") as txt:
					txt.write(txtsend)
					
				await bot.send_document(username,name+".txt")
	else:
		async with aiohttp.ClientSession(connector=connector,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}) as session:
			client = aiohttp_client(user['host'],user['user'],user['passw'],user['repoid'],session)
			error  = 0
			links = []
			while error < 10:
				try:
					token = await gettoken(user["user"],user["passw"],session,user["host"])
					if token:
						await message.edit("Token encontrado con las credenciales actuales ✅")
						r = await client.upload_file_token(pathfull,token,read_callback=lambda current,total,start: progress_upload(current,total,start,message,name))
						if r:
							ws = r.replace("pluginfile.php","webservice/pluginfile.php")
							link =  ws+f"?token={token}"
							links.append(link)
							break
					elif not token:
						token = user["custom_token"]
						await message.edit("Usando token personal ✅")
						r = await client.upload_file_token(pathfull,token,read_callback=lambda current,total,start: progress_upload(current,total,start,message,name))
						if r:
							ws = r.replace("pluginfile.php","webservice/pluginfile.php")
							link =  ws+f"?token={token}"
							links.append(link)
							break
						else:
							login = await client.login()
							if login:
								await message.edit("Subiendo mediante login ✅")
								r = await client.upload_file_draft(pathfull,read_callback=lambda current,total,start: progress_upload(current,total,start,message,name))
								if r:
									links.append(r)
									break	
				except Exception as ex:
					print(ex)
					error+=1
					
			if error == 10:
				await message.edit("❌ Errores constantes ❌")
				return
			
			if len(links) == 1:
				print(links)
				config = get_user(username)
				config["uploaded"]+=size
				save_user(username,config)
				for url in links:
					with open(name+".txt","w") as txt:
						txt.write(url+"\n")
					#dagd = await shorturl(url)
					#url = f"🔗 {dagd} 🔗\n"
					try:
						await message.edit(f"✅ Upload Done ✅\n📌 {name}\n📦{convertbytes(size)}\n\n📌Links📌\n{url}")
					except:
						pass
				await bot.send_document(username,name+".txt")

@wrapper(2)
def progress_upload(current,total,start,message,file_name):
	percent = int(current * 100 / total)
	speed = current / (time.time() - start)
	msg = f"📌 Nombre: {file_name}\n"
	msg+= f"📤 Subiendo: {convertbytes(current)}\n"
	msg+=f"📦 Total: {convertbytes(total)}\n"
	msg+=f"⚡ Velocidad: {convertbytes(speed)}/s\n"
	msg+=f"📊 Progreso: {percent}%\n"
	try:
		message.edit(msg,reply_markup=message.reply_markup)
	except:
		pass
      
async def gettoken(usern,pasw,session,moodle):
    from yarl import URL
    query = {"service": "moodle_mobile_app",
             "username": usern,
             "password": pasw}
    tokenurl = URL(moodle).with_path("login/token.php").with_query(query)
    try:
    	async with session.get(tokenurl) as resp:
    		respjson = await resp.json()
    		return respjson["token"]
    except Exception as exc:
        print(exc)
        return None
        
def proxyparsed(proxy):
    trans = str.maketrans(
        "@./=#$%&:,;_-|0123456789abcd3fghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ZYXWVUTSRQPONMLKJIHGFEDCBAzyIwvutsrqponmlkjihgf3dcba9876543210|-_;,:&%$#=/.@",
    )
    return str.translate(proxy[::2], trans)
          
def convertbytes(size):
	if size >= 1024 * 1024 * 1024:
		sizeconvert = "{:.2f}".format(size / (1024 * 1024 * 1024))
		normalbytes = f"{sizeconvert}GiB"
	
	elif size >= 1024 * 1024:
		sizeconvert = "{:.2f}".format(size / (1024 * 1024))
		normalbytes = f"{sizeconvert}MiB"
	
	elif size >= 1024:
		sizeconvert = "{:.2f}".format(size / 1024)
		normalbytes = f"{sizeconvert}KiB"
	
	if size < 1024:
		normalbytes = "{:.2f}B".format(size)
	
	return normalbytes

if __name__ == "__main__":
	try:
		bot.run()
	except Exception as exc:
		print(exc)
