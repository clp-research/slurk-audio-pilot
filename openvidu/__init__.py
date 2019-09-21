import logging
import base64
from datetime import datetime
from json import JSONDecodeError

import requests
import json


class OpenViduException(Exception):
    def __init__(self, status_code, error):
        if error:
            try:
                super().__init__('{}: {}'.format(status_code, json.loads(error)['message']))
            except (KeyError, JSONDecodeError):
                super().__init__('{}: {}'.format(status_code, error))
        else:
            super().__init__('{}: Unknown error'.format(status_code))


class Connection:
    def __init__(self, server, session_id, data):
        self.server = server
        self.session_id = session_id
        self._data = data

    def __repr__(self):
        return str({
            "id": self.id,
            "created_at": str(self.created_at),
            "location": self.location,
            "platform": self.platform,
            "role": self.role,
            "client_data": self.client_data,
            "server_data": self.server_data,
            "token": self.token,
            "publishers": self.publishers,
            "subscribers": self.subscribers,
        })

    @property
    def logger(self):
        return logging.getLogger('openvidu.Connection')

    @property
    def id(self):
        return self._data['connectionId']

    @property
    def created_at(self):
        return datetime.utcfromtimestamp(self._data['createdAt'] / 1000)

    @property
    def location(self):
        return self._data.get('location')

    @property
    def platform(self):
        return self._data['platform']

    @property
    def role(self):
        return self._data['role']

    @property
    def client_data(self):
        return self._data.get('clientData')

    @property
    def server_data(self):
        return self._data.get('serverData')

    @property
    def token(self):
        return self._data['token']

    @property
    def publishers(self):
        return self._data.get('publishers')

    @property
    def subscribers(self):
        return self._data.get('subscribers')

    def disconnect(self):
        response = requests.post('{}/api/sessions/{}/connection/{}'.format(self.server.url, self.session_id, self.id),
                                 verify=self.server.verify,
                                 headers=self.server.request_headers
                                 )

        if response.status_code == 204:
            self.logger.info('Connection `%s` closed', self.id)
        elif response.status_code == 400:
            raise OpenViduException(response.status_code, 'Session `{}` does not exist'.format(self.session_id))
        elif response.status_code == 404:
            raise OpenViduException(response.status_code, 'Connection `{}` does not exist'.format(self.id))
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))


class Token:
    def __init__(self, data):
        self._data = data

    def __repr__(self):
        return str({
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "data": self.data,
            "video_min_send_bandwith": self.video_min_send_bandwith,
            "video_max_send_bandwith": self.video_max_send_bandwith,
            "video_min_recv_bandwith": self.video_min_recv_bandwith,
            "video_max_recv_bandwith": self.video_max_recv_bandwith,
        })

    @property
    def id(self):
        return self._data['id']

    @property
    def session_id(self):
        return self._data['session']

    @property
    def role(self):
        return self._data['role']

    @property
    def data(self):
        return self._data['data']

    @property
    def video_min_send_bandwith(self):
        return self._data['kurentoOptions']['videoMinSendBandwidth']

    @property
    def video_max_send_bandwith(self):
        return self._data['kurentoOptions']['videoMaxSendBandwidth']

    @property
    def video_min_recv_bandwith(self):
        return self._data['kurentoOptions']['videoMinRecvBandwidth']

    @property
    def video_max_recv_bandwith(self):
        return self._data['kurentoOptions']['videoMaxRecvBandwidth']


class Recording:
    def __init__(self, server, id, _data=None):
        self.server = server

        if _data:
            self._data = _data
        else:
            self.update(id)

    def __repr__(self):
        return str({
            "id": self.id,
            "session_id": self.session_id,
            "name": self.name,
            "output_mode": self.output_mode,
            "has_audio": self.has_audio,
            "has_video": self.has_video,
            "recording_layout": self.recording_layout,
            "custom_layout": self.custom_layout,
            "created_at": str(self.created_at),
            "size": self.size,
            "duration": self.duration,
            "url": self.url,
            "status": self.status,
        })

    @property
    def logger(self):
        return logging.getLogger('openvidu.Connection')

    @property
    def id(self):
        return self._data['id']

    @property
    def session_id(self):
        return self._data['session_id']

    @property
    def name(self):
        return self._data['name']

    @property
    def output_mode(self):
        return self._data['outputMode']

    @property
    def has_audio(self):
        return self._data['hasAudio']

    @property
    def has_video(self):
        return self._data['hasVideo']

    @property
    def recording_layout(self):
        return self._data.get('recordingLayout')

    @property
    def custom_layout(self):
        return self._data.get('customLayout')

    @property
    def resolution(self):
        return self._data.get('resolution')

    @property
    def created_at(self):
        return datetime.utcfromtimestamp(self._data['createdAt'] / 1000)

    @property
    def size(self):
        size = self._data['size']
        if size == 0:
            return None
        else:
            return size

    @property
    def duration(self):
        duration = self._data['duration']
        if duration == 0:
            return None
        else:
            return duration

    @property
    def url(self):
        return self._data.get('url')

    @property
    def status(self):
        return self._data.get('status')

    def update(self, _id=None):
        if not _id:
            _id = self.id

        response = requests.get('{}/api/recordings/{}'.format(self.server.url, _id),
                                verify=self.server.verify,
                                headers=self.server.request_headers,
                                )

        if response.status_code == 200:
            self._data = response.json()
        elif response.status_code == 404:
            raise OpenViduException(response.status_code, 'Recording `{}` does not exist'.format(_id))
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))

    def stop_recording(self):
        response = requests.post('{}/api/recordings/stop/{}'.format(self.server.url, self.id),
                                 verify=self.server.verify,
                                 headers=self.server.request_headers
                                 )

        if response.status_code == 200:
            self.logger.info('Recording of session `%s` stopped', self.id)
            self._data = response.json()
        elif response.status_code == 404:
            raise OpenViduException(response.status_code, 'Recording `{}` does not exist'.format(self.id))
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))


class Session:
    def __init__(self, server, id, _data=None):
        self.server = server

        if _data:
            self._data = _data
        else:
            self.update(id)

    def __repr__(self):
        return str({
            "id": self.id,
            "created_at": str(self.created_at),
            "media_mode": self.media_mode,
            "recording": self.recording,
            "recording_mode": self.recording_mode,
            "default_output_mode": self.default_output_mode,
            "default_recording_layout": self.default_recording_layout,
            "default_custom_layout": self.default_custom_layout,
            "custom_session_id": self.custom_session_id,
            "connections": str(self.connections),
        })

    @property
    def logger(self):
        return logging.getLogger('openvidu.Session')

    @property
    def id(self):
        return self._data['sessionId']

    @property
    def created_at(self):
        return datetime.utcfromtimestamp(self._data['createdAt'] / 1000)

    @property
    def media_mode(self):
        return self._data['mediaMode']

    @property
    def recording(self):
        return self._data['recording']

    @property
    def recording_mode(self):
        return self._data['recordingMode']

    @property
    def default_output_mode(self):
        return self._data['defaultOutputMode']

    @property
    def default_recording_layout(self):
        return self._data.get('defaultRecordingLayout')

    @property
    def default_custom_layout(self):
        return self._data.get('defaultCustomLayout')

    @property
    def custom_session_id(self):
        custom_session_id = self._data.get('customSessionId')
        if custom_session_id and custom_session_id != '':
            return custom_session_id
        else:
            return None

    @property
    def connections(self):
        return [Connection(self.server, self.id, connection) for connection in self._data['connections']['content']]

    def update(self, _id=None):
        if not _id:
            _id = self.id

        response = requests.get('{}/api/sessions/{}'.format(self.server.url, _id),
                                verify=self.server.verify,
                                headers=self.server.request_headers,
                                )

        if response.status_code == 200:
            self._data = response.json()
        elif response.status_code == 404:
            raise OpenViduException(response.status_code, 'Session `{}` does not exist'.format(_id))
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))

    def close(self):
        response = requests.delete('{}/api/sessions/{}'.format(self.server.url, self.id),
                                   verify=self.server.verify,
                                   headers=self.server.request_headers,
                                   )

        if response.status_code == 204:
            self.logger.info('Session `%s` has been closed', self.id)
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))

    def generate_token(self, role: str = None, data: str = None, video_min_send_bandwidth: int = 0,
                       video_max_send_bandwidth: int = 0, video_min_recv_bandwidth: int = 0,
                       video_max_recv_bandwidth: int = 0, allowed_filters=None) -> Token:
        if not allowed_filters:
            allowed_filters = []

        response = requests.post('{}/api/tokens'.format(self.server.url),
                                 verify=self.server.verify,
                                 headers=self.server.request_headers,
                                 data=json.dumps({
                                     "session": self.id,
                                     "role": role,
                                     "data": data,
                                     "kurentoOptions": json.dumps({
                                         "videoMinSendBandwidth": video_min_send_bandwidth,
                                         "videoMaxSendBandwidth": video_max_send_bandwidth,
                                         "videoMinRecvBandwidth": video_min_recv_bandwidth,
                                         "videoMaxRecvBandwidth": video_max_recv_bandwidth,
                                         "allowedFilters": allowed_filters,
                                     }),
                                 })
                                 )

        if response.status_code == 200:
            data = response.json()
            self.logger.info('Token created: `%s`', data['id'])
            return Token(data)
        elif response.status_code == 404:
            raise OpenViduException(response.status_code, 'Session `{}` does not exist'.format(self.id))
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))

    def unpublish(self, stream):
        response = requests.post('{}/api/sessions/{}/stream/{}'.format(self.server.url, self.id, stream),
                                 verify=self.server.verify,
                                 headers=self.server.request_headers
                                 )

        if response.status_code == 204:
            self.logger.info('Stream `%s` unpublished', stream)
        elif response.status_code == 400:
            raise OpenViduException(response.status_code, 'Session `{}` does not exist'.format(self.id))
        elif response.status_code == 404:
            raise OpenViduException(response.status_code, 'Stream `{}` does not exist'.format(stream))
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))

    def start_recording(self, name: str = None, output_mode='COMPOSED', has_audio=True, has_video=True,
                        recording_layout='BEST_FIT', custom_layout: str = None, resolution: str = None) -> Recording:
        response = requests.post('{}/api/recordings/start'.format(self.server.url),
                                 verify=self.server.verify,
                                 headers=self.server.request_headers,
                                 data=json.dumps({
                                     "session": self.id,
                                     "name": name,
                                     "outputMode": output_mode,
                                     "hasAudio": has_audio,
                                     "hasVideo": has_video,
                                     "recordingLayout": recording_layout,
                                     "customLayout": custom_layout,
                                     "resolution": resolution,
                                 })
                                 )

        if response.status_code == 200:
            self.logger.info('Recording of session `%s` started', self.id)
            return Recording(self.server, None, _data=response.json())
        elif response.status_code == 422:
            raise OpenViduException(response.status_code, '`resolution` exceeds accaptable values')
        elif response.status_code == 404:
            raise OpenViduException(response.status_code, 'Session `{}` does not exist'.format(self.id))
        elif response.status_code == 406:
            raise OpenViduException(response.status_code,
                                    'Session `{}` does not have connected participants'.format(self.id))
        elif response.status_code == 409:
            raise OpenViduException(response.status_code,
                                    'Session `{}` is not configured for using MediaMode ROUTED or it is already being recorded'.format(
                                        self.id))
        elif response.status_code == 501:
            raise OpenViduException(response.status_code, 'OpenVidu Server recording module is disabled')
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))


class Server:
    def __init__(self, url, secret, verify=True):
        self.url = url
        self.verify = verify
        self._auth_token = base64.b64encode(bytes('OPENVIDUAPP:' + secret, 'utf8')).decode('utf8')

        response = requests.get('{}/config'.format(self.url),
                                verify=self.verify,
                                headers=self.request_headers
                                )

        if response.status_code == 200:
            self._config = response.json()
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))

    def __repr__(self):
        return str({
            "url": self.url,
            "version": self.version,
            "public_url": self.public_url,
            "cdr": self.cdr,
            "min_send_bandwidth": self.min_send_bandwidth,
            "max_send_bandwidth": self.max_send_bandwidth,
            "min_recv_bandwidth": self.min_recv_bandwidth,
            "max_recv_bandwidth": self.max_recv_bandwidth,
            "recording": self.recording,
            "webhook": self.webhook,
        })

    @property
    def logger(self):
        return logging.getLogger('openvidu.Server')

    @property
    def version(self):
        return self._config['version']

    @property
    def public_url(self):
        return self._config['openviduPublicurl']

    @property
    def cdr(self):
        return self._config['openviduCdr']

    @property
    def min_send_bandwidth(self):
        return self._config['minSendBandwidth']

    @property
    def max_send_bandwidth(self):
        return self._config['maxSendBandwidth']

    @property
    def min_recv_bandwidth(self):
        return self._config['minRecvBandwidth']

    @property
    def max_recv_bandwidth(self):
        return self._config['maxRecvBandwidth']

    @property
    def recording(self):
        return self._config['openviduRecording']

    @property
    def webhook(self):
        return self._config['openviduWebhook']

    @property
    def request_headers(self) -> dict:
        return {
            "Authorization": 'Basic ' + self._auth_token,
            "Content-Type": 'application/json',
        }

    def initialize_session(self, custom_session_id: str = None, media_mode='ROUTED', recording_mode='MANUAL',
                           default_output_mode='COMPOSED', default_recording_layout='BEST_FIT',
                           default_custom_layout=''):
        response = requests.post('{}/api/sessions'.format(self.url),
                                 verify=self.verify,
                                 headers=self.request_headers,
                                 data=json.dumps({
                                     "mediaMode": media_mode,
                                     "recordingMode": recording_mode,
                                     "customSessionId": custom_session_id,
                                     "defaultOutputMode": default_output_mode,
                                     "defaultRecordingLayout": default_recording_layout,
                                     "defaultCustomLayout": default_custom_layout,
                                 })
                                 )

        if response.status_code == 200:
            id = response.json()['id']
            self.logger.info('Created new session `%s`', id)
            return Session(self, id)
        elif response.status_code == 409:
            id = custom_session_id
            self.logger.info('Using existing session `%s`', id)
            return Session(self, id)
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))

    @property
    def get_sessions(self):
        response = requests.get('{}/api/sessions'.format(self.url),
                                verify=self.verify,
                                headers=self.request_headers
                                )

        if response.status_code == 200:
            return [Session(self, session['sessionId'], _data=session) for session in response.json()['content']]
        else:
            raise OpenViduException(response.status_code, response.content.decode('utf-8'))
