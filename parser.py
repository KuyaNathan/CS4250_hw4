from bs4 import BeautifulSoup
from urllib.request import urlopen
from pymongo import *


class hw4parser:
	def __init__(self):
		self.db = None
		self.pages = None

	def connectDataBase(self):
		DB_NAME = "hw4_crawler"
		DB_HOST = "localhost"
		DB_PORT = 27017

		try:
			client = MongoClient(host = DB_HOST, port = DB_PORT)
			self.db = client[DB_NAME]
			self.pages = self.db['pages']
			print("successful connection")
			return client[DB_NAME]
		except Exception:
			print("error connecting to database")

	def retriveHTML(self, url):
		try:
			page = self.pages.find_one({'url': url})
			if page:
				return page['html']
		except Exception:
			print("error retrieving html")
	
	def parseInfo(self, html):
		faculty_info = {}
		bs = BeautifulSoup(html, 'html.parser')
		faculty = bs.find('ul', class_='directory')
		for professor in faculty.find_all('li'):
			name = professor.find('h3').text.strip()
			title = professor.find('p', class_='title').text.strip()
			office = professor.find('p', class_='office').text.strip()
			phone = professor.find('p', class_='phone').text.strip()
			email = professor.find('p', class_='email').text.strip()
			website = professor.find('a', href=True)['href']

			faculty_info[name] = {
				'title': title,
				'office': office,
				'phone': phone,
				'email': email,
				'website': website
			}
		return faculty_info
	
	def persistInfo(self, faculty_info):
		professors = self.db['professors']
		for name, info in faculty_info.items():
			professor_info = {
				'name': name,
				'title': info['title'],
				'office': info['office'],
				'phone': info['phone'],
				'email': info['email'],
				'website': info['website']
			}
			professors.insert_one(professor_info)
		print("done persisting faculty info")
	

if __name__ == "__main__":
	parser = hw4parser()
	parser.connectDataBase()
	url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
	html = parser.retriveHTML(url)
	if html:
		faculty_info = parser.parseInfo(html)
		parser.persistInfo(faculty_info)

