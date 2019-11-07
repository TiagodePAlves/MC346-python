# Projeto de Python - Paradigmas de Programação (MC346)

## Alunos

- [João Victor Flores da Costa](mailto:j199818@dac.unicamp.br) (199818)
- [Tiago de Paula Alves](mailto:t187679@dac.unicamp.br) (187679)

## Enunciado do Projeto

 Escreva um programa em Python que vai calcular o caminho mais rápido (e o segundo mais rápido) na média entre uma origem em um destino dado. O programa recebe um grafo direcionado e informação sobre a distancia e velocidade máxima na aresta, e recebe também várias medições sobre a velocidade real das arestas deve calcular o cominho mais rápido na média e o segundo mais rápido na média (assumindo que o motorista andará na maior velocidade permitida em cada aresta) entre uma origem e um destino dados.

Os dados tem a seguinte forma:

```text
25.0
aa b 0.4
aa c 0.5 50.0
b d 1.2
b z 0.2
z f4 0.3 40.0

aa b 12.5 11.3 10.2 15.3 12.0
aa c 4.1 4.3 4.7
z f4 19.0
b z 0
aa
z
```

A primeira linha indica a velocidade máxima default nas ruas da cidade, neste caso, se não ha indicação de velocidade máxima na rua, assume-se que seja 25k/h e que o motorista vai dirigir a 25 k/h

As linhas seguintes são as arestas direcionadas que possuem 3 ou quatro valores. Os dois primeiros são os vértices. O terceiro valor é a distancia em quilômetros entre os vértices. Se houver um quarto valor ele é a velocidade máxima naquele trecho e naquele sentido. O fato da velocidade máxima entre `a` e `c` ser 50k/h não significa que ele seja a velocidade no sentido de `c` para `a`. Na verdade pode não haver uma aresta de `c` para `a` (ou seja esse trecho da rua é mão única).

Ao final do grafo haverá uma linha sem dados. A partir deste ponto os dados indicam diferentes medidas de velocidades atuais nas arestas. Nos últimos 10 minutos, a velocidade de usuários do Waze de `aa` para `b` foram medidas como 12.5, 11.3, 10.2, 15.3 e 12.0 k/h. O sistema assume que alguma as dessas sejam a velocidade máxima (neste momento) nessas arestas. Note que nem todas as arestas terão uma linha de atualização da sua velocidade real. Note também que algumas ruas podem ter velocidade máxima de 0k/h ou seja a rua esta fechada e aquela aresta temporariamente não existe.

Finalmente haverá duas linhas com a origem (`aa`) e o destino (`z`).

Calcule o caminho mais rápido (na média) e o segundo mais rapido (como alternativa p/ o motorista) o entre a origem e o destino.

Dado que voce não sabe realmente a velocidade máxima em algumas arestas, o sue programa deve trabalhar com amostragens. Selecione aleatoriamente uma das velocidades para cada uma das arestas que tem varias velocidades. Com essa amostra, voce usar o Dykstra para calcular o caminho mais rapido da origem para o destino. Vamos assumir que é o caminho aa, b, c, z e que o tempo de transito é de 24.3 minutos.

Amostre novamente as velocidades e recalcule o caminho mais rapido. Vamos dizer que neste caso é `a`,`e`,`f`,`zz` com tempo 22.7 min. Repita o processo e neste terceiro caso, o caminho mais rapido é de novo `aa`, `b`, `c`, `z` com tempo de 29.4 minutos.

Repita o processo de amonstragem aleatória e calculo do caminho mais rapido 100 vezes. Ao final voce terá varios caminhos, com varias medidas do tempo de transito. Retorne o caminho com menor média do tempo de transito e o caminho com a segunda menor media no tempo de transito. Note que o segundo melhor caminho não é o segundo melhor caminho de cada Dykstra, é o melhor caminho de cada Dikstra que tem a segunda melhor média nas amostragens.

Para os dois caminhos, imprima o tempo de transito **em minutos** com 1 casa decimal, e na próxima linha a sequencia de vértices, da origem ate o destino separados por um espaço.

Por exemplo:

```text
18.6
a b d e g z
```

indica que o tempo de transito será de 18.6 minutos e que o caminho mais rápido é de `a` para `b` para `d` … até `z`

Seu programa será executado como

```bash
python3 prog3.py < arq1.in
```

Ou seja, você precisa chamar o programa de `prog3.py` e precisa ter as linhas no final:

```python
if __name__ == "__main__":
    funcprincipa()
```

que indica que o Python executará funcprincipal (use o nome que vc quiser) como a primeira chamada do programa.
