import os
from gallery.models import Album
import hashlib
from PIL import Image
import yaml

def sync_album(album_id):
    album = Album.objects.get(id=album_id)
    for root, _, files in os.walk(album.folder):
        for f in files:
            if f[-3:].lower() != 'jpg':
                continue
            fullpath = os.path.join(root, f)
            md5 = hashlib.md5(open(fullpath).read()).hexdigest()
            photo, created = album.photo_set.get_or_create(md5=md5, defaults={'image': fullpath[6:]})
            if not created:
                photo.image = fullpath[6:]
                photo.save()
            # else:
            #     generate_thumbnails(Photo, photo.id, 'image')


def import_legacy_albums():
    for root, folders, _ in os.walk("media/gallery/"):
        if len(folders) == 0:
            print root
            stream = open(os.path.join(root, "info.yaml"), 'r')
            data = yaml.load(stream)
            if not data.get('photographer'):
                data.update({'photographer': ''})
            print data
            stream.close()
            album, created = Album.objects.get_or_create(folder=root, defaults=data)
            if not created:
                for key in data:
                    setattr(album, key, data.get(key))
                album.save()
            sync_album(album.id)


# For legacy pictures. Sorting folders.
def replace_folder_names():
    for root, folders, _ in os.walk("fotoatteli2"):
        for folder in folders:
            f_path = os.path.join(root, folder)
            files = os.listdir(f_path)
            file_path = os.path.join(f_path, files[0])
            img = Image.open(file_path)
            exif_data = img._getexif()
            date_taken = exif_data.get(36867, None)
            if date_taken:
                dt = date_taken[0:10].replace(':', '-')
                new_folder_name = "%s_%s" % (dt, folder)
                print "rename %s to %s" % (folder, new_folder_name)
                os.rename(os.path.join(root, folder), os.path.join(root, new_folder_name))
