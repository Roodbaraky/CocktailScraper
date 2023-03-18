#Imports
from __future__ import print_function
from bs4 import BeautifulSoup
from datetime import date
import calendar
import requests
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def cockscraper():
    #Generating first url

    #first we need to scrape the url from the cocktail of the day page
    #the format for this url is
    #https://www.diffordsguide.com/on-this-day/<current month>/<current day>
    #so we need to use the date/time library to generate this in the first place

    url = 'https://www.diffordsguide.com/on-this-day/'
    var = date.today()
    #print(var)

    num = var.month
   #print(num)

    month=(calendar.month_name[num])
    day=var.day
    #print(month)
    #print(day)

    #generates the cocktail of the day page using datetime x calendar
    newurl = str(url) + str(month) +'/'+str(day)
    #print(newurl)


    #Generating 2nd url
    #headers and page info that beautiful soup needs in order to scra
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
    page=requests.get(newurl, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    #keeping these incase the webpage changes:
    #div class="cell auto calendar-title-block calendar-title-block--cocktail flex-container align-center-middle"
    #a href="/cocktails/recipe/<unique cocktailID>/<unique cocktail name>"


    #scrapes for section containing cocktail title and assigns variable
    title = soup.find("h3", {"class": "calendar-title-block__cocktail-heading"}).get_text()
    test = re.compile(r'/cocktails/recipe/.*')
    title2 = soup.find("h3", {"class": "calendar-title-block__cocktail-heading"})
    title = title.strip()
    print(title)
    print(title2)
    title3 =test.search(str(title2)).group()
    title3 = title3[:(len(title3) - 2)]
    print(title3)
    url2scrape = title3


    #using regex to find a string with the right format
    #we're lucky that this link is only going to appear once, so we don't need to be too specific
    #hence the '.' wildcard
    #test=re.compile(r'/cocktails/recipe/.')

    #gets the new url for the webpage we actually want to scrape
    #url2scrape = soup.find("a", {"href": test}).get('href')
    #url2scrape= title.find_next('a').get_text()

    #let's clean them both up

    #url2scrape = url2scrape.strip()
    #print(title)
    #print(url2scrape)

    url = 'https://www.diffordsguide.com' + url2scrape
    #print(url)
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    #print(title)

    # conveniently, this is the same hyperlink on every cocktail page, so far anyway
    glass = (soup.find('a', {'href': '/encyclopedia/329/cocktails/cocktail-glassware'}).get_text()).strip()
    #print(glass)

    # This was annoyingly easy once I got it to work.
    # The page again, conveniently will always say 'Garnish:'
    # So we search for this and then the next <p> tag, which is exactly what we want
    garnish = soup.find(string='Garnish:')
    garnish2 = garnish.find_next('p').get_text().strip()
    #print(garnish2)

    # rinse and repeat the previous - it's super effective!
    pre = soup.find(string='How to make:')
    method = pre.find_next('p').get_text().strip()
    #print(method)

    # creates a list for the specs
    specslist = []
    test = re.compile(r'td-align-top.*')
    specs = soup.find_all("td", {"class": test})
    for ing in specs:
        ing1 = (ing.get_text()).strip()
        specslist.append(ing1)
    # conveniently this scrapes as <measurement>, <ingredient>
    # so we will index the list in this manner later - consistent, nice!

    # this is to convert the list into string format before we write it to the sheets file
    # it may turn out to be more useful in list format for a later stage of the project
    # so for now we will keep 'specslist' and 'specsliststr'
    pos = 0
    global specsliststr
    specsliststr=''
    #print (len(specslist))


    for i in specslist:
        while pos < len(specslist):
            #print (specslist.index(i))
            #print (len(specslist))
            #print (pos)
            specsliststr = specsliststr + specslist[pos] + ' ' + specslist[pos + 1] + ',\n'
            pos = pos + 2
            #print(specsliststr)
            global cock2save
            cock2save = [title, glass, garnish2, method, specsliststr]

    specstorer()


def specstorer():
    attributes = ['Cocktail', 'Glass', 'Garnish', 'Method', 'Specs']
    #Reading and printing all filled rows
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=scopes)
    file = gspread.authorize(creds)
    workbook = file.open('Cocktails')
    sheet = workbook.sheet1

    num = len(sheet.get_all_values())
    filledrows = num
    for cell in sheet.range('A2:E1000'):
        while num > 0:
            #print(sheet.row_values(num))
            num = num - 1

    #insert new cocktail row
    newrange = 'A'+str(filledrows+1)+':'+'E'+str(filledrows+1)
    oldrange = 'A'+str(filledrows)+':'+'E'+str(filledrows)
    #print(newrange)
    if (sheet.get_values(oldrange)) == [cock2save]:
        print("Oops, that one's already saved, try again tomorrow :)")
    else:
        sheet.update(newrange, [cock2save])

cockscraper()
