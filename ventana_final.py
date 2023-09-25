import pygame
import sys
import time
import asyncio

class VentanaFinal:
    def __init__(self, score):
        self.score = score

        pygame.mixer.init()

        self.inicio_sound = pygame.mixer.Sound("sfx/inicio.ogg")
        self.final_sound = pygame.mixer.Sound("sfx/final.ogg")
        self.sound_timer = time.time()


    async def reiniciar(self):
        pygame.init()
        pygame.mixer.init()

        pantalla = pygame.display.set_mode((1200, 600))
        pygame.display.set_caption("Game Over")

        self.final_sound.play()
        self.inicio_sound.play()

        font = pygame.font.Font(None, 70)
        texto_score = font.render(f"Has muerto, tu score es: {self.score}", True, (255, 0, 0))
        texto_enter = font.render("Presiona ENTER para reiniciar", True, (255, 0, 0))
        fondo = pygame.image.load("gfx/final.jpg")
        fondo = pygame.transform.scale(fondo, (1200, 600))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:

                        self.final_sound.stop()
                        self.inicio_sound.stop()
                        pygame.mixer.stop()

                        pygame.quit()
                        return True  # El usuario presionó ENTER para reiniciar

            pantalla.blit(fondo, (0, 0))
            pantalla.blit(texto_score, (200, 200))
            pantalla.blit(texto_enter, (200, 300))
            pygame.display.update()
        
            await asyncio.sleep(0)
        
        await asyncio.sleep(0.1)
        self.final_sound.stop()
        self.inicio_sound.stop()
        pygame.mixer.stop()