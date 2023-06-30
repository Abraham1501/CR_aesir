#Code that detect motion
import cv2

class motion_detector():
    def __init__(self, Cam):
        self.Cam = Cam
    def frames(self, frame1, frame2):
        #Find the difference between the frames
        diff = cv2.absdiff(frame1, frame2)
        #Coloured grayscale image
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        #Remove noise from an image
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        #Differentiates the colors of the pixels that are below or above a threshold value
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        # Adding pixels to the boundaries
        dilated = cv2.dilate(thresh, None, iterations=3)
        #Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #Draw each of the contours
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)

            if cv2.contourArea(contour) < 900:
                continue
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return frame1
