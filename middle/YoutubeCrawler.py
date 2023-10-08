from dataclasses import dataclass
from typing import List, Optional
import requests
from urllib.parse import urlencode
import json

@dataclass
class YoutubeSearchVideoInfo:
    id: str
    thumbnails: List[dict]
    url: str
    title: str
    published_time_ago: Optional[str]
    view_count: int
    formatted_view_count: int
    description: Optional[str]
    duration: int
    formatted_duration: str
    formatted_readable_duration: str
    author: dict

    def get_properties(self):
        return {
            'id': self.id,
            'thumbnails': self.thumbnails,
            'url': self.url,
            'title': self.title,
            'published_time_ago': self.published_time_ago,
            'view_count': self.view_count,
            'formatted_view_count': self.formatted_view_count,
            'description': self.description,
            'duration': self.duration,
            'formatted_duration': self.formatted_duration,
            'formatted_readable_duration': self.formatted_readable_duration,
            'author': self.author,
        }

class YoutubeSearchResults:
    def __init__(self, json):
        self.json = json

    def get_estimated_results(self):
        return int(self.json['estimatedResults'])

    @property
    def videos(self):
        return self._get_videos()

    def video(self, index):
        return self._get_videos(1, index)[0] if self._get_videos(1, index) else None

    def videos_from(self, index=0, limit=None):
        return self.video(index) if limit == 1 else self._get_videos(limit, index)

    def _get_videos(self, limit=None, start=0):
        arr = []

        videos = self.json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']

        for data in (videos[start:limit+start] if limit else videos[start:]):
            video = data.get('videoRenderer')

            if video:
                raw_view_count = video.get('viewCountText', {}).get('simpleText', '').split(" ")[0] or video.get('viewCountText', {}).get('runs', [{}])[0].get('text')
                formatted_duration = video.get('lengthText', {}).get('simpleText', '0')
                formatted_readable_duration = video.get('lengthText', {}).get('accessibility', {}).get('accessibilityData', {}).get('label', '0')
                formatted_view_count = video.get('shortViewCountText', {}).get('simpleText') or video.get('shortViewCountText', {}).get('runs', [{}])[0].get('text')

                arr.append(YoutubeSearchVideoInfo(
                    url = "https://www.youtube.com/watch?v=" + video['videoId'],
                    id = video['videoId'],
                    thumbnails = video['thumbnail']['thumbnails'],
                    title = video['title']['runs'][0]['text'],
                    author = {
                        'name': video['ownerText']['runs'][0]['text'],
                        'id': video['ownerText']['runs'][0]['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url'].split("/")[-1],
                        'thumbnails': video['channelThumbnailSupportedRenderers']['channelThumbnailWithLinkRenderer']['thumbnail']['thumbnails']
                    },
                    view_count = int(raw_view_count.replace(',', '')) if raw_view_count else 0,
                    published_time_ago = video.get('publishedTimeText', {}).get('simpleText'),
                    formatted_duration = formatted_duration,
                    formatted_readable_duration = formatted_readable_duration,
                    formatted_view_count = formatted_view_count,
                    description = "".join([e['text'] for e in video.get('detailedMetadataSnippets', [{}])[0].get('snippetText', {}).get('runs', [])]),
                    duration = sum([int(d) * (1000 if y == 0 else 60000 if y == 1 else 3600000 if y == 2 else 86400000 if y == 3 else 0) for y, d in enumerate(reversed(formatted_duration.split(":")))]) if formatted_duration != '0' else 0
                ))

        return arr

def get_between(body, one, two):
    try:
        return body.split(one)[1].split(two)[0]
    except IndexError:
        return None
    
def json_parser(read_data):
    try:
        return json.loads(read_data)
    except json.JSONDecodeError:
        index = read_data.rfind("}")
        read_data = read_data[:index+1]
        try:
            return json.loads(read_data)
        except json.JSONDecodeError:
            read_data += "}"
            return json.loads(read_data)

async def search(manager, query):
    params = {
        'search_query': query,
        'hl': 'en'
    }

    try:
        response = await manager.request(method="GET", url=f"https://www.youtube.com/results?{urlencode(params)}", get="text")
    except requests.RequestException:
        return None

    try:
        json_string = get_between(response, 'var ytInitialData = ', ';</script>')
        json = json_parser(json_string)
        return YoutubeSearchResults(json)
    except Exception as error:
        return None
