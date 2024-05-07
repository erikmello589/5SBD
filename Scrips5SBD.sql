CREATE TABLE tb_cargatmp (
    pedido_id INT,
    item_pedido_id INT,
    data_compra DATETIME,
    data_pagamento DATETIME,
    cliente_email VARCHAR(100),
    cliente_nome VARCHAR(100),
    cliente_cpf VARCHAR(20),
    cliente_celular VARCHAR(20),
    produto_sku VARCHAR(50),
    produto_nome VARCHAR(100),
    quantidade_comprada INT,
    moedaUtilizada VARCHAR(10),
    item_pedido_preco DECIMAL(10, 2),
    tipo_entrega VARCHAR(50),
    destinatario_nome VARCHAR(100),
    endereco_entrega VARCHAR(200),
    cidade_entrega VARCHAR(50),
    estado_entrega VARCHAR(50),
    cep_entrega VARCHAR(20),
    pais_entrega VARCHAR(50)
);

CREATE TABLE clientes (
    cliente_email VARCHAR(100) NULL,
    cliente_nome VARCHAR(100) NULL,
    cliente_cpf VARCHAR(20) NULL,
    cliente_celular VARCHAR(20) NULL,
    PRIMARY KEY (cliente_cpf),
    UNIQUE (cliente_cpf)
);

CREATE TABLE produtos (
    produto_id INT UNIQUE,
    produto_sku VARCHAR(50) NULL,
    produto_nome VARCHAR(100) NULL,
    produto_estoque INT DEFAULT 0,
    PRIMARY KEY (produto_id),
    UNIQUE (produto_id)
);

CREATE TABLE pedidos (
    pedido_id INT UNIQUE,
    cliente_cpf VARCHAR(20) NULL,
    preco_total DECIMAL(10, 2) NULL,
    data_compra DATETIME NULL,
    data_pagamento DATETIME NULL,
    tipo_entrega VARCHAR(50) NULL,
    destinatario_nome VARCHAR(100) NULL,
    endereco_entrega VARCHAR(200) NULL,
    cidade_entrega VARCHAR(100) NULL,
    estado_entrega VARCHAR(50) NULL,
    cep_entrega VARCHAR(20) NULL,
    pais_entrega VARCHAR(50) NULL,
    status_pedido VARCHAR(50) NULL,
    PRIMARY KEY (pedido_id),
    FOREIGN KEY (cliente_cpf) REFERENCES clientes (cliente_cpf)
);

CREATE TABLE itensPedido (
    item_pedido_id INT UNIQUE,
    pedido_id INT NULL,
    produto_id INT NULL,
    quantidade_comprada INT NULL,
    item_pedido_preco DECIMAL(10, 2) NULL,
    PRIMARY KEY (item_pedido_id),
    FOREIGN KEY (pedido_id) REFERENCES pedidos (pedido_id)
    FOREIGN KEY (produto_id) REFERENCES produtos(produto_id)
);

-- preenche carga temporaria com exemplos (ou pode vir do .csv)
INSERT INTO tb_cargatmp (pedido_id, item_pedido_id, data_compra, data_pagamento, cliente_email, cliente_nome, cliente_cpf, cliente_celular, produto_sku, produto_nome, quantidade_comprada, moedaUtilizada, item_pedido_preco, tipo_entrega, destinatario_nome, endereco_entrega, cidade_entrega, estado_entrega, cep_entrega, pais_entrega)
VALUES
    (1, 101, '2024-05-06 09:30:00', '2024-05-06 09:45:00', 'cliente1@email.com', 'Cliente 1', '123.456.789-00', '(11) 98765-4321', 'SKU123', 'Produto 1', 2, 'USD', 25.99, 'Entrega Expressa', 'Destinatário 1', 'Rua A, 123', 'Cidade A', 'Estado A', '12345-678', 'País A'),
    (2, 102, '2024-05-05 14:00:00', '2024-05-05 14:15:00', 'cliente2@email.com', 'Cliente 2', '987.654.321-00', '(22) 12345-6789', 'SKU456', 'Produto 2', 1, 'EUR', 39.99, 'Entrega Padrão', 'Destinatário 2', 'Rua B, 456', 'Cidade B', 'Estado B', '98765-432', 'País B'),
    (3, 103, '2024-05-04 11:45:00', '2024-05-04 12:00:00', 'cliente3@email.com', 'Cliente 3', '456.789.123-00', '(33) 54321-9876', 'SKU789', 'Produto 3', 3, 'BRL', 15.99, 'Entrega Rápida', 'Destinatário 3', 'Rua C, 789', 'Cidade C', 'Estado C', '54321-876', 'País C');

-- inserindo produtos no estoque INICIAL
INSERT INTO produtos(produto_id, produto_sku, produto_nome, produto_estoque)
VALUES
(1, 'SKU1001', 'Camisa de lã', 10),
(2, 'SKU1002', 'Mochila', 20),
(3, 'SKU1003', 'Bexiga', 15);

-- Inserindo em Clientes que estão na CargaTemp em Clientes [Não vai inserir o mesmo cliente 2 vezes porque o CPF é único e há o DISTINCT]
INSERT INTO clientes (cliente_cpf, cliente_nome, cliente_email, cliente_celular)
SELECT DISTINCT cliente_cpf, cliente_nome, cliente_email, cliente_celular
FROM tb_cargatmp
WHERE cliente_cpf NOT IN (SELECT cliente_cpf FROM clientes);

-- Inserindo em Pedidos os que estão em CargaTemp, ele também calcula o total de cada pedido 
INSERT INTO pedidos (pedido_id, data_compra, data_pagamento, cliente_cpf, preco_total)
SELECT pedido_id, data_compra, data_pagamento, cliente_cpf, (item_pedido_preco * quantidade_comprada) AS preco_total
FROM tb_cargatmp;

-- Inserção de Itens de Pedido [se o produto já existir na lista, soma a quantidade comprada com a que se deseja inserir]
INSERT INTO itensPedido (item_pedido_id, pedido_id, produto_id, quantidade_comprada, item_pedido_preco)
SELECT tbc.item_pedido_id, tbc.pedido_id, p.produto_id, tbc.quantidade_comprada, tbc.item_pedido_preco
FROM tb_cargatmp tbc
JOIN produtos p ON tbc.produto_sku = p.produto_sku
ON DUPLICATE KEY UPDATE
    quantidade_comprada = itensPedido.quantidade_comprada + VALUES(quantidade_comprada);


-- Atualizando o estoque de Produtos baseado em cada quantidade comprada pelos clientes nos pedidos [diz o total de quantos itens foram comprados de cada produto]
UPDATE produtos p
INNER JOIN itensPedido ip ON p.produto_id = ip.produto_id
SET p.produto_estoque = p.produto_estoque - ip.quantidade_comprada;

--TRUNCATE TABLE tb_cargatmp;
