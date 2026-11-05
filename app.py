import os
import sys
import sqlite3
import tkinter as tk
import tkinter.messagebox as messagebox
import customtkinter as ctk
from PIL import Image

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = getattr(sys, "_MEIPASS", APP_DIR)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = APP_DIR

DB_PATH = os.path.join(APP_DIR, "inventario.db")
LOGO_PATH = os.path.join(RESOURCE_DIR, "logo.png")

COLORS = {
    "bg": ("#f1f5f9", "#0f172a"),
    "surface": ("#e2e8f0", "#111827"),
    "surface_alt": ("#cbd5e1", "#1e293b"),
    "text_muted": ("#475569", "#94a3b8"),
    "text_main": ("#0f172a", "#f8fafc"),
    "accent": ("#2563eb", "#2563eb"),
    "success": ("#059669", "#34d399"),
    "warning": ("#d97706", "#f59e0b"),
    "danger": ("#dc2626", "#ef4444"),
    "danger_hover": ("#b91c1c", "#991b1b"),
    "info": ("#2563eb", "#60a5fa"),
}

STOCK_BAJO_LIMITE = 5

def db_get_connection():
    return sqlite3.connect(DB_PATH)

def db_init():
    with db_get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                stock INTEGER NOT NULL,
                precio REAL NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATETIME DEFAULT (datetime('now', 'localtime')),
                producto_id INTEGER,
                cantidad INTEGER,
                total REAL,
                FOREIGN KEY(producto_id) REFERENCES productos(id)
            )
            """
        )
        conn.commit()

def db_agregar_producto(nombre, categoria, stock, precio):
    with db_get_connection() as conn:
        conn.execute(
            "INSERT INTO productos (nombre, categoria, stock, precio) VALUES (?, ?, ?, ?)",
            (nombre, categoria, int(stock), float(precio)),
        )
        conn.commit()

def db_editar_producto(producto_id, nombre, categoria, stock, precio):
    with db_get_connection() as conn:
        conn.execute(
            "UPDATE productos SET nombre = ?, categoria = ?, stock = ?, precio = ? WHERE id = ?",
            (nombre, categoria, int(stock), float(precio), producto_id),
        )
        conn.commit()

def db_obtener_productos(busqueda=""):
    with db_get_connection() as conn:
        cursor = conn.cursor()
        criterio = f"%{busqueda}%"
        cursor.execute(
            "SELECT id, nombre, categoria, stock, precio FROM productos "
            "WHERE nombre LIKE ? OR categoria LIKE ? ORDER BY stock ASC, nombre ASC",
            (criterio, criterio),
        )
        return cursor.fetchall()

def db_eliminar_producto(producto_id):
    with db_get_connection() as conn:
        conn.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        conn.commit()

def db_obtener_resumen():
    with db_get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(stock), 0) FROM productos")
        total_productos, total_stock = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= ?", (STOCK_BAJO_LIMITE,))
        stock_bajo = cursor.fetchone()[0]
        return int(total_productos), int(total_stock), int(stock_bajo)

def db_registrar_venta(producto_id, cantidad=1):
    with db_get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stock, precio FROM productos WHERE id = ?", (producto_id,))
        resultado = cursor.fetchone()

        if not resultado or resultado[0] < cantidad:
            return False

        precio_unitario = resultado[1]
        total_venta = precio_unitario * cantidad

        cursor.execute(
            "UPDATE productos SET stock = stock - ? WHERE id = ? AND stock >= ?",
            (cantidad, producto_id, cantidad),
        )
        if cursor.rowcount == 0:
            return False

        cursor.execute(
            "INSERT INTO ventas (fecha, producto_id, cantidad, total) VALUES (datetime('now', 'localtime'), ?, ?, ?)",
            (producto_id, cantidad, total_venta),
        )
        conn.commit()
        return True


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nexus 3S - Sistema de Gestión")
        self.geometry("1100x750")
        self.minsize(950, 650)
        self._msg_timer = None
        self._redraw_timer = None  # NEW
        self.fullscreen_activo = False

        try:
            if os.path.exists(LOGO_PATH):
                self.icon_img = tk.PhotoImage(file=LOGO_PATH)
                self.iconphoto(False, self.icon_img)
        except Exception:
            pass

        self.configure(fg_color=COLORS["bg"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.bind("<F11>", lambda _e: self.toggle_fullscreen())
        self.bind("<Escape>", lambda _e: self.salir_fullscreen())
        self.bind("<Configure>", self._on_configure)  # NEW

        db_init()
        self.build_ui()
        self.cargar_productos()

    # ---------- NEW: forced redraw after resize / fullscreen ----------
    def _on_configure(self, event):
        # Only react to the main window being resized, not to child widgets
        if event.widget is self:
            self._programar_redibujado(150)

    def _programar_redibujado(self, delay):
        if self._redraw_timer is not None:
            self.after_cancel(self._redraw_timer)
        self._redraw_timer = self.after(delay, self._forzar_redibujado)

    def _forzar_redibujado(self):
        self._redraw_timer = None
        self.update_idletasks()
        self._redibujar_widgets(self)
        self.update()

    def _redibujar_widgets(self, widget):
        for child in widget.winfo_children():
            if hasattr(child, "_draw"):
                try:
                    child._draw()
                except Exception:
                    pass
            self._redibujar_widgets(child)
    # ------------------------------------------------------------------

    def toggle_tema(self):
        modo_actual = ctk.get_appearance_mode()
        if modo_actual == "Light":
            ctk.set_appearance_mode("dark")
            self.btn_tema.configure(text="☀️ Modo Claro")
        else:
            ctk.set_appearance_mode("light")
            self.btn_tema.configure(text="🌙 Modo Oscuro")

    def toggle_fullscreen(self):
        self.fullscreen_activo = not self.fullscreen_activo
        self.attributes("-fullscreen", self.fullscreen_activo)
        # Alternative if it still glitches:
        # self.state("zoomed" if self.fullscreen_activo else "normal")
        texto_btn = "🗗 Salir Pantalla Completa" if self.fullscreen_activo else "⛶ Pantalla Completa"
        self.btn_fullscreen.configure(text=texto_btn)
        self._programar_redibujado(200)  # NEW

    def salir_fullscreen(self):
        if self.fullscreen_activo:
            self.fullscreen_activo = False
            self.attributes("-fullscreen", False)
            self.btn_fullscreen.configure(text="⛶ Pantalla Completa")
            self._programar_redibujado(200)  # NEW

    def build_ui(self):
        self.build_header()
        self.build_resumen()
        self.build_panel()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 14), sticky="ew")
        # Corrección de columnas para evitar superposiciones en pantalla completa
        header.grid_columnconfigure(0, weight=0)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=0)

        try:
            if os.path.exists(LOGO_PATH):
                logo_img = Image.open(LOGO_PATH)
                self.logo_ctk = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(50, 50))
                logo_label = ctk.CTkLabel(header, image=self.logo_ctk, text="")
                logo_label.grid(row=0, column=0, rowspan=2, padx=(0, 15), sticky="w")
        except Exception:
            pass

        ctk.CTkLabel(header, text="Nexus 3S", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLORS["text_main"], anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(header, text="Gestión de inventario y registro de ventas automático.", font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"], anchor="w").grid(row=1, column=1, sticky="w", pady=(2, 0))

        controles_vista = ctk.CTkFrame(header, fg_color="transparent")
        controles_vista.grid(row=0, column=2, rowspan=2, sticky="e")

        self.btn_tema = ctk.CTkButton(
            controles_vista, text="🌙 Modo Oscuro", width=125, height=34,
            fg_color=COLORS["surface_alt"], text_color=COLORS["text_main"],
            hover_color=COLORS["surface"], command=self.toggle_tema
        )
        self.btn_tema.pack(side="left", padx=(0, 8))

        self.btn_fullscreen = ctk.CTkButton(
            controles_vista, text="⛶ Pantalla Completa", width=145, height=34,
            fg_color=COLORS["surface_alt"], text_color=COLORS["text_main"],
            hover_color=COLORS["surface"], command=self.toggle_fullscreen
        )
        self.btn_fullscreen.pack(side="left")

    def build_resumen(self):
        resumen = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=18)
        resumen.grid(row=1, column=0, padx=24, pady=(0, 16), sticky="ew")
        resumen.grid_columnconfigure((0, 1, 2), weight=1, uniform="tarjetas")

        self.label_total_productos = self._tarjeta_resumen(resumen, "Productos Diferentes", col=0)
        self.label_total_stock = self._tarjeta_resumen(resumen, "Unidades en Stock", col=1)
        self.label_stock_bajo = self._tarjeta_resumen(resumen, "Alertas (Stock Bajo)", col=2, color=COLORS["warning"])

    def _tarjeta_resumen(self, parent, titulo, col, color=None):
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface_alt"], corner_radius=14)
        card.grid(row=0, column=col, padx=10, pady=12, sticky="nsew")
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]).pack(anchor="w", padx=14, pady=(10, 0))
        label = ctk.CTkLabel(card, text="-", font=ctk.CTkFont(size=20, weight="bold"), text_color=color if color else COLORS["text_main"])
        label.pack(anchor="w", padx=14, pady=(4, 10))
        return label

    def build_panel(self):
        self.tabview = ctk.CTkTabview(self, corner_radius=15, fg_color=COLORS["surface"])
        self.tabview.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="nsew")

        self.tab_inventario = self.tabview.add("📦 Inventario y Productos")
        self.tab_ventas = self.tabview.add("💰 Historial de Ventas")

        self.tab_inventario.grid_columnconfigure(0, weight=1)
        self.tab_inventario.grid_rowconfigure(2, weight=1)

        top_bar = ctk.CTkFrame(self.tab_inventario, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=18, pady=(14, 6), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar(value="")
        self.search_entry = ctk.CTkEntry(top_bar, height=36, placeholder_text="Buscar por nombre o categoría...", textvariable=self.search_var)
        self.search_entry.grid(row=0, column=0, padx=(0, 16), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda _event: self.cargar_productos())

        buttons = ctk.CTkFrame(top_bar, fg_color="transparent")
        buttons.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(buttons, text="+ Nuevo producto", height=36, width=140, command=self.abrir_formulario).pack(side="left", padx=(0, 8))
        ctk.CTkButton(buttons, text="Actualizar", height=36, width=105, command=self.cargar_productos).pack(side="left")

        self.message_label = ctk.CTkLabel(self.tab_inventario, text="", height=20, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["info"])
        self.message_label.grid(row=1, column=0, padx=18, pady=(0, 6), sticky="w")

        self.list_container = ctk.CTkScrollableFrame(self.tab_inventario, corner_radius=16, fg_color=COLORS["bg"])
        self.list_container.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="nsew")

        self.tab_ventas.grid_columnconfigure(0, weight=1)
        self.tab_ventas.grid_rowconfigure(1, weight=1)

        ventas_top = ctk.CTkFrame(self.tab_ventas, fg_color="transparent")
        ventas_top.grid(row=0, column=0, padx=18, pady=12, sticky="ew")
        ctk.CTkLabel(ventas_top, text="Registro Histórico de Ventas", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_main"]).pack(side="left")
        ctk.CTkButton(ventas_top, text="Recargar Historial", command=self.cargar_historial_ventas).pack(side="right")

        self.ventas_container = ctk.CTkScrollableFrame(self.tab_ventas, corner_radius=16, fg_color=COLORS["bg"])
        self.ventas_container.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")

    def cargar_productos(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        productos = db_obtener_productos(self.search_var.get().strip())
        total_productos, total_stock, stock_bajo = db_obtener_resumen()

        self.label_total_productos.configure(text=f"{total_productos}")
        self.label_total_stock.configure(text=f"{total_stock}")
        self.label_stock_bajo.configure(text=f"{stock_bajo}")

        if not productos:
            ctk.CTkLabel(self.list_container, text="No se encontraron productos.", font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"]).pack(pady=32)
            self.cargar_historial_ventas()
            return

        for producto_id, nombre, categoria, stock, precio in productos:
            row = ctk.CTkFrame(self.list_container, fg_color=COLORS["surface_alt"], corner_radius=14)
            row.pack(fill="x", padx=8, pady=8)
            row.grid_columnconfigure(0, weight=1)

            top_row = ctk.CTkFrame(row, fg_color="transparent")
            top_row.grid(row=0, column=0, padx=14, pady=(12, 4), sticky="ew")
            top_row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(top_row, text=nombre, font=ctk.CTkFont(size=15, weight="bold"), text_color=COLORS["text_main"], anchor="w").grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(top_row, text=categoria, font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"], anchor="w").grid(row=1, column=0, sticky="w", pady=(1, 0))

            details = ctk.CTkFrame(row, fg_color="transparent")
            details.grid(row=1, column=0, padx=14, pady=(0, 8), sticky="ew")
            details.grid_columnconfigure(0, weight=1)
            details.grid_columnconfigure(1, weight=1)

            if stock == 0:
                stock_color = COLORS["danger"]
                stock_text = "SIN STOCK (0 unidades)"
            elif stock <= STOCK_BAJO_LIMITE:
                stock_color = COLORS["warning"]
                stock_text = f"Stock Bajo: {stock} unidades"
            else:
                stock_color = COLORS["success"]
                stock_text = f"Stock: {stock} unidades"

            ctk.CTkLabel(details, text=stock_text, font=ctk.CTkFont(size=13, weight="bold"), text_color=stock_color, anchor="w").grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(details, text=f"Precio: ${precio:,.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_main"], anchor="e").grid(row=0, column=1, sticky="e")

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=2, column=0, padx=14, pady=(0, 12), sticky="e")

            ctk.CTkButton(actions, text="Registrar Venta", width=115, height=32, fg_color=COLORS["accent"], hover_color="#1d4ed8", command=lambda pid=producto_id: self.vender_producto(pid)).pack(side="left", padx=(0, 8))
            ctk.CTkButton(actions, text="Editar", width=85, height=32, command=lambda pid=producto_id, n=nombre, c=categoria, s=stock, p=precio: self.abrir_formulario((pid, n, c, s, p))).pack(side="left", padx=(0, 8))
            ctk.CTkButton(actions, text="Eliminar", width=85, height=32, fg_color="#b91c1c", hover_color=COLORS["danger_hover"], command=lambda pid=producto_id: self.eliminar_producto(pid)).pack(side="left")

        self.cargar_historial_ventas()

    def cargar_historial_ventas(self):
        for widget in self.ventas_container.winfo_children():
            widget.destroy()

        with db_get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.fecha, COALESCE(p.nombre, 'Producto Eliminado'), v.cantidad, v.total
                FROM ventas v
                LEFT JOIN productos p ON v.producto_id = p.id
                ORDER BY v.id DESC
            """)
            ventas = cursor.fetchall()

        if not ventas:
            ctk.CTkLabel(self.ventas_container, text="Aún no hay ventas registradas.", text_color=COLORS["text_muted"]).pack(pady=30)
            return

        for fecha, nombre, cantidad, total in ventas:
            row = ctk.CTkFrame(self.ventas_container, fg_color=COLORS["surface_alt"], corner_radius=10)
            row.pack(fill="x", padx=8, pady=4)
            row.grid_columnconfigure(0, weight=2)
            row.grid_columnconfigure(1, weight=3)
            row.grid_columnconfigure(2, weight=1)
            row.grid_columnconfigure(3, weight=1)

            fecha_corta = fecha.split(".")[0] if "." in fecha else fecha

            ctk.CTkLabel(row, text=fecha_corta, text_color=COLORS["text_muted"]).grid(row=0, column=0, padx=12, pady=10, sticky="w")
            ctk.CTkLabel(row, text=nombre, font=ctk.CTkFont(weight="bold"), text_color=COLORS["text_main"]).grid(row=0, column=1, padx=12, pady=10, sticky="w")
            ctk.CTkLabel(row, text=f"{cantidad} unid.", text_color=COLORS["text_main"]).grid(row=0, column=2, padx=12, pady=10, sticky="w")
            ctk.CTkLabel(row, text=f"+ ${total:,.2f}", text_color=COLORS["success"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=12, pady=10, sticky="e")

    def abrir_formulario(self, producto=None):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Agregar producto" if not producto else "Editar producto")
        ventana.geometry("420x440")
        ventana.resizable(False, False)
        ventana.configure(fg_color=COLORS["bg"])
        ventana.transient(self)
        ventana.after(100, ventana.grab_set)
        ventana.after(100, ventana.focus_force)

        ctk.CTkLabel(ventana, text="Detalles del Producto", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_main"]).pack(pady=(18, 16))

        campos = {}
        for label, placeholder in [("Nombre", "Ej: Taza blanca sublimable"), ("Categoría", "Ej: Sublimación"), ("Stock", "Ej: 25"), ("Precio", "Ej: 150")]:
            ctk.CTkLabel(ventana, text=label, text_color=COLORS["text_main"], anchor="w").pack(padx=24, anchor="w")
            entry = ctk.CTkEntry(ventana, width=300, placeholder_text=placeholder)
            entry.pack(padx=24, pady=(2, 10))
            campos[label] = entry

        if producto:
            producto_id, nombre, categoria, stock, precio = producto
            campos["Nombre"].insert(0, nombre)
            campos["Categoría"].insert(0, categoria)
            campos["Stock"].insert(0, str(stock))
            campos["Precio"].insert(0, f"{precio:.2f}")
            producto_id_guardado = producto_id
        else:
            producto_id_guardado = None

        error_label = ctk.CTkLabel(ventana, text="", text_color=COLORS["danger"], font=ctk.CTkFont(size=12, weight="bold"))
        error_label.pack(pady=(4, 2))

        def guardar():
            nombre = campos["Nombre"].get().strip()
            categoria = campos["Categoría"].get().strip()
            stock_text = campos["Stock"].get().strip()
            precio_text = campos["Precio"].get().strip().replace(",", ".")

            if not all([nombre, categoria, stock_text, precio_text]):
                error_label.configure(text="Completá todos los campos.")
                return

            try:
                stock_val = int(stock_text)
                precio_val = float(precio_text)
            except ValueError:
                error_label.configure(text="Stock (entero) y precio deben ser numéricos.")
                return

            if stock_val < 0 or precio_val < 0:
                error_label.configure(text="Stock y precio no pueden ser negativos.")
                return

            if producto_id_guardado is None:
                db_agregar_producto(nombre, categoria, stock_val, precio_val)
            else:
                db_editar_producto(producto_id_guardado, nombre, categoria, stock_val, precio_val)

            self.cargar_productos()
            ventana.destroy()

        ventana.bind("<Return>", lambda _event: guardar())
        ctk.CTkButton(ventana, text="Guardar Cambios", width=200, command=guardar).pack(pady=14)

    def mostrar_mensaje(self, texto, color):
        if self._msg_timer is not None:
            self.after_cancel(self._msg_timer)
        self.message_label.configure(text=texto, text_color=color)
        self._msg_timer = self.after(3000, lambda: self.message_label.configure(text=""))

    def vender_producto(self, producto_id):
        if db_registrar_venta(producto_id, 1):
            self.mostrar_mensaje("✅ Venta registrada correctamente.", COLORS["success"])
        else:
            self.mostrar_mensaje("❌ Error: No hay stock suficiente para vender.", COLORS["danger"])
        self.cargar_productos()

    def eliminar_producto(self, producto_id):
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto permanentemente?"):
            db_eliminar_producto(producto_id)
            self.cargar_productos()

if __name__ == "__main__":
    # If your Windows display scaling is above 100% and it still glitches,
    # uncomment the next line:
    # ctk.deactivate_automatic_dpi_awareness()
    app = App()
    app.mainloop()