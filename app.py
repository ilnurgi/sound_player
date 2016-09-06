#!/usr/bin/env /home/ilnurgi/envs/vlc-audio/bin/python
# coding: utf-8

import os
import random
from Tkinter import Tk, Listbox, Label, END, Button

import json
from tkFileDialog import askdirectory

import vlc


import settings


class App(object):

    def __init__(self):

        self.w_window = Tk()

        self.w_listbox_tracks = Listbox(self.w_window)
        self.w_label_base_path = Label(
            self.w_window,
            highlightbackground='red',
            highlightthickness=1,
        )
        self.w_btn_next = Button(
            self.w_window,
            text=u'Следующая',
            command=self.btn_next,
        )
        self.w_btn_pause = Button(
            self.w_window,
            text=u'Пауза/Играть',
            command=self.btn_pause,
        )
        self.w_btn_stop = Button(
            self.w_window,
            text=u'Стоп',
            command=self.btn_stop,
        )
        self.w_btn_plus = Button(
            self.w_window,
            text=u'+',
            command=self.btn_plus,
        )
        self.w_btn_minus = Button(
            self.w_window,
            text=u'-',
            command=self.btn_minus,
        )
        self.buttons = (
            self.w_btn_next,
            self.w_btn_pause,
            self.w_btn_stop,
            self.w_btn_plus,
            self.w_btn_minus,
        )

        self.music_path = ''
        self.musics = getattr(settings, 'musics', {})

        self.musics_map = {}

        self.media_instance = vlc.get_default_instance()
        self.player = self.media_instance.media_player_new()

        self.media = self.media_instance.media_new(u'')
        self.mediaManager = self.media.event_manager()

        self.mark5 = self.mark4 = self.mark3 = self.mark2 = 0
        self.current_play_path = u''

        # для исключения ошибки, get_position не всегда равен 1
        self._last_pos = 2

        self.worked = False

    def _nur_configure(self):
        self.w_window.protocol('WM_DELETE_WINDOW', self.end)
        self.w_label_base_path.bind('<Double-Button-1>', self.set_new_path)
        self.w_listbox_tracks.bind('<Double-Button-1>', self.select_music)

        self.w_window.minsize(
            width=settings.MAIN_WINDOW_MIN_WIDTH,
            height=settings.MAIN_WINDOW_MIN_HEIGHT)
        self.w_window.geometry(
            u'{0}x{1}+{2}+{3}'.format(
                settings.MAIN_WINDOW_WIDTH,
                settings.MAIN_WINDOW_HEIGHT,
                settings.MAIN_WINDOW_X,
                settings.MAIN_WINDOW_Y))

    def _nur_layout(self):
        rel_label_height = 0.1
        rel_btns_height = 0.1
        rel_btns_width = 1.0 / len(self.buttons)
        rel_btns_y = 1 - rel_btns_height
        rel_listbox_heigth = 1 - rel_label_height - rel_btns_height

        self.w_label_base_path.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=rel_label_height,
        )
        self.w_listbox_tracks.place(
            relx=0,
            rely=rel_label_height,
            relwidth=1,
            relheight=rel_listbox_heigth,
        )
        x = 0
        for btn in self.buttons:

            btn.place(
                relx=x,
                rely=rel_btns_y,
                relwidth=rel_btns_width,
                relheight=rel_btns_height,
            )
            x += rel_btns_width

    def start(self):
        self._nur_configure()
        self._nur_layout()
        self.set_new_path()
        self.w_window.mainloop()

    def end(self):
        self.write_settings()
        self.w_window.destroy()

    def write_settings(self):
        with open(settings.CONFIG_FILE_PATH, 'w') as f:
            json.dump({
                'MUSIC_PATH': self.music_path,
                'musics': self.musics,
                'VOLUME': self.player.audio_get_volume()
            }, f, indent=4)


    def set_new_path(self, event=None):
        if event:
            self.music_path = askdirectory(
                title=u'Выберите папку с музыкой',
                initialdir=self.music_path) or self.music_path
        else:
            self.music_path = settings.MUSIC_PATH

        self.w_label_base_path['text'] = self.music_path
        self._load_musics()

    def _get_musics(self):
        _musics = {}
        for root, dirs, files in os.walk(self.music_path):
            for fil in files:
                if fil.endswith('.mp3'):
                    file_path = os.path.join(root, fil)
                    _musics[file_path] = {
                        'file_name': fil,
                        'album': (
                            file_path
                            .replace(self.music_path, '')
                            .replace(fil, '')),
                    }
        return _musics

    def _load_musics(self):
        for mus_path, meta in self._get_musics().iteritems():
            if mus_path not in self.musics:
                self.musics[mus_path] = meta
                meta['last_positions'] = [1.0]

        self.__load_musics()

    def __load_musics(self):        
        self.musics_map = [
            (mus_path, u'{album}{file_name}'.format(**mus_meta))
            for mus_path, mus_meta in self.musics.iteritems()]
        self.musics_map.sort(key=lambda x: x[1])

        self.musics_map = [
            (item[0], 
             u'{0} - {2} - {1}'.format(
                index, 
                item[1], 
                (
                    sum(self.musics[item[0]]['last_positions'])
                    /len(self.musics[item[0]]['last_positions']))))
            for index, item in enumerate(self.musics_map)
        ]
        self.w_listbox_tracks.delete(0, END)

        self.w_listbox_tracks.insert(
            END, *(title for mus_path, title in self.musics_map))

    def select_music(self, event=None):
        self.calculate_mark()
        try:
            index = self.w_listbox_tracks.curselection()[0]
            self.current_play_path, music_title = self.musics_map[index]
        except IndexError:
            return
        else:
            self.player.stop()

            self.media = self.media_instance.media_new(self.current_play_path)
            self.mediaManager = self.media.event_manager()

            self.player.set_media(self.media)
            self.player.play()
            self.player.audio_set_volume(settings.VOLUME)
            if not self.worked:
                self.worked = True
                self.w_window.after(3000, self.after)
            # self.player.set_position(0.9)

    def btn_pause(self):
        self.player.pause()
        self.worked = not self.worked
        print self.worked
        if self.worked:
            self.w_window.after(3000, self.after)

    def btn_stop(self):
        self.player.stop()
        self.worked = False

    def btn_plus(self):
        volume = self.player.audio_get_volume()
        if volume < 100:
            self.player.audio_set_volume(volume + 10)

    def btn_minus(self):
        volume = self.player.audio_get_volume()
        if volume > 0:
            self.player.audio_set_volume(volume - 10)

    def btn_next(self):
        if not self.musics:
            return

        self.calculate_mark()

        if self.mark5 < 10:
            mark = 0.8
            self.mark5 += 1
        elif self.mark4 < 8:
            mark = 0.6
            self.mark4 += 1
        elif self.mark3 < 6:
            mark = 0.4
            self.mark3 += 1
        elif self.mark2 < 4:
            mark = 0.2
            self.mark2 += 1
        else:
            mark = 0
            self.mark5 = self.mark4 = self.mark3 = self.mark2 = 0
            self.write_settings()
            self.__load_musics()

        music_path = random.choice(
            [path for path, meta in self.musics.iteritems()
             if sum(meta['last_positions'])/len(meta['last_positions']) > mark])
        for index, music in enumerate(self.musics_map):
            if music[0] == music_path:
                break
        self.w_listbox_tracks.selection_clear(0, END)
        self.w_listbox_tracks.activate(index)
        self.w_listbox_tracks.selection_set(index)
        self.w_listbox_tracks.see(index)
        self.select_music()

    def calculate_mark(self):
        try:
            self.musics[self.current_play_path]['last_positions'].append(
                self.player.get_position())
        except KeyError:
            pass
        else:
            self.musics[self.current_play_path]['last_positions'] = (
                self.musics[self.current_play_path]['last_positions'][-10:])

    def after(self):
        pos = self.player.get_position()
        if pos in (1.0, self._last_pos):
            self.btn_next()

        self._last_pos = pos
        if self.worked:
            self.w_window.after(3000, self.after)

App().start()
