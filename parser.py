from bs4 import BeautifulSoup
from urllib.request import urlopen
from pymongo import *
import re


class hw4parser:
	def __init__(self):
		pass

	def connectDatabase(self):
		DB_NAME = "hw4_crawler"
		DB_HOST = "localhost"
		DB_PORT = 27017

		try:
			client = MongoClient(host = DB_HOST, port = DB_PORT)
			db = client[DB_NAME]
			self.pages = db.pages
			self.professors = db.professors
			return db
		except:
			print("Database not connected successfully")

	
	def retrieveHTMLFromDB(self, url):
		html = self.pages.find_one({"url": url})['html']
		if html is None:
			print("unable to get HTML from database")
			exit()
		return html
	

	def parseFacultyPageInfo(self, html):
		prof_list = []

		bs = BeautifulSoup(html, 'html.parser')

		for professor in bs.find_all("div", {"class": "clearfix"}):
			if professor.img:
				name = professor.find("h2").text.strip()
				title = professor.find("strong", string=re.compile("Title")).next_sibling.strip()
				office = professor.find("strong", string=re.compile("Office")).next_sibling.strip()
				phone = professor.find("strong", string=re.compile("Phone")).next_sibling.strip()
				email = professor.find("a", string=re.compile("@cpp.edu")).text.strip()
				website = professor.find("a", string=re.compile("cpp.edu/")).text.strip()

				prof_info = {
					'name': name,
					'title': title.replace(":", ""),
					'office': office.replace(":", ""),
					'phone': phone.replace(":", ""),
					'email': email,
					'website': website
				}
				prof_list.append(prof_info)
		
		for prof in prof_list:
			professor = {
				'name': prof['name'],
				'title': prof['title'],
				'office': prof['office'],
				'phone': prof['phone'],
				'email': prof['email'],
				'website': prof['website']
			}
			self.professors.insert_one(professor)

		print("done")


	

if __name__ == "__main__":
	url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
	parser = hw4parser()
	parser.connectDatabase()
	html = parser.retrieveHTMLFromDB(url)
	parser.parseFacultyPageInfo(html)

