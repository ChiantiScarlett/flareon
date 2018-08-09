import sys
import os
import dropbox
from dropbox.files import WriteMode
from datetime import datetime
from hashlib import md5


class MarkdownFile:
    def __init__(self, local_path, dbx_tmp_dir, filename=None, index=None):
        self.index = index
        self.local_path = local_path
        self.filename = filename
        self.title = None  # "LOREM IPSUM"
        self.date = None  # YYYY-MM-DD
        self.tags = ''  # str
        self.dbx_sync_id = dbx_tmp_dir  # Unique ID
        self.contents = ''  # Actual markdown data
        self.dbx_files = []

        # Let it auto reads the file when initialized
        self.read_file()

    def read_file(self):
        if not self.filename:
            return

        full_path = self.local_path + '/' + self.filename
        with open(full_path, 'r') as fp:
            data = fp.read()

        items = data.split("---")[1].split('\n')
        for item in items:
            if 'title' in item:
                self.title = ":".join(item.split(':')[1:]).strip()
                self.title = self.title[1:-1]  # Remove quotes
            elif 'date' in item:
                self.date = item.split(':')[-1].strip()
            elif 'category' in item:
                self.category = ":".join(item.split(':')[1:]).strip()
            elif 'tags' in item:
                _tags = ":".join(item.split(':')[1:]).strip()
                _tags = _tags[1:-1].split(',')
                _tags = ", ".join(list(map(lambda x: x.strip(), _tags)))
                self.tags = _tags
            elif 'dbx_sync_id' in item:
                self.dbx_sync_id = item.split(":")[1].strip()

        self.contents = "---".join(data.split('---')[2:]).strip()

    def save_file(self, md_data):
        _parts = ["---",
                  'layout: post',
                  'title: "{title}"',
                  'date: {date}',
                  'category: {category}',
                  'tags: [{tags}]',
                  'dbx_sync_id: {dbx_sync_id}',
                  '---',
                  '',
                  '{contents}']

        md = "\n".join(_parts).format(**md_data)

        if self.filename is None:
            self.filename = md_data['filename']
            full_path = self.local_path + '/' + md_data['filename']
            with open(full_path, 'w') as fp:
                fp.write(md)

        else:
            full_path = self.local_path + '/' + self.filename

            with open(full_path, 'w') as fp:
                fp.write(md)

            new_name = "/".join([self.local_path,
                                 md_data['filename']])
            prev_name = '/'.join([self.local_path,
                                  self.filename])
            os.rename(prev_name, new_name)

            print(new_name)
            print(prev_name)
            self.filename = new_name

        return True

    def __lt__(self, other):
        return self.date < other.date


class Flareon:
    def __init__(self):
        # Load settings
        self.load_Flareon()
        self.md_file = MarkdownFile(self._local_path, self._dbx_tmp_dir)
        self.update_dbx_files()

    def load_Flareon(self):
        # Read flareon.config file
        try:
            with open("flareon.config", 'r') as fp:
                CONFIG = {}
                for line in fp.read().split('\n'):
                    if not line.startswith('#') and len(line):
                        CONFIG[line.split('=')[0].strip()] = \
                            line.split('=')[1].strip()

            self._dbx_tmp_dir = CONFIG['TEMPORARY_DIR']
            self._dbx_root_dir = CONFIG['ROOT_DIR']
            self._local_path = CONFIG['DIRPATH']
            self._dbx_access_token = CONFIG['ACCESS_TOKEN']

        except Exception:
            sys.exit("[*] Cannot load './flareon.config'. \
                Please check if it is in right format.")

        # Validate _local_path
        self._local_path = os.path.expanduser(self._local_path)
        if self._local_path[-1] == "/":
            self._local_path = self._local_path[:-1]

        if not os.path.isdir(self._local_path):
            sys.exit("[*] DIRPATH is not a valid path.")

        # Validate ACCESS_TOKEN
        try:
            self.dbx = dropbox.Dropbox(self._dbx_access_token)
            self.dbx.users_get_current_account()
        except Exception:
            sys.exit(["[*] Cannot initialize Dropbox API. \
                Please verify your ACCESS_TOKEN."])

    def load_local_files(self):
        # Load all *.flareon.md file from self._local_path
        md_files = []
        files = os.listdir(self._local_path)
        for file in files:
            if file.lower().endswith("flareon.md"):
                index = files.index(file)
                md_file = MarkdownFile(self._local_path, self._dbx_tmp_dir,
                                       filename=file, index=index)
                md_files.append(md_file)

        md_files.sort()  # Sort by date
        md_files.reverse()  # in descending order

        # Save
        self.md_files = md_files

        # Create HTML Template
        files = []
        for md in md_files:
            file = {}
            file['index'] = md.index
            file['date'] = md.date
            file['title'] = md.title
            file['category'] = md.category
            file['tags'] = md.tags
            file['dbx_sync_id'] = md.dbx_sync_id
            files.append(file)

        return files

    def load_md(self, index):
        for md_file in self.md_files:
            if index == md_file.index:
                HTML = {}
                HTML['filename'] = md_file.filename
                HTML['index'] = md_file.index
                HTML['date'] = md_file.date
                HTML['title'] = md_file.title
                HTML['category'] = md_file.category
                HTML['tags'] = md_file.tags
                HTML['contents'] = md_file.contents
                HTML['dbx_sync_id'] = md_file.dbx_sync_id

                # Update current md file
                self.md_file = md_file
                self.md_dbx_files = []
                self.update_dbx_files()
                print(self.md_file.dbx_files)

                return HTML

    def save_md(self, md_data):
        successful = self.md_file.save_file(md_data)
        return successful, self.md_file.filename

    def update_dbx_files(self):
        dbx_path = os.path.join(self._dbx_root_dir, self.md_file.dbx_sync_id)
        total_size = 0
        total_num = 0

        self.md_file.dbx_files = []
        self.md_file.dbx_files_stat = None
        for item in self.dbx.files_list_folder(dbx_path).entries:
            file = {}
            file['name'] = item.name
            file['size'] = self._convert_size(item.size)
            file['full_path'] = self._dbx_root_dir + \
                '/' + self.md_file.dbx_sync_id + item.name

            self.md_file.dbx_files.append(file)
            total_size += item.size
            total_num += 1

        self.md_file.dbx_files_stat = '{} ({} file{})'.format(
            self._convert_size(total_size), total_num,
            '' if total_num == 1 else 's')

    def add_dbx_file(self, fp, filename):
        # If uploading first file, create new media folder
        if self.md_file.dbx_sync_id == self._dbx_tmp_dir:
            self.md_file.dbx_sync_id = self._create_dbx_sync_id()

        # Upload file
        dropbox_path = os.path.join(self._dbx_root_dir,
                                    self.md_file.dbx_sync_id)
        print("[*] Adding media <{}>...".format(filename))

        if True:
            self.dbx.files_upload(
                fp.read(), dropbox_path + '/' + filename,
                mode=WriteMode('overwrite'))

            self.update_dbx_files()
            return True

        # except Exception:
            # print("[*] Error. Unable to upload file.")

        # return False

    def remove_dbx_file(self, filename):
        try:
            full_path = "/".join([self._dbx_root_dir,
                                  self.md_file.dbx_sync_id,
                                  filename])
            self.dbx.files_delete(full_path)
            self.update_dbx_files()
            return True

        except Exception:
            print('[*] Unable to remove file.')
            return False

    def create_file_link(self, filename):
        if True:
            full_path = "/".join([self._dbx_root_dir,
                                  self.md_file.dbx_sync_id,
                                  filename])
            print(full_path)
            url = self.dbx.sharing_create_shared_link(full_path).url

            # If it is an image file, fabricate into MD view type.
            if filename.split('.')[-1].lower() in ['png',
                                                   'jpg',
                                                   'jpeg',
                                                   'gif']:
                url = url[:-len('dl=0')] + "raw=1"
                text = '![{}]({})'.format(filename, url)
            else:
                text = '[DESC]({})'.format(url)

            return True, text

        # except Exception:
            print("[*] Unable to create file link.")
            return False, None

    def _create_dbx_sync_id(self):
        media_id = md5(str(datetime.now()).encode('utf-8')).hexdigest()
        return media_id

    def _convert_size(self, filesize):
        # filesize = self.dbx.files_get_metadata(dropbox_path).size

        # If the size is 0, return 0 Byte
        if(filesize == 0):
            return "0 Byte"

        # Else convert the filesize into readable format
        limit = 1024
        n = 0
        display_names = {0: 'Bytes', 1: 'KB', 2: 'MB', 3: 'GB'}
        while filesize > limit:
            filesize /= limit
            n += 1

        filesize = "{:.2f} {}".format(filesize, display_names[n])
        return filesize
