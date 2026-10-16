# Cuatro pruebas visuales del llenado

Ejemplos generados con el motor PDF del programa sobre una plantilla de demostración. Todos los datos, el logo y las firmas son ficticios. No son imágenes creadas con inteligencia artificial ni copias de documentos privados. Las fuentes disponibles aquí pueden diferir de las instaladas en Windows.

[Ver las cuatro pruebas juntas](pruebas-visuales/00-todas-las-pruebas.png)

## 1. Dirección corta

Una línea a 9 puntos, alineada a la derecha.

![Dirección corta](pruebas-visuales/01-direccion-corta.png)

## 2. Dirección larga

Tres líneas a 8.25 puntos, alineadas a la derecha, dentro de su espacio.

![Dirección larga](pruebas-visuales/02-direccion-larga.png)

## 3. Razón social larga

Empresa en tres líneas a 9 puntos; dirección en dos líneas. También se conserva el cero inicial del número E-00007.

![Razón social larga](pruebas-visuales/03-razon-social-larga.png)

## 4. Logo, nombres y firmas

Logo proporcional, tres nombres distintos y firmas simuladas en las casillas de la plantilla de demostración. No son firmas de personas reales.

![Nombres y firmas simuladas](pruebas-visuales/04-logo-nombres-firmas.png)

Se verificó que los trazos de las tablas permanecieran iguales antes y después del llenado. Los tamaños y líneas resultantes están en [resultados.json](pruebas-visuales/resultados.json).

Para reproducir estas imágenes sin PDF privados:

```sh
python scripts/ejemplos_visuales.py docs/pruebas-visuales
```
