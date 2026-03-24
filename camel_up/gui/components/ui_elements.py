"""
ui_elements.py - Reusable UI widgets
"""
import pygame
from config.settings import COLORS, FONT_NAME

pygame.font.init()

def get_font(size: int):
    try:
        return pygame.font.SysFont(FONT_NAME, size)
    except:
        return pygame.font.SysFont("arial", size)

class Label:
    def __init__(self, x: int, y: int, text: str, size: int=24, color: tuple=COLORS['TEXT']):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = get_font(size)
        
    def draw(self, surface: pygame.Surface):
        img = self.font.render(self.text, True, self.color)
        surface.blit(img, (self.x, self.y))

class Button:
    def __init__(self, x: int, y: int, w: int, h: int, text: str, on_click=None, disabled: bool=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.on_click = on_click
        self.disabled = disabled
        self.font = get_font(20)
        self.hovered = False
        
    def update(self, event: pygame.event.Event):
        if self.disabled:
             return
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.on_click:
                self.on_click()
                
    def draw(self, surface: pygame.Surface):
        color = COLORS['BUTTON_DISABLED'] if self.disabled else (COLORS['BUTTON_HOVER'] if self.hovered else COLORS['BUTTON'])
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLORS['BLACK'], self.rect, 2, border_radius=5)
        
        text_color = COLORS['BLACK'] if self.disabled else COLORS['TEXT']
        img = self.font.render(self.text, True, text_color)
        text_rect = img.get_rect(center=self.rect.center)
        surface.blit(img, text_rect)

class TextInput:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.font = get_font(24)

    def update(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key != pygame.K_RETURN:
                if len(self.text) < 15:
                    self.text += event.unicode
                    
    def draw(self, surface: pygame.Surface):
        color = COLORS['HIGHLIGHT'] if self.active else COLORS['BUTTON']
        pygame.draw.rect(surface, COLORS['WHITE'], self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        
        img = self.font.render(self.text, True, COLORS['TEXT'])
        surface.blit(img, (self.rect.x + 5, self.rect.y + 5))

class Panel:
    def __init__(self, x: int, y: int, w: int, h: int, color: tuple=COLORS['PANEL']):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['BLACK'], self.rect, 2, border_radius=10)
