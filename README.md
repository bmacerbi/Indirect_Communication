# Laboratório #6 -- Eleição e Coordenação Distribuída
## Integrantes: Bruno Menegaz, Gustavo Dutra, Leonardo Albergaria
---
## **Instruções para Compilação e Execução**

### **Inicializando Ambiente**

Para realizar a instalação, o primeiro passo é clonar o repositório para um diretório local e instalar o python em conjunto das bibliotecas utilizadas. Para realizar o download de todas as dependências, basta utilizando o seguinte comando:

```
$ pip3 install -r requirements.txt
```

Em sequência, é necessário realizar a instalação do broker *EMQX* caso deseje executar o projeto utilizando um broker local. Para isso basta acessar o link e seguir as instruções para o seu sistema operacional:

> https://www.emqx.com/en/try?product=broker

### **Execução**

Para realizar a execução do projeto, o primeiro passo é inicializar o *EMQX* caso você tenha feito a sua instalação. Para isso basta entrar com a seguinte linha de comando linux:

```
$ sudo emqx start
```

Em sequência, podemos inicializar a aplicação por meio da seguinte chamada, onde o <ip_do_broker> será **127.0.0.1** caso ele tenha sido instanciado localmente:

```
$ python3 application.py <número_de_clients> <ip_do_broker>
```

Por fim, caso queire finalizar o *EMQX* ao final da execução, podemos chamar o seguinte comando:

```
$ sudo emqx stop
```

---
## **Link para o vídeo no Youtube**

> https://youtu.be/8Gfp4N2vZuM

---
## **Implementação**

---
## **Resultados**

Para demonstrarmos alguns resultados da aplicação, resolvemos por executar um ambiente com **4** clientes e um broker local. A partir daí, iremos exibir o comportamento do sistema, visto que aplicações gráficas não se encaixam bem nesse contexto.

Podemos dividir a execução do sistema em dois estágios, eleição e mineiração. No primeiro momento os processos irão realizar uma votação para eleger um cliente controlador, podemos visualizar o resultado dessa votação na *imagem 1*, onde cada cliente irá exibir uma lista com os votos de todos os participantes, tais votos são computados e o **ID** com mais pontos é eleito o controlador.

> ![Imagem 1](results/eleicao.png)

Visualiza-se no exemplo acima a exibição dessas listas, onde cada elemento representa um voto, sendo o primeiro **ID** do **votante** e o segundo **ID** do **votado**, sendo assim, a partir dessa execução, podemos chegar na seguinte tabela de eleição:

- Client **56834** recebeu 0 votos
- Client **4118** recebeu 0 votos
- Client **8363** recebeu 2 votos
  - De **4118** e **8363**
- Client **60513** recebeu 2 votos
  - De **56834** e **60513**

Podemos ver que um impate ocorreu! Nesse caso escolhemos o cliente com maior ID como critério de desempate, dessa forma o processo **60513** foi eleito o controlador.

Prosseguimos agora para o segundo estado do sistema, a mineiração, exibido na *imagem 2*. Visualizamos a primeira ação sendo do controlador, que é a exibição da tabela de desafios, nesse caso contendo **1** desafio de dificuldade **19**. Em sequência os mineradores irão receber a mensagem e iniciar a busca por uma solução.

Quando o desafio é solucionado, o controlador exibe a tabela atualizada com a solução enviada e o ID do vencedor. Nesse caso o ID que primeiro solucionou o problema foi o cliente **8363**, com a respota **eaTKaDJRV9**. Em sequência, publica-se a mensagem que o desafio foi solucionado e os mineradores irão atualizar as suas tabelas própias, contabilizando uma vitória ou uma derrota. 

> ![Imagem 2](results/mineracao.png)

A partir desse estágio, podemos prosseguir postando mais desafios ou sair da aplicação com o caractere 'e'.

## **Conclusão**
