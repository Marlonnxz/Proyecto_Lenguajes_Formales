-- Script de inicialización de la Base de Datos PostgreSQL
-- Proyecto: Compilador de Lenguaje Natural a SQL (ESQL)

DROP TABLE IF EXISTS pedidos CASCADE;
DROP TABLE IF EXISTS productos CASCADE;
DROP TABLE IF EXISTS empleados CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;
DROP TABLE IF EXISTS usuarios_activos CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- Tabla: usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    edad INT NOT NULL,
    correo VARCHAR(120) NOT NULL
);

INSERT INTO usuarios (nombre, edad, correo) VALUES
('Carlos Mendoza', 28, 'carlos.mendoza@email.com'),
('Ana Gomez', 22, 'ana.gomez@email.com'),
('Marlon Gomez', 24, 'marlon.gomez@email.com'),
('Laura Rodriguez', 35, 'laura.rodriguez@email.com'),
('David Martinez', 19, 'david.martinez@email.com');

-- Tabla: usuarios_activos (para soporte de nombres compuestos en Reglas 6 y 10)
CREATE TABLE usuarios_activos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'activo',
    ultimo_acceso DATE DEFAULT CURRENT_DATE
);

INSERT INTO usuarios_activos (nombre, estado, ultimo_acceso) VALUES
('Carlos Mendoza', 'activo', '2026-09-20'),
('Ana Gomez', 'activo', '2026-09-25'),
('Marlon Gomez', 'activo', '2026-09-27');

-- Tabla: clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) NOT NULL,
    telefono VARCHAR(30),
    ciudad VARCHAR(80)
);

INSERT INTO clientes (nombre, correo, telefono, ciudad) VALUES
('Empresa Alfa', 'contacto@alfa.com', '555-1020', 'Bogota'),
('Comercializadora Beta', 'ventas@beta.com', '555-3040', 'Medellin'),
('Soluciones Gamma', 'info@gamma.com', '555-5060', 'Cali'),
('Inversiones Delta', 'admin@delta.com', '555-7080', 'Barranquilla');

-- Tabla: empleados
CREATE TABLE empleados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    puesto VARCHAR(80) NOT NULL,
    salario NUMERIC(10, 2) NOT NULL,
    edad INT NOT NULL
);

INSERT INTO empleados (nombre, puesto, salario, edad) VALUES
('Julian Silva', 'Desarrollador Senior', 5200.00, 31),
('Harold Ortiz', 'Arquitecto de Software', 6800.00, 34),
('Elena Torres', 'Disenadora UX', 3400.00, 26),
('Mateo Ramirez', 'Analista QA', 2900.00, 23),
('Sofia Herrera', 'Project Manager', 4800.00, 29);

-- Tabla: productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio NUMERIC(10, 2) NOT NULL,
    stock INT NOT NULL,
    categoria VARCHAR(60)
);

INSERT INTO productos (nombre, precio, stock, categoria) VALUES
('Laptop Pro 15', 1250.00, 15, 'Electronica'),
('Teclado Mecanico', 85.50, 40, 'Accesorios'),
('Monitor 27 4K', 380.00, 12, 'Pantallas'),
('Mouse Ergonomico', 45.00, 50, 'Accesorios'),
('Silla Ergonomica', 210.00, 8, 'Mobiliario');

-- Tabla: pedidos
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    cliente_id INT REFERENCES clientes(id),
    total NUMERIC(10, 2) NOT NULL
);

INSERT INTO pedidos (fecha, cliente_id, total) VALUES
('2026-09-01', 1, 1335.50),
('2026-09-10', 2, 425.00),
('2026-09-15', 3, 210.00),
('2026-09-22', 1, 85.50);
