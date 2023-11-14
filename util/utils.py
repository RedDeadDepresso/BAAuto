import cv2
import numpy
import time
import struct
import os
import lz4.block
from imutils import contours, grab_contours
from datetime import datetime, timedelta
from random import uniform, gauss, randint
from scipy import spatial
from util.adb import Adb
from util.logger import Logger
from util.config_consts import UtilConsts
from threading import Thread
from pponnxcr import TextSystem
from util.exceptions import GameStuckError, GameNotRunningError, ReadOCRError

class Region(object):
    x, y, w, h = 0, 0, 0, 0

    def __init__(self, x, y, w, h):
        """Initializes a region.

        Args:
            x (int): Initial x coordinate of the region (top-left).
            y (int): Initial y coordinate of the region (top-left).
            w (int): Width of the region.
            h (int): Height of the region.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def equal_approximated(self, region, tolerance=15):
        """Compares this region to the one received and establishes if they are the same
        region tolerating a difference in pixels up to the one prescribed by tolerance.

        Args:
            region (Region): The region to compare to.
            tolerance (int, optional): Defaults to 15.
                Highest difference of pixels tolerated to consider the two Regions equal.
                If set to 0, the method becomes a "strict" equal.
        """
        valid_x = (self.x - tolerance, self.x + tolerance)
        valid_y = (self.y - tolerance, self.y + tolerance)
        valid_w = (self.w - tolerance, self.w + tolerance)
        valid_h = (self.h - tolerance, self.h + tolerance)
        return (valid_x[0] <= region.x <= valid_x[1] and valid_y[0] <= region.y <= valid_y[1] and
                valid_w[0] <= region.w <= valid_w[1] and valid_h[0] <= region.h <= valid_h[1])


    def intersection(self, other):
        """Checks if there is an intersection between the two regions,
        and if that is the case, returns it.
        Taken from https://stackoverflow.com/a/25068722

        Args:
            other (Region): The region to intersect with.

        Returns:
            intersection (Region) or None.
        """
        a = (self.x, self.y, self.x+self.w, self.y+self.h)
        b = (other.x, other.y, other.x+other.w, other.y+other.h)
        x1 = max(min(a[0], a[2]), min(b[0], b[2]))
        y1 = max(min(a[1], a[3]), min(b[1], b[3]))
        x2 = min(max(a[0], a[2]), max(b[0], b[2]))
        y2 = min(max(a[1], a[3]), max(b[1], b[3]))
        if x1<x2 and y1<y2:
            return type(self)(x1, y1, x2-x1, y2-y1)

    def get_center(self):
        """Calculate and returns the center of this region."""
        return [(self.x * 2 + self.w)//2, (self.y * 2 + self.h)//2]

    def contains(self, coords):
        """Checks if the specified coordinates are inside the region.
        Args:
            coords (list or tuple of two elements): x and y coordinates.

        Returns:
            (bool): whether the point is inside the region.
        """
        return (self.x <= coords[0] <= (self.x + self.w)) and (self.y <= coords[1] <= (self.y + self.h))

screen = None
last_ocr = ''
bytepointer = 0


class Utils(object):
    screen = None
    color_screen = None
    small_boss_icon = False
    screencap_mode = None

    DEFAULT_SIMILARITY = 0.9
    assets = ''
    locations = ()
    ocr = None
    record = {
        'last_touch':[None, 0],
        'last_swipe':[None, 0],
        'game_started':False,
        'restart_attempts':0
    }

    @classmethod
    def init_screencap_mode(cls,mode):
        consts = UtilConsts.ScreenCapMode

        cls.screencap_mode = mode

        if cls.screencap_mode == consts.ASCREENCAP:
            # Prepare for ascreencap, push the required libraries
            Adb.exec_out('rm /data/local/tmp/ascreencap')
            cpuArc = Adb.exec_out('getprop ro.product.cpu.abi').decode('utf-8').strip()
            sdkVer = int(Adb.exec_out('getprop ro.build.version.sdk').decode('utf-8').strip())
            ascreencaplib = 'ascreencap_{}'.format(cpuArc)
            if sdkVer in range(21, 26) and os.path.isfile(ascreencaplib):
                Adb.cmd('push {} /data/local/tmp/ascreencap'.format(ascreencaplib))
            else:
                Logger.log_warning(
                    'No suitable version of aScreenCap lib is available locally, using ascreencap_local...')
                if os.path.isfile('ascreencap_local'):
                    Adb.cmd('push ascreencap_local /data/local/tmp/ascreencap')
                else:
                    Logger.log_error(
                        'File "ascreencap_local" not found. Please download the appropriate version of aScreenCap for your device from github.com/ClnViewer/Android-fast-screen-capture and save it as "ascreencap_local"')
                    Logger.log_warning('Since aScreenCap is not ready, falling back to normal adb screencap')
                    Utils.useAScreenCap = False
            Adb.shell('chmod 0777 /data/local/tmp/ascreencap')

    @classmethod
    def init_ocr_mode(cls, EN=None):
        # https://github.com/hgjazhgj/pponnxcr
        if EN:
            cls.ocr = TextSystem('en')
        else:
            server_to_ocr = {   
            "ZHS": 'zhs',
            "CN":'zht',
            "JP":'ja',
            "EN":'en',
            }
            cls.ocr = TextSystem(server_to_ocr[cls.assets])

    @staticmethod
    def reposition_byte_pointer(byteArray):
        """Method to return the sanitized version of ascreencap stdout for devices
            that suffers from linker warnings. The correct pointer location will be saved
            for subsequent screen refreshes
        """
        global bytepointer
        while(byteArray[bytepointer:bytepointer + 4] != b'BMZ1'):
            bytepointer += 1
            if bytepointer >= len(byteArray):
                raise Exception('Repositioning byte pointer failed, corrupted aScreenCap data received')
        return byteArray[bytepointer:]

    @staticmethod
    def multithreader(threads):
        """Method for starting and threading multithreadable Threads in
        threads.

        Args:
            threads (list): List of Threads to multithread.
        """
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    @staticmethod
    def script_sleep(base=None, flex=None):
        """Method for putting the program to sleep for a random amount of time.
        If base is not provided, defaults to somewhere along with 0.3 and 0.7
        seconds. If base is provided, the sleep length will be between base
        and 2*base. If base and flex are provided, the sleep length will be
        between base and base+flex. The global SLEEP_MODIFIER is than added to
        this for the final sleep length.

        Args:
            base (int, optional): Minimum amount of time to go to sleep for.
            flex (int, optional): The delta for the max amount of time to go
                to sleep for.
        """
        if base is None:
            time.sleep(uniform(0.4, 0.7))
        else:
            flex = base if flex is None else flex
            time.sleep(uniform(base, base + flex))

    @classmethod
    def update_screen(cls):
        """Uses ADB to pull a screenshot of the device and then read it via CV2
        and then stores the images in grayscale and color to screen and color_screen, respectively.

        Returns:
            image: A CV2 image object containing the current device screen.
        """
        consts = UtilConsts.ScreenCapMode

        global screen
        screen = None
        color_screen = None
        while color_screen is None:
            if Adb.legacy:
                color_screen = cv2.imdecode(
                    numpy.fromstring(Adb.exec_out(r"screencap -p | sed s/\r\n/\n/"), dtype=numpy.uint8),
                    cv2.IMREAD_COLOR)
            else:
                if cls.screencap_mode == consts.SCREENCAP_PNG:
                    start_time = time.perf_counter()
                    color_screen = cv2.imdecode(numpy.frombuffer(Adb.exec_out('screencap -p'), dtype=numpy.uint8),
                                                cv2.IMREAD_COLOR)
                    elapsed_time = time.perf_counter() - start_time
                    Logger.log_debug("SCREENCAP_PNG took {} ms to complete.".format('%.2f' % (elapsed_time * 1000)))
                elif cls.screencap_mode == consts.SCREENCAP_RAW:
                    start_time = time.perf_counter()
                    pixel_size = 4

                    byte_arr = Adb.exec_out('screencap')
                    header_format = 'III'
                    header_size = struct.calcsize(header_format)
                    if len(byte_arr) < header_size:
                        continue
                    header = struct.unpack(header_format, byte_arr[:header_size])
                    width = header[0]
                    height = header[1]
                    if len(byte_arr) != header_size + width * height * pixel_size:
                        continue
                    tmp = numpy.frombuffer(byte_arr, dtype=numpy.uint8, count=width * height * 4, offset=header_size)
                    rgb_img = tmp.reshape((height, width, -1))
                    color_screen = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
                    elapsed_time = time.perf_counter() - start_time
                    Logger.log_debug("SCREENCAP_RAW took {} ms to complete.".format('%.2f' % (elapsed_time * 1000)))
                elif cls.screencap_mode == consts.UIAUTOMATOR2:
                    start_time = time.perf_counter()
                    color_screen = Adb.u2device.screenshot(format='opencv')
                    elapsed_time = time.perf_counter() - start_time
                    Logger.log_debug("uiautomator2 took {} ms to complete.".format('%.2f' % (elapsed_time * 1000)))
                elif cls.screencap_mode == consts.ASCREENCAP:
                    start_time = time.perf_counter()
                    raw_compressed_data = Utils.reposition_byte_pointer(
                        Adb.exec_out('/data/local/tmp/ascreencap --pack 2 --stdout'))
                    compressed_data_header = numpy.frombuffer(raw_compressed_data[0:20], dtype=numpy.uint32)
                    if compressed_data_header[0] != 828001602:
                        compressed_data_header = compressed_data_header.byteswap()
                        if compressed_data_header[0] != 828001602:
                            Logger.log_error('If error persists, disable aScreenCap and report traceback')
                            raise Exception(
                                'aScreenCap header verification failure, corrupted image received. HEADER IN HEX = {}'.format(
                                    compressed_data_header.tobytes().hex()))
                    uncompressed_data_size = compressed_data_header[1].item()
                    color_screen = cv2.imdecode(numpy.frombuffer(
                        lz4.block.decompress(raw_compressed_data[20:], uncompressed_size=uncompressed_data_size),
                        dtype=numpy.uint8), cv2.IMREAD_COLOR)
                    elapsed_time = time.perf_counter() - start_time
                    Logger.log_debug("aScreenCap took {} ms to complete.".format('%.2f' % (elapsed_time * 1000)))
                else:
                    raise Exception('Unknown screencap mode')

            screen = cv2.cvtColor(color_screen, cv2.COLOR_BGR2GRAY)
            cls.color_screen = color_screen
            cls.screen = screen

    @classmethod
    def wait_update_screen(cls, time=None):
        """Delayed update screen.

        Args:
            time (int, optional): seconds of delay.
        """
        if time is None:
            cls.script_sleep()
        else:
            cls.script_sleep(time)
        cls.update_screen()

    @staticmethod
    def get_color_screen():
        """Uses ADB to pull a screenshot of the device and then read it via CV2
        and then returns the read image. The image is in a BGR format.

        Returns:
            image: A CV2 image object containing the current device screen.
        """
        color_screen = None
        while color_screen is None:
            if Adb.legacy:
                color_screen = cv2.imdecode(
                    numpy.fromstring(Adb.exec_out(r"screencap -p | sed s/\r\n/\n/"), dtype=numpy.uint8), 1)
            else:
                color_screen = cv2.imdecode(numpy.fromstring(Adb.exec_out('screencap -p'), dtype=numpy.uint8), 1)
        return color_screen

    @classmethod
    def get_mask_from_alpha(cls, image):
        """Calculate the mask of the specified image from its alpha channel.
        The mask returned is a binary image, where the transparent pixels have been blacked.

        Args:
            image (string): image to load and use to calculate the mask.

        Returns:
            mask (numpy array): binary image obtained from the source image's alpha channel.
        """
        source = cv2.imread('assets/{}/{}.png'.format(cls.assets, image), cv2.IMREAD_UNCHANGED)
        # split into BGRA and get A
        alpha_channel = cv2.split(source)[3]
        ret, thresh = cv2.threshold(alpha_channel, 0, 255, cv2.THRESH_BINARY)
        return thresh

    @classmethod
    def show_on_screen(cls, coordinates):
        """ Shows the position of the received coordinates on a screenshot
            through green dots. It pauses the script. Useful for debugging.
        """
        color_screen = cls.get_color_screen()
        for coords in coordinates:
            cv2.circle(color_screen, tuple(coords), 5, (0, 255, 0), -1)
        cv2.imshow("targets", color_screen)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    @staticmethod
    def draw_region(screen, region, color, thickness):
        """Method which draws a region (a rectangle) on the image (screen) passed as argument.

        Args:
            screen (numpy array): image to draw on.
            region (Region): rectangle which needs to be drawn.
            color (tuple): specifiy the color of the rectangle's lines.
            thickness (int): specify the thickness of the rectangle's lines (-1 for it to be filled).

        See cv2.rectangle() docs.
        """
        cv2.rectangle(screen, (region.x, region.y), (region.x+region.w, region.y+region.h), color=color, thickness=thickness)

    @classmethod
    def find(cls, image, similarity=DEFAULT_SIMILARITY, color=False):
        """Finds the specified image on the screen

        Args:
            image (string): [description]
            similarity (float, optional): Defaults to DEFAULT_SIMILARITY.
                Percentage in similarity that the image should at least match.
            color (boolean): find the image in color screen

        Returns:
            Region: region object containing the location and size of the image
        """
        Utils.check_game_status()
        if color:
            template = cv2.imread('assets/{}/{}.png'.format(cls.assets, image), cv2.IMREAD_COLOR)
            match = cv2.matchTemplate(cls.color_screen, template, cv2.TM_CCOEFF_NORMED)
        else:
            template = cv2.imread('assets/{}/{}.png'.format(cls.assets, image), 0)
            match = cv2.matchTemplate(cls.screen, template, cv2.TM_CCOEFF_NORMED)

        height, width = template.shape[:2]
        value, location = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        # Check if the template match is not obscured by comparing pixel darkness
        if value >= similarity and not cls.is_obscured(location, template.shape[:2], color):
            return Region(location[0], location[1], width, height)
        return None

    @classmethod
    def is_obscured(cls, location, template_shape, color):
        """Check if the template match is obscured by surrounding pixels.

        Args:
            location (tuple): Location of the template match.
            template_shape (tuple): Shape (height, width) of the template.
            color (boolean): Whether to check in color screen.

        Returns:
            bool: True if obscured, False otherwise.
        """
        if color:
            # Extract the region around the template match
            x, y = location
            region = cls.color_screen[y:y+template_shape[0], x:x+template_shape[1]]

            # Calculate the average darkness level of the region
            avg_darkness = numpy.mean(region)

            # You can adjust the darkness threshold as needed
            darkness_threshold = 100  

            return avg_darkness < darkness_threshold
        else:
            pass  

    @classmethod
    def find_in_scaling_range(cls, image, similarity=DEFAULT_SIMILARITY, lowerEnd=0.8, upperEnd=1.2):
        """Finds the location of the image on the screen. First the image is searched at its default scale,
        and if it isn't found, it will be resized using values inside the range provided until a match that satisfy
        the similarity value is found. If the image isn't found even after it has been resized, the method returns None.

        Args:
            image (string): Name of the image.
            similarity (float, optional): Defaults to DEFAULT_SIMILARITY.
                Percentage in similarity that the image should at least match
            lowerEnd (float, optional): Defaults to 0.8.
                Lowest scaling factor used for resizing.
            upperEnd (float, optional): Defaults to 1.2.
                Highest scaling factor used for resizing.

        Returns:
            Region: Coordinates or where the image appears.
        """
        template = cv2.imread('assets/{}/{}.png'.format(cls.assets, image), 0)
        # first try with default size
        width, height = template.shape[::-1]
        match = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        value, location = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        if (value >= similarity):
            return Region(location[0], location[1], width, height)

        # resize and match using threads

        # change scaling factor if the boss icon searched is small
        # (some events has as boss fleet a shipgirl with a small boss icon at her bottom right)
        if cls.small_boss_icon and image == 'enemy/fleet_boss':
            lowerEnd = 0.4
            upperEnd = 0.6

        # preparing interpolation methods
        middle_range = (upperEnd + lowerEnd) / 2.0
        if lowerEnd < 1 and upperEnd > 1 and middle_range == 1:
            l_interpolation = cv2.INTER_AREA
            u_interpolation = cv2.INTER_CUBIC
        elif upperEnd < 1 and lowerEnd < upperEnd:
            l_interpolation = cv2.INTER_AREA
            u_interpolation = cv2.INTER_AREA
        elif lowerEnd > 1 and upperEnd > lowerEnd:
            l_interpolation = cv2.INTER_CUBIC
            u_interpolation = cv2.INTER_CUBIC
        else:
            l_interpolation = cv2.INTER_NEAREST
            u_interpolation = cv2.INTER_NEAREST

        results_list = []
        count = 0
        loop_limiter = (middle_range - lowerEnd) * 100

        thread_list = []
        while (upperEnd > lowerEnd) and (count < loop_limiter):
            thread_list.append(Thread(target=cls.resize_and_match, args=(results_list, template, lowerEnd, similarity, l_interpolation)))
            thread_list.append(Thread(target=cls.resize_and_match, args=(results_list, template, upperEnd, similarity, u_interpolation)))
            lowerEnd+=0.02
            upperEnd-=0.02
            count +=1
        cls.multithreader(thread_list)
        if results_list:
            return results_list[0]
        else:
            return None

    @classmethod
    def find_all(cls, image, similarity=DEFAULT_SIMILARITY, useMask=False):
        """Finds all locations of the image on the screen

        Args:
            image (string): Name of the image.
            similarity (float, optional): Defaults to DEFAULT_SIMILARITY.
                Percentage in similarity that the image should at least match.
            useMask (boolean, optional): Defaults to False.
                If set to True, this function uses a different comparison method and
                a mask when searching for match.

        Returns:
            array: Array of all coordinates where the image appears
        """
        del cls.locations

        if useMask:
            comparison_method = cv2.TM_CCORR_NORMED
            mask = cls.get_mask_from_alpha(image)
        else:
            comparison_method = cv2.TM_CCOEFF_NORMED
            mask = None

        template = cv2.imread('assets/{}/{}.png'.format(cls.assets, image), 0)
        match = cv2.matchTemplate(screen, template, comparison_method, mask=mask)
        cls.locations = numpy.where(match >= similarity)

        return cls.filter_similar_coords(
            list(zip(cls.locations[1], cls.locations[0])))

    @classmethod
    def find_all_with_resize(cls, image, similarity=DEFAULT_SIMILARITY, useMask=False):
        """Finds all locations of the image at default size on the screen.
        If nothing is found, the method proceeds to resize the image within the
        scaling range of (0.8, 1.2) with a step interval of 0.2 and repeats
        the template matching operation for each resized images.

        Args:
            image (string): Name of the image.
            similarity (float, optional): Defaults to DEFAULT_SIMILARITY.
                Percentage in similarity that the image should at least match.
            useMask (boolean, optional): Defaults to False.
                If set to True, this function uses a different comparison method and
                a mask when searching for match.

        Returns:
            array: Array of all coordinates where the image appears
        """
        del cls.locations

        if useMask:
            comparison_method = cv2.TM_CCORR_NORMED
            mask = cls.get_mask_from_alpha(image)
        else:
            comparison_method = cv2.TM_CCOEFF_NORMED
            mask = None

        template = cv2.imread('assets/{}/{}.png'.format(cls.assets, image), 0)
        match = cv2.matchTemplate(screen, template, comparison_method, mask=mask)
        cls.locations = numpy.where(match >= similarity)

        if len(cls.locations[0]) < 1:
            count = 1.20
            thread_list = []
            results_list = []
            while count > 0.80:
                thread_list.append(Thread(target=cls.match_resize, args=(results_list,template,count,comparison_method,similarity,useMask,mask)))
                count -= 0.02
            Utils.multithreader(thread_list)
            for i in range(0, len(results_list)):
                cls.locations = numpy.append(cls.locations, results_list[i], axis=1)

        return cls.filter_similar_coords(
            list(zip(cls.locations[1], cls.locations[0])))

    @classmethod
    def match_resize(cls, results_list, image, scale, comparison_method, similarity=DEFAULT_SIMILARITY, useMask=False, mask=None):
        template_resize = cv2.resize(image, None, fx = scale, fy = scale, interpolation = cv2.INTER_NEAREST)
        if useMask:
            mask_resize = cv2.resize(mask, None, fx = scale, fy = scale, interpolation = cv2.INTER_NEAREST)
        else:
            mask_resize = None
        match_resize = cv2.matchTemplate(screen, template_resize, comparison_method, mask=mask_resize)
        results_list.append(numpy.where(match_resize >= similarity))

    @classmethod
    def resize_and_match(cls, results_list, templateImage, scale, similarity=DEFAULT_SIMILARITY, interpolationMethod=cv2.INTER_NEAREST):
        template_resize = cv2.resize(templateImage, None, fx = scale, fy = scale, interpolation = interpolationMethod)
        width, height = template_resize.shape[::-1]
        match = cv2.matchTemplate(screen, template_resize, cv2.TM_CCOEFF_NORMED)
        value, location = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        if (value >= similarity):
            results_list.append(Region(location[0], location[1], width, height))

    @classmethod
    def touch(cls, x, y):
        """Sends an input command to touch the device screen at the specified
        coordinates via ADB

        Args:
            coords (array): An array containing the x and y coordinate of
                where to touch the screen
        """
        last_touch = cls.record.get('last_touch', [None, 0])

        if last_touch[0] == (x, y):
            if last_touch[1] >= 60:
                raise GameStuckError
            else:
                last_touch[1] += 1
        else:
            last_touch = [(x, y), 0]

        cls.record['last_touch'] = last_touch
        Utils.check_game_status()
        Adb.u2device.click(x, y)

    @classmethod
    def touch_randomly(cls, region=Region(0, 0, 1280, 720)):
        """Touches a random coordinate in the specified region

        Args:
            region (Region, optional): Defaults to Region(0, 0, 1280, 720).
                specified region in which to randomly touch the screen
        """
        x = cls.random_coord(region.x, region.x + region.w)
        y = cls.random_coord(region.y, region.y + region.h)
        cls.touch(x, y)

    @classmethod
    def swipe(cls, x1, y1, x2, y2, ms=0):
        """Sends an input command to swipe the device screen between the
        specified coordinates via ADB

        Args:
            x1 (int): x-coordinate to begin the swipe at.
            y1 (int): y-coordinate to begin the swipe at.
            x2 (int): x-coordinate to end the swipe at.
            y2 (int): y-coordinate to end the swipe at.
            ms (int): Duration in ms of swipe. This value shouldn't be lower than 300, better if it is higher.
        """
        last_swipe = cls.record.get('last_swipe', [None, 0])

        if last_swipe[0] == (x1, y1, x2, y2, ms):
            if last_swipe[1] >= 35:
                raise GameStuckError
            else:
                last_swipe[1] += 1
        else:
            last_swipe = [(x1, y1, x2, y2, ms), 0]

        cls.record['last_swipe'] = last_swipe
        Utils.check_game_status()
        Adb.u2device.swipe(x1, y1, x2, y2, ms)

    @classmethod
    def find_and_touch(cls, image, similarity=DEFAULT_SIMILARITY, color=False):
        """Finds the image on the screen and touches it if it exists

        Args:
            image (string): Name of the image.
            similarity (float, optional): Defaults to DEFAULT_SIMILARITY.
                Percentage in similarity that the image should at least match.
            color (boolean): find the image in color screen

        Returns:
            bool: True if the image was found and touched, false otherwise
        """
        region = cls.find(image, similarity, color)
        if region is not None:
            cls.touch_randomly(region)
            return True
        return False

    @classmethod
    def random_coord(cls, min_val, max_val):
        """Wrapper method that calls cls._randint() or cls._random_coord() to
        generate the random coordinate between min_val and max_val, depending
        on which return line is enabled.

        Args:
            min_val (int): Minimum value of the random number.
            max_val (int): Maximum value of the random number.

        Returns:
            int: The generated random number
        """
        return cls._randint(min_val, max_val)
        # return cls._randint_gauss(min_val, max_val)

    @staticmethod
    def _randint(min_val, max_val):
        """Method to generate a random value based on the min_val and max_val
        with a uniform distribution.

        Args:
            min_val (int): Minimum value of the random number.
            max_val (int): Maximum value of the random number.

        Returns:
            int: The generated random number
        """
        return randint(min_val, max_val)

    @classmethod
    def filter_similar_coords(cls, coords, distance=50):
        """Filters out coordinates that are close to each other.

        Args:
            coords (array): An array containing the coordinates to be filtered.
            distance (int): minimum distance at which two set of coordinates
                are no longer considered close.

        Returns:
            array: An array containing the filtered coordinates.
        """
        #Logger.log_debug("Coords: " + str(coords))
        filtered_coords = []
        if len(coords) > 0:
            filtered_coords.append(coords[0])
            for coord in coords:
                if cls.find_closest(filtered_coords, coord)[0] > distance:
                    filtered_coords.append(coord)
        Logger.log_debug("Filtered Coords: " + str(filtered_coords))
        return filtered_coords

    @staticmethod
    def find_closest(coords, coord):
        """Utilizes a k-d tree to find the closest coordiante to the specified
        list of coordinates.

        Args:
            coords (array): Array of coordinates to search.
            coord (array): Array containing x and y of the coordinate.

        Returns:
            array: An array containing the distance of the closest coordinate
            in the list of coordinates to the specified coordinate as well the
            index of where it is in the list of coordinates
        """
        return spatial.cKDTree(coords).query(coord)

    @classmethod
    def get_region_color_average(cls, region, hsv=True):
        """
        Get the average color in the region
        :param region: the region to average the color
        :param hsv: return color in HSV if true. BGR otherwise.
        :return:  BGR or HSV color
        """
        crop = cls.color_screen[region.y:region.y + region.h, region.x:region.x + region.w]
        bgr_avg_color = numpy.average(crop, axis=(0, 1)).astype(numpy.uint8)
        bgr_avg_color = numpy.expand_dims(bgr_avg_color, axis=(0, 1))
        if hsv:
            hsv_avg_color = cv2.cvtColor(bgr_avg_color, cv2.COLOR_BGR2HSV)[0, 0, :]
            return hsv_avg_color
        else:
            return bgr_avg_color

    @classmethod
    def reset_record(cls):
        """Reset game records for last touch and swipe."""
        cls.record['last_touch'] = [None, 0]
        cls.record['last_swipe'] = [None, 0]

    @classmethod
    def check_game_status(cls):
        """Check if the game is running; raise an exception if not."""
        if Adb.u2device.app_current()['package'] != 'com.nexon.bluearchive':
            raise GameNotRunningError
        cls.record['game_started'] = True

    @classmethod
    def scan(cls, region, resize=False, color=False, bbox=False):
        """Perform OCR scanning on a given region of the screen.

        Args:
            region (Region): The region to scan.
            resize (bool): Whether to resize the scanned region.
            color (bool): Whether to use color scanning.
            bbox (bool): Whether to include bounding box information in results.

        Returns:
            list: A list of scan results.
        """
        results = []
        crop = cls.color_screen[region.y:region.y + region.h, region.x:region.x + region.w]
        if resize:
            crop = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        data = cls.ocr.detect_and_ocr(crop)
        if data == [[]]:
            raise ReadOCRError
        for entry in data:
            if bbox:
                top_left = entry.box[0]
                bottom_right = entry.box[2]
                # Calculate attributes
                adjusted_x = region.x + top_left[0]
                adjusted_y = region.y + top_left[1]
                adjusted_w = region.x + bottom_right[0] - (top_left[0] + adjusted_x)
                adjusted_h = region.y + bottom_right[1] - (top_left[1] + adjusted_y)
                adjusted_bbox = Region(adjusted_x, adjusted_y, adjusted_h, adjusted_w)
                results.append({'bbox': adjusted_bbox, 'text': entry.ocr_text, 'score': entry.score})
            else:
                results.append({'text': entry.ocr_text, 'score': entry.score})
        return results

    @classmethod
    def find_word(cls, word, region):
        """Find a specific word within a given region.

        Args:
            word (str): The word to search for.
            region (Region): The region to search within.

        Returns:
            tuple: A tuple containing a boolean indicating whether the word was found and the bounding box of the word.
        """
        text = None
        results = cls.scan(region, bbox=True)
        for entry in results:
            bbox, text = entry['bbox'], entry['text']
            if word.lower().replace(" ", "") == text.lower().replace(" ",""):
                return True, bbox
        last_text = text
        return False, last_text

    @classmethod
    def find_button(cls, button, text_region, stage_region, similarity=DEFAULT_SIMILARITY):
        """Find a button's location within a specified region.

        Args:
            button (str): The name of the button.
            text_region (Region): The region containing stage text.
            stage_region (Region): The region containing the stages.
            similarity (float): The similarity threshold for matching.

        Returns:
            Region: The region of the found button.
        """
        button = cv2.imread('assets/{}/{}.png'.format(Utils.assets, button), 0)
        search_region_height = stage_region.h - text_region.h
        if button.shape[0] > abs(search_region_height):
            button = button[:search_region_height, :]
        matches = cv2.matchTemplate(screen, button, cv2.TM_CCOEFF_NORMED)
        matches = numpy.where(matches >= similarity)
        matches = cls.filter_similar_coords(list(zip(matches[1], matches[0])))
        if not matches:
            return None
        match_index = cls.find_closest(matches, [text_region.x, text_region.y])[1]
        match = matches[match_index]
        match_region =  Region(int(match[0]), int(match[1]), button.shape[1], button.shape[0])
        search_region = Region(text_region.x, text_region.y, 1280, search_region_height)
        if search_region.intersection(match_region):
            return match_region
        else:
            return None

    @classmethod
    def find_stage(cls, desired_stage):
        """Find a specific game stage.

        Args:
            desired_stage (str): The name of the desired game stage.

        Returns:
            str or bool: The name of the found stage or False if not found.
        """
        stage_list = Region(677, 132, 747, 678)
        left = (900, 600, 900, 350)
        right = (900, 350, 900, 600)
        detected_stage = False
        old_last_stage = None
        while True:
            cls.wait_update_screen(1)
            detected_stage, new_last_stage = cls.find_word(desired_stage, stage_list)
            if detected_stage == True:
                return new_last_stage
            elif detected_stage == False and old_last_stage == new_last_stage:
                Logger.log_msg('Stage not found. Check spelling.')
                return False
            else:
                if new_last_stage < desired_stage:
                    cls.swipe(*left)
                else:
                    cls.swipe(*right)
                old_last_stage = new_last_stage

    @classmethod
    def sweep(cls, num):
        """Perform a sweep action in the game.

        Args:
            num (int): The number of sweeps to perform.

        Returns:
            tuple: A tuple containing the sweep status and the last current value.
        """
        minus = (835, 300)
        counter = Region(885, 280, 105, 40)
        plus = (1035, 295)
        sweep_status = ('success')
        last_current = None
        if cls.find('farming/stars_required'):
            Logger.log_error('3 stars not achieved. Unable to sweep')
            sweep_status = ('failed')
            return sweep_status
        while True:
            cls.wait_update_screen(1)
            current = cls.scan(counter, resize=True)[0]['text']
            if not current.isdigit():
                raise ReadOCRError
            current = int(current)
            if current == 0:
                sweep_status = ('incomplete', 0)
                return sweep_status
            if current < num:
                if current == last_current:
                    num = current
                    sweep_status = ('incomplete', last_current)
                else:
                    for i in range(num - current):
                        cls.touch(*plus)
                        time.sleep(0.7)
                    last_current = current
                    continue
            if current > num:
                for i in range(current - num):
                    cls.touch(*minus)
                    time.sleep(0.7)
                last_current = current
                continue
            if current == num:
                while True:
                    Utils.update_screen()
                    if Utils.find('farming/sweep'):
                        Utils.touch(940, 400)
                        continue
                    if Utils.find('farming/confirm'):
                        Utils.touch(770, 500)
                        continue
                    if Utils.find('farming/sweep_complete'):
                        if sweep_status[0] == 'success':
                            Logger.log_success('Sweep completed successfully')
                        return sweep_status

class GoTo(object):

    home_subsections = {
    'cafe': {'click_position':(90,660), 'template':'goto/cafe'},
    'club': {'click_position':(560,650), 'template':'goto/club'},
    'tasks': {'click_position':(61,235), 'template':'goto/tasks'},
    'mailbox': {'click_position':(1142,38), 'template':'goto/mailbox'},
    'campaign': {'click_position':(1220,580), 'template':'goto/campaign'}
    }

    campaign_subsections = {
        'mission': {'click_position':(785,155), 'template':'goto/mission'},
        'bounty': {'click_position':(735,430), 'template':'goto/bounty'},
        'scrimmage': {'click_position':(720,600), 'template':'goto/scrimmage'},
        'commissions': {'click_position':(700,505), 'template':'goto/commissions'},
        'tactical_challenge': {'click_position':(1100,500), 'template':'goto/tactical_challenge'}
    }

    home_button = (1235, 21)
    back_button = (55,40)
    skip_confirm_button = (765, 500)
    wake_up_coords = (475, 20) # coords to touch to show widgets/skip lobby in the homescreen
    
    @classmethod
    def home(cls):
        """Navigate to the home screen."""
        while True:
            Utils.wait_update_screen(1)
            if Utils.find('goto/home', color=True):
                break
            elif Utils.find('goto/skip'):
                Utils.touch(*cls.skip_confirm_button)
            else:
                Utils.touch(*cls.home_button)

    @classmethod
    def sub_home(cls, section):
        """Navigate to a subsection of the home screen.

        Args:
            section (str): The name of the subsection.
        """
        waiting_time = 0
        while True:
            Utils.wait_update_screen(1)
            if Utils.find(cls.home_subsections[section]['template'], color=True):
                break
            elif Utils.find('goto/home', color=True):
                Utils.touch(*cls.home_subsections[section]['click_position'])
            elif Utils.find('goto/skip'):
                Utils.touch(*cls.skip_confirm_button)
            elif waiting_time < 5 and not Utils.find('goto/settings'):
                Utils.touch(*cls.wake_up_coords)
                waiting_time += 1
                continue
            elif waiting_time == 5:
                cls.home()
            else:
                Utils.touch(*cls.back_button)
            waiting_time = 0

    @classmethod
    def sub_campaign(cls, section):
        """Navigate to a subsection of the campaign screen.

        Args:
            section (str): The name of the subsection.
        """
        waiting_time = 0
        while True:
            Utils.wait_update_screen(1)
            if Utils.find(cls.campaign_subsections[section]['template'], color=True):
                break
            elif Utils.find('goto/campaign', color=True):
                Utils.touch(*cls.campaign_subsections[section]['click_position'])
            elif Utils.find('goto/home', color=True):
                cls.sub_home('campaign')
            elif Utils.find('goto/skip'):
                Utils.touch(*cls.skip_confirm_button)
            elif waiting_time < 5 and not Utils.find('goto/settings'):
                Utils.touch(*cls.wake_up_coords)
                waiting_time += 1
                continue
            elif waiting_time == 5:
                cls.home()
            else:
                Utils.touch(*cls.back_button)
            waiting_time = 0


    @classmethod
    def event(cls):
        waiting_time = 0
        while True:
            Utils.wait_update_screen(1)
            if Utils.find('goto/event', color=True):
                break
            elif Utils.find_and_touch('goto/event_banner'):
                continue
            elif Utils.find("goto/campaign", color=True):
                Utils.swipe(40,160, 260, 40)
            elif Utils.find('goto/home', color=True):
                cls.sub_home('campaign')
            elif Utils.find('goto/skip'):
                Utils.touch(*cls.skip_confirm_button)
            elif waiting_time < 5 and not Utils.find('goto/settings'):
                Utils.touch(*cls.wake_up_coords)
                waiting_time += 1
                continue
            elif waiting_time == 5:
                cls.home()
            else:
                Utils.touch(*cls.back_button)
            waiting_time = 0