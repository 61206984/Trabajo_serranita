"""Estado del pedido en curso entre pantallas (cliente y líneas). Se limpia al registrar."""
from dataclasses import dataclass, field


@dataclass
class Cliente:
    id_cliente: int
    tipo_doc: str
    nro_doc: str
    nombre: str
    telefono: str | None = None
    direccion: str | None = None

    @property
    def documento(self) -> str:
        return f"{self.tipo_doc} {self.nro_doc}"


@dataclass
class Linea:
    id_producto: int
    codigo: str
    nombre: str
    precio: float
    stock: float
    cantidad: float = 1

    @property
    def subtotal(self) -> float:
        return round(self.precio * self.cantidad, 2)


@dataclass
class Carrito:
    cliente: Cliente | None = None
    lineas: dict[int, Linea] = field(default_factory=dict)
    observaciones: str = ""

    def seleccionar_cliente(self, cliente: Cliente) -> None:
        # Cambiar de cliente vacía el pedido: las líneas eran de otro cliente.
        if self.cliente is None or self.cliente.id_cliente != cliente.id_cliente:
            self.lineas.clear()
            self.observaciones = ""
        self.cliente = cliente

    def total(self) -> float:
        return round(sum(l.subtotal for l in self.lineas.values()), 2)

    def limpiar(self) -> None:
        self.cliente = None
        self.lineas.clear()
        self.observaciones = ""


carrito = Carrito()
