# -*- coding: utf-8 -*-
import os 
import datetime
import checksumdir

changelog_template = '''%(record_hash_prefix)s %(hash_str)s\n\
%(now_date)s [auto]\n\
#New version created, add comment...\n\n'''

# sha1 has of a folder
def get_sha_by_real_folder_path(path):
    return checksumdir.dirhash(path, 'sha1', excluded_files=['ChangeLog.txt'])

# define the hash logged to the ChangeLog file
def keep_hash_by_real_file_path(path, hash_str):
    now_date = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    record_hash_prefix = 'FILEHASH:'
    changelog = changelog_template % locals()
    with open(path) as f:
        first_line = f.readline()
    if hash_str in first_line:
        pass
    else:
        with open(path, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(changelog)
            f.write(content)
        print '***** Version change, please write Changelog *****'
    return
    