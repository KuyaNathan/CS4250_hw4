from bs4 import BeautifulSoup
from pymongo import *
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError
import re

class hw4crawler:
	def __init__(self, seed):
		self.seed = seed
		self.frontier = [seed]
		self.visited = set()

	def connectDataBase(self):
		DB_NAME = "hw4_crawler"
		DB_HOST = "localhost"
		DB_PORT = 27017

		try:
			client = MongoClient(host = DB_HOST, port = DB_PORT)
			db = client[DB_NAME]
			self.pages = db.pages
			return db
		except:
			print("Database not connected successfully")

	def retrieveHTML(self, url):
		try:
			html = urlopen(url).read()
			return html
		except Exception:
			print(f"error retrieving HTML from {url}")

	def storePage(self, url, html):
		self.pages.insert_one({'url': url, 'html': html.decode('utf-8')})

	def target_page(self, html):
		bs = BeautifulSoup(html, 'html.parser')
		headings = bs.find_all(name=re.compile(r'^h\d+$'))
		for heading in headings:
			if "permanent faculty" in heading.text.lower():
				return True
		return False
	
	def parse(self, html):
		bs = BeautifulSoup(html, 'html.parser')
		links = bs.find_all('a', href=True)
		for link in links:
			url = link['href']
			if url.startswith('http'):
				self.frontier.append(url)
			elif url.startswith('/'):
				self.frontier.append('https://www.cpp.edu' + url)

	def crawlerThread(self):
		while self.frontier:
			url = self.frontier.pop(0)
			html = self.retrieveHTML(url)
			self.storePage(url, html)
			if self.target_page(html):
				self.frontier.clear()
			else:
				self.parse(html)
		print("done")
		

if __name__ == "__main__":
	seed = "https://www.cpp.edu/sci/computer-science/"
	crawler = hw4crawler(seed)
	crawler.connectDataBase()
	crawler.crawlerThread()
	
			