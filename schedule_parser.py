import urllib.request
from bs4 import BeautifulSoup

BAK_URL = 'https://home.mephi.ru/study_groups?faculty_id=34&term_id=5'
SPEC_URL = 'https://home.mephi.ru/study_groups?faculty_id=38&term_id=5'
BASE_URL = 'https://home.mephi.ru'

def get_html(url):
        response = urllib.request.urlopen(url)
        return response.read()

def parse_schedule(html):
    subjects=[]
    soup = BeautifulSoup(html)
    table = soup.find('div', class_='list-group')

    for item in table.find_all('div', class_='list-group-item'):
        time = item.find('div', class_='lesson-time').text.replace(u'\xa0', u'').replace(' ', '')
        for subj in item.find('div', class_='lesson-lessons').find_all('div', recursive=False):
            for t_name in subj.div.findAll(text=True, recursive=False):
               if (len(t_name) >= 3): name = t_name.strip()
            room = subj.find('div', class_='pull-right').a.text
            type = subj.find('div', class_='label label-default label-lesson').text
            lecturers = subj.div.find_all('a', class_="text-nowrap", recursive=False)
            if len(lecturers) !=0: 
                t_lecturers=lecturers[0].text.replace(u'\xa0', u' ')
                for lecturer in lecturers[1:]:
                    t_lecturers=t_lecturers + ", " + lecturer.text.replace(u'\xa0', u' ')
            else:
                t_lecturers = "???"
            subjects.append({'time':time, 'name':name, 'room':room, 'type':type, 'lecturers': t_lecturers})

    return subjects

def get_url(group):
    if group[0]=="Б":
        html=get_html(BAK_URL)
    else:
        html = get_html(SPEC_URL)
    soup = BeautifulSoup(html)
    url = soup.find('a', class_="list-group-item text-center text-nowrap", text=group+"\n")
    return url['href'].replace('schedule', 'day')

def get_schedule(group, day=""):
    try:
        url = get_url(group)
    except TypeError:
        raise Exception("Group not found")
    try:
        subj = parse_schedule(get_html(BASE_URL+url+'?date=%s'%day))
        return subj
    except Exception:
        raise Exception("Schedule not found!")


def main():
    subj = get_schedule("Б14-501", "2017-09-07")
    for s in subj:
        print(s)

if __name__ == '__main__':
    main()