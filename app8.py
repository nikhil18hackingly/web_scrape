import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

BASE_URL = "https://www.edsys.in/search-college-list/"

def extract_college_info(html_content, state, district):
    soup = BeautifulSoup(html_content, 'html.parser')
    colleges = soup.find('div', class_='row', id='school_list_table').find_all('div', class_='_cw_1')
    print("extracting the colleges")
    print(colleges)
    college_info = []
    for college in colleges:
        college_name = college.find('div', class_='_img_cot').find('a').text.strip()
        college_link = college.find('div', class_='_img_cot').find('a')['href']
        college_info.append({
            'name': college_name,
            'link': college_link,
            'district': district,
            'state': state
        })
        
    print(college_info)
    return college_info
def scrape_colleges(state, district, college_type):
    params = {
        'college_name': '',
        'college_state': state,
        'college_dist': district,
        'college_type': college_type
    }
    url = BASE_URL + '?' + urlencode(params)
    college_info = []
    print("scraping the college -->")
    # Start with the first page
    page = 1
    while True:
        page_url = f"{url}&page={page}"
        response = requests.get(page_url)
        if response.status_code != 200:
            break  # Stop if page not found or other error occurs

        # Extract college info from the current page
        colleges = extract_college_info(response.content, state, district)
        college_info.extend(colleges)

        # Check if there is another page
        soup = BeautifulSoup(response.content, 'html.parser')
        next_page_button = soup.find('select', id='select_page')
        if not next_page_button or not next_page_button.find('option', selected=True):
            break  # Stop if there's no next page or it's the last page

        page += 1  # Move to the next page

    return college_info


def get_states():
    response = requests.get(BASE_URL)
    print("got the response")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        states = soup.find('select', id='state_id').find_all('option')
        return [state['value'] for state in states if state['value'] != 'Select State']
        
    return []

def get_districts(state):
    params = {
        
        'college_name': '',
        'college_state': state,
        'college_dist': '',
        'college_type': ''
    }
    url = BASE_URL + '?' + urlencode(params)
    print(f"for->>>>>>{state}--->{url}")
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        districts = soup.find('select', id='district_id').find_all('option')
        return [district['value'] for district in districts if district['value'] != 'Select District']
        
    return []

def get_college_types():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        types = soup.find('select', id='syllabus_id').find_all('option')
        return [college_type['value'] for college_type in types if college_type['value'] != 'Select Type']
    return []

def save_to_csv(college_info, filename):
    fields = ['name', 'link', 'district', 'state']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(college_info)

if __name__ == "__main__":
    college_info = []
    states = get_states()
    states.remove(states[0])
    print(states)
    for state in states:
        print(f"for--->{state}")
        districts = get_districts(state)
        districts.remove(districts[0])
        print(districts)
        for district in districts: 
            college_types = get_college_types()
            college_types.remove(college_types[0])
            for college_type in college_types:
                print(f"college type ---->{college_types}")
                colleges = scrape_colleges(state, district, college_type)
                college_info.extend(colleges)
    
    save_to_csv(college_info, 'colleges1.csv')

