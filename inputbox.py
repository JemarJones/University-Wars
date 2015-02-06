# by Timothy Downs, inputbox written for my map editor
#(Capitilization, string length limiting, and bareable aesthetics added by Jemar Jones)

# A program to get user input, allowing backspace etc
# shown in a box in the middle of the screen
# Called by:
# import inputbox
# answer = inputbox.ask(screen, "Your name")
#
# Only near the center of the screen is blitted to

import pygame, pygame.font, pygame.event, pygame.draw, string
from pygame.locals import *

def get_key():
  while 1:
    event = pygame.event.poll()
    if event.type == KEYDOWN:
      return event.key
    else:
      pass

def display_box(screen, message,backcolor = (0,0,0),fontsize = 14, divisor = 2):
  "Print a message in a box in the middle of the screen"
  fontobject = pygame.font.SysFont("monospace", fontsize )
  pygame.draw.rect(screen, backcolor,
                   ((screen.get_width() / divisor),
                    (screen.get_height() / 2) - 10,
                    270,20), 0)
  if len(message) != 0:
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / divisor) - 125, (screen.get_height() / 2) - 10))
  pygame.display.flip()

def ask(screen, question,backcolor = (0,0,0),fontsize = 14,divisor = 2):
  "ask(screen, question) -> answer"
  pygame.font.init()
  current_string = []
  display_box(screen, question + ": " + string.join(current_string,""),backcolor,fontsize,divisor)
  while 1:
    cap = False
    letterEntered = False
    inkey = get_key()
    if inkey == K_BACKSPACE:
      current_string = current_string[0:-1]
    elif inkey == K_RETURN:
      break
    elif inkey <= 127:
      if len(current_string) <= 7:
        current_string.append(chr(inkey))
        letterEntered = True
    if letterEntered and (pygame.key.get_mods() & KMOD_SHIFT or pygame.key.get_mods() & KMOD_CAPS):
      current_string[-1] = current_string[-1].upper()
    display_box(screen,"                                                                ")
    display_box(screen, question + ": " + string.join(current_string,""),backcolor,fontsize,divisor)
  return string.join(current_string,"")

