from flask import Response
from io import BytesIO
import xml.etree.ElementTree

from fHDHR.tools import sub_el, channel_sort


class RMG_Devices_DeviceKey_Channels():
    endpoints = ["/rmg/devices/<devicekey>/channels"]
    endpoint_name = "rmg_devices_devicekey_channels"
    endpoint_methods = ["GET"]

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, devicekey, *args):
        return self.get(devicekey, *args)

    def get(self, devicekey, *args):
        """Returns the current channels."""

        out = xml.etree.ElementTree.Element('MediaContainer')

        if devicekey.startswith(self.fhdhr.config.dict["main"]["uuid"]):
            origin_name = devicekey.split(self.fhdhr.config.dict["main"]["uuid"])[-1]
            out.set('size', str(self.fhdhr.origins.origins_dict[origin_name].channels.count_channels))

            channelslist = {}
            for fhdhr_channel_id in self.fhdhr.origins.origins_dict[origin_name].channels.list_channel_ids:
                channel_obj = self.fhdhr.origins.origins_dict[origin_name].channels.get_channel_obj("id", fhdhr_channel_id)
                if channel_obj:
                    if channel_obj.enabled:
                        channelslist[channel_obj.number] = channel_obj

            # Sort the channels
            sorted_channel_list = channel_sort(list(channelslist.keys()))
            for channel in sorted_channel_list:

                channel_obj = channelslist[channel]

                sub_el(out, 'Channel',
                       drm="0",
                       channelIdentifier="id://%s" % channel_obj.number,
                       name=channel_obj.dict["name"],
                       origin_name=channel_obj.dict["callsign"],
                       number=str(channel_obj.number),
                       type="tv",
                       # TODO param
                       signalStrength="100",
                       signalQuality="100",
                       )

        fakefile = BytesIO()
        fakefile.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        fakefile.write(xml.etree.ElementTree.tostring(out, encoding='UTF-8'))
        device_xml = fakefile.getvalue()

        return Response(status=200,
                        response=device_xml,
                        mimetype='application/xml')
