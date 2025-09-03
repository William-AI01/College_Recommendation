from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from database import get_connection

import time

def scrape_program(college_data):
    programs = []

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    try:
        # The loop iterates through tuples of (college_id, url)
        for college_id, url in college_data:
            print(f"Fetching page: {url} for college id {college_id}")

            driver.get(url)
            time.sleep(3) # Let the page load

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # The main container for each program
            program_cards = soup.select("div.w-full")

            for card in program_cards:
                program_name_tag = card.select_one('a[href^="/course/"]')
                program_name = program_name_tag.get_text(strip=True) if program_name_tag else None

                duration_tag = card.select_one("button[data-state]")
                duration = duration_tag.get_text(strip=True) if duration_tag else None

                if program_name:
                    programs.append({
                        "college_id": college_id,
                        "program_name": program_name,
                        "duration": duration
                    })
                    
            print(f"Successfully scraped program from {url}")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error while scraping program from {url}: {e}")
    finally:
        driver.quit()
    return programs

def get_college_data_from_db():
    conn = get_connection()
    cur = conn.cursor()
    # This now correctly fetches and returns a list of (id, url) tuples
    cur.execute("SELECT id, url FROM colleges;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def save_program_to_db(programs):
    conn = get_connection()
    cur = conn.cursor()
    for p in programs:
        cur.execute("""
            INSERT INTO programs (college_id, program_name, duration)
            VALUES (%s, %s, %s)
            """, (p["college_id"], p["program_name"], p["duration"])
            )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    college_data = get_college_data_from_db()
    programs = scrape_program(college_data)
    save_program_to_db(programs)
    print("Program data inserted")