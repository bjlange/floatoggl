"""Functions that grab data from Float and Toggl APIs and do useful things with
that data"""
# imports
import sys
import logging

import requests

import settings

logging.basicConfig(level=logging.DEBUG)


# constants

# exception classes

# interface functions

# classes
class Datascope(object):
    people = []
    projects = []

    def people_as_emails(self):
        return [a.email for a in self.people]

    def fetch_people_from_float(self):
        float_people = float_request("/people/")
        logging.info("Adding people from Float")
        emails = self.people_as_emails()
        for float_person in float_people['people']:
            if float_person['email'] not in emails:
                person_obj = Person()
                person_obj.add_profile_from_float(float_person)
                self.people.append(person_obj)
            else:
                raise NotImplementedError()
        logging.debug("done, here's the emails: %s", self.people_as_emails())

    def fetch_people_from_toggl(self):
        """
        Grabs people from the Toggl API and merges them with existing people via email.
        Currently assumes the self.people list has already been populated.
        """
        toggl_people = toggl_request('/workspaces/%d/users' % settings.TOGGL_WORKSPACE_ID)
        logging.info("Adding people from Toggl")
        for toggl_person in toggl_people:
            found = False
            for person in self.people:  # TODO: make this able to be called even when self.people hasn't been populated
                if toggl_person['email'] == person.email:
                    person.add_profile_from_toggl(toggl_person)
                    found = True
            if not found and toggl_person['email'] not in settings.DEPARTED_EMAILS:
                raise Exception("No match found for %s" % toggl_person['email'])


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

    def add_profile_from_toggl(self, toggl_profile):
        self._toggl_profile = toggl_profile
        if not self.name:
            self.name = toggl_profile['fullname']
        if not self.email:
            self.email = toggl_profile['email']

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
    datascope.fetch_people_from_toggl()
    import pprint
    for person in datascope.people:
        pprint.pprint(person)

    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
