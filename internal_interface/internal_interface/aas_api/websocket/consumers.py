import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class UpdateConsumer(WebsocketConsumer):
    def connect(self):
        #self.room_name = 'status'
        self.room_group_name = 'status_update'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        self.close()
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))

    def send_to_aas(self, event):
        print("Send_to_aas called")
        
        rid = event['rid']
        robot = event['robot']
        component = event['component']
        component_status = event['component_status']
        self.send(text_data=json.dumps({
            'rid' : rid,
            'robot' : robot,
            'component' : component,
            'component_status' : component_status
        }))

class StreamConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'stream_update'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        self.close()
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def send_frame(self, event):
        frame = event['frame']
        self.send(frame)