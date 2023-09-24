import asyncio
from ventana_inicio import VentanaInicio
from shooter import Shooter
from juego import Juego
from ventana_final import VentanaFinal

async def jugar():
    ventana_inicio = VentanaInicio()
    entrada = await ventana_inicio.mostrar_pantalla_inicio()
    nombre, dificultad = entrada
    
    shooter = Shooter(nombre, dificultad)

    juego = Juego(shooter)
    score = await juego.iniciar()
    
    ventana_final = VentanaFinal(score)
    reiniciar = await ventana_final.reiniciar()

    if  reiniciar:
       await jugar()

if __name__ == "__main__":
    asyncio.run(jugar())