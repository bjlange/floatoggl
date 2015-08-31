"""Functions that grab data from Float and Toggl APIs and do useful things with
that data"""
# imports
import sys
import logging

import requests

import settings


# constants

# exception classes

# interface functions

# classes
class Datascope(object):
    people = []
    projects = []

    def fetch_people_from_float(self):
        float_people = float_request("/people/")
        logging.info("Adding people from Float")
        for float_person in float_people['people']:
            if float_person['email'] not in [a.email for a in self.people]:
                person_obj = Person()
                person_obj.add_profile_from_float(float_person)
                self.people.append(person_obj)
            else:
                raise NotImplementedError()


class Person(object):
    name = ""
    email = ""
    _float_profile = {}
    _toggl_profile = {}

    def add_profile_from_float(self, float_profile):
        self._float_profile = float_profile
        if not self.name:
            self.name = float_profile['name']
        if not self.email:
            self.email = float_profile['email']

    def __repr__(self):
        return "<Person: %s>" % self.name


# internal functions & classes
def float_request(endpoint):
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Authorization": "Bearer " + settings.FLOAT_ACCESS_TOKEN,
               "User-Agent": settings.FLOAT_USER_AGENT
               }
    resp = requests.get("https://api.floatschedule.com/api/v1" + endpoint,
                        headers=headers)
    return resp.json()


def toggl_request(endpoint):
    auth_credentials = (settings.TOGGL_API_TOKEN, settings.TOGGL_PASSWORD)
    req = requests.get("https://www.toggl.com/api/v8" + endpoint,
                       auth=auth_credentials)
    return req.json()


def main():
    datascope = Datascope()
    datascope.fetch_people_from_float()
    print [a.email for a in datascope.people]
    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
