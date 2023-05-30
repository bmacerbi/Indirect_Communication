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

## **Conclusão**
