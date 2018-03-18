# coding: utf-8
from __future__ import unicode_literals

import re

from .brightcove import BrightcoveNewIE
from ..utils import update_url_query


class SevenPlusIE(BrightcoveNewIE):
    IE_NAME = '7plus'
    _VALID_URL = r'https?://(?:www\.)?7plus\.com\.au/(?P<path>[^?]+\?.*?\bepisode-id=(?P<id>[^&#]+))'
    _TESTS = [{
        'url': 'https://7plus.com.au/BEAT?episode-id=BEAT-001',
        'info_dict': {
            'id': 'BEAT-001',
            'ext': 'mp4',
            'title': 'S1 E1 - Help / Lucy In The Sky With Diamonds',
            'description': 'md5:37718bea20a8eedaca7f7361af566131',
            'uploader_id': '5303576322001',
            'upload_date': '20171031',
            'timestamp': 1509440068,
        },
        'params': {
            'format': 'bestvideo',
            'skip_download': True,
        }
    }, {
        'url': 'https://7plus.com.au/MDAY?episode-id=MDAY5-001',
        'info_dict': {
            'id': 'MDAY5-001',
            'ext': 'mp4',
            'title': 'S5 E1 - Invisible Killer',
            'description': 'md5:bea06aef0fe4bdefb2dce2e6af873fab',
            'uploader_id': '5303576322001',
            'upload_date': '20180219',
            'timestamp': 1519012651,
            'series': 'Air Crash Investigations',
        },
        'params': {
            'format': 'bestvideo',
            'skip_download': True,
        }
    }, {
        'url': 'https://7plus.com.au/UUUU?episode-id=AUMS43-001',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        path, episode_id = re.match(self._VALID_URL, url).groups()

        media = self._download_json(
            'https://videoservice.swm.digital/playback', episode_id, query={
                'appId': '7plus',
                'deviceType': 'web',
                'platformType': 'web',
                'accountId': 5303576322001,
                'referenceId': 'ref:' + episode_id,
                'deliveryId': 'csai',
                'videoType': 'vod',
            })['media']

        for source in media.get('sources', {}):
            src = source.get('src')
            if not src:
                continue
            source['src'] = update_url_query(src, {'rule': ''})

        info = self._parse_brightcove_metadata(media, episode_id)

        content = self._download_json(
            'https://component-cdn.swm.digital/content/' + path,
            episode_id, headers={
                'market-id': 4,
            }, fatal=False) or {}
        for item in content.get('items', {}):
            if item.get('componentData', {}).get('componentType') == 'infoPanel':
                for src_key, dst_key in [('title', 'title'), ('shortSynopsis', 'description')]:
                    value = item.get(src_key)
                    if value:
                        info[dst_key] = value

        webpage = self._download_webpage(url, episode_id)
        info['series'] = self._search_regex(r'<title>(.+?) +\| +7 ?[pP]lus ?</title>', webpage, 'title', fatal=False)

        return info
