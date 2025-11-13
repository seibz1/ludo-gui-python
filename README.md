# 🎲 Ludo GUI: Jogo de Tabuleiro em Python

![Language](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![GUI](https://img.shields.io/badge/Interface-Tkinter-success?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Concluído-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

Uma implementação completa, visual e interativa do clássico jogo de tabuleiro **Ludo**, desenvolvida inteiramente em Python utilizando a biblioteca nativa `Tkinter`.

O projeto se destaca pelo uso de **Multithreading** para gerenciar a lógica do jogo e as animações simultaneamente, garantindo uma experiência fluida sem travamentos na interface.

---


## ✨ Funcionalidades

Este projeto implementa as regras oficiais do Ludo com uma interface gráfica amigável:

* **Tabuleiro Visual Completo:** Grade 15x15 renderizada com precisão, incluindo bases coloridas, caminhos principais e retas finais.
* **Sistema de Dados:** Rolagem de dados aleatória com feedback visual.
* **Regras de Movimentação:**
    * 🔒 **Saída da Base:** O peão só sai da casa inicial ao tirar **6** no dado.
    * ⚔️ **Captura:** Peões adversários são enviados de volta para a base se capturados (exceto em zonas seguras).
    * 🛡️ **Zonas Seguras:** Casas marcadas com estrela (★) protegem os peões de captura.
    * 🔄 **Rodada Extra:** O jogador ganha uma nova vez ao tirar 6 ou capturar uma peça.
* **Animação Suave:** Os peões deslizam pelo tabuleiro (interpolação linear) ao invés de "teleportar", graças ao sistema de threads.
* **Condição de Vitória:** O jogo termina quando um jogador leva seus 4 peões ao centro do tabuleiro.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Interface Gráfica:** Tkinter (Canvas e Widgets)
* **Concorrência:** Módulo `threading` e `threading.Lock` para *Thread Safety*.

## 📂 Estrutura do Projeto

O código foi estruturado de forma modular para facilitar o estudo e a manutenção. O arquivo `coment.py` contém explicações detalhadas, divididas em 6 módulos lógicos:

1.  **Mapeamento Visual:** Constantes que traduzem a lógica do jogo para coordenadas (pixels) na tela.
2.  **Modelagem de Dados:** Classes `Pawn` (Peão) e `Player` (Jogador).
3.  **Lógica de Regras:** Validação de movimentos legais (`_get_valid_moves`).
4.  **Motor de Física/Trajetória:** Cálculo de rotas e waypoints para a animação.
5.  **Interface (GUI):** Classe `LudoBoardGUI` responsável pelo desenho e captura de cliques.
6.  **Controle de Estado:** Gerenciamento de turnos e sincronização de threads.

## 🚀 Como Executar

Não é necessária a instalação de bibliotecas externas (como Pygame ou NumPy), pois o projeto utiliza apenas bibliotecas padrão do Python.

### Pré-requisitos
* Python 3.x instalado.

### Passo a Passo

1.  Clone este repositório:
    ```bash
    git clone [https://github.com/SEU-USUARIO/ludo-gui-python.git](https://github.com/SEU-USUARIO/ludo-gui-python.git)
    ```
2.  Acesse a pasta do projeto:
    ```bash
    cd ludo-gui-python
    ```
3.  Execute o jogo:
    ```bash
    python final.py
    ```
    *(Ou execute `python coment.py` se quiser rodar a versão comentada)*

## 🕹️ Como Jogar

1.  Execute o script.
2.  O jogo inicia com o **Vermelho**.
3.  Clique no botão **"Rolar Dados"**.
4.  Se o resultado permitir um movimento, os peões válidos serão destacados em **Dourado**.
5.  Clique no peão desejado para movê-lo.
6.  O turno passa automaticamente para o próximo jogador (Verde -> Amarelo -> Azul), a menos que você tire um 6 ou capture uma peça.

---


---
<p align="center">
  <sub>Desenvolvido para fins educacionais.</sub>
</p>
