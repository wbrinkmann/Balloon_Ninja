# Script for live visualization of balloon detecting.
# howtorun.md for run instructions

from main.detect_balloon import detect_balloons
import cv2

def main(): 
    # Select camera 0 is webcam
    source = "/dev/video0"
    camera = cv2.VideoCapture(source,cv2.CAP_V4L2)
    # Error if video source cant be opened
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(f"Could not open video source: {source}")
    # Reading frames and displaying detections
    try: 
        while True:
        # Read next frame
            ok, frame = camera.read()
            if not ok: 
                break
            # Draw on a copy so the original frame stays unchanged.
            display = frame.copy() 
            # Create the detection list
            detection_list = detect_balloons(frame)
            # Draw a radius sized circle around each detection
            for detection in detection_list:
                u,v,radius = detection
                # Convert center to integer
                center = (round(u),round(v))
                # Draw a green outline around the ball
                cv2.circle(display,center,round(radius),(0,255,0),2)
                # Create a detection status
                status = "ball detected"
            else:
                status = "no ball detected"

            # Display status in top left
            cv2.putText(
                display, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2,
            )
            # Display the live video
            cv2.imshow("Live ball detection", display)
            # q: quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
    finally:
        # Free camera and close 
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

