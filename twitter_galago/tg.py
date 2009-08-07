#!/usr/bin/env python

import ConfigParser
import getpass
import keyring # This may have to be renamed after keyring's release
import logging
import os
import pynotify
import shutil
import socket
import tempfile
import twitter
import urllib2
import xdg.BaseDirectory
import logging
import time

SOCKET_TIMEOUT = 10

SVC_NAME = "twitter_galago"
KEYRING_SVC = SVC_NAME
XDG_RESOURCE = SVC_NAME

CONFIG_FILENAME = "settings.ini"
SLEEP_DELAY = 60 * 5


logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

socket.setdefaulttimeout(SOCKET_TIMEOUT)

class GalagoException(Exception):
    pass

class NotAuthenticatedException(Exception):
    pass

if not pynotify.init("twitter_galago"):
    raise GalagoException


class TwitterGalago(object):

    def __init__(self):
        LOG.info("Creating Twitter Galago")
        config_dir = xdg.BaseDirectory.load_first_config(XDG_RESOURCE)
        if config_dir is None:
            LOG.info("Had to create config directory")
            config_dir = xdg.BaseDirectory.save_config_path(XDG_RESOURCE)
        self.config_filename = os.path.join(config_dir, CONFIG_FILENAME)
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(self.config_filename)
        self.__api = None
        self.__last_seen = None

    def auth(self, ensure_creds_exist=False):
        """Sets property api to valid values"""
        if ensure_creds_exist:
            self.ensure_username_exists()
            self.ensure_password_exists()
        user = self.username
        password = self.password
        self.api = twitter.Api(username=user, password=password)

    def requires_auth(self):
        if self.api is None:
            raise NotAuthenticatedException

    @property
    def api(self):
        return self.__api

    @api.setter
    def api(self, val):
        if self.api is not None:
            del self.api
        self.__api = val

    @api.deleter
    def api(self):
        if self.__api is None:
            return
        self.api.ClearCredentials()
        del self.__api
        self.__api = None

    def get_new_messages(self):
        self.requires_auth()
        statuses = self.api.GetFriendsTimeline(since_id=self._last_seen)
        statuses.sort(key=lambda x:x.created_at_in_seconds)
        LOG.info("Found %d new statuses" % len(statuses))
        for status in statuses:
            self.alert_status(status)
        if len(statuses) > 0:
            self._last_seen = statuses[-1].id

    def alert_status(self, status):
        summary = status.user.name
        message = status.text
        icon_url = status.user.profile_image_url

        with tempfile.NamedTemporaryFile() as icon_file:
            req = urllib2.urlopen(icon_url)
            shutil.copyfileobj(req, icon_file)
            icon_file.file.flush()
            LOG.info("Saving temporary icon to %s" % icon_file.name)
            n = pynotify.Notification(summary, message, icon_file.name)
            n.show()

    @property
    def _last_seen(self):
        if self.__last_seen is None:
            LOG.info("Last seen not set, getting from twitter")
            self.requires_auth()
            try:
                last_message = self.api.GetFriendsTimeline(count=1)[0]
            except IndexError:
                self.__last_seen = None
            else:
                self.__last_seen = last_message.id
        return self.__last_seen

    @_last_seen.setter
    def _last_seen(self, val):
        LOG.debug("Setting last seen to %d" % val)
        self.__last_seen = val

    @property
    def password(self):
        return keyring.get_password(KEYRING_SVC, self.username)

    @password.setter
    def password(self, password):
        keyring.set_password(KEYRING_SVC, user, password)

    def ensure_username_exists(self):
        if (not self.config.has_section("auth") or
                not self.config.has_option("auth", "username")):
            self.username = raw_input("Username: ")

    def ensure_password_exists(self):
        user = self.username
        try:
            password = keyring.get_password(KEYRING_SVC, user)
        except OSError:
            self.password = getpass("Password: ")

    @property
    def username(self):
        return self.config.get("auth", "username")

    @username.setter
    def username(self, username):
        self.config.set("auth", "username", username)
        with open(self.config_filename, "w") as f:
            self.config.write(f)

def main():
    twit = TwitterGalago()
    twit.ensure_username_exists()
    twit.ensure_password_exists()
    twit.auth()
    try:
        while True:
            twit.get_new_messages()
            time.sleep(SLEEP_DELAY)
    except KeyboardInterrupt:
        del twit.api


if __name__ == "__main__":
    main()

