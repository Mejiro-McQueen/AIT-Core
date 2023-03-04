from bifrost.common.service import Service
from bifrost.common.loud_exception import with_loud_exception, with_loud_coroutine_exception
from bifrost.services.downlink.frame_processors.depacketizer import Frame_Depacketizer
from ait.core import log
import traceback
from sunrise.depacketizers.sunrise_depacketizer import SunRISE_Depacketization
from bifrost.services.downlink.frame_processors.packet_tagger import CCSDS_Packet_Tagger
from bifrost.common.time_utility import packet_time_stamp_from_gps_s_ns


class RealTime_Telemetry_Frame_Processor(Service):
    """
    Depacketize frames
    Tag packets
    """
    @with_loud_exception
    def __init__(self):
        Service.__init__(self)
        self.vcid = 1
        self.processor_name = "Real Time Telemetry"
        self.frame_depacketizer = Frame_Depacketizer(SunRISE_Depacketization,
                                                     self.processor_name)
        self.packet_tagger = CCSDS_Packet_Tagger(self.vcid,
                                                 self.processor_name,
                                                 packet_time_stamp_from_gps_s_ns)
        self.start()

    @with_loud_coroutine_exception
    async def process(self, topic, data, reply):
        log.debug(f"REAL TIME! {data.channel_counter}")
        try:
            packets = self.frame_depacketizer(data)
            tagged_packets = self.packet_tagger(packets)
            for tagged_packet in tagged_packets:
                subj = f'Telemetry.AOS.VCID.{tagged_packet.vcid}.TaggedPacket.{tagged_packet.packet_name}'
                await self.publish(subj, tagged_packet.subset_map())
        except Exception as e:
            log.error(e)
            traceback.print_exc()
            raise e

    @with_loud_coroutine_exception
    async def reconfigure(self, topic, data, reply):
        self.pass_id = await self.config_request_pass_id()
        await super().reconfigure(topic, data, reply)
