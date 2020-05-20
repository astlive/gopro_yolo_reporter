import cv2

def cv_size(img):
    return tuple(img.shape[1::-1])

def draw_msg(img, str1, str2, color1 = (0,255,0), color2 = (0,0,255)):
    cv2.putText(img, str1, (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color1, 2)
    cv2.putText(img, str2, (10,80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color2, 2)
    return img

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def roiDrawBoxes(detections, img, top = 0.1, bot = 0.1):
    #it's BGR in opencv
    red = (255, 0, 0)
    green = (0, 255, 0)
    color = (0, 0, 0)
    min_y = round(img.shape[0] * top, 0)
    max_y = round(img.shape[0] * (1-bot), 0)
    flag = False

    for detection in detections:
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)

        if(ymin >= min_y and ymax <= max_y):
            flag = True
            color = red
            cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
            cv2.putText(img,
                        detection[0] +
                        " [" + str(round(detection[1] * 100, 2)) + "]",
                        (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        color, 2)
    return flag, img