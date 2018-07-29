import dropbox
import sys
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError
from os.path import isfile, getsize, expanduser, abspath
import logging
from hashlib import md5
from datetime import datetime

# logging.basicConfig(level=logging.DEBUG)

ACCESS_TOKEN = ""


class FlareonMediaManager:
    def __init__(self):
        self.dbx = dropbox.Dropbox(ACCESS_TOKEN)
        self.dbx.users_get_current_account()
        self.media = []

        self._dropbox_path = '/temporary/'

    def create_media_id(self):
        media_id = md5(str(datetime.now()).encode('utf-8')).hexdigest()
        return media_id

    def create_shared_link(self, dropbox_path):
        obj = self.dbx.sharing_create_shared_link(dropbox_path)
        return obj.url[:-len('dl=0')] + "raw=1"

    def get_size(self, dropbox_path):
        filesize = self.dbx.files_get_metadata(dropbox_path).size
        return filesize

    def add_media(self, filename, fp):
        """
        Uplaod file to self._dropbox_path. Returns shared link.

        """

        dropbox_path = self._dropbox_path + filename
        print("[*] Adding media <{}>...".format(filename))

        try:
            self.dbx.files_upload(
                fp.read(), dropbox_path, mode=WriteMode('overwrite'))

        except Exception:
            print("\n[*] Error. Unable to upload media.")

        media = {}
        media['name'] = filename
        media['size'] = self.get_size(self._dropbox_path + filename)
        media['url'] = self.create_shared_link(self._dropbox_path + filename)
        media['local_id'] = self.create_media_id()

        self.media.append(media)

    def remove_media(self, media_local_id):
        for media in self.media:
            if media_local_id == media['local_id']:
                self.media.pop(self.media.index(media))
                return


# class FlareonMediaManager:
#     def __init__(self):
#         self.dbx = dropbox.Dropbox(ACCESS_TOKEN)
#         self.dbx.users_get_current_account()
#         self._default_path = '/Flareon'
#         self.media = []
#         self.unique_id = 'localID_1'

    # def remove_media(self, local_id):
    #     for media in self.media:
    #         if media['local_id'] == local_id:
    #             self.media.pop(self.media.index(media))
    #             return

    # def add_media(self, file_path):
    #     file_path = expanduser(file_path)

    #     if not isfile(file_path):
    #         sys.exit("[*] Invalid file path <{}>.".format(file_path))

    #     # Set extension for the file
    #     ext = file_path.split('.')
    #     ext = None if len(ext) == 1 else file_path.split('.')[-1].upper()

    #     # Metadata
    #     name = file_path.split('/')[-1]
    #     path = abspath(file_path)

    #     # Convert filesize into fancy format
    #     size = getsize(file_path)

    #     limit = 1024
    #     n = 0
    #     display_names = {0: 'Bytes', 1: 'KB', 2: 'MB', 3: 'GB'}
    #     while size > limit:
    #         size /= limit
    #         n += 1

    #     size = "{:.2f}{}".format(size, display_names[n])

    #     media = {
    #         'name': name,
    #         'local_path': path,
    #         'extension': ext,
    #         'size': size,
    #         'shared_link': None,
    #         'local_id': self.unique_id
    #     }

    #     self.media.append(media)

    #     # update unique_id
    #     self.unique_id = 'localID_' + \
    #         str(int(self.unique_id.split('_')[1]) + 1)

    #     logging.debug('Media <{}> added.'.format(name))

    # def upload_to(self, folder_name):
    #     # Upload all files
    #     folder_name = self._default_path + '/' + folder_name

    #     for media in self.media:
    #         self._upload(media['local_path'],
    #                      folder_name + '/' + media['name'])

    #         link = self._create_shared_link(folder_name + '/' + media['name'])
    #         self.media[self.media.index(media)]['shared_link'] = link

    #     print(self.media)

    # def _create_shared_link(self, full_path):
    #     obj = self.dbx.sharing_create_shared_link(full_path, short_url=False)
    #     return obj.url[:-len('dl=0')] + "raw=1"

    # def get_file_size(self, full_path):

    # def _upload(self, local_path, dropbox_path):
    #     with open(local_path, 'rb') as fp:
    #         print("[*] Uploading the file to <{}>...".format(dropbox_path))
    #         try:
    #             self.dbx.files_upload(
    #                 fp.read(), dropbox_path, mode=WriteMode('overwrite'))

    #         except ApiError as error:
    #             if (error.error.is_path() and
    #                     error.error.get_path().error.is_insufficient_space()):
    #                 sys.exit("[*] Not enough space in the Dropbox.")
    #             elif error.user_message_text:
    #                 print(error.user_message_text)
    #                 sys.exit()
    #             else:
    #                 print(error)
    #                 sys.exit()

    # def add_media(self, filename, fp):
    #     dropbox_path = self._default_path + '/' + filename
    #     print("[*] Adding media <>...".format(filename))

    #     try:
    #         self.dbx.files_upload(
    #             fp.read(), dropbox_path, mode=WriteMode('overwrite'))

    #         link = self._create_shared_link(
    #             self._default_path + '/' + filename)
    #         return link

    #     except Exception:
    #         print("[*] Error. ")
