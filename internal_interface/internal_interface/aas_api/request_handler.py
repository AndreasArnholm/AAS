from io import BytesIO
import sys
sys.path.insert(0, "..")
import logging
import asyncio

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from opcua import ua, Server, uamethod
from .models import Robot
import json

from cv2 import cv2 as cv
import numpy as np

class RequestMiddleware:
    def __init__(self, get_response):
        self.main()
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        
        try:
            print(response.data['command'])

            command_splt = response.data['command'].split(":")

            if command_splt[0] == "lbr":
                self.lbrEvgen.event.Message = ua.LocalizedText(command_splt[1])
                self.lbrEvgen.trigger()
                print("LBREvent sent!")
            elif command_splt[0] == "kmp":
                self.kmpEvgen.event.Message = ua.LocalizedText(command_splt[1])
                self.kmpEvgen.trigger()
                print("KMPEvent sent!")

        except (KeyError, AttributeError) as e:
            pass

        return response

    @uamethod
    def update_status(self, parent, msg):
        loop = asyncio.get_running_loop()
        loop.create_task(self.update_database(msg))
        loop.create_task(self.send_async(msg))

    async def update_database(self, msg):
        rid, robot, component, component_status = msg.split(':')
        print(component, bool(int(component_status)))
        obj, created = await sync_to_async(Robot.objects.update_or_create)(
            id=rid, name=robot,
            defaults={component: bool(int(component_status))}
        )

    async def send_async(self, msg):
        rid, robot, component, component_status = msg.split(':')

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            'status_update',
            {
                'type': 'send_to_aas',
                'rid' : rid,
                'robot' : robot,
                'component' : component,
                'component_status' : bool(int(component_status))
            }
        )  

    @uamethod
    def receive_image(self, parent, bytes):        
        frame = BytesIO(bytes)
        loaded_frame = np.load(frame, allow_pickle=True)

        cv.imshow("WINDOW", loaded_frame)
        cv.waitKey(3)

    def main(self):
        logging.basicConfig(level=logging.WARN)
        logger = logging.getLogger("opcua.server.internal_subscription")
        #logger.setLevel(logging.DEBUG)

        # setup our server with IP of the computer running the internal_interface

        with open("config.json", "r") as f:
            ip_dict = json.load(f)

        server = Server()
        server.set_endpoint("opc.tcp://" + ip_dict["OPCUA_URL"] + "/freeopcua/server/")

        # setup our own namespace, not really necessary but should as spec
        uri = "OPCUA_AAS_COMMUNICATION_SERVER"
        idx = server.register_namespace(uri)

        # get Objects node, this is where we should put our custom stuff
        objects = server.get_objects_node()

        # populating our address space
        myobj = objects.add_object(idx, "MyObject")
        status_node = myobj.add_method(idx, "update_status", self.update_status, [ua.VariantType.String], [ua.VariantType.Int64])
        print(status_node)
        image_node = myobj.add_method(idx, "update_frame", self.receive_image)
        
        lbrEvent = server.create_custom_event_type(idx, 'LBREvent')
        kmpEvent = server.create_custom_event_type(idx, 'KMPEvent')

        self.lbrEvgen = server.get_event_generator(lbrEvent, myobj)
        self.kmpEvgen = server.get_event_generator(kmpEvent, myobj)

        # starting!
        server.start()