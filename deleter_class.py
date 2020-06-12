import re
import tkinter as tk
from tkinter import Label
import os.path
import os
import time
import random
import requests
import vk_api
import time
import sys
from tqdm import trange
import glob
import os

class Window_vk_app:
    def __init__(self, master):
        self.master = master
        self.label = Label(text='Enter user login and password')
        self.label.pack()
        self.login_entry = tk.Entry(self.master)
        
        self.password_entry = tk.Entry(self.master)
        if os.path.isfile('login_and_password.txt'):
            self.login_entry.insert(tk.END, self.get_userdata_from_file()[0])
            self.password_entry.insert(tk.END,
                                       self.get_userdata_from_file()[1])
        else:
            self.login_entry.insert(tk.END, 'enter a login here')
            self.password_entry.insert(tk.END, 'enter a password here')
        self.login_entry.pack()
        self.password_entry.pack()
        # self.detect_file()
        self.submit_login_and_password = tk.Button(self.master,
                                                   text='Remember Me',
                                                   fg='black', width=17,
                                                   command
                                                   =self.save_info)
        self.submit_login_and_password.pack()
        self.init_delete_button = tk.Button(self.master, text='Delete Likes',
                                            fg='black', width=17,
                                            command=self.delete_like_from_content)
        self.init_delete_button.pack()
        self.delete_photolike_button = tk.Button(self.master,
                                                 text='download photos',
                                                 fg='black', width=17,
                                                 command=self.download_user_saved_photos)
        self.delete_photolike_button.pack()

    def save_info(self):
        self.login = self.login_entry.get()
        self.password = self.password_entry.get()
        user_data = open('login_and_password.txt', 'a')
        user_data.write(str(self.login) + '\n' + str(self.password))

    def get_userdata_from_file(self):
        self.read_file = open('login_and_password.txt', 'r')
        self.user_data = [line.rstrip() for line in self.read_file]
        return self.user_data

    def autorization_vk(self):
        self.vk_session = vk_api.VkApi(
            token='f9cd411cd4cf479462f9ed4caca84ff29197404e7853e34d43bcaf0de4ec92e152edd12e304a7e0b37392')#token='58deb4ef05cb9468fb1c108eb24b71c17b8d880c5ad84f241e5df690bf639dd4fc21ec2f9ed3574f0d504'
        #self.vk_session.auth()
        self.vk = self.vk_session.get_api()
        self.tools = vk_api.VkTools(self.vk_session)

    def read_file_and_make_list(self):
        access_denied_group = []
        try:
            create_txt = open('access_denied_groups.txt', 'a')
            create_txt.close()
        except Exception:
            pass
        if os.stat('access_denied_groups.txt').st_size != 0:
            open_txt = open('access_denied_groups.txt', 'r')
            access_denied_group = [int(line.rstrip()) for line in open_txt]
            print('List of unacceptable groups', access_denied_group)
            open_txt.close()
        return access_denied_group

    def delete_like_from_content(self):
        self.autorization_vk()
        likes_all_info = self.tools.get_all('fave.getPosts', 10000000)
        likes_required_info = []
        for one_like_info in likes_all_info['items']:
            info = {'post_type': one_like_info['post_type'],
                    'id': one_like_info['id'],
                    'owner_id': one_like_info['owner_id']}
            likes_required_info.append(info)
        # return self.likes_required_info
        # liked_content = self.get_liked_posts()
        denied_group_list = self.read_file_and_make_list()
        denied_content_counter = 0
        like_denied_counter = 0
        for like in likes_required_info:
            if like['owner_id'] in denied_group_list:
                continue
            else:
                try:
                    self.vk.likes.delete(owner_id=like['owner_id'],
                                         item_id=like['id'],
                                         type=like['post_type'])
                    print('SUCESS')
                    time.sleep(random.randint(12, 30))

                except vk_api.exceptions.ApiError:
                    if str(like['owner_id']) not in denied_group_list:
                        denied_group_list.append(like['owner_id'])
                        self.write_access_denied_groups(like['owner_id'])
                        denied_content_counter += 1
                        continue

    def download_user_saved_photos(self):
        self.autorization_vk()
        albums = dict((album['title'],album['id']) for album in
                      self.vk.photos.getAlbums()['items'])
        if 'Already saved' not in albums:
            create_album = self.vk.photos.createAlbum(title='Already saved')
            album_id = create_album['id']
        else:
            album_id = albums['Already saved']

        likes_photo_info = self.vk.photos.get(album_id='-15', count = 1000)
        save_photo_path = '/home/greg/Pictures/VK2/{0}'
        files_in_savedir = glob.glob('/home/greg/Pictures/VK2/*')
        try:
            latest_file =max(files_in_savedir, key=os.path.getctime)
            photo_number = int(''.join(re.findall('\d', latest_file.split(
                '/')[-1])))
        except ValueError:
            photo_number = 1
        saved_photos = dict((photo['id'], [ph['url'] for ph in photo[
            'sizes'] if ph['type']== 'x' and 'w']) for photo in
                            likes_photo_info['items'])

        for id, url in saved_photos.items():
            request = requests.get(url[0])
            with open(save_photo_path.format(str(photo_number)+'.jpg'),
                      'wb') as file:
                file.write(request.content)
                photo_number+=1
            self.vk.photos.move(target_album_id = album_id, photo_id = id)


    def write_access_denied_groups(self, access_denied_group):
        wr_file = open('access_denied_groups.txt', 'a')
        wr_file.write(str(access_denied_group) + '\n')
        wr_file.close()


def main():
    root = tk.Tk()
    root.title('VK_manipulator')
    root.geometry('240x170')
    Window_vk_app(root)
    root.mainloop()


if __name__ == '__main__':
    main()
