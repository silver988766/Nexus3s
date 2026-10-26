# Nexus 3S - Sistema de Gestión de Inventario y Ventas

**Nexus 3S** es una aplicación de escritorio de código abierto, desarrollada a medida para la **Imprenta 3 Soles** (San Carlos, Maldonado). El sistema sustituye el control memorístico e informal en papel por una solución digital local, ágil y autónoma.

---

## Problemática Resuelta
En el diagnóstico operativo del comercio se detectaron tres dificultades principales:
- **Demoras en mostrador:** Pérdida de 3 a 5 minutos por cliente al verificar físicamente las existencias en estanterías.
- **Quiebres imprevistos de stock:** Artículos de alta rotación (papelería e insumos de oficina en general) agotados sin advertencia.
- **Falta de trazabilidad financiera:** Registros contables manuales propensos a errores aritméticos y omisiones de transacciones.

---

## Características Técnicas y Módulos
- **Operatividad 100% Offline:** Persistencia de datos embebida con SQLite 3 bajo principios ACID, asegurando tolerancia a fallos eléctricos sin depender de conexión a internet ni servidores externos.
- **Búsqueda Dinámica:** Filtrado en tiempo real por nombre o categoría mediante eventos `<KeyRelease>`, reduciendo las consultas a menos de 2 segundos.
- **Monitoreo y Alertas:** Tarjetas de métricas con advertencia visual automática ante insumos críticos (stock <= 5 unidades).
- **Cálculo de Capital Invertido:** Balance monetario actualizado al instante en base al inventario registrado.
- **Integridad Contable Histórica:** Consultas relacionales estructuradas con `LEFT JOIN` y `COALESCE` para mantener intactos los balances de ingresos aun si un producto es removido del catálogo.
- **Validación Estricta:** Formularios con manejo de excepciones y control SQL para evitar cantidades negativas o ventas sin stock suficiente.

---

## Ficha Técnica
- **Lenguaje:** Python 3.x
- **Interfaz Gráfica:** CustomTkinter
- **Base de Datos:** SQLite 3 (`inventario.db`)
- **Entorno y Dependencias:** `uv` / `.venv` (Pillow, CustomTkinter)
- **Plataforma de Despliegue:** Windows 11 / Windows 10
- **Licencia:** Código Abierto---

## Instalación y Ejecución

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/silver988766/Nexus3s.git](https://github.com/silver988766/Nexus3s.git)
   cd Nexus3s
   pip install customtkinter pillow
   python app.py





   
