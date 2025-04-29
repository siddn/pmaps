import pygetwindow as gw
import mss
import cv2
import numpy as np
import win32gui
import win32con
import win32ui
import win32api
import screeninfo
import pyautogui as pag
import mouse


def select_monitor(monitor_index):
    with mss.mss() as sct:
        if monitor_index < 0:
            print("Select from the available monitors:")
            print(sct.monitors)
            monitor_index = int(input("Enter the monitor index: "))
        monitor = sct.monitors[monitor_index]
        monitor_width = monitor['width']
        monitor_height = monitor['height']
        print(f"Selected Monitor {monitor_index}: {monitor}")
    
    return monitor_index, monitor_width, monitor_height, monitor['left'], monitor['top']

def initialize_projection(monitor_width, monitor_height, monitor_x, monitor_y):
    cv2.namedWindow('Fullscreen Window Projection', cv2.WND_PROP_FULLSCREEN)
    cv2.resizeWindow('Fullscreen Window Projection', monitor_width, monitor_height)
    cv2.moveWindow('Fullscreen Window Projection', monitor_x, monitor_y)
    cv2.setWindowProperty('Fullscreen Window Projection', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

def capture_window(hwnd) -> np.ndarray:
    with mss.mss() as sct:        # Get client area dimensions
        client_rect = win32gui.GetClientRect(hwnd)
        client_width = client_rect[2] - client_rect[0]
        client_height = client_rect[3] - client_rect[1]
        client_point = win32gui.ClientToScreen(hwnd, (0, 0))
        left, top = client_point

        frame_space = { 'top': top, 'left': left, 'width': client_width, 'height': client_height}

        sct_img = sct.grab(frame_space)
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return img

def project_img(img, screen_width, screen_height, fill):
        if fill:
            full_screen_frame = cv2.resize(img, (screen_width, screen_height))
            img = full_screen_frame
        width = img.shape[1]
        height = img.shape[0]
        x_offset = (screen_width - width) // 2
        y_offset = (screen_height - height) // 2
        # Fill the black background with the zeros
        black_background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        black_background[y_offset:y_offset + height, x_offset:x_offset + width] = img
        img = black_background.copy()
        return img, x_offset, y_offset

def apply_transform(img, transform_matrix):
    transformed_img = cv2.warpPerspective(img, transform_matrix, (img.shape[1], img.shape[0]))
    return transformed_img

def pick_transform_points():
    # Click four points on the screen to define the transformation
    print("Click four points on the screen to define the transformation.")
    points = []
    while len(points) < 4:
        mouse.wait(button='left', target_types='down')
        points.append(mouse.get_position())
        print(f"Point {len(points)}: {points[-1]}")
    mouse.unhook_all()
    print("Points selected.")
    return points

if __name__ == "__main__":
    print("Press 'q' to exit the projection. Welcom to pmaps, the projection tool.")
    print("You can run can save a config to load your setup each time.")
    input("Ready to start the projection? Press Enter to continue...")
    monitor_index, monitor_width, monitor_height, monitor_x, monitor_y = select_monitor(-1)
    hwnd = gw.getWindowsWithTitle('Anaconda Prompt')[0]._hWnd
    print("Initializing projection...")
    black_background = np.zeros((monitor_height, monitor_width, 3), dtype=np.uint8)
    initialize_projection(monitor_width=monitor_width, monitor_height=monitor_height, monitor_x=monitor_x, monitor_y=monitor_y)
    transform_points = pick_transform_points()

    # Define homogrophy matrix. Transform the image to the points selected.
    dst_pts = np.array([transform_points[0], transform_points[1], transform_points[3], transform_points[2]], dtype=np.float32)
    print("Transform matrix:")
    #          G               B             R             OTHER
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]
    while True:
        img_base = capture_window(hwnd)
        # Source points are the corners of the image, once they are placed in the center of the screen.
        img, x_offset, y_offset = project_img(img_base, monitor_width, monitor_height, fill=False)
        src_pts = np.array([[x_offset, y_offset], [x_offset + img_base.shape[1], y_offset],
                            [x_offset + img_base.shape[1], y_offset + img_base.shape[0]], [x_offset, y_offset + img_base.shape[0]]], dtype=np.float32)

        transform_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        img = cv2.warpPerspective(img, transform_matrix, (monitor_width, monitor_height))
        cv2.imshow('Fullscreen Window Projection', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()