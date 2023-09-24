import pygame
import math
import time
import sys


#Clase bala
class Bala:
    def __init__(self, x, y, target_x, target_y, velocidad):
        self.x = x
        self.y = y
        self.velocidad = velocidad

        dx = target_x - x
        dy = target_y - y
        distancia = math.sqrt(dx ** 2 + dy ** 2)
        if distancia == 0:
            distancia = 1 
        self.dx = dx / distancia * velocidad
        self.dy = dy / distancia * velocidad

    def mover(self):
        self.x += self.dx
        self.y += self.dy

    def dibujar(self, ventana):
        pygame.draw.circle(ventana, (255, 0, 0), (int(self.x), int(self.y)), 5)

#Juego
class Juego:
    def __init__(self, shooter):
        self.shooter = shooter
        self.estado = True

        self.juego_sound = pygame.mixer.Sound("./sound/juego.ogg")
        self.zombie_sound = pygame.mixer.Sound("./sound/zombie.ogg")
        self.disparo_sound = pygame.mixer.Sound("./sound/disparo.ogg")
        self.recarga_sound = pygame.mixer.Sound("./sound/recarga.ogg")

        self.zombie_sound_timer = time.time()

        self.principal_sound_timer = time.time()

        #Tamaño de la ventana
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 600

        self.miraX = 550
        self.miraY = 200;

        self.mira_img = pygame.image.load("./img/crosshair.png")
        self.mira_img = pygame.transform.scale(self.mira_img, (50, 50))

        self.shooter_img_original = pygame.image.load(self.shooter.img)
        self.shooter_img_original = pygame.transform.scale(self.shooter_img_original, (50, 50))
        self.shooter_img = self.shooter_img_original

        self.recarga_duracion = self.shooter.tiempoRecarga()
        self.recarga_tiempo = 0

        self.duracion_disparo = 0.05
        self.tiempo_disparo = 0

        self.duracion_generacion_z = 0.5
        self.tiempo_ultimo_z = 0

        self.balas = []
        self.zombies = []

    # Información en la ventana
    def mostrar_info(self, ventana):
        font = pygame.font.Font(None, 36)
        vida_text = font.render(f"Vida: {self.shooter.vida}", True, (255, 255, 255))
        municion_text = font.render(f"Municion: {self.shooter.municion}", True, (255, 255, 255))
        puntaje_text = font.render(f"Puntaje: {self.shooter.score}", True, (255, 255, 255))

        ventana.blit(vida_text, (10, 10))  # Posición de la barra de vida
        ventana.blit(municion_text, (10, 50))  # Posición de la munición
        ventana.blit(puntaje_text, (10, 90))  # Posición del puntaje

    def moverShooter(self, ventana):
        # Manejo de eventos de teclado
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.shooter.moverIzquierda()
            if self.shooter.x < 0:
                self.shooter.x = 0  # Limita el movimiento hacia la izquierda
        if keys[pygame.K_RIGHT]:
            self.shooter.moverDerecha()
            if self.shooter.x + 50 > self.SCREEN_WIDTH:
                self.shooter.x = self.SCREEN_WIDTH - 50  # Limita el movimiento hacia la derecha

        # Dibuja al shooter en su posición actual
        shooter_x = self.shooter.x
        shooter_y = self.shooter.y
        shooter_img = pygame.image.load(self.shooter.img)
        shooter_img = pygame.transform.scale(shooter_img, (50, 50))

        # Dibuja el nombre del personaje arriba de él
        font = pygame.font.Font(None, 36)
        nombre_text = font.render(self.shooter.nombre, True, (255, 255, 255))
        nombre_rect = nombre_text.get_rect(center=(shooter_x + 25, shooter_y - 20))

        ventana.blit(nombre_text, nombre_rect)

    def disparar(self, ventana): 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.tiempo_disparo == 0:
                self.tiempo_disparo = time.time()

            tiempo_actual = time.time()
            tiempo_transcurrido = tiempo_actual - self.tiempo_disparo
            
            if self.shooter.municion > 0 and tiempo_transcurrido >= self.duracion_disparo:
                # Crear una nueva bala desde la posición del jugador hacia la mira
                nueva_bala = Bala(self.shooter.x+25, self.shooter.y+20, self.miraX, self.miraY, velocidad=100)
                self.balas.append(nueva_bala)
                self.shooter.disparar()
                self.disparo_sound.play()
                self.actualizar_info(ventana)
                self.tiempo_disparo = 0

    def recargar(self, ventana):
        if self.shooter.municion <= 0:
            if self.recarga_tiempo == 0:
                self.recarga_tiempo = time.time()

            tiempo_actual = time.time()
            tiempo_transcurrido = tiempo_actual - self.recarga_tiempo

            # Comprobar si ya se ha pasado suficiente tiempo para recargar
            if tiempo_transcurrido >= self.recarga_duracion:
                self.recarga_tiempo = 0
                self.shooter.recargar()
                self.recarga_sound.play()
                self.actualizar_info(ventana)
            else:
                self.mostrar_recargando(ventana)

    def mostrar_recargando(self, ventana):
        font = pygame.font.Font(None, 36)
        recargando_text = font.render("Recargando...", True, (255, 0, 0))
        text_rect = recargando_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
        ventana.blit(recargando_text, text_rect)
    
    def actualizar_balas(self):
        for bala in self.balas:
            bala.mover()
            # Eliminar la bala cuando alcance el borde derecho de la pantalla
            if bala.x > self.SCREEN_WIDTH:
                self.balas.remove(bala)
            else:
                # Verificar colisiones con zombies
                for zombie in self.zombies:
                    if bala.x < zombie.x + 50 and bala.x + 10 > zombie.x and \
                    bala.y < zombie.y + 50 and bala.y + 10 > zombie.y:
                        # Si la bala colisiona con un zombie, elimina la bala y el zombie
                        self.balas.remove(bala)
                        self.zombies.remove(zombie)

                        self.shooter.score += 1 
                        break

    def dibujar_balas(self, ventana):
        for bala in self.balas:
            bala.dibujar(ventana)

    def actualizar_info(self, ventana):
        # Llama a la función para mostrar la información
        self.mostrar_info(ventana)

        # Actualiza la posición del shooter
        self.moverShooter(ventana)

    def rotarShooter(self, ventana):
        # Calcular el ángulo entre el shooter y la mira
        dx = self.miraX - self.shooter.x
        dy = self.miraY - self.shooter.y
        angulo = math.degrees(math.atan2(-dy, dx))  # -dy porque la coordenada Y crece hacia abajo en la pantalla

        # Rotar la imagen del shooter
        self.shooter_img = pygame.transform.rotate(self.shooter_img_original, angulo - 70)

        # Obtener un nuevo rectángulo para la imagen rotada
        rect = self.shooter_img.get_rect(center=(self.shooter.x + 25, self.shooter.y + 25))

        # Dibujar la imagen rotada en la posición correcta
        ventana.blit(self.shooter_img, rect.topleft)

    def apuntar(self, ventana):
        # Detectar eventos de movimiento del mouse
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                # Obtener la posición del mouse en movimiento
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.miraX, self.miraY = mouse_x, mouse_y

        # Dibujar la mira usando la imagen cargada previamente
        ventana.blit(self.mira_img, (self.miraX - 25, self.miraY - 25))

    def generarZombie(self, ventana):
        if self.tiempo_ultimo_z == 0:
            self.tiempo_ultimo_z = time.time()

        tiempo_actual = time.time()
        tiempo_transcurrido = tiempo_actual - self.tiempo_ultimo_z

        # Comprobar si ya se ha pasado suficiente tiempo para generar un zombie
        if tiempo_transcurrido >= self.duracion_generacion_z:
            self.tiempo_ultimo_z = tiempo_actual  # Actualizar el tiempo del último zombie generado

            # Crear un nuevo zombie y agregarlo a la lista de zombies
            nuevo_zombie = Zombie(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.shooter.dificultad, self.shooter)
            self.zombies.append(nuevo_zombie)

    def actualizar_zombies(self, ventana):
        for zombie in self.zombies:
            zombie.mover()
            # Eliminar el zombie cuando salga de la pantalla
            if zombie.y > self.SCREEN_HEIGHT:
                self.zombies.remove(zombie)
            # Verificar colisión con el shooter
            if zombie.x < self.shooter.x + 50 and zombie.x + 50 > self.shooter.x and \
            zombie.y < self.shooter.y + 50 and zombie.y + 50 > self.shooter.y:
                self.shooter.recibirDano(zombie.damage)
                self.zombies.remove(zombie)

    def dibujar_zombies(self, ventana):
        for zombie in self.zombies:
            zombie.dibujar(ventana)

    def verificarEstado(self):
        if self.shooter.vida <= 0:
            return False
        else:
            return True

    def repetirSonidos(self):
        if (time.time() - self.zombie_sound_timer) >= 20:
            self.zombie_sound.play()
            self.zombie_sound_timer = time.time()
        
        if (time.time() - self.principal_sound_timer) >= 121:
            self.juego_sound.play()
            self.principal_sound_timer = time.time()

    def iniciar(self):
        pygame.init()
        pygame.mixer.init()

        self.juego_sound.play()

        # Instancia de la ventana
        ventana = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Zombie Shooter")

        while self.estado:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.estado = False

            ventana.fill((100, 100, 100))  # Fondo negro

            # Llama a la función para mostrar la información

            self.estado = self.verificarEstado()

            self.repetirSonidos()

            self.generarZombie(ventana)

            self.actualizar_zombies(ventana)

            self.dibujar_zombies(ventana)

            self.mostrar_info(ventana)

            self.apuntar(ventana)

            self.rotarShooter(ventana)

            self.disparar(ventana)

            self.recargar(ventana)

            self.actualizar_balas()

            self.dibujar_balas(ventana)

            self.moverShooter(ventana)

            # Actualiza la ventana para mostrar los cambios
            pygame.display.flip()
        
        self.juego_sound.stop()
        
        pygame.quit()
        return self.shooter.score
    
#Shoter
class Shooter:
    def __init__(self, nombre, dificultad):
        if nombre and nombre != "":
            self.nombre = nombre
        else:
            self.nombre = "Guest"

        self.x = 550
        self.y = 280
        self.vida = 100
        self.img = './img/shooter.png'
        self.dificultad = dificultad
        self.score = 0
        self.municion = None
        
        if dificultad == "Fácil":
            self.municion = 30
        elif dificultad == "Medio":
            self.municion = 25
        elif dificultad == "Difícil":
            self.municion = 20
        elif dificultad == "Infierno":
            self.municion = 10

    def moverDerecha(self):
        if self.dificultad in ["Fácil", "Medio"]:
            self.x = self.x + 10
        elif self.dificultad == "Difícil":
            self.x = self.x + 8
        elif self.dificultad == "Infierno":
            self.x = self.x + 8

    def moverIzquierda(self):
        if self.dificultad in ["Fácil", "Medio"]:
            self.x = self.x - 10
        elif self.dificultad == "Difícil":
            self.x = self.x - 8
        elif self.dificultad == "Infierno":
            self.x = self.x - 8

    def disparar(self):
        if self.municion > 0:
            self.municion = self.municion - 1
            return 0
        else:
            return self.recargar()

    def recargar(self):
        if self.dificultad == "Fácil":
            self.municion = 30
        elif self.dificultad == "Medio":
            self.municion = 25
        elif self.dificultad == "Difícil":
            self.municion = 20
        elif self.dificultad == "Infierno":
            self.municion = 10
    
    def tiempoRecarga(self):
        if self.dificultad == "Fácil":
            return 1
        elif self.dificultad == "Medio":
            return 2
        elif self.dificultad == "Difícil":
            return 3
        elif self.dificultad == "Infierno":
            return 4

    def estado(self):
        estado_shooter = {
            "nombre": self.nombre,
            "x": self.x,
            "y": self.y,
            "vida": self.vida,
            "dificultad": self.dificultad,
            "score": self.score,
            "municion": self.municion
        }
        return estado_shooter
    
    def recibirDano(self, cantidad):
        self.vida -= cantidad

#Zombie
import pygame
import random

class Zombie:
    def __init__(self, screen_width, screen_height, dificultad, target):
        self.x = random.randint(0, screen_width)  # Valor aleatorio entre 0 y el ancho de la pantalla
        self.y = random.choice([0, screen_height])  # Genera en la parte superior o inferior de la pantalla
        self.velocidad = 1
        self.damage = 0
        self.image = "./img/zombie.png"
        self.target = target

        if dificultad == "Fácil":
            self.velocidad += 1
            self.damage += 5
        elif dificultad == "Medio":
            self.velocidad += 2
            self.damage += 10
        elif dificultad == "Difícil":
            self.velocidad += 3
            self.damage += 25
        elif dificultad == "Infierno":
            self.velocidad = 5
            self.damage += 25

    def mover(self):
        # Calcula la dirección hacia la que debe moverse el zombie para perseguir al objetivo (target)
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distancia = max(1, abs(dx) + abs(dy))  # Evita la división por cero
        direccion_x = dx / distancia
        direccion_y = dy / distancia

        # Actualiza la posición del zombie en función de la dirección calculada
        self.x += direccion_x * self.velocidad
        self.y += direccion_y * self.velocidad

    def dibujar(self, ventana):
        # Carga la imagen del zombie y la dibuja en la posición actual
        zombie_img = pygame.image.load(self.image)
        zombie_img = pygame.transform.scale(zombie_img, (50, 50))
        ventana.blit(zombie_img, (self.x, self.y))

#Ventana final
class VentanaFinal:
    def __init__(self, score):
        self.score = score

        pygame.mixer.init()

        self.inicio_sound = pygame.mixer.Sound("./sound/inicio.ogg")
        self.final_sound = pygame.mixer.Sound("./sound/final.ogg")
        self.sound_timer = time.time()


    def reiniciar(self):
        pygame.init()

        pantalla = pygame.display.set_mode((1200, 600))
        pygame.display.set_caption("Game Over")

        self.final_sound.play()
        self.inicio_sound.play()

        font = pygame.font.Font(None, 70)
        texto_score = font.render(f"Has muerto, tu score es: {self.score}", True, (255, 0, 0))
        texto_enter = font.render("Presiona ENTER para reiniciar", True, (255, 0, 0))
        fondo = pygame.image.load("./img/final.jpg")
        fondo = pygame.transform.scale(fondo, (1200, 600))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.quit()
                        return True  # El usuario presionó ENTER para reiniciar

            pantalla.blit(fondo, (0, 0))
            pantalla.blit(texto_score, (200, 200))
            pantalla.blit(texto_enter, (200, 300))
            pygame.display.update()

        self.final_sound.stop()
        self.inicio_sound.stop()

#Ventana Inicio
class VentanaInicio:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Constantes
        SCREEN_WIDTH = 1200
        SCREEN_HEIGHT = 600

        self.inicio_sound = pygame.mixer.Sound("./sound/inicio.ogg")
        self.sound_timer = time.time()

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.FONT = pygame.font.Font(None, 36)

        # Inicialización de la pantalla
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Zoombie Shooter")

        # Cargar la imagen de fondo
        self.fondo = pygame.image.load('./img/fondo.jpg')
        self.fondo = pygame.transform.scale(self.fondo, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Campo de entrada de texto
        self.input_text = ""
        self.input_rect = pygame.Rect(400, 200, 400, 40)
        self.input_color = pygame.Color(self.BLACK)
        self.input_active = False

        # Variables para los botones de dificultad
        self.dificultades = ["Fácil", "Medio", "Difícil", "Infierno"]
        self.selected_difficulty = "Fácil"
        self.button_font = pygame.font.Font(None, 32)
        self.buttons = []

        # Almacenar la entrada del usuario
        self.entrada = None

        # Bandera para cerrar la ventana
        self.cerrar_ventana = False

    # Función para manejar el campo de entrada de texto
    def control_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    # Realiza alguna acción con el texto ingresado (por ejemplo, almacenarlo en 'nombre')
                    self.nombre = self.input_text
                    self.input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    self.input_text += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Verificar si se hizo clic en el campo de entrada de texto
            if self.input_rect.collidepoint(event.pos):
                self.input_active = not self.input_active
            else:
                self.input_active = False

    # Función para manejar los eventos de los botones de dificultad
    def handle_button_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button, difficulty in self.buttons:
                if button.collidepoint(event.pos):
                    self.selected_difficulty = difficulty

    # Función para crear botones de dificultad
    def create_difficulty_buttons(self):
        button_width, button_height = 200, 50
        x, y = 200, 300

        for difficulty in self.dificultades:
            button_rect = pygame.Rect(x, y, button_width, button_height)
            self.buttons.append((button_rect, difficulty))
            x += button_width + 20

    # Función para mostrar los botones de dificultad
    def draw_difficulty_buttons(self):
        for button, difficulty in self.buttons:
            if self.selected_difficulty == difficulty:
                color = (255, 0, 0)  # Rojo para el botón seleccionado
            else:
                color = self.BLACK

            pygame.draw.rect(self.screen, color, button)
            pygame.draw.rect(self.screen, self.WHITE, button, 2)

            text = self.button_font.render(difficulty, True, self.WHITE if color != self.WHITE else self.BLACK)
            text_rect = text.get_rect(center=button.center)
            self.screen.blit(text, text_rect)

    def repetirSonido(self):
        if (time.time() - self.sound_timer) >= 86:
            self.inicio_sound.play()
            self.sound_timer = time.time()

    # Función para mostrar la pantalla de inicio
    def mostrar_pantalla_inicio(self):
        self.create_difficulty_buttons()

        self.inicio_sound.play()
        
        while not self.cerrar_ventana:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                self.control_input(event)
                self.handle_button_events(event)

            self.screen.blit(self.fondo, (0, 0))
            self.mostrar_mensaje("Bienvenido al juego", 450, 40)
            self.mostrar_mensaje("Ingrese su Nombre:", 400, 160)

            pygame.draw.rect(self.screen, self.input_color, self.input_rect, 2)
            text_surface = self.FONT.render(self.input_text, True, self.WHITE)
            self.screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))

            self.draw_difficulty_buttons()

            self.repetirSonido()

            if self.selected_difficulty:
                self.mostrar_mensaje(f"Dificultad seleccionada: {self.selected_difficulty}", 450, 400)
            
            self.mostrar_mensaje("Presiona Enter Para Comenzar a Jugar", 350, 500)

            pygame.display.update()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.input_text:
                    self.entrada = (self.input_text, self.selected_difficulty)
                else:
                    self.entrada = ("Guest", self.selected_difficulty)
                self.cerrar_ventana = True

            # Verificar si el usuario presionó Enter y devolver los datos
            if self.entrada:
                self.inicio_sound.stop()
                return self.entrada

    # Función para mostrar un mensaje en pantalla
    def mostrar_mensaje(self, texto, x, y):
        mensaje = self.FONT.render(texto, True, self.WHITE)
        self.screen.blit(mensaje, (x, y))

#MAIN
def inicio():
    ventana_inicio = VentanaInicio()
    entrada = ventana_inicio.mostrar_pantalla_inicio()
    nombre, dificultad = entrada
    
    shooter = Shooter(nombre, dificultad)

    juego = Juego(shooter)
    score = juego.iniciar()
    
    ventana_final = VentanaFinal(score)
    reiniciar = ventana_final.reiniciar()

    if  reiniciar == True:
       inicio()
 
if __name__ == "__main__":
    inicio()