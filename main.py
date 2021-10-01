import spotipy

from os import path, environ
from loguru import logger
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from yandex_music import Client

base = path.abspath(path.dirname(__file__))

if path.exists('.env'):
    load_dotenv('.env')


class YandexMusicClient:
    def __init__(self):
        self.ya_music_client = Client.from_token(environ.get('YANDEX_TOKEN'))

    def get_track_id(self, track_name):
        try:
            logger.debug(f'[Yandex Music] get track id with name --> {track_name}')
            search_result = self.ya_music_client.search(track_name)
            if search_result:
                track_id = search_result.best.result.id
                logger.debug(f'[Yandex Music] return track id --> {track_id}')
                return track_id
        except Exception as e:
            logger.exception(e)

    def save_track(self, track_id):
        result = self.ya_music_client.users_likes_tracks_add(track_id)
        logger.debug(f'[Yandex Music] save track with id --> {track_id}, result --> {result}')


class SpotifyClient:
    def __init__(self):
        self.spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=environ.get('SPOTIFY_APP_CLIENT_ID'),
                                                                        client_secret=environ.get(
                                                                            'SPOTIFY_APP_CLIENT_SECRET'),
                                                                        redirect_uri=environ.get(
                                                                            'SPOTIFY_APP_REDIRECT_URI'),
                                                                        scope="user-library-read"))

    def get_current_user_saved_tracks(self):
        track_results = self.spotify_client.current_user_saved_tracks()
        while track_results['next']:
            track_results = self.spotify_client.next(track_results)
            for item in track_results['items']:
                track = item['track']
                track_artist_name = track['artists'][0]['name']
                track_name = track['name']
                logger.debug(f'[Spotify] return track --> {track_artist_name} - {track_name}')
                yield f'{track_artist_name} - {track_name}'


def main():
    try:
        spotify_client = SpotifyClient()
        yandex_music_client = YandexMusicClient()
        spotify_saved_tracks = spotify_client.get_current_user_saved_tracks()
        for sp_track in spotify_saved_tracks:
            ya_music_track_id = yandex_music_client.get_track_id(sp_track)
            if ya_music_track_id:
                yandex_music_client.save_track(ya_music_track_id)
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    main()
