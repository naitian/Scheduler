import re

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


def get_list_of_sections(subject, nbr, df):
    return df[(df['Subject'] == subject) & (df['Catalog Nbr'] == nbr)]


def get_section_to_info_map(section_list, df):
    acronym_map = create_acronym_to_subject_map(df)
    section_dict = dict()
    for section in section_list:
        subject, nbr = course_name_to_tuple(section, acronym_map)
        section_iter = get_list_of_sections(subject, nbr, df).iterrows()
        i = 0
        for _, row in section_iter:
            sec = {
                'id': row['Class Nbr'],
                'catalog_number': row['Catalog Nbr']
            }
            print(row['Class Nbr'])
            i += 1
        print(i)


df = pd.read_csv('./WN2019_open.csv')
df = preprocess(df)

get_section_to_info_map(['EECS281', 'MATH217'], df)
