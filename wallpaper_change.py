import sys
import time, spotipy, numpy, requests, ctypes, os, python_utils
import cv2,spotipy
from PIL import Image
import numpy as np

# Universal values
SPOTIPY_CLIENT_ID = "33bef6aa56ac42c2a2583fce959d5a31"
SPOTIPY_CLIENT_SECRET = "42059ccc9ead41d5aedf3210b9b9f047"
username = "gurashish"
scope = "user-read-currently-playing"
redirect_uri = "http://localhost:8080/"


# Does the spotify aythentication and stuff. returns the spotipy spotify object.
def spotify_auth():
    """
    Does theconnection stuff regarding both spotify and spotipy
    :return: Spotify object
    """
    sp_oauth = spotipy.SpotifyOAuth(
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=".cache",
        show_dialog=True
    )
    token_info = sp_oauth.get_cached_token()
    if token_info:
        print ('Found cached token!')
        access_token = token_info['access_token']
    else:
        print('Cached Token not found!')

    try:
        sp = spotipy.Spotify(auth=access_token)
        return sp, token_info
        # print(sp.current_user_playing_track())
        # return spotipy.Spotify(auth=token), sp_oauth, token_info
    except:
        print("User token could not be created")
        sys.exit()

# method to refresh token
def refresh_token(token_info):
    """
    Method to refresh the token.
    :param token_info: token we use to get all the data.
    :return: None
    """
    sp_oauth = spotipy.SpotifyOAuth(
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=".cache",
        show_dialog=True
    )
    try:
        if  sp_oauth.is_token_expired(token_info=token_info):
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
            token = token_info['access_token']
            sp = spotipy.Spotify(auth=token)
            print("TOKEN REFRESHED")
    except:
        print("FAILED TO REFRESH TOKEN")

# return the list of the info about a song
def current_playing_song_info(sp):
    """
    Returns the list containing info about the song.
    ex- ['https://i.scdn.co/image/ab67616d0000b273eedabed826eeb6506a4c700d', 'OneRepublic', 'Oh My My', 'Born']
    :param sp: Spotify object
    :return: List containing song info
    """
    info_lst = []
    track = sp.current_user_playing_track()
    artist = track["item"]["artists"][0]["name"]
    album = track["item"]["album"]["name"]
    song = track["item"]["name"]
    img_url = track["item"]["album"]["images"][0]["url"]
    info_lst.extend([img_url,artist,album,song])
    # print(info_lst)
    # print(img_url)
    # print('IS PLAYING = ' + str(track["is_playing"]))
    # print(artist)
    # print(album)
    # print(song)
    return info_lst

# Download the image from the url given.
def download_album_art(img_url):
    """
    Downloads the img from the img url provided.
    :param img_url: String
    :return: None
    """
    Picture_request = requests.get(img_url)
    if Picture_request.status_code == 200:
        with open("default.jpg", 'wb') as f:
            f.write(Picture_request.content)

# returns the bgr values of the dominant color
def get_dominant_color():
    """
    returns the list of bgr values of the dominant color of song art. With b representing blue
    g representing green and r representing red.
    :return:List of bgr values
    """
    img = cv2.imread('default.jpg', cv2.IMREAD_UNCHANGED)

    data = np.reshape(img, (-1, 3))
    print(data.shape)
    data = np.float32(data)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    compactness, labels, centers = cv2.kmeans(data, 1, None, criteria, 10, flags)
    color_lst = centers[0].astype(np.int32)
    print('Dominant color is: bgr({})'.format(centers[0].astype(np.int32)))
    return color_lst

#Creates a 1080p background image with the most dominant colour of the album art
def create_background(bgr):
    """
    Creates a 1080p background image with the most dominant colour of the album
    art.
    :param bgr: List
    :return: Doesn't return. Overwrites a background.jpg file.
    """
    red, green, blue = bgr[2], bgr[1], bgr[0]
    w, h = 1080, 1920
    array = np.zeros([w, h, 3], dtype=np.uint8)
    array[:] = [red, green, blue]  # this takes the rgb format. SO need to convert from bgr to rgb
    img = Image.fromarray(array)
    img.save('background.jpg')

# Creates the final wallpaper
def create_album_wallpaper():
    """
    Creates the final wallpaper as a out.jpg file.
    :return: None. Changes the wallpaper
    """
    image_background = Image.open('background.jpg')
    bg_w, bg_h = image_background.size

    image_foreground = Image.open('default.jpg')
    fg_w, fg_h = image_foreground.size
    offset = ((bg_w - fg_w) // 2, (bg_h - fg_h) // 2)
    image_background.paste(image_foreground, offset)
    image_background.save('out.jpg')
    print('Album background created')

# changes the desktop wallpaper to the image path provided
def setWallpaper():
    # the below code only works for 64 bit windows.
    abs_path = os.path.abspath("out.jpg")
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, abs_path, 3)
    print('Wallpaper changed')

if __name__ == "__main__":
    sp, token_info = spotify_auth()
    song = ''
    while(1):
        songInfoList = current_playing_song_info(sp)
        if (song == songInfoList[3]):
            time.sleep(2)
            continue
        else :
            download_album_art(songInfoList[0])
            bgr_values = get_dominant_color()           #rbgr_Values is a list.
            create_background(bgr_values)
            create_album_wallpaper()
            setWallpaper()
            song= songInfoList[3]
            time.sleep(2)
