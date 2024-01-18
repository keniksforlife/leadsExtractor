import csv
from pprint import pprint
import time
import string
import random
import re
import requests
import asyncio
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from pyppeteer import launch
import os
from dotenv import load_dotenv

load_dotenv()



def create_session(username, password):
    session = requests.Session()

    session.headers = {
        "authority": "app.apollo.io",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36",
        "sec-ch-ua-platform": '"macOS"',
        "accept": "*/*",
        "origin": "https://app.apollo.io",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://app.apollo.io/",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    }

    json_data = {
        "email": username,
        "password": password,
        "timezone_offset": 0,
        "cacheKey": int(time.time()),
    }

    pprint(json_data)

    response = session.post(
        "https://app.apollo.io/api/v1/auth/login", json=json_data)
    print(response.url)

    json_dict = response.json()

    view_id = (
        json_dict.get("bootstrapped_data", dict()).get(
            "finder_views")[0].get("id")
    )

    return session, view_id


def make_Json_dynamically(query):
    json = {}
    # split the url and query string
    url, query_string = query.strip().split("?")
    # split the type of api like in case companies and other one is people
    filter_type = url.strip().split("#/")[1]

    # split all queries values
    query_string_list = query_string.strip().split("&")

    for filter in query_string_list:
        # make a dictionary for searching
        if 'page=' in filter or 'finderViewId' in filter or not '[]=' in filter:
            key, value = filter.split('=')
            # change the camel case keys in to snake case as per the requirement of the api
            temp_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
            # change %2C to , and %20 to space and place the value in the dictioanry
            json[temp_key] = value.replace("%2C", ",").replace("%20", " ")
        elif not 'finderViewId' in filter:
            data = filter.strip().split("[]=")
            key, value = data
            temp_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
            if temp_key in json.keys():
                # if key already present then append the json key
                json[temp_key].append(value.replace(
                    "%2C", ",").replace("%20", " "))
            else:
                # initialize with list
                json[temp_key] = []
                json[temp_key].append(value.replace(
                    "%2C", ",").replace("%20", " "))
    return filter_type, json


def scrape_data(session, view_id, query, output_csv_path, show_result):
    page = 1
    results = []  # List to store the scraped data
    # filter_type , json = make_Json_dynamically(query)
    # if filter type give company value make the  csv accordingly

    # json = query
    filter_type = 'people'

    if filter_type == 'companies':
        json_data = json

        json_data["page"] = page
        json_data["display_mode"] = "explorer_mode"
        json_data["per_page"] = 25
        json_data["open_factor_names"] = []
        json_data["num_fetch_result"] = 1
        json_data["open_factor_names"] = ["prospected_by_current_team"]

        if show_result == '2':
            json_data["prospected_by_current_team"] = ['no']
        elif show_result == '3':
            json_data["prospected_by_current_team"] = ['yes']

        json_data["context"] = "companies-index-page"
        json_data["show_suggestions"] = "False"
        json_data["ui_finder_random_seed"] = "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(6)
        )
        json_data["cacheKey"] = int(time.time())

        out_f = open(output_csv_path, "w", encoding="utf-8")
        csv_writer = csv.DictWriter(
            out_f,
            fieldnames=["name", "linkedin_url", "twitter_url", "facebook_url", "website_url",
                        "primary_domain", "blog_url", "phone", "founded_year", "logo_url"],
            lineterminator="\n",
        )
        csv_writer.writeheader()

        while True:
            resp = session.post(
                "https://app.apollo.io/api/v1/mixed_companies/search", json=json_data
            )
            print(resp.url)

            json_dict = resp.json()
            data = json_dict.get("organizations", [])
            if show_result == '3':
                data = json_dict.get("accounts", [])
            # also wite save data in the account
            if show_result == '1':
                for org_dict in json_dict.get("accounts", []):
                    name = org_dict.get("name")
                    linkedin_url = org_dict.get("linkedin_url")
                    twitter_url = org_dict.get("twitter_url")
                    facebook_url = org_dict.get("facebook_url")
                    website_url = org_dict.get("website_url")
                    primary_domain = org_dict.get("primary_domain")
                    blog_url = org_dict.get("blog_url")
                    phone = org_dict.get("phone")
                    founded_year = org_dict.get("founded_year")
                    logo_url = org_dict.get("logo_url")

                    row = {
                        "name": name,
                        "linkedin_url": linkedin_url,
                        "twitter_url": twitter_url,
                        "facebook_url": facebook_url,
                        "website_url": website_url,
                        "primary_domain": primary_domain,
                        "blog_url": blog_url,
                        "phone": phone,
                        "founded_year": founded_year,
                        "logo_url": logo_url,
                    }

                    pprint(row)
                    csv_writer.writerow(row)

            for org_dict in data:
                name = org_dict.get("name")
                linkedin_url = org_dict.get("linkedin_url")
                twitter_url = org_dict.get("twitter_url")
                facebook_url = org_dict.get("facebook_url")
                website_url = org_dict.get("website_url")
                primary_domain = org_dict.get("primary_domain")
                blog_url = org_dict.get("blog_url")
                phone = org_dict.get("phone")
                founded_year = org_dict.get("founded_year")
                logo_url = org_dict.get("logo_url")

                row = {
                    "name": name,
                    "linkedin_url": linkedin_url,
                    "twitter_url": twitter_url,
                    "facebook_url": facebook_url,
                    "website_url": website_url,
                    "primary_domain": primary_domain,
                    "blog_url": blog_url,
                    "phone": phone,
                    "founded_year": founded_year,
                    "logo_url": logo_url,
                }

                pprint(row)
                csv_writer.writerow(row)

            try:
                pagination_dict = json_dict.get("pagination")
                total_pages = pagination_dict.get("total_pages")

                if total_pages == page:
                    break
            except:
                print("Invalid parameters we can't continue check about json please")
                break

            page += 1
            json_data["page"] = page

        out_f.close()
    elif filter_type == 'people':

        json_data = query

        json_data["page"] = page
        json_data["display_mode"] = "explorer_mode"
        json_data["per_page"] = 25
        json_data["open_factor_names"] = []
        json_data["num_fetch_result"] = 1
        json_data["open_factor_names"] = ["prospected_by_current_team"]
        json_data["context"] = "people-index-page"
        json_data["show_suggestions"] = "False"

        if show_result == '2':
            json_data["prospected_by_current_team"] = ['no']
        elif show_result == '3':
            json_data["prospected_by_current_team"] = ['yes']

        json_data["ui_finder_random_seed"] = "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(6)
        )
        json_data["cacheKey"] = int(time.time())

        print("the requrst ", json_data)
        out_f = open(output_csv_path, "w", encoding="utf-8")
        csv_writer = csv.DictWriter(
            out_f,
            fieldnames=[
                "first_name",
                "last_name",
                "name",
                "linkedin_url",
                "title",
                "company_name",
                "company_website",
                "company_linkedin",
                "city",
                "state",
                "country",
                "email",
                "email_status",


            ],
            lineterminator="\n",
        )
        csv_writer.writeheader()

        while True:
            resp = session.post(
                "https://app.apollo.io/api/v1/mixed_people/search", json=json_data
            )
            # print(resp.url)

            json_dict = resp.json()
            data = json_dict.get("people", [])
            if show_result == '3':
                data = json_dict.get("contacts", [])

            if show_result == '1':
                for org_dict in json_dict.get("contacts", []):
                    name = org_dict.get("name")
                    first_name = org_dict.get("first_name")
                    last_name = org_dict.get("last_name")
                    linkedin_url = org_dict.get("linkedin_url")
                    title = org_dict.get("title")
                    email_status = org_dict.get("email_status")
                    photo_url = org_dict.get("photo_url")

                    # ignore this statis profile url
                    if photo_url == 'https://static-exp1.licdn.com/sc/h/244xhbkr7g40x6bsu4gi6q4ry':
                        photo_url = ''
                    # headline = org_dict.get("headline")
                    email = org_dict.get("email")
                    # email contains email_not_unlocked@domain.com then leave it blank
                    if 'email_not_unlocked@domain.com' == email:
                        email = ''
                    try:
                        company_name = org_dict.get("organization")["name"]

                    except:
                        company_name = ''

                    try:
                        company_webiste_url = org_dict.get(
                            "organization")["website_url"]
                    except:
                        company_webiste_url = ''

                    try:
                        company_linkedin_url = org_dict.get(
                            "organization")["linkedin_url"]
                    except:
                        company_linkedin_url = ''

                    state = org_dict.get("state")
                    city = org_dict.get("city")
                    country = org_dict.get("country")

                    row = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "name": name,
                        "linkedin_url": linkedin_url,
                        "title": title,
                        "company_name": company_name,
                        "company_website": company_webiste_url,
                        "company_linkedin": company_linkedin_url,
                        "city": city,
                        "state": state,
                        "country": country,
                        "email": email,
                        "email_status": email_status,
                    }

                    # pprint(row)
                    # csv_writer.writerow(row)
                    results.append(row)

            for org_dict in data:
                name = org_dict.get("name")
                first_name = org_dict.get("first_name")
                last_name = org_dict.get("last_name")
                linkedin_url = org_dict.get("linkedin_url")
                title = org_dict.get("title")
                email_status = org_dict.get("email_status")
                photo_url = org_dict.get("photo_url")
                # ignore this statis profile url
                if photo_url == 'https://static-exp1.licdn.com/sc/h/244xhbkr7g40x6bsu4gi6q4ry':
                    photo_url = ''
                # headline = org_dict.get("headline")
                email = org_dict.get("email")
                # email contains email_not_unlocked@domain.com then leave it blank
                if 'email_not_unlocked@domain.com' == email:
                    email = ''
                try:
                    company_name = org_dict.get("organization")["name"]
                except:
                    company_name = ''

                try:
                    company_webiste_url = org_dict.get(
                        "organization")["website_url"]
                except:
                    company_webiste_url = ''

                try:
                    company_linkedin_url = org_dict.get(
                        "organization")["linkedin_url"]
                except:
                    company_linkedin_url = ''
                state = org_dict.get("state")
                city = org_dict.get("city")
                country = org_dict.get("country")

                row = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "name": name,
                    "linkedin_url": linkedin_url,
                    "title": title,
                    "company_name": company_name,
                    "company_website": company_webiste_url,
                    "company_linkedin": company_linkedin_url,
                    "city": city,
                    "state": state,
                    "country": country,
                    "email": email,
                    "email_status": email_status
                }

                # pprint(row)
                # csv_writer.writerow(row)
                results.append(row)
            try:
                pagination_dict = json_dict.get("pagination")
                total_pages = pagination_dict.get("total_pages")

                if total_pages == page:
                    print("page", page, total_pages)
                    break
            except:

                print("Invalid parameters we can't continue check about json please")
                break
            page += 1
            json_data["page"] = page

        out_f.close()
        return results
    else:
        print(f"this {filter_type} type is not implemented yet")

# async def main():

#     username = "kentluckybuhawe@gmail.com" #input("Username: ")
#     password = 'E$oxO5,isT8jjCN5"LVt' #input("Password: ")

#     query = "https://app.apollo.io/#/people?finderViewId=6362c91506c25c00a3810414&personTitles[]=ceo&personTitles[]=owner&personTitles[]=president&personTitles[]=founder&organizationNumEmployeesRanges[]=1,10&organizationNumEmployeesRanges[]=11,20&organizationNumEmployeesRanges[]=21,50&organizationNumEmployeesRanges[]=51,100&organizationNumEmployeesRanges[]=101,200&organizationNumEmployeesRanges[]=201,500&organizationNumEmployeesRanges[]=501,1000&organizationNumEmployeesRanges[]=1001,2000&organizationNumEmployeesRanges[]=2001,5000&personLocations[]=United%20States&qOrganizationKeywordTags[]=nursing%20home&qOrganizationKeywordTags[]=skilled%20nursing&qOrganizationKeywordTags[]=nursing&qNotOrganizationKeywordTags[]=saas&qNotOrganizationKeywordTags[]=software&qNotOrganizationKeywordTags[]=tech&qNotOrganizationKeywordTags[]=technology&qNotOrganizationKeywordTags[]=consultant&qNotOrganizationKeywordTags[]=recruit&qNotOrganizationKeywordTags[]=billing&qNotOrganizationKeywordTags[]=hr&qNotOrganizationKeywordTags[]=platform&organizationIndustryTagIds[]=5567cdde73696439812c0000&notContactStageIds[]=6051001ff0e99a00e2650156&notContactStageIds[]=6051001ff0e99a00e2650155&notContactStageIds[]=6051001ff0e99a00e2650159&notAccountStageIds[]=6051001ff0e99a00e265015d&notAccountStageIds[]=6051001ff0e99a00e265015e&notAccountStageIds[]=6051001ff0e99a00e2650160&contactEmailStatus[]=verified&contactEmailStatus[]=guessed" #input("Search query: ")
#     show_result = input("show result 1 : total , 2: net new , 3:saved")
#     output_csv_path = input("Output CSV path: ")

#     session, view_id = create_session(username, password)

#     print(session.cookies)

#     scrape_data(session, view_id, query, output_csv_path , show_result)


app = FastAPI()


@app.post("/scrape")
async def scrape(request: Request):
    try:
        # Read the JSON content from request body
        json_data = await request.json()

        # Now you can access the data like json_data['finder_view_id'], etc.
        # and pass it to your scraping logic.
        output_csv_path = "output.csv"  # Generate a unique name as needed
        show_result = "1"  # or take this from the request

        username = os.getenv("username")
        password = os.getenv("password")

        loop = asyncio.get_running_loop()
        session, view_id = await loop.run_in_executor(None, create_session, username, password)

        scraped_data = await loop.run_in_executor(None, scrape_data, session, view_id, json_data, output_csv_path, show_result)

        return {"data": scraped_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# if __name__ == "__main__":
#     main()
