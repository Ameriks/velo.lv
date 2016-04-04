# coding=utf-8
from __future__ import unicode_literals
import re
from django.core.management.base import BaseCommand
import csv
from gallery.models import Video
from gallery.utils import youtube_video_id


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('videos.csv', 'rb') as csvfile:
            videos = csv.reader(csvfile)
            for row in videos:
                link = row[0]
                if "youtube" not in link and "youtu.be" not in link and "vimeo" not in link:
                    raise Exception("You can add only youtube and vimeo videos.")

                if "youtube" in link or "youtu.be" in link:
                    if not youtube_video_id(link):
                        raise Exception("Incorrect youtube link.")
                else:
                    video_id = re.search(r'^((http|https)://)?(www\.)?(vimeo\.com/)?(\d+)', link).group(5)
                    if not video_id:
                        raise Exception("Incorrect vimeo link.")

                instance = Video(competition_id=row[1], status=1)
                if "youtube" in link or "youtu.be" in link:
                    instance.kind = 1
                    instance.video_id = youtube_video_id(link)
                else:
                    instance.kind = 2
                    instance.video_id = re.search(r'^((http|https)://)?(www\.)?(vimeo\.com/)?(\d+)', link).group(5)

                check = Video.objects.filter(video_id=instance.video_id)
                if not check:
                    instance.save()