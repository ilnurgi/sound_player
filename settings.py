# coding: utf-8

import os

import yaml

BASE_DIR = os.path.dirname(__file__)

MUSIC_PATH = BASE_DIR

CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'settings.yaml')

MAIN_WINDOW_MIN_HEIGHT = 600
MAIN_WINDOW_MIN_WIDTH = 800

MAIN_WINDOW_HEIGHT = 600
MAIN_WINDOW_WIDTH = 800

MAIN_WINDOW_X = 0
MAIN_WINDOW_Y = 0

VOLUME = 50


# ==============================================================================
# LOAD_CONFIG
# ==============================================================================

def update(path):
    with open(path) as stream:
        config = yaml.load(stream)
    if config:
        gl = globals()
        for key, value in config.iteritems():
            if key in gl:
                if isinstance(value, dict):
                    for k, v in value.iteritems():
                        gl[key][k] = v
            else:
                gl[key] = value

if os.path.exists(CONFIG_FILE_PATH):
    update(CONFIG_FILE_PATH)

MUSIC_PATH = unicode(MUSIC_PATH)
