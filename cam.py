import v4l2
import os
import fcntl


class Camera(object):
    def __init__(self, device_name):
        self.device_name = device_name
        self.open_device()

    def open_device(self):
        self.fd = os.open(self.device_name, os.O_RDWR, os.O_NONBLOCK, 0)

    def init_device(self):
        cap = v4l2.v4l2_capability
        cropcap = v4l2.v4l2_cropcap
        crop = v4l2.v4l2_crop
        fmt = v4l2.v4l2_format
        
        if -1 == fcntl.ioctl(self.fd, v4l2.VIDIOC_QUERYCAP, cap):
            raise Exception("unable to query device {}".format(self.device_name))
        
    def start_capturing(self):
        pass
    def main_loop(self):
        pass


if __name__ == "__main__":
    cam = Camera("/dev/video0")