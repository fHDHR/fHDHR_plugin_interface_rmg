from flask import Response, request
from io import BytesIO
import xml.etree.ElementTree

from fHDHR.tools import sub_el


class RMG_Devices_Probe():
    endpoints = ["/rmg/devices/probe"]
    endpoint_name = "rmg_devices_probe"
    endpoint_methods = ["GET", "POST"]
    endpoint_parameters = {
                            "uri": {
                                    "default": "<base_url>"
                                    }
                            }

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def __call__(self, *args):
        return self.handler(*args)

    def handler(self, *args):
        """Probes a specific URI for a network device, and returns a device, if it exists at the given URI."""

        base_url = request.url_root[:-1]

        uri = request.args.get('uri', default=None, type=str)

        out = xml.etree.ElementTree.Element('MediaContainer')
        out.set('size', str(len(self.fhdhr.origins.list_origins)))

        for origin_name in self.fhdhr.origins.list_origins:

            if uri == "%s/rmg/%s%s" % (base_url, self.fhdhr.config.dict["main"]["uuid"], origin_name):

                if self.fhdhr.origins.get_origin_property(origin_name, "setup_success"):
                    alive_status = "alive"
                else:
                    alive_status = "dead"

                sub_el(out, 'Device',
                       key="%s%s" % (self.fhdhr.config.dict["main"]["uuid"], origin_name),
                       make=self.fhdhr.config.dict["rmg"]["reporting_manufacturer"],
                       model=self.fhdhr.config.dict["rmg"]["reporting_model"],
                       modelNumber=self.fhdhr.config.internal["versions"]["fHDHR"],
                       protocol="livetv",
                       status=alive_status,
                       title="%s %s" % (self.fhdhr.config.dict["fhdhr"]["friendlyname"], origin_name),
                       tuners=str(self.fhdhr.origins.get_origin_property(origin_name, "tuners")),
                       uri="%s/rmg/%s%s" % (base_url, self.fhdhr.config.dict["main"]["uuid"], origin_name),
                       uuid="device://tv.plex.grabbers.fHDHR/%s%s" % (self.fhdhr.config.dict["main"]["uuid"], origin_name),
                       thumb="favicon.ico",
                       interface='network'
                       )

        fakefile = BytesIO()
        fakefile.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        fakefile.write(xml.etree.ElementTree.tostring(out, encoding='UTF-8'))
        device_xml = fakefile.getvalue()

        return Response(status=200,
                        response=device_xml,
                        mimetype='application/xml')
