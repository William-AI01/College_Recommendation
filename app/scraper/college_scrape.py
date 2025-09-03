from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from database import get_connection
import time

BASE_URL = "https://www.collegeinfonepal.com/college?affiliated=&collegetype=&course=&discipline=&district=35&level=&faculty=&is_foreign_affiliated=&page={}"

def scrape_college():
    colleges = []

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
    options.add_argument("--disable-gpu") 

    driver = webdriver.Chrome(options=options)

    try:
        for page in range(1, 14):
            url = BASE_URL.format(page)
            print(f"Fetching page {page}...")
            
            driver.get(url)
            time.sleep(3) # Give the page time to load its content
            
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # The main container for each college appears to be an <a> tag
            # with an href attribute that starts with '/college/'
            for card in soup.select('a[href^="/college/"]'):

                # College Name is inside a h2 tag within the card
                name_tag = card.select_one('div.flex.w-full.items-center.gap-3')
                name = name_tag.get_text(strip=True) if name_tag else None

                # University and Location info are still in li tags with specific titles
                university = None
                location =  None

                uni_tag = card.select_one('span.text-neutral.flex.gap-2.items-start.line-clamp-2')
                if uni_tag:
                    university = uni_tag.get_text(strip=True)

                loc_tag = card.select_one('span.text-neutral.flex.gap-2.items-center.line-clamp-1')
                if loc_tag:
                    location = loc_tag.get_text(strip=True)
                
                print(f"University: {university}")
                print(f"location: {location}")

                # The URL is the href attribute of the main card <a> tag
                college_url = f"https://www.collegeinfonepal.com{card['href']}"
                
                if name:
                    colleges.append({
                        "name": name,
                        "university": university,
                        "location": location,
                        "url": college_url
                    })
            
            print(f"Successfully scraped page {page}.")
            time.sleep(2)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        driver.quit()

    return colleges

def save_to_db(colleges):
    conn = get_connection()
    cur = conn.cursor()
    for c in colleges:
        cur.execute("""
            INSERT INTO colleges (name, university, location, url)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING;
            """, (c["name"], c["university"], c["location"], c["url"])
        )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    colleges = scrape_college()
    print(f"Scraping {len(colleges)} colleges")
    save_to_db(colleges)
    print("Data inserted")