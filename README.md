# AutoMacro Studio Pro

Aplicativo para Windows desenvolvido para gravação e reprodução automatizada de eventos de mouse e teclado com preservação exata de temporização (delays em milissegundos).

---

## 1. Visão Geral

O AutoMacro Studio Pro captura e reproduz com precisão:
- Movimentos contínuos do cursor (coordenadas X e Y).
- Cliques do mouse (botão esquerdo, direito e central, incluindo pressionamento e soltura).
- Rolagem de scroll do mouse (eixos vertical e horizontal).
- Digitação de teclado (caracteres alfanuméricos, símbolos e teclas modificadoras como Shift, Ctrl, Alt, Enter, etc.).
- Intervalos exatos decorridos entre cada interação.

O sistema opera de forma autônoma e não exige ambiente de desenvolvimento ou interpretador Python instalado no computador do usuário final.

---

## 2. Requisitos do Sistema

- Sistema Operacional: Windows 10 ou Windows 11 (64 bits).
- Privilégios: Usuário padrão (não requer privilégios de administrador).
- Espaço em disco: Aproximadamente 25 MB livres.

---

## 3. Instruções de Instalação e Execução

### 3.1. Modo Executável (Usuário Final - Sem necessidade de Python)

Este é o modo recomendado para uso direto em qualquer máquina. Não requer instalação prévia de dependências.

1. Baixe ou acesse a pasta da aplicação.
2. Para criar o atalho oficial na Área de Trabalho:
   - Dê dois cliques no arquivo `Instalar_Atalho_Area_de_Trabalho.bat`.
   - Um atalho chamado **AutoMacro Studio Pro** será gerado automaticamente na sua Área de Trabalho.
3. Para iniciar a aplicação:
   - Dê dois cliques no atalho gerado na Área de Trabalho ou execute diretamente o arquivo `AutoMacroStudio.exe`.

---

### 3.2. Modo Código-Fonte (Desenvolvedores)

Caso queira executar ou modificar diretamente os scripts em Python:

1. Requisitos: Python 3.10 ou superior instalado.
2. Instalação das dependências necessárias via terminal:
   ```bash
   pip install customtkinter pynput pillow
   ```
3. Execução da interface gráfica:
   ```bash
   python app_ui.py
   ```
4. Alternativamente, para executar a versão simplificada via linha de comando:
   ```bash
   python gravador_macro.py
   ```

---

## 4. Teclas de Atalho Globais

Os atalhos funcionam globalmente no Windows, mesmo quando o painel do aplicativo estiver em segundo plano ou minimizado:

- **F6**: Iniciar gravação / Encerrar gravação.
- **F7**: Iniciar reprodução da macro carregada.
- **ESC**: Parada de emergência imediata (interrompe qualquer execução em andamento).

---

## 5. Guia de Operação da Interface

### Gravação de Ações
1. No painel à esquerda, configure os filtros desejados (captura de cliques, rolagem, movimento contínuo do mouse ou digitação).
2. Defina o tempo de contagem regressiva (de 0 a 5 segundos) para posicionar o cursor antes do início.
3. Clique em "Iniciar Gravação" ou pressione a tecla **F6**.
4. Realize normalmente a sequência de ações desejada no computador.
5. Pressione **F6** para finalizar. A gravação será salva automaticamente no arquivo padrão.

### Reprodução de Ações
1. No painel à direita, ajuste as opções de execução:
   - **Repetições**: Informe o número de vezes a executar ou marque a opção de "Loop Infinito".
   - **Velocidade**: Ajuste o controle deslizante (ex: 1.0x para tempo idêntico, 2.0x para o dobro da velocidade).
   - **Pausa entre ciclos**: Intervalo de espera em segundos entre cada repetição.
2. Clique em "Reproduzir Macro" ou pressione **F7**.
3. Para interromper a execução antes do término, pressione a tecla **ESC**.

### Gerenciamento de Arquivos
- **Salvar Como**: Permite nomear e armazenar rotinas específicas no formato JSON na pasta `macros/`.
- **Carregar Arquivo**: Importa rotinas previamente salvas.
- **Abrir Pasta de Macros**: Abre o diretório do sistema onde os arquivos JSON estão armazenados.
- **Sempre no Topo**: Fixa a janela do aplicativo sobre as demais janelas do sistema operacional.

---

## 6. Estrutura dos Arquivos do Projeto

- `AutoMacroStudio.exe`: Executável independente compilado para Windows.
- `Instalar_Atalho_Area_de_Trabalho.bat`: Script de instalação do atalho na Área de Trabalho.
- `app_ui.py`: Código-fonte da interface gráfica (CustomTkinter).
- `gravador_macro.py`: Código-fonte do motor de automação (modo console).
- `iniciar.bat`: Inicializador alternativo via script em lote.
- `macros/`: Diretório de armazenamento dos arquivos de automação gravados (.json).
- `README.md`: Documentação técnica do sistema.
