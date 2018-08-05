import dropbox
import sys
import os


class Flareon:
    def __init__(self):
        self.dbx = None               # Dropbox API Class

        self.dirpath = None           # directory path
        self.dbx_root_dir = None  # Root directory for Dropbox
        self.dbx_tmp_dir = None   # Temporary directory when writing draft
        self.dbx_access_token = None  # ACCESS TOKEN for Dropbox API

        self.md_files = []      # markdown files

        self.metadata = None
        self.dropbox_contents = []    # Dropbox data contents
        self.contents = None

        self.initialize()  # Set variable

    def initialize(self):
        if not self._read_config():
            sys.exit("[*] './flareon.config' is not properly set.")

        if not self._init_dropbox():
            sys.exit("[*} Access Token Error: Please check your access token.")

        # if not self._sync_dropbox():
        #     sys.exit("[*] Cannot Synchronize Dropbox.")

    def load(self):
        """
        Get file data from dirpath
        This function BOTH saves the data to self.md_files and return md_files
        """
        md_files = []

        files = os.listdir(self.dirpath)
        for file in files:
            if file.lower().endswith("flareon.md"):
                full_path = os.path.join(self.dirpath, file)

                md_file = self._load_md(full_path)

                if md_file:
                    md_files.append(md_file)

        # Sort by date, descending order
        md_files = sorted(md_files, key=lambda k: k['date'])
        md_files.reverse()

        # Create index
        for md_file in md_files:
            md_file['index'] = md_files.index(md_file)

        # Save and return
        self.md_files = md_files
        return md_files

    def _read_config(self):
        """
        Reads flareon.config file and validate the contents.the
        Returns True if everything is OK, otherwise False.
        """

        NECESSARY_KEYS = ['DIRPATH',
                          'ACCESS_TOKEN',
                          'TEMPORARY_DIR',
                          'ROOT_DIR']

        # Read flareon.config
        try:
            with open("flareon.config", 'r') as fp:
                CONFIG = {}
                for line in fp.read().split('\n'):
                    if not line.startswith('#') and len(line):
                        CONFIG[line.split('=')[0].strip()] = \
                            line.split('=')[1].strip()

            # Check necessary keys
            for key in NECESSARY_KEYS:
                if key not in CONFIG:
                    return False

            # Update data
            self.dbx_tmp_dir = CONFIG['TEMPORARY_DIR']
            self.dbx_root_dir = CONFIG['ROOT_DIR']
            self.dirpath = CONFIG['DIRPATH']
            self.dbx_access_token = CONFIG['ACCESS_TOKEN']

            # Check path
            self.dirpath = os.path.expanduser(self.dirpath)
            if not os.path.isdir(self.dirpath):
                sys.exit("[*] DIRPATH is not a valid path.")

        except Exception:
            return False

        # Otherwise return True
        return True

    def _load_md(self, file_path):
        """
        Read and validate MD file.

        Returns:
            False, if it is invalid or has wrong metadata.
            md_file <dict type>, if everything is good to go.
        """

        md_file = {
            'index': None,
            'filename': None,
            'dbx_sync_id': None,
            'date': None,
            'title': None,
            'category': None,
            'tags': None,
            'contents': None
        }

        # Check file directory
        try:
            with open(file_path, 'r') as fp:
                data = fp.read()

            md_file['filename'] = file_path.split('/')[-1]

            items = data.split("---")[1].split('\n')
            for item in items:
                if 'title' in item:
                    md_file['title'] = ":".join(item.split(':')[1:]).strip()
                    md_file['title'] = md_file['title'][1:-1]  # Remove quotes
                elif 'date' in item:
                    md_file['date'] = item.split(':')[-1].strip()
                elif 'category' in item:
                    md_file['category'] = ":".join(item.split(':')[1:]).strip()
                elif 'tags' in item:
                    _tags = ":".join(item.split(':')[1:]).strip()
                    _tags = _tags[1:-1].split(',')
                    _tags = ", ".join(list(map(lambda x: x.strip(), _tags)))
                    md_file['tags'] = _tags
                elif 'dbx_sync_id' in item:
                    md_file['dbx_sync_id'] = item.split(":")[1].strip()

            md_file['contents'] = "---".join(data.split('---')[2:]).strip()
            return md_file

        except Exception:
            print(Exception)

        return False

    def _save_md(self):
        """
        Save MD file.

        Case 1: If new file, create YYYY-MM-DD-TITLE.flareon.md format.
        Case 2: If updated, overwrite file without name change.
        """

        pass

    def _sync_dropbox(self):
        """
        Sync Dropbox media data.
        """
        pass

    def _change_dropbox_folder(self, folder_name):
        """
        Change Dropbox folder name

        Returns:
            True, if OK.
            False, otherwise.
        """
        pass

    def _init_dropbox(self):
        """
        Set Dropbox API and hook up to Internet, load current media file data.
        """
        try:
            self.dbx = dropbox.Dropbox(self.dbx_access_token)
            self.dbx.users_get_current_account()

        except Exception:
            return False

        return True

    def convert_size(self, size):
        """
        Convert to human readable file size
        """

        # If the size is 0, return 0 Byte
        if(size == 0):
            return "0 Byte"

        # Else convert the size into readable format
        limit = 1024
        n = 0
        display_names = {0: 'Bytes', 1: 'KB', 2: 'MB', 3: 'GB'}
        while size > limit:
            size /= limit
            n += 1

        size = "{:.2f} {}".format(size, display_names[n])
        return size
