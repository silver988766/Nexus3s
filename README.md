# 📦 Nexus 3S — Gestión de Stock y Ventas (100% Offline)

**Nexus 3S** es un sistema de escritorio libre y gratuito, desarrollado a medida para **Imprenta 3 Soles**, que sustituye el control memorístico e informal en papel por una solución digital local, ágil y autónoma. Nació como proyecto de investigación aplicada en el Liceo N° 1 de San Carlos (2026).

## Problemática resuelta

En el diagnóstico operativo del comercio se detectaron tres dificultades principales:

- **Demoras en mostrador:** pérdida de minutos por cliente al verificar físicamente las existencias en estanterías.
- **Quiebres imprevistos de stock:** artículos de alta rotación (papelería e insumos de oficina) agotados sin advertencia.
- **Falta de trazabilidad financiera:** registros contables manuales propensos a errores aritméticos y omisiones de transacciones.

## 📥 Instalación fácil (Windows)

No necesitás saber programación ni instalar nada adicional:

1. Andá a la sección **[Releases](../../releases)** (a la derecha de esta pantalla).
2. Descargá el archivo **`Nexus3S.exe`**.
3. Guardalo en una carpeta de tu Escritorio y hacé **doble clic** para abrirlo.
   - Si Windows muestra el aviso de SmartScreen, tocá "Más información" → "Ejecutar de todas formas".
4. Listo. El programa crea automáticamente su base de datos local (`inventario.db`) en esa misma carpeta.

## ⚡ Características principales

- **Operatividad 100% offline:** persistencia de datos embebida con SQLite 3 bajo principios ACID, tolerante a fallos eléctricos y sin depender de internet ni servidores externos.
- **Búsqueda dinámica (< 2 seg):** filtrado en tiempo real por nombre o categoría a medida que escribís.
- **Alertas automáticas de stock:** indicadores visuales cuando un producto llega a 5 unidades o menos, para evitar quedarte sin mercadería de alta rotación.
- **Integridad contable histórica:** los balances de ingresos se mantienen intactos aun si un producto es removido del catálogo.
- **Validación estricta:** controles que evitan cantidades negativas o ventas sin stock suficiente.
- **Interfaz adaptable:** Modo Claro / Oscuro y vista en Pantalla Completa (`F11`).

## 🛠️ Ejecución desde el código fuente (desarrolladores)

Si querés auditar el código, modificarlo para tu negocio, o correrlo en Linux/Windows con Python:

```bash
git clone https://github.com/silver988766/Nexus3s.git
cd Nexus3s
pip install customtkinter pillow
python app.py
```

## Ficha técnica

| | |
|---|---|
| **Lenguaje** | Python 3.x |
| **Interfaz gráfica** | CustomTkinter |
| **Base de datos** | SQLite 3 (`inventario.db`) |
| **Dependencias** | CustomTkinter, Pillow |
| **Plataforma de despliegue** | Windows 10 / 11 |
| **Licencia** | Código abierto |

## Documentación académica

El marco teórico, las matrices de requerimientos, la bitácora de debugging y las conclusiones están documentados en detalle en el proyecto.

👉 [Ver Cuaderno de Campo Completo (PDF)](https://github.com/silver988766/Nexus3s/blob/main/Nexus3s%20cuaderno%20de%20campo.pdf)
