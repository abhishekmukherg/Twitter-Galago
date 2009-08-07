#!/usr/bin/env python

import os
import twitter
import keyring # This may have to be renamed after keyring's release
import logging
import xdg.BaseDirectory
import getpass
import ConfigParser

SVC_NAME = "twitter_galago"
KEYRING_SVC = SVC_NAME
XDG_RESOURCE = SVC_NAME

CONFIG_FILENAME = "settings.ini"

class TwitterGalago(object):

    def __init__(self):
        config_dir = xdg.BaseDirectory.load_first_config(XDG_RESOURCE)
        if config_dir is None:
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
        pass

    def alert_status(self, status):
        pass

    @property
    def _last_seen(self):
        if self.__last_seen is None:
            try:
                last_message = self.api.GetFriendsTimeline(count=1)[0]
            except IndexError:
                self.__last_seen_id = None
            else:
                self.__last_seen_id = last_message.GetId()
        return self.__last_seen_id

    @_last_seen.setter
    def _last_seen(self, val):
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
    x = TwitterGalago()
    x.ensure_username_exists()
    x.ensure_password_exists()
    print x.username
    print x.password

if __name__ == "__main__":
    main()

