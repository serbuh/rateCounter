# version 1.0.2 - 29.08.2019
import time
import sys
import logging

timer = time.time
    
# class for printing message rates
class rateCounter(object):
    def __init__(self, msg_name, msg_rate_expected, msg_timeout, print_cycle, to_print, logger = None):
        self.to_print = to_print
        
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(msg_name)
            self.logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
            self.logger.propagate = False
        
        self.logger.info("Init rate counter for {}, expected rate {} sec, timeout {} sec".format(msg_name, msg_rate_expected, msg_timeout))

        self.msg_rate_expected = msg_rate_expected
        self.msg_name = msg_name
        self.msg_timeout = msg_timeout
        self.print_cycle = print_cycle
        now = timer()
        self.start_time = now
        self.last_msg_time = now
        self.last_msg_interval_start = -1
        self.last_msg_interval_end = now
        self.last_print_cycle = now
        self.msg_received = False
        self.msg_count = 0
        self.msg_interval_count = 1.0
        self.msg_rate = 0.0
        
        
    def newMessage(self):
        self.msg_count += 1
        self.msg_interval_count += 1
        self.last_msg_time = timer()
        
    def printRate(self, print_immediately = False):
        now = timer()
        
        fps = None
        if not self.msg_received and self.msg_count > 0:
            self.msg_received = True
            self.logger.info("{:9} | First msg |".format(self.msg_name))
            self.last_msg_interval_start = now
            self.msg_interval_count = 1.0
            self.last_print_cycle = now

        elif (print_immediately) or (now - self.last_print_cycle >= self.print_cycle):
            # check timeout
            if now - self.last_msg_time >= self.msg_timeout:
                if self.to_print:
                    self.logger.info("{:9} | ********* |  No {} for {:.0f} seconds".format(self.msg_name, self.msg_name, now - self.last_msg_time))

                fps = -1

            else:
                # check rate
                self.last_msg_interval_end = self.last_msg_time
                if self.last_msg_interval_end - self.last_msg_interval_start > 0: # check if received more than one message for the last interval
                    self.msg_rate = (self.msg_interval_count - 1) / (self.last_msg_interval_end - self.last_msg_interval_start)
                    #print("rate {:.2f} : start {:.2f} end {:.2f} count {}".format(self.msg_rate, self.last_msg_interval_start, self.last_msg_interval_end, self.msg_interval_count))
                else:
                    self.msg_rate = 0.0
                self.last_msg_interval_start = self.last_msg_time
                self.msg_interval_count = 1.0
                if self.to_print:
                    diff = self.msg_rate - self.msg_rate_expected
                    if abs(diff) <= self.msg_rate_expected/10.0:
                        self.logger.info("{:9} | {:6.2f} Hz |   ".format(self.msg_name, self.msg_rate))
                    elif diff > 0:
                        self.logger.info("{:9} | {:6.2f} Hz |  * Above expected {} * ".format(self.msg_name, self.msg_rate, self.msg_rate_expected))
                    elif diff < 0:
                        self.logger.info("{:9} | {:6.2f} Hz |  * Below expected {} * ".format(self.msg_name, self.msg_rate, self.msg_rate_expected))

                fps = round(self.msg_rate, 2)

            self.last_print_cycle = timer()
            
        return fps

if __name__ == "__main__":
    import threading
    msg_timeout = 5                         # messages timeout (in seconds). After that period, "No <message name>" will be printed
    print_rate = 2                          # print messages rate every <print_rate> seconds
    videoCounter  = rateCounter("Video",  25, msg_timeout, print_rate, True) # <----- Init video reate counter
    telemCounter  = rateCounter("Telem",  40, msg_timeout, print_rate, True) # <----- Init telem rate counter
    outputCounter = rateCounter("Output", 25, msg_timeout, print_rate, True) # <----- Init output rate counter
    
    keepgoing = True
    def videoLoop():
        while keepgoing:
            tic = timer()
            # bla bla bla video code bla bla bla
            videoCounter.newMessage() # <----- New video message
            while True:
                if (timer() - tic >= 1.0/25.0):
                    break
                time.sleep(0.0001)
        print("Stopped videoLoop")
    
    def telemLoop():
        while keepgoing:
            tic = timer()
            # bla bla bla telem code bla bla bla
            telemCounter.newMessage() # <----- New telem message
            while True:
                if (timer() - tic >= 1.0/40.0):
                    break
                time.sleep(0.0001)
        print("Stopped telemLoop")
        
    def outputLoop():
        while keepgoing:
            tic = timer()
            # bla bla bla calculations bla bla bla
            outputCounter.newMessage() # <----- New output message
            while True:
                if (timer() - tic >= 1.0/25.4):
                    break
                time.sleep(0.0001)
        print("Stopped outputLoop")
        
    def mainLoop():
        while keepgoing:
            videoCounter.printRate(print_immediately = False) # <----- Print (with time condition)
            telemCounter.printRate(print_immediately = False) # <----- Print (with time condition)
            outputCounter.printRate(print_immediately = False) # <----- Print (with time condition)
            time.sleep(0.01)
        print("Stopped mainLoop")
        
    videoThread  = threading.Thread(target=videoLoop,  args=())
    telemThread  = threading.Thread(target=telemLoop,  args=())
    outputThread = threading.Thread(target=outputLoop, args=())
    mainThread   = threading.Thread(target=mainLoop,   args=())
    
    videoThread.start()
    telemThread.start()
    outputThread.start()
    mainThread.start()
    
    time.sleep(15)
    
    #enough ...
    
    keepgoing = False
    videoThread.join()
    telemThread.join()
    outputThread.join()
    mainThread.join()
    
    print("End test")