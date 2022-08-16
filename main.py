from scipy.io.wavfile import write
import sounddevice as sd
import pygame
from ShazamAPI import Shazam
import requests
from PIL import Image, ImageFilter, ImageEnhance
from pygame.locals import *
import os

if __name__ == '__main__':

    os.environ["DISPLAY"] = ":0"
    pygame.init()

    "Set screen"
    screen = pygame.display.set_mode((1280, 1024), pygame.FULLSCREEN)

    "Fill background"
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))

    fs = 44100  # this is the frequency sampling; also: 4999, 64000
    seconds = 10  # Duration of recording

    count = 0
    rest_time = 3

    img = Image.open('please-stand-by.jpg')
    img = img.resize((850, 850))
    img.save('coverart.jpg')
    blur = img.filter(ImageFilter.GaussianBlur(5))
    blur = blur.resize((1280, 1024))
    enhancer = ImageEnhance.Brightness(blur)
    blur = enhancer.enhance(0.8)
    blur.save('blur.jpg')

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
            write('output.wav', fs, myrecording)  # Save as WAV file

            mp3_file_content_to_recognize = open('output.wav', 'rb').read()
            shazam = Shazam(mp3_file_content_to_recognize)
            recognize_generator = shazam.recognizeSong()
            data = next(recognize_generator)

            if len(data[1]['matches']) == 0:
                print('no song detected')
                count += 1
            else:
                title = data[1]['track']['title']
                artist = data[1]['track']['subtitle']
                coverart = requests.get(data[1]['track']['images']['coverarthq']).content
                with open('coverart.jpg', 'wb') as handler:
                    handler.write(coverart)
                img = Image.open('coverart.jpg')
                # Applying GaussianBlur filter
                blur = img.filter(ImageFilter.GaussianBlur(10))
                enhancer = ImageEnhance.Brightness(blur)
                blur = enhancer.enhance(0.8)
                blur.save('blur.jpg')
                count = 0
        else:
            print('no noise detected')
            count += 1

        if count < rest_time:
            screen.fill((0, 0, 0))
            blur = pygame.image.load("blur.jpg").convert_alpha()
            blur = pygame.transform.scale(blur, (1280, 1024))
            screen.blit(blur, (0, 0))
            img = pygame.image.load("coverart.jpg").convert_alpha()
            img = pygame.transform.scale(img, (850, 850))
            screen.blit(img, (215, 25))

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
            img = Image.open('please-stand-by.jpg')
            img = img.resize((850, 850))
            blur = img.filter(ImageFilter.GaussianBlur(5))
            blur = blur.resize((1280, 1024))
            enhancer = ImageEnhance.Brightness(blur)
            blur = enhancer.enhance(0.8)
            blur.save('blur.jpg')
            img.save('coverart.jpg')

            screen.fill((0, 0, 0))
            blur = pygame.image.load("blur.jpg").convert_alpha()
            blur = pygame.transform.scale(blur, (1280, 1024))
            screen.blit(blur, (0, 0))
            img_ = pygame.image.load("coverart.jpg").convert_alpha()
            screen.blit(img_, (215, 25))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    running = False

    pygame.quit()