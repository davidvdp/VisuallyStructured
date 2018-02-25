from .Variables import FloatVar
from .FlowBlocks import FlowBlock
import time
import logging
from FlowBlocks import FlowBlockFactory

smbus2_found = True
try:
    import smbus2
except ImportError:
    smbus2_found = False

if smbus2_found:
    class LidarLiteV2(FlowBlock):
        type_name = "LidarLiteV2"

        def __init__(self, name=type_name):
            super().__init__(name=name)
            self.SubVariables = {
            }
            self.OutputVars = {"Distance": FloatVar()}
            self.address = 0x62
            self.distWriteReg = 0x00
            self.distWriteVal = 0x04
            self.distReadReg1 = 0x8f
            self.distReadReg2 = 0x10
            self.velWriteReg = 0x04
            self.velWriteVal = 0x08
            self.velReadReg = 0x09
            self.bus = None

        def __connect(self, bus=1):
            try:
                self.bus = smbus2.SMBus(bus)
                time.sleep(0.5)
                return 0
            except:
                self.bus = None
                return -1

        def __writeAndWait(self, register, value):
            self.bus.write_byte_data(self.address, register, value);
            time.sleep(0.02)

        def __readAndWait(self, register):
            res = self.bus.read_byte_data(self.address, register)
            time.sleep(0.02)
            return res

        def __getDistance(self):
            self.__writeAndWait(self.distWriteReg, self.distWriteVal)
            dist1 = self.__readAndWait(self.distReadReg1)
            dist2 = self.__readAndWait(self.distReadReg2)
            logging.debug("Dist1: %.5f" % dist1)
            logging.debug("Dist2: %.5f" % dist2)
            return (dist1 << 8) + dist2

        def execute(self, results_controller):
            logging.info("Executing %s" % self.name)

            if self.bus is None:
                if self.__connect() == -1:
                    logging.warning("Could not connect to lidar lite v2")
                    return

            distance = self.__getDistance()
            self.OutputVars["Distance"].value = distance


    FlowBlockFactory.AddBlockType(LidarLiteV2)
else:
    logging.info("Could not load Lidar Lite V2.")

