import cv2
from fcntl import ioctl
import mmap
import numpy as np
import os
import struct
import v4l2


NUM_BUFFERS = 10


class Camera(object):
    def __init__(self, device_name):
        self.device_name = device_name
        self.open_device()
        self.init_device()

    def open_device(self):
        self.fd = os.open(self.device_name, os.O_RDWR, 0)

    def init_device(self):
        cap = v4l2.v4l2_capability()
        fmt = v4l2.v4l2_format()
        
        ioctl(self.fd, v4l2.VIDIOC_QUERYCAP, cap)
        
        if not (cap.capabilities & v4l2.V4L2_CAP_VIDEO_CAPTURE):
            raise Exception("{} is not a video capture device".format(self.device_name))
        
        fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        ioctl(self.fd, v4l2.VIDIOC_G_FMT, fmt)
        
        self.init_mmap()
    
    def init_mmap(self):
        req = v4l2.v4l2_requestbuffers()
        
        req.count = NUM_BUFFERS
        req.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        req.memory = v4l2.V4L2_MEMORY_MMAP
        
        try:
            ioctl(self.fd, v4l2.VIDIOC_REQBUFS, req)
        except Exception:
            raise Exception("video buffer request failed")
        
        if req.count < 2:
            raise Exception("Insufficient buffer memory on {}".format(self.device_name))

        self.buffers = []
        for x in range(req.count):
            buf = v4l2.v4l2_buffer()
            buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = v4l2.V4L2_MEMORY_MMAP
            buf.index = x
            
            ioctl(self.fd, v4l2.VIDIOC_QUERYBUF, buf)

            buf.buffer =  mmap.mmap(self.fd, buf.length, mmap.PROT_READ, mmap.MAP_SHARED, offset=buf.m.offset)
            self.buffers.append(buf)

    def start_capturing(self):
        for buf in self.buffers:
            ioctl(self.fd, v4l2.VIDIOC_QBUF, buf)
        video_type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        ioctl(self.fd, v4l2.VIDIOC_STREAMON, struct.pack('I', video_type))
        self.main_loop()
    
    def process_image(self, buf):
        video_buffer = self.buffers[buf.index].buffer
        data = video_buffer.read(buf.bytesused)
        try:
            image = cv2.imdecode(np.fromstring(data, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
            cv2.imshow(self.device_name, image)
            cv2.waitKey(1)
            video_buffer.seek(0)
        except Exception as e:
            # Not entirely sure what Exceptions I'm looking for here, potentially a bad read?
            print e


    def main_loop(self):
        for x in range(100):
            print "grabbing frame {}".format(x)
            buf = self.buffers[x % NUM_BUFFERS]
            ioctl(self.fd, v4l2.VIDIOC_DQBUF, buf)
            self.process_image(buf)
            ioctl(self.fd, v4l2.VIDIOC_QBUF, buf)


if __name__ == "__main__":
    cam = Camera("/dev/video0")
    cam.start_capturing()