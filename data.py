import re

from itertools import product
from datetime import datetime, timedelta

import pandas as pd


def map_day_to_true(value):
    return [not not a for a in value]


def strip_spaces(value):
    return value.strip()


def preprocess(df):
    df = df.drop('Unnamed: 26', axis=1)
    df[['M', 'T', 'W', 'TH', 'F', 'S', 'SU']] = df[['M', 'T', 'W', 'TH', 'F', 'S', 'SU']].fillna(False)
    df[['M', 'T', 'W', 'TH', 'F', 'S', 'SU']] = df[['M', 'T', 'W', 'TH', 'F', 'S', 'SU']].apply(map_day_to_true)
    df['AutoEnroll'] = df['Codes'].str.contains('A')
    df['Primary'] = df['Codes'].str.contains('P')
    df['Secondary'] = df['Codes'].str.contains('S')
    df['DepPermission'] = df['Codes'].str.contains('D')
    df['InsPermission'] = df['Codes'].str.contains('I')
    df['ReserveCapacity'] = df['Codes'].str.contains('R')
    df['Waitlist'] = df['Codes'].str.contains('W')
    df = df.drop('Codes', axis=1)
    df['Subject'] = df['Subject'].apply(strip_spaces)
    df['Catalog Nbr'] = df['Catalog Nbr'].apply(strip_spaces)
    df = df.drop('Has WL', axis=1)
    df = df[df['Time'] != 'ARR']
    return df


def create_acronym_to_subject_map(df):
    names = df['Subject'].unique()
    pattern = re.compile(r'\((.+)\)')
    return {
        pattern.findall(name)[0]: name for name in names
    }


def course_name_to_tuple(course_name, mapping):
    """ Expects course name to be formatted: EECS280
        Also need to pass in name mapping
    """
    pattern = re.compile(r'([A-Z]+)([0-9]+)')
    acr, number = pattern.match(course_name).groups()
    course_name = mapping[acr]
    return course_name, number


def get_real_list_of_courses(course_list, mapping, df):
    """ Returns list of courses with LAB and LEC suffixes
    """
    real_course_list = []
    for course in course_list:
        components = get_list_of_sections(*course_name_to_tuple(course, mapping), df)['Component'].unique()
        real_course_list += [course + component for component in components]
    return real_course_list


def get_list_of_sections(subject, nbr, df):
    return df[(df['Subject'] == subject) & (df['Catalog Nbr'] == nbr)]


def invert_am_pm(am_pm):
    return 'PM' if am_pm == 'AM' else 'AM'


def get_timedelta(str_time, am_pm):
    if len(str_time) <= 2:
        hours = int(str_time)
        minutes = 0
    else:
        hours = int(str_time[:-2])
        minutes = int(str_time[-2:4]) if str_time[-2:4] else 0
    hours = hours % 12 + 12 if am_pm == 'PM' else hours
    return timedelta(hours=hours, minutes=minutes)


def get_start_and_end_times(row, day):
    """ Return tuple of start and end times
    """
    raw_time = row['Time']
    start_end = raw_time[:-2]
    start, end = start_end.split('-')
    end_am_pm = raw_time[-2:]
    start_am_pm = end_am_pm if int(end) % 12 - int(start) % 12 > 0 else invert_am_pm(end_am_pm)
    start_time = get_timedelta(start, start_am_pm)
    end_time = get_timedelta(end, end_am_pm)
    return (start_time, end_time)


def get_times(row):
    """ Returns dict mapping days to tuple of start and end times
    """
    days = ['M', 'T', 'W', 'TH', 'F', 'S', 'SU']
    time = dict()
    for day in days:
        time[day] = get_start_and_end_times(row, day) if row[day] else None
    return time


def get_section_to_info_map(course_list, df):
    acronym_map = create_acronym_to_subject_map(df)
    course_to_section_map = {course: [] for course in get_real_list_of_courses(course_list,
                                                                               acronym_map, df)}
    course_dict = dict()
    for course in course_list:
        subject, nbr = course_name_to_tuple(course, acronym_map)
        section_iter = get_list_of_sections(subject, nbr, df).iterrows()
        for _, row in section_iter:
            # I'm going ahead and using nested dicts and all sorts of stuff,
            # since we'll just do lookups on this dict instead of actually
            # making copies and passing these around, so performance shouldn't
            # actually suffer too much.
            section = {
                'id': row['Class Nbr'],
                'catalog_number': row['Catalog Nbr'],
                'building': row['Location'],
                'times': get_times(row)
            }
            course_dict[str(section['id'])] = section
            course_to_section_map[course + row['Component']].append(str(section['id']))
    return course_to_section_map, course_dict


df = pd.read_csv('./WN2019_open.csv')
df = preprocess(df)

course_to_section_map, cdict = get_section_to_info_map(['EECS281', 'MATH217', 'ENGR101', 'CHEM125', 'CHEM130'], df)


# Let's just do a BFS
# Backtracking Backpacking
def bfs(course_to_section_map, cdict):
    visited = set()
    pass
