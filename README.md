Raspberry Pi Motion Detection using OpenCV/Python
===
Adaptation of code from
(http://thorbek.net/online/2014/05/27/a-simple-motion-detection-program-for-raspberry-pi/).
I have changed the code to get the motion detection frames from the
video port at a lower resolution, and to snap a high resolution shot
when motion is detected.

This allows me to capture most movement in front of the camera at a high
resolution (bearing in mind that it can take 750 ms to get a good
quality still capture), but with relatively little cpu load (the pi load
average is around 0.40)
