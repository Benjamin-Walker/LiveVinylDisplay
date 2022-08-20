from scipy.io.wavfile import write
import sounddevice as sd
import pygame
from ShazamAPI import Shazam
import requests
from PIL import Image, ImageFilter, ImageEnhance
from pygame.locals import *
import os
import io

if __name__ == '__main__':

    os.environ["DISPLAY"] = ":0"
    pygame.init()

    "Set screen"
    # screen = pygame.display.set_mode((1280, 1024), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((1280, 1024))
    "Fill background"
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))

    fs = 44100  # this is the frequency sampling; also: 4999, 64000
    seconds = 10  # Duration of recording

    count = 0
    rest_time = 3

    img_size = (850, 850)
    background_size = (1280, 1024)

    img_loaded_size = img_size
    background_loaded_size = background_size

    img = Image.open('retro_november.jpg')
    img = img.resize(background_size)
    img_screen = pygame.image.fromstring(img.tobytes("raw", 'RGB'),
                                         background_loaded_size, 'RGB')
    img_screen = pygame.transform.scale(img_screen, background_size)
    screen.blit(img_screen, (0, 0))
    song_detect = False

    pygame.display.update()

    ident = ''
    title = ''
    artist = ''

    running = True

    while running:

        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        print("Recording")
        sd.wait()  # Wait until recording is finished
        print("Finished")
        if myrecording.max() > 0.02:
            bytes_wav = bytes()
            byte_io = io.BytesIO(bytes_wav)
            write(byte_io, fs, myrecording)
            shazam = Shazam(byte_io.read())
            recognize_generator = shazam.recognizeSong()
            data = next(recognize_generator)

            if len(data[1]['matches']) == 0:
                print('no song detected')
                count += 1
                if count > rest_time:
                    song_detect = False
            else:
                title = data[1]['track']['title']
                artist = data[1]['track']['subtitle']
                response = requests.get(data[1]['track']['images']['coverarthq'])
                img = Image.open(io.BytesIO(response.content))
                # Applying GaussianBlur filter
                blur = img.filter(ImageFilter.GaussianBlur(10))
                enhancer = ImageEnhance.Brightness(blur)
                blur = enhancer.enhance(0.8)
                count = 0
                img_loaded_size = img.size
                background_loaded_size = blur.size
                song_detect = True
        else:
            print('no noise detected')
            count += 1
            if count > rest_time:
                song_detect = False

        if song_detect:
            screen.fill((0, 0, 0))
            background_screen = pygame.image.fromstring(blur.tobytes("raw", 'RGB'), img_loaded_size, 'RGB')
            background_screen = pygame.transform.scale(background_screen, background_size)
            screen.blit(background_screen, (0, 0))
            img_screen = pygame.image.fromstring(img.tobytes("raw", 'RGB'), background_loaded_size, 'RGB')
            img_screen = pygame.transform.scale(img_screen, img_size)
            screen.blit(img_screen, (215, 25))

            font = pygame.font.Font('freesansbold.ttf', 46)
            text = font.render(title, True, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = (640, 925)
            screen.blit(text, textRect)

            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render(artist, True, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = (640, 975)
            screen.blit(text, textRect)
        else:
            img = Image.open('retro_november.jpg')
            img = img.resize((1280, 1024))
            img_loaded_size = img.size
            img_screen = pygame.image.fromstring(img.tobytes("raw", 'RGB'),
                                                 img_loaded_size, 'RGB')
            img_screen = pygame.transform.scale(img_screen, background_size)
            screen.blit(img_screen, (0, 0))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    running = False

    pygame.quit()