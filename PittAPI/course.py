"""
The Pitt API, to access workable data of the University of Pittsburgh
Copyright (C) 2015 Ritwik Gupta

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import re
from datetime import datetime
from typing import Union, List, Dict, Any

import requests
from bs4 import BeautifulSoup, Tag

SUBJECTS = ['ADMJ', 'ADMPS', 'AFRCNA', 'AFROTC', 'ANTH', 'ARABIC', 'ARTSC', 'ASL', 'ASTRON', 'ATHLTR', 'BACC', 'BCHS',
            'BECN', 'BFAE', 'BFIN', 'BHRM', 'BIND', 'BIOENG', 'BIOETH', 'BIOINF', 'BIOSC', 'BIOST', 'BMIS', 'BMKT',
            'BOAH', 'BORG', 'BQOM', 'BSEO', 'BSPP', 'BUS', 'BUSACC', 'BUSADM', 'BUSBIS', 'BUSECN', 'BUSENV', 'BUSERV',
            'BUSFIN', 'BUSHRM', 'BUSMKT', 'BUSORG', 'BUSQOM', 'BUSSCM', 'BUSSPP', 'CDACCT', 'CDENT', 'CEE', 'CGS',
            'CHE', 'CHEM', 'CHIN', 'CLASS', 'CLRES', 'CLST', 'CMME', 'CMMUSIC', 'CMPBIO', 'CMPINF', 'COE', 'COEA',
            'COEE', 'COMMRC', 'CS', 'CSD', 'DENHYG', 'DENT', 'DIASCI', 'DMED', 'DSANE', 'DUPOSC', 'EAS', 'ECE', 'ECON',
            'EDUC', 'EM', 'ENDOD', 'ENGCMP', 'ENGFLM', 'ENGLIT', 'ENGR', 'ENGSCI', 'ENGWRT', 'ENRES', 'EOH', 'EPIDEM',
            'FACDEV', 'FILMG', 'FILMST', 'FP', 'FR', 'FTADMA', 'FTDA', 'FTDB', 'FTDC', 'FTDJ', 'FTDR', 'GEOL', 'GER',
            'GERON', 'GREEK', 'GREEKM', 'GSWS', 'HAA', 'HEBREW', 'HIM', 'HINDI', 'HIST', 'HONORS', 'HPA', 'HPM', 'HPS',
            'HRS', 'HUGEN', 'IDM', 'IE', 'IL', 'IMB', 'INFSCI', 'INTBP', 'IRISH', 'ISB', 'ISSP', 'ITAL', 'JPNSE', 'JS',
            'KOREAN', 'LATIN', 'LAW', 'LCTL', 'LDRSHP', 'LEGLST', 'LING', 'LIS', 'LSAP', 'MATH', 'ME', 'MED', 'MEDEDU',
            'MEMS', 'MILS', 'MOLBPH', 'MSBMS', 'MSCBIO', 'MSCBMP', 'MSCMP', 'MSE', 'MSMBPH', 'MSMGDB', 'MSMI', 'MSMPHL',
            'MSMVM', 'MSNBIO', 'MUSIC', 'NEURO', 'NPHS', 'NROSCI', 'NUR', 'NURCNS', 'NURNM', 'NURNP', 'NURSAN', 'NURSP',
            'NUTR', 'ODO', 'ORBIOL', 'ORSUR', 'OT', 'PAS', 'PEDC', 'PEDENT', 'PEDS', 'PERIO', 'PERS', 'PETE', 'PHARM',
            'PHIL', 'PHYS', 'PIA', 'POLISH', 'PORT', 'PROSTH', 'PS', 'PSY', 'PSYC', 'PSYED', 'PT', 'PUBHLT', 'PUBSRV',
            'PWEA', 'QUECH', 'REHSCI', 'REL', 'RELGST', 'RESTD', 'RUSS', 'SA', 'SERCRO', 'SLAV', 'SLOVAK', 'SOC',
            'SOCWRK', 'SPAN', 'STAT', 'SWAHIL', 'SWBEH', 'SWCED', 'SWCOSA', 'SWE', 'SWGEN', 'SWINT', 'SWRES', 'SWWEL',
            'TELCOM', 'THEA', 'TURKSH', 'UKRAIN', 'URBNST', 'VIET']

CLASS_SEARCH_URL = 'https://psmobile.pitt.edu/app/catalog/classSearch'
CLASS_SEARCH_API_URL = 'https://psmobile.pitt.edu/app/catalog/getClassSearch'
SECTION_DETAIL_URL = 'https://psmobile.pitt.edu/app/catalog/classsection/UPITT/{term}/{section_number}'

extract = lambda s: s.split(': ')[1]


class PittSubject:
    def __init__(self, subject: str, term: str):
        self.subject = subject
        self.term = term
        self._courses = {}

    def __getitem__(self, item):
        if isinstance(item, str):
            item = _validate_course(item)
            if item in self._courses:
                return self._courses[item]
            raise ValueError('Course {} not present in subject'.format(item))

    @property
    def courses(self):
        """Return list of course numbers offered that semester"""
        return list(self._courses.keys())

    def parse_webpage(self, resp: requests.Response) -> None:
        soup = BeautifulSoup(resp.text, 'lxml')
        classes = soup.find('div', {'class': 'primary-head'}).parent.contents
        course = None
        for child in classes:
            if any(child != i for i in ['\n', ' ']):
                if isinstance(child, Tag):
                    if 'class' not in child.attrs:
                        class_sections_url = child.attrs['href']
                        course.append(PittSection(self,
                                                  class_section_url=class_sections_url,
                                                  course=course,
                                                  class_data=child.text.strip().split('\n')
                                                  ))
                    elif child.text != '':
                        class_description = child.text
                        number, *_ = class_description.split(' - ')
                        number = number.split(' ')[1]
                        if number not in self._courses:
                            self._courses[number] = PittCourse(parent=self, course_number=number)
                        course = self._courses[number]

    def to_dict(self, extra_details: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        return {k: v.to_dict(extra_details=extra_details) for k, v in self._courses.items()}

    def __repr__(self):
        return '< Pitt Subject | {term} | {subject} | {num} courses >'.format(
            term=self.term,
            subject=self.subject,
            num=len(self._courses))


class PittCourse:
    def __init__(self, parent: Union['PittSubject', None], course_number: str, *, term: str = None,
                 subject: str = None):
        self.parent_subject = parent

        # Variables to be used if there isn't a parent subject
        self._term = term
        self._subject = subject

        self.number = course_number
        self.sections = []

    def __getitem__(self, item) -> 'PittSection':
        return self.sections[item]

    @property
    def term(self) -> str:
        if self.parent_subject is not None:
            return self.parent_subject.term
        return self._term

    @property
    def subject(self) -> str:
        if self.parent_subject is not None:
            return self.parent_subject.subject
        return self._subject

    def append(self, section: 'PittSection') -> None:
        self.sections.append(section)

    def parse_webpage(self, resp: requests.Response) -> None:
        soup = BeautifulSoup(resp.text, 'lxml')
        classes = soup.find('div', {'class': 'primary-head'}).parent.contents
        for child in classes:
            if any(child != i for i in ['\n', ' ']):
                if isinstance(child, Tag):
                    if 'class' not in child.attrs:
                        class_sections_url = child.attrs['href']
                        self.append(PittSection(parent=self.parent_subject,
                                                class_section_url=class_sections_url,
                                                course=self,
                                                class_data=child.text.strip().split('\n')
                                                ))

    def to_dict(self, extra_details: bool = False) -> List[Dict[str, Any]]:
        return [section.to_dict(extra_details=extra_details) for section in self.sections]

    def __repr__(self) -> str:
        return '< Pitt Course | {term} | {subject} {number} >'.format(
            term=self.term,
            subject=self.subject,
            number=self.number)


class PittSection:
    def __init__(self, parent: Union['PittSubject', None], course: Union['PittCourse', None], class_section_url: str,
                 class_data: Union[List[str], None], *, extra: Dict[str, str] = None, term: Union[str, int] = None):
        self.parent_subject = parent
        self.parent_course = course

        # Variables to be used if there isn't a parent subject and/or course
        self._term = term
        self._subject = None
        self._course_number = None

        if class_data is not None:
            class_info = extract(class_data[0]).split(' ')
            self.section, self.section_type = class_info[0].split('-')
            self.number = class_info[1][1:6]

            days_times = extract(class_data[2])
            self.days = None
            self.times = None
            if days_times != 'TBA':
                days_times = days_times.split(' - ')
                self.days, times = days_times[0].split(' ')
                self.days = [self.days[i * 2:(i * 2) + 2] for i in range(len(self.days) // 2)]
                self.times = [times] + [days_times[1]]

            self.room = extract(class_data[3])
            self.instructor = extract(class_data[4])

            date = extract(class_data[5]).split(' - ')
            self.start_date = datetime.strptime(date[0], '%m/%d/%Y')
            self.end_date = datetime.strptime(date[1], '%m/%d/%Y')

        self.url = class_section_url
        self._extra = extra

    @property
    def term(self) -> str:
        if self.parent_subject is not None:
            return self.parent_subject.term
        elif self.parent_course is not None:
            return self.parent_course.term
        return self._term

    @property
    def subject(self) -> str:
        if self.parent_subject is not None:
            return self.parent_subject.subject
        elif self.parent_course is not None:
            return self.parent_course.subject
        return self._subject

    @property
    def course_number(self) -> str:
        if self.parent_course is not None:
            return self.parent_course.number
        return self._course_number

    @property
    def extra_details(self) -> Dict[str, Any]:
        if self._extra is not None:
            return self._extra
        resp = requests.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')
        data = soup.find('div', {'class': 'section-content clearfix'})
        data = [point for point in data.next_siblings if point != '\n']
        extract_data = lambda x: x.find('div', {'class': 'pull-right'}).next_element.next_element.next_element
        self._extra = {
            'units': extract_data(data[2]),
            'description': extract_data(data[4]),
            'preq': extract(extract_data(data[5]))
        }
        if 'Class Attributes' in data[6].text:
            self._extra['class_attributes'] = extract_data(data[6])
        return self._extra

    def parse_webpage(self, resp: requests.Response) -> None:
        soup = BeautifulSoup(resp.text, 'lxml')
        classes = soup.find('div', {'class': 'primary-head'}).parent.contents
        for child in classes:
            if any(child != i for i in ['\n', ' ']):
                if isinstance(child, Tag):
                    if 'class' not in child.attrs:
                        self.url = child.attrs['href']

                        class_data = child.text.strip().split('\n')
                        class_info = extract(class_data[0]).split(' ')
                        self.section, self.section_type = class_info[0].split('-')
                        self.number = class_info[1][1:6]

                        days_times = extract(class_data[2])
                        self.days = None
                        self.times = None
                        if days_times != 'TBA':
                            days_times = days_times.split(' - ')
                            self.days, times = days_times[0].split(' ')
                            self.days = [self.days[i * 2:(i * 2) + 2] for i in range(len(self.days) // 2)]
                            self.times = [times] + [days_times[1]]

                        self.room = extract(class_data[3])
                        self.instructor = extract(class_data[4])

                        date = extract(class_data[5]).split(' - ')
                        self.start_date = datetime.strptime(date[0], '%m/%d/%Y')
                        self.end_date = datetime.strptime(date[1], '%m/%d/%Y')

                    elif child.text != '':
                        class_description = child.text
                        data, *_ = class_description.split(' - ')
                        subject, number = data.split(' ')
                        self._subject = subject
                        self._course_number = number

    def to_dict(self, extra_details: bool = False) -> Dict[str, Any]:
        data = {
            'subject': self.subject,
            'term': self.term,
            'days': self.days,
            'times': self.times,
            'room': self.room,
            'instructor': self.instructor,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'section': self.section,
            'section_type': self.section_type,
            'number': self.number
        }

        if extra_details:
            data['extra'] = self.extra_details

        return data

    def __repr__(self) -> str:
        return '<Pitt Section | {subject} {course_number} | {section_type} {class_number} | {instructor} >'.format(
            term=self.term,
            subject=self.subject,
            course_number=self.course_number,
            class_number=self.number,
            section_type=self.section_type,
            instructor=self.instructor)


def _validate_subject(subject: str) -> str:
    """Validates that the subject entered is in fact a valid Pitt subject."""
    subject = subject.upper()
    if subject in SUBJECTS:
        return subject
    raise ValueError("Subject entered isn't a valid Pitt subject.")


def _validate_term(term: Union[str, int]) -> str:
    """Validates that the term entered follows the pattern that Pitt does for term codes."""
    valid_terms = re.compile('2\d\d[147]')
    if isinstance(term, int):
        term = str(term)
    if valid_terms.match(term):
        return term
    raise ValueError("Term entered isn't a valid Pitt term.")


def _validate_course(course: Union[int, str]) -> str:
    """Validates that the course name entered is 4 characters long and in string form."""
    if isinstance(course, int):
        course = str(course)
    course_length = len(course)
    if course_length < 4:
        return ('0' * (4 - course_length)) + course
    elif course_length > 4:
        raise ValueError('Invalid course number.')
    return course


def _get_payload(term, *, subject='', course='', section=''):
    """Make payload for request and generates CSRFToken for the request"""

    # Generate new CSRFToken
    session = requests.Session()
    session.get(CLASS_SEARCH_URL)

    payload = {
        'CSRFToken': session.cookies['CSRFCookie'],
        'term': term,
        'campus': 'PIT',
        'subject': subject,
        'acad_career': '',
        'catalog_nbr': course,
        'class_nbr': section
    }
    return session, payload


def get_term_courses(term: Union[str, int], subject: str) -> PittSubject:
    """Returns a list of courses available in term for a particular subject."""
    term = _validate_term(term)
    subject = _validate_subject(subject)
    session, payload = _get_payload(term, subject=subject)
    response = session.post(CLASS_SEARCH_API_URL, data=payload)
    container = PittSubject(subject=subject, term=term)
    container.parse_webpage(response)
    return container


def get_course_sections(term: Union[str, int], subject: str, course: Union[str, int]) -> PittCourse:
    """Return details on all sections taught in a certain course"""
    term = _validate_term(term)
    subject = _validate_subject(subject)
    course = _validate_course(course)
    session, payload = _get_payload(term, subject=subject, course=course)
    response = session.post(CLASS_SEARCH_API_URL, data=payload)
    container = PittCourse(parent=None, course_number=course, term=term, subject=subject)
    container.parse_webpage(response)
    return container


def get_section_details(term: Union[str, int], section_number: Union[str, int]) -> PittSection:
    """Returns information pertaining to a certain section."""
    term = _validate_term(term)
    if isinstance(section_number, int):
        section_number = str(section_number)
    session, payload = _get_payload(term, section=section_number)
    response = session.post(CLASS_SEARCH_API_URL, data=payload)
    container = PittSection(parent=None, course=None, class_section_url='', class_data=None, term=term)
    container.parse_webpage(response)
    return container
