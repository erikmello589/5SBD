CREATE TABLE produto (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    descricao TEXT,
    preco DECIMAL(10, 2)
);

INSERT INTO produto (nome, descricao, preco) VALUES
('Camiseta branca', 'Camiseta básica branca de algodão', 20.00),
('Calça jeans', 'Calça jeans azul com corte moderno', 45.00),
('Tênis esportivo', 'Tênis preto para corrida com amortecimento', 60.00),
('Mochila escolar', 'Mochila resistente com compartimentos', 35.00),
('Relógio digital', 'Relógio de pulso com cronômetro e alarme', 25.00),
('Óculos de sol', 'Óculos de sol estilo aviador com lentes polarizadas', 30.00),
('Fones de ouvido', 'Fones de ouvido sem fio com cancelamento de ruído', 50.00),
('Câmera digital', 'Câmera compacta com zoom óptico e gravação em Full HD', 120.00),
('Mouse sem fio', 'Mouse ergonômico com conectividade Bluetooth', 15.00),
('Teclado mecânico', 'Teclado retroiluminado com switches mecânicos', 80.00);

CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    email VARCHAR(255),
    endereco VARCHAR(255),
    telefone VARCHAR(20)
);

INSERT INTO cliente (nome, email, endereco, telefone) VALUES
('João Silva', 'joao@example.com', 'Rua A, 123', '(11) 1234-5678'),
('Maria Santos', 'maria@example.com', 'Av. B, 456', '(11) 9876-5432'),
('José Oliveira', 'jose@example.com', 'Rua C, 789', '(11) 5555-4444'),
('Ana Souza', 'ana@example.com', 'Rua D, 321', '(11) 2222-3333'),
('Pedro Pereira', 'pedro@example.com', 'Av. E, 654', '(11) 9999-8888'),
('Carla Rodrigues', 'carla@example.com', 'Rua F, 987', '(11) 7777-6666'),
('Lucas Almeida', 'lucas@example.com', 'Av. G, 321', '(11) 3333-2222'),
('Mariana Costa', 'mariana@example.com', 'Rua H, 456', '(11) 6666-7777'),
('Fernanda Oliveira', 'fernanda@example.com', 'Av. I, 789', '(11) 8888-9999'),
('Rafael Santos', 'rafael@example.com', 'Rua J, 654', '(11) 1111-2222');

CREATE TABLE itemPedido (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT,
    id_produto INT,
    quantidade INT,
    preco_unitario DECIMAL(10, 2),
    subtotal DECIMAL(10, 2)
);

INSERT INTO itemPedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal) VALUES
(1, 1, 2, 25.00, 50.00),
(1, 3, 1, 45.00, 45.00),
(2, 2, 3, 20.00, 60.00),
(2, 5, 1, 30.00, 30.00),
(3, 4, 2, 35.00, 70.00),
(3, 7, 1, 50.00, 50.00),
(4, 1, 2, 25.00, 50.00),
(4, 6, 2, 30.00, 60.00),
(5, 3, 3, 45.00, 135.00),
(5, 8, 1, 120.00, 120.00);

CREATE TABLE pedido (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    data_pedido DATE,
    status VARCHAR(50)
);

INSERT INTO pedido (id_cliente, data_pedido, status) VALUES
(1, '2022-04-01', 'Em processamento'),
(2, '2022-04-02', 'Aguardando pagamento'),
(3, '2022-04-03', 'Em transporte'),
(4, '2022-04-04', 'Entregue'),
(5, '2022-04-05', 'Em processamento'),
(1, '2022-04-06', 'Aguardando pagamento'),
(2, '2022-04-07', 'Em transporte'),
(3, '2022-04-08', 'Entregue'),
(4, '2022-04-09', 'Em processamento'),
(5, '2022-04-10', 'Aguardando pagamento');

CREATE TABLE tb_carga (
    id_produto INT,
    data_pedido DATE,
    nome_produto VARCHAR(255),
    quantidade_produto INT,
    subtotal_itemPedido DECIMAL(10, 2),
    email_cliente VARCHAR(255),
    nome_cliente VARCHAR(255),
    endereco_cliente VARCHAR(255)
);

INSERT INTO tb_carga (id_produto, data_pedido, nome_produto, quantidade_produto, subtotal_itemPedido, email_cliente, nome_cliente, endereco_cliente) VALUES
(1, '2022-04-01', 'Camiseta branca', 2, 50.00, 'joao@example.com', 'João Silva', 'Rua A, 123'),
(2, '2022-04-02', 'Calça jeans', 1, 45.00, 'maria@example.com', 'Maria Santos', 'Av. B, 456'),
(3, '2022-04-03', 'Tênis esportivo', 3, 60.00, 'jose@example.com', 'José Oliveira', 'Rua C, 789'),
(4, '2022-04-04', 'Mochila escolar', 2, 70.00, 'ana@example.com', 'Ana Souza', 'Rua D, 321'),
(5, '2022-04-05', 'Relógio digital', 1, 30.00, 'pedro@example.com', 'Pedro Pereira', 'Av. E, 654'),
(6, '2022-04-06', 'Óculos de sol', 2, 60.00, 'carla@example.com', 'Carla Rodrigues', 'Rua F, 987'),
(7, '2022-04-07', 'Fones de ouvido', 3, 150.00, 'lucas@example.com', 'Lucas Almeida', 'Av. G, 321'),
(8, '2022-04-08', 'Câmera digital', 1, 120.00, 'mariana@example.com', 'Mariana Costa', 'Rua H, 456'),
(9, '2022-04-09', 'Mouse sem fio', 2, 30.00, 'fernanda@example.com', 'Fernanda Oliveira', 'Av. I, 789'),
(10, '2022-04-10', 'Teclado mecânico', 1, 80.00, 'rafael@example.com', 'Rafael Santos', 'Rua J, 654');

SELECT p.id_pedido, SUM(ip.subtotal) AS total_pedido
FROM pedido p
JOIN itemPedido ip ON p.id_pedido = ip.id_pedido
GROUP BY p.id_pedido;


