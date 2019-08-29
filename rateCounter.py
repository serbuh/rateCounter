# version 1.0.2 - 29.08.2019
import time
import sys

timer = time.time

# class for printing message rates
class rateCounter(object):
    def __init__(self, msg_name, msg_rate_expected, msg_timeout, print_time):
        self.msg_rate_expected = msg_rate_expected
        self.msg_name = msg_name
        self.msg_timeout = msg_timeout
        self.print_time = print_time
        now = timer()
        self.start_time = now
        self.last_msg_time = now
        self.last_msg_interval_start = now
        self.last_msg_interval_end = now
        self.last_print_time = now
        self.msg_count = 0
        self.msg_interval_count = 0.0
        self.msg_rate = 0.0
        
    def newMessage(self):
        self.msg_count +=1
        self.msg_interval_count +=1
        self.last_msg_time = timer()
        
    def printRate(self, print_immediately):
        now = timer()
    
        if (print_immediately) or (now - self.last_print_time >= self.print_time):
            # check timeout
            if  now - self.last_msg_time >= self.msg_timeout:
                print("{:9} | ********** | No {} for {:.0f} seconds".format(self.msg_name, self.msg_name, now - self.last_msg_time))
            else:
                # check rateCounter
                self.last_msg_interval_end = self.last_msg_time
                if self.last_msg_interval_end - self.last_msg_interval_start > 0:
                    self.msg_rate = self.msg_interval_count/(self.last_msg_interval_end - self.last_msg_interval_start)
                else:
                    self.msg_rate = 0.0
                self.last_msg_interval_start = self.last_msg_interval_end
                self.msg_interval_count = 0.0
                diff = self.msg_rate - self.msg_rate_expected
                if abs(diff) <= self.msg_rate_expected/10.0:
                    print("{:9} | {:6.2f} Hz |".format(self.msg_name, self.msg_rate, self.msg_rate_expected))
                elif diff > 0:
                    print("{:9} | {:6.2f} Hz | * Above expected {} *".format(self.msg_name, self.msg_rate, self.msg_rate_expected))
                elif diff < 0:
                    print("{:9} | {:6.2f} Hz | * Below expected {} *".format(self.msg_name, self.msg_rate, self.msg_rate_expected))
            
            self.last_print_time = timer()

if __name__ == "__main__":
    import threading
    msg_timeout = 5                         # messages timeout (in seconds). After that priod "No <message name>" will be printed
    print_rate = 2                          # print messages rate every <print_rate> seconds
    videoCounter  = rateCounter("Video",  25, msg_timeout, print_rate)
    telemCounter  = rateCounter("Telem",  40, msg_timeout, print_rate)
    outputCounter = rateCounter("Output", 25, msg_timeout, print_rate)
    
    keepgoing = True
    def videoLoop():
        while keepgoing:
            tic = timer()
            # bla bla bla calculations bla bla bla
            videoCounter.newMessage()
            while True:
                if (timer() - tic >= 1.0/26.0):
                    break
                time.sleep(0.0001)
        print("Stopped videoLoop")
    
    def telemLoop():
        while keepgoing:
            tic = timer()
            # bla bla bla calculations bla bla bla
            telemCounter.newMessage()
            while True:
                if (timer() - tic >= 1.0/40.5):
                    break
                time.sleep(0.0001)
        print("Stopped telemLoop")
    
    def outputLoop():
        while keepgoing:
            tic = timer()
            # bla bla bla calculations bla bla bla
            outputCounter.newMessage()
            while True:
                if (timer() - tic >= 1.0/25.4):
                    break
                time.sleep(0.0001)
        print("Stopped outputLoop")
    
    def mainLoop():
        while keepgoing:
            videoCounter.printRate(print_immediately = False)
            telemCounter.printRate(print_immediately = False)
            outputCounter.printRate(print_immediately = False)
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
    
    # enough ...
    
    keepgoing = False
    videoThread.join()
    telemThread.join()
    outputThread.join()
    mainThread.join()
    
    print("End Test")