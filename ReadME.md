🍔 Food Subscription - Plataforma de Assinatura de Refeições

Este projeto é uma plataforma web de pedidos de comida baseada em assinatura, inspirada no modelo do iFood, porém com um sistema de planos mensais.

O usuário pode criar uma conta, fazer login, escolher um plano de refeições e definir endereço e dia de entrega. O sistema possui integração com banco de dados MySQL e backend em Python.

📌 Tecnologias Utilizadas

Python (Backend)

Flask (Servidor Web)

MySQL (Banco de dados)

HTML5

CSS3

JavaScript

Fetch API

Sessões Flask

Login com Google

⚙️ Como executar o projeto

Para rodar o projeto localmente é necessário configurar o ambiente corretamente.

Siga os passos abaixo.

1️⃣ Instalar o Python

Caso ainda não tenha instalado:

Baixe em:

https://www.python.org/downloads/

Durante a instalação marque a opção:

Add Python to PATH

Depois verifique se instalou corretamente:

python --version
2️⃣ Instalar o MySQL

O projeto utiliza MySQL como banco de dados.

Baixe o MySQL em:

https://dev.mysql.com/downloads/mysql/

Após instalar, abra o MySQL Workbench ou o MySQL Command Line.

3️⃣ Importar o banco de dados

Dentro do projeto existe um arquivo de banco de dados.

Exemplo:

database.sql

Para importar:

No MySQL Workbench

Abra o MySQL Workbench

Vá em Server → Data Import

Selecione o arquivo .sql do projeto

Execute a importação

Ou via terminal:

SOURCE caminho/do/arquivo/database.sql;

Isso criará todas as tabelas necessárias, como:

usuários

assinaturas

pedidos

etc

4️⃣ Configurar conexão com o banco

No arquivo Python do projeto, configure as credenciais do MySQL.

Exemplo:

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sua_senha",
    database="nome_do_banco"
)

Substitua:

user

password

database

pelas credenciais do seu MySQL.

5️⃣ Instalar dependências

Se necessário, instale as bibliotecas usadas no projeto.

exemplo:

pip install -r requirements.txt

6️⃣ Iniciar o servidor

Agora basta executar o arquivo principal em Python.

Exemplo:

python app.py

ou

python main.py

Após executar, o servidor Flask será iniciado.

Normalmente o acesso será:

http://127.0.0.1:5000
🚀 Como usar o site

Após iniciar o servidor, o site estará completamente funcional.

1️⃣ Criar conta

O usuário pode criar uma conta fornecendo:

Nome

Email

Senha

Também é possível fazer:

Login tradicional

Login com Google

2️⃣ Login

Após criar a conta, o usuário pode entrar no sistema.

O login cria uma sessão Flask, permitindo acessar áreas privadas do site.

3️⃣ Escolher um plano

O usuário pode selecionar um plano mensal de refeições.

Cada plano possui características como:

quantidade de refeições

valor mensal

4️⃣ Definir entrega

Durante a assinatura o usuário informa:

Endereço de entrega

Dia da entrega

Essas informações são armazenadas no banco de dados.

5️⃣ Gerenciar assinatura

Após contratar o plano, o usuário pode acessar seu perfil, onde pode visualizar:

plano contratado

dados da assinatura

informações de entrega

🗄 Estrutura básica do projeto

Exemplo de organização:

/projeto
│
├── app.py
├── database.sql
│
├── static
│   ├── css
│   ├── js
│
├── templates
│   ├── login.html
│   ├── cadastro.html
│   ├── planos.html
│   ├── perfil.html
│
└── README.md
🔐 Sistema de autenticação

O sistema utiliza:

Sessões Flask

Cookies

Fetch API com credentials

Exemplo:

fetch("/perfil", {
  credentials: "include"
})

Isso garante que apenas usuários autenticados possam acessar certas rotas.

📌 Funcionalidades implementadas

✔ Cadastro de usuário
✔ Login com sessão
✔ Login com Google
✔ Sistema de assinatura mensal
✔ Definição de endereço de entrega
✔ Escolha de dia de entrega
✔ Integração com banco MySQL
✔ Área de perfil do usuário

👨‍💻 Autor

Projeto desenvolvido por Pedro Oliveira
Estudante de Engenharia de Software.
