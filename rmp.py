import json
import pickle as pkl

import requests
from bs4 import BeautifulSoup


def get_rmp_prof_id(name):
    search_url = ("http://search.mtvnservices.com/typeahead/suggest/?"
                  "solrformat=true&rows=20&callback=noCB&q={}&defType=edismax&"
                  "sort=score+desc&siteName=rmp&group=on&group.field=content_type_s&group.limit=20")
    search_res = requests.get(search_url.format(name))
    results = json.loads(search_res.text[5:-2])['grouped']['content_type_s']['groups'][0]['doclist']['docs']  # hacc
    results = [prof for prof in results if prof['schoolname_s'] == 'University of Michigan']
    if len(results) > 1:
        print('Duplicates found: {}'.format(results))
    prof_id = results[0]['pk_id']
    return prof_id


def get_rmp_rating(prof_id):
    rating_url = "http://www.ratemyprofessors.com/ShowRatings.jsp?tid={}"
    rating_res = requests.get(rating_url.format(prof_id))
    soup = BeautifulSoup(rating_res.text, 'html.parser')

    overall = soup.select(".quality .grade")[0].text.strip()
    difficulty = soup.select(".difficulty .grade")[0].text.strip()

    return (overall, difficulty)


def get_professor_rating(name):
    """ Returns normalized tuple of (overall, difficulty)
    """
    try:
        prof_id = get_rmp_prof_id(name)
        ov, dif = get_rmp_rating(prof_id)
        print("Overall: {} -- Difficulty: {}".format(ov, dif))
        return (ov / 5, dif / 5)
    except Exception:
        return (-1, -1)


def download_rmp_ratings(df):
    prof_to_rating = dict()
    for prof_list in df.groupby('Instructor')['Instructor'].first():
        for prof in prof_list.split(','):
            prof = prof.strip()
            print(prof)
            if prof in prof_to_rating:
                continue
            prof_to_rating[prof] = get_professor_rating(prof)

    pkl.dump(prof_to_rating, open("rmp_ratings.pkl", "wb"))
