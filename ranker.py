import json


raw_json = json.load(open('response.json', 'r'))
schedules = raw_json['schedules']
section_info = raw_json['sections']

# build id to section index dict
id_to_section_map = {section['id']: i for i, section in enumerate(section_info)}


def parse_registration_block(reg_block):
    course_name, sections = reg_block.split('@')
    course_name = ' '.join(course_name.split(';;'))
    sections = sections.split('-')
    return (course_name, sections)


def parse_schedule(combination):
    schedule = []
    for registration_block in combination:
        course_name, sections = parse_registration_block(registration_block)
        schedule.append({
            'course_name': course_name,
            'sections': [id_to_section_map[section] for section in sections]
        })
    return schedule


def get_time_friendly_schedule(schedule):
    """ Returns a dict of days, with lists of start and end times
    """
    week = {}
    for course in schedule:
        for section in course['sections']:
            section_details = section_info[section]
            days = section_details['meetings'][0]['daysRaw']
            start_time = section_details['meetings'][0]['startTime']
            end_time = section_details['meetings'][0]['endTime']
            for day in days:
                if day in week:
                    week[day].append((start_time, end_time))
                else:
                    week[day] = [(start_time, end_time)]
    return {day: sorted(week[day], key=lambda x: x[0]) for day in week}


def get_true_time_difference(a, b):
    """ Returns true time difference in minutes
        get_true_time_difference(1300, 1200) should return 60, for example
        get_true_time_difference(1300, 1230) should return 30
        get_true_time_difference(1230, 1200) should return 30
    """
    hour_diff = a // 100 - b // 100
    minute_diff = a % 100 - b % 100
    return hour_diff * 60 + minute_diff


def eight_am_classes(schedule):
    """ The fewer 8ams, the better
    """
    earliest = 800  # because CHEM 126, for example, as at 100 smh
    score = 0
    tf_sched = get_time_friendly_schedule(schedule)
    for day in tf_sched:
        if not day[0]:
            continue
        if max(tf_sched[day][0][0], earliest) // 100 != 8:
            score += 1
    return (score / 5)


def lunch_time(schedule):
    """ Find schedules with at least 30 minutes free at some point between 1200 and 1400
    """
    tf_sched = get_time_friendly_schedule(schedule)
    score = 0
    for day in tf_sched:
        for i in range(len(tf_sched[day]) - 1, 0, -1):
            if tf_sched[day][i][1] <= 1330 \
               and get_true_time_difference(tf_sched[day][i + 1][0], tf_sched[day][i][1]) >= 30:
                score += get_true_time_difference(tf_sched[day][i + 1][0], tf_sched[day][i][1])
                break
    return (score)


def get_normalized_scores(scores, raw_scores, weights):
    means = [sum(heuristic_raw) / len(heuristic_raw) for heuristic_raw in raw_scores.values()]
    return {sid: sum([hs * weights[i] / means[i] for i, hs in enumerate(scores[sid])]) / len(scores[sid]) for sid in scores}


heuristics = [
                eight_am_classes,
                lunch_time
             ]
weights = [.1, 1]
scores = {}
raw_scores = {}
for schedule in schedules:
    schedule_id = schedule['id']
    schedule = parse_schedule(schedule['combination'])
    score = 0
    for i, heuristic in enumerate(heuristics):
        heuristic_score = heuristic(schedule)
        if i in raw_scores:
            raw_scores[i].append(heuristic_score)
        else:
            raw_scores[i] = [heuristic_score]
        if schedule_id in scores:
            scores[schedule_id].append(heuristic_score)
        else:
            scores[schedule_id] = [heuristic_score]
scores = get_normalized_scores(scores, raw_scores, weights)

s = [(k, scores[k]) for k in sorted(scores, key=scores.get, reverse=True)]
[print(schedules[sc[0]], sc[1]) for sc in s[:5]]
