from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


URLS = [
        "https://bhetincha.com/search/?q=nepal-government-organizations&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H",
        "https://bhetincha.com/search/?q=hotel-and-lodge&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H",
        "https://bhetincha.com/search/?q=petrol-pumps&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H",
        "https://bhetincha.com/search/?q=health-care-centers&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H"
        "https://bhetincha.com/search/?q=hospitals&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H",
        "https://bhetincha.com/search/?q=homeopathy&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H",
        "https://bhetincha.com/search/?q=pharmacy&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H",
        "https://bhetincha.com/search/?q=pathology-services&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H",
        "https://bhetincha.com/search/?q=polyclinics&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H"
        "https://bhetincha.com/search/?q=schools&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H",
        "https://bhetincha.com/search/?q=colleges-and-universities&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H",
        "https://bhetincha.com/search/?q=banks&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H",
        "https://bhetincha.com/search/?q=ngo-and-ingo&_qt=B&cto=1&filter_location=Kathmandu&filter_name=&_fr=H"
]



def match_class(target):                                                        
    def do_match(tag):                                                          
        classes = tag.get('class', [])                                          
        return all(c in classes for c in target)                                
    return do_match  

def parse_list_page(url):
    browser = webdriver.Firefox()
    browser.get(url)
    browser.implicitly_wait(30)

    delay = 5
    lenOfPage = 0
    max_retry = 5
    cur_retry = 0
    browser.get(url)
    browser.find_element_by_link_text("Load More").click()

    print "Starting crawler"
    for i in range(1,500):
        print "Page %s" % i
        lastCount = lenOfPage
        # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        time.sleep(delay)
        if lastCount==lenOfPage:
            cur_retry = cur_retry + 1
            print "Retry count %s" % cur_retry
            if(cur_retry == max_retry):
                print "Max retry of %s reached " % max_retry
                break
    html_source = browser.page_source
  
    print "crawling finished"


    bheticha_soup = BeautifulSoup(html_source,from_encoding="utf-8")

    #create file name
    page_name = bheticha_soup.title.string
    page_name = page_name[:-12]
    page_name = page_name.replace(" ","_")
   
    potential_place_tags =  bheticha_soup.find_all(match_class(["list_brief"]))

    with open('%s.csv' % page_name, 'w') as csvfile:
        #init csv 
        fieldnames = ['Name', 'Short Description',"Address","Latitude","Longitude"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        #parse data
        for tag in potential_place_tags:
            cleaned_deals_in = ""
            lat = "0"
            lon = "0"
            cleaned_address  = ""
            
            name = tag.find(match_class(["list_title"]))
            cleaned_name = name.a.contents[0]

            deals_in = tag.find(match_class(["list_desc"]))
            if deals_in:
                if deals_in.div:
                    cleaned_deals_in = deals_in.div.contents[1]
            
            potential_address = tag.find(match_class(["list_info"]))
            potential_address = potential_address.find_all("div", { "class" : "list-info-item" })
            count = len(potential_address)
           
            if count is 2:
                address = potential_address[1]
            elif count is 1:
                address = potential_address[0]

            cleaned_address = address.text
            has_gmap_link =  len(address.findChildren()) == 2
            if(has_gmap_link):
                if address.find(match_class(["gmap-link"])):
                    tag_with_location = address.find(match_class(["gmap-link"]))
                    lat = tag_with_location['data-lat']
                    lon = tag_with_location ['data-lng']


            print "Name: {cleaned_name} Short Description: {cleaned_deals_in} Address: {cleaned_address} lat: {lat} lon: {lon}".format(cleaned_name = cleaned_name,cleaned_deals_in = cleaned_deals_in,cleaned_address = cleaned_address,lat = lat, lon = lon)
            dict = {}
            dict['Name'] = cleaned_name.encode('utf-8')
            dict['Short Description'] = cleaned_deals_in.encode('utf-8')
            dict['Address'] = cleaned_address.encode('utf-8')
            dict['Latitude'] = lat.encode('utf-8')
            dict['Longitude'] = lon.encode('utf-8')
            writer.writerow(dict)
       
    

        # print cleaned_address
        
        # print "Name %s " % cleaned_name
    # with open('%s.csv' % page_name, 'w') as csvfile:
    #     fieldnames = ['lat', 'lon',"desc"]
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     for tag in potential_place_tags:
    #         if tag.has_attr('onclick'):
    #             desc = tag['onclick']
    #         if tag.has_attr('data-lng'):
    #             lat = tag['data-lat']
    #             lon = tag ['data-lng']
        
    #             dict = {}
    #             dict['lat'] = lat.encode('utf-8')
    #             dict['lon'] = lon.encode('utf-8')


    #             clean_desc = desc.replace("return doko.v0SrtIHNCU(this, { title: 'Address Map - ","").replace("', showsubmit: false, method: 'gmap', widerwidth : true, gmap: { show: true, height: '400px', width: '100%', bubble: '', markertitle: '' }})","")
    #             dict['desc'] = clean_desc.encode('utf-8')
    #             writer.writerow(dict)

            
    #         print "Adding a row"
    browser.close()


def main():
    for url in URLS:
        print "Crawling %s" % url
        parse_list_page(url)

main()